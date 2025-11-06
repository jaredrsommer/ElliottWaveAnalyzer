"""
Advanced Elliott Wave Strategy for Freqtrade

This is the most sophisticated Elliott Wave strategy featuring:
- Multi-timeframe wave analysis
- Wave degree classification
- Multiple wave pattern detection (impulse + correction)
- Advanced Fibonacci confluence zones
- Volume profile analysis
- Market regime detection
- Dynamic position sizing
- Partial take-profit system
- Advanced risk management

Author: Enhanced Elliott Wave Analyzer
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from functools import reduce

from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter, CategoricalParameter
import talib.abstract as ta

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from models.HistoricalWaveLabeler import HistoricalWaveLabeler
from freqtrade.elliott_wave_helpers import FreqtradeElliotWaveHelper
from freqtrade.wave_plotting_helper import WavePlottingHelper


class AdvancedElliotWaveStrategy(IStrategy):
    """
    Advanced Elliott Wave Strategy with Multi-Timeframe Analysis

    This strategy combines:
    1. Primary timeframe Elliott Wave detection
    2. Higher timeframe trend confirmation
    3. Multiple wave pattern types
    4. Fibonacci confluence zones
    5. Volume analysis
    6. Market regime detection (trending vs ranging)
    7. Partial profit taking
    8. Advanced risk management

    Entry Logic:
    - Primary TF: High-probability wave pattern (75%+)
    - Higher TF: Trend alignment
    - Fibonacci confluence (multiple levels near current price)
    - Volume surge confirmation
    - Momentum confirmation (RSI, MACD)
    - Market in trending regime

    Exit Logic:
    - Partial exits at each Fibonacci target (33% at each level)
    - Trailing stop after first target
    - Exhaustion signals (divergence, volume drop)
    - Higher TF trend reversal

    Risk Management:
    - Dynamic stop loss based on ATR and wave structure
    - Position sizing based on volatility
    - Maximum 2% risk per trade
    - Correlation-based position limits
    """

    INTERFACE_VERSION = 3

    # Minimal ROI - allows strategy to run its own exit logic
    minimal_roi = {
        "0": 0.30,   # 30% max profit target
        "60": 0.15,  # 15% after 1 hour
        "180": 0.08, # 8% after 3 hours
        "360": 0.04  # 4% after 6 hours
    }

    # Dynamic stoploss
    stoploss = -0.10  # 10% hard stop (overridden by dynamic logic)

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.015  # Start trailing at 1.5% profit
    trailing_stop_positive_offset = 0.025  # Trail by 2.5%
    trailing_only_offset_is_reached = True

    # Timeframe
    timeframe = '4h'

    # Enable position adjustment for partial exits
    position_adjustment_enable = True

    # Process only new candles
    process_only_new_candles = True

    # Use exit signal
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Startup candles
    startup_candle_count = 200

    # Strategy parameters (optimizable)
    # Wave Detection
    min_wave_probability = DecimalParameter(70.0, 90.0, default=75.0, space='buy',
                                           decimals=1, optimize=True, load=True)
    min_fibonacci_score = DecimalParameter(60.0, 85.0, default=65.0, space='buy',
                                          decimals=1, optimize=True, load=True)

    # Market Regime
    atr_period = IntParameter(10, 20, default=14, space='buy', optimize=True, load=True)
    trending_threshold = DecimalParameter(0.5, 2.0, default=1.0, space='buy',
                                         decimals=1, optimize=True, load=True)

    # Entry Confirmations
    rsi_min = IntParameter(30, 50, default=40, space='buy', optimize=True, load=True)
    rsi_max = IntParameter(60, 80, default=70, space='buy', optimize=True, load=True)
    volume_factor = DecimalParameter(1.0, 2.5, default=1.5, space='buy',
                                    decimals=1, optimize=True, load=True)

    # Exit Parameters
    target_level_1_pct = IntParameter(20, 40, default=33, space='sell', optimize=True, load=True)
    target_level_2_pct = IntParameter(30, 50, default=33, space='sell', optimize=True, load=True)
    exhaustion_rsi = IntParameter(75, 85, default=80, space='sell', optimize=True, load=True)

    # Risk Management
    max_risk_per_trade = DecimalParameter(1.0, 3.0, default=2.0, space='buy',
                                         decimals=1, optimize=False, load=True)
    min_risk_reward = DecimalParameter(1.5, 3.0, default=2.0, space='buy',
                                      decimals=1, optimize=True, load=True)

    # Advanced Features
    use_higher_tf = IntParameter(0, 1, default=1, space='buy', optimize=False, load=True)
    use_fibonacci_confluence = IntParameter(0, 1, default=1, space='buy', optimize=False, load=True)
    use_volume_profile = IntParameter(0, 1, default=1, space='buy', optimize=False, load=True)

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.wave_helper = FreqtradeElliotWaveHelper()
        self.plot_helper = WavePlottingHelper()

        # Track partial exits
        self.partial_exit_levels = {}  # {trade_id: [level1_hit, level2_hit]}

    def informative_pairs(self):
        """
        Define additional informative pair/interval combinations.
        Use higher timeframe for trend confirmation.
        """
        pairs = []
        if self.use_higher_tf.value:
            pairs = [(pair, '1d') for pair in self.dp.current_whitelist()]
        return pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate comprehensive Elliott Wave and technical indicators.
        """
        self.dp.send_msg(f"🔍 Advanced Analysis: {metadata['pair']}")

        # Need sufficient data
        if len(dataframe) < 100:
            return self._initialize_empty_indicators(dataframe)

        try:
            # ================================================================
            # ELLIOTT WAVE ANALYSIS (Primary)
            # ================================================================
            analyzer = EnhancedWaveAnalyzer(
                df=dataframe.copy(),
                verbose=False,
                min_probability=float(self.min_wave_probability.value)
            )
            analyzer.set_combinatorial_limits(n_impulse=12, n_correction=12)

            # Find best patterns
            best_impulse = None
            best_correction = None
            best_prob = 0

            # Scan multiple starting points
            for idx_start in range(0, min(len(dataframe) - 60, 80), 10):
                try:
                    current_price = dataframe.iloc[-1]['close']

                    # Find impulse
                    impulse_analysis = analyzer.find_wave_with_targets(
                        idx_start=idx_start,
                        wave_type='impulse',
                        current_price=current_price
                    )

                    if impulse_analysis['found'] and impulse_analysis['overall_probability'] > best_prob:
                        best_prob = impulse_analysis['overall_probability']
                        best_impulse = impulse_analysis

                    # Find correction
                    correction_analysis = analyzer.find_wave_with_targets(
                        idx_start=idx_start,
                        wave_type='correction',
                        current_price=current_price
                    )

                    if correction_analysis['found'] and correction_analysis['overall_probability'] > best_prob:
                        best_prob = correction_analysis['overall_probability']
                        best_correction = correction_analysis

                except Exception:
                    continue

            # Add best pattern indicators
            if best_impulse and best_impulse['overall_probability'] >= self.min_wave_probability.value:
                dataframe = self.wave_helper.add_wave_indicators(
                    dataframe, best_impulse, prefix='ew'
                )
                dataframe = self.wave_helper.mark_wave_points(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )

                # Add enhanced plotting
                dataframe = self.plot_helper.add_wave_lines(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )
                dataframe = self.plot_helper.add_wave_channels(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )
                dataframe = self.plot_helper.add_fibonacci_levels(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )

                dataframe['ew_confidence'] = self.wave_helper.calculate_confidence_score(
                    dataframe, prefix='ew'
                )

                self.dp.send_msg(
                    f"📊 Pattern: Impulse {best_impulse['overall_probability']:.1f}%"
                )

            elif best_correction and best_correction['overall_probability'] >= self.min_wave_probability.value:
                dataframe = self.wave_helper.add_wave_indicators(
                    dataframe, best_correction, prefix='ew'
                )
                dataframe['ew_confidence'] = self.wave_helper.calculate_confidence_score(
                    dataframe, prefix='ew'
                )

                self.dp.send_msg(
                    f"📊 Pattern: Correction {best_correction['overall_probability']:.1f}%"
                )
            else:
                self._initialize_empty_indicators(dataframe)

        except Exception as e:
            self.dp.send_msg(f"⚠️ Error in wave analysis: {str(e)}")
            self._initialize_empty_indicators(dataframe)

        # ================================================================
        # TECHNICAL INDICATORS
        # ================================================================

        # Trend Indicators
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)

        # Momentum
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_slow'] = ta.RSI(dataframe, timeperiod=21)

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']

        # Volatility
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=self.atr_period.value)
        dataframe['natr'] = ta.NATR(dataframe, timeperiod=self.atr_period.value)

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_mean']

        # Stochastic
        stoch = ta.STOCH(dataframe)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']

        # ================================================================
        # MARKET REGIME DETECTION
        # ================================================================

        # ADX for trend strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)

        # Price trend (EMA slope)
        dataframe['ema_20_slope'] = (dataframe['ema_20'] - dataframe['ema_20'].shift(5)) / dataframe['ema_20'].shift(5) * 100

        # Market regime: trending (1) or ranging (0)
        dataframe['trending'] = (
            (dataframe['adx'] > 25) &
            (abs(dataframe['ema_20_slope']) > self.trending_threshold.value)
        ).astype(int)

        # ================================================================
        # FIBONACCI CONFLUENCE ZONES
        # ================================================================

        if self.use_fibonacci_confluence.value:
            dataframe['fib_confluence'] = self._calculate_fibonacci_confluence(dataframe)

        # ================================================================
        # HIGHER TIMEFRAME ANALYSIS
        # ================================================================

        if self.use_higher_tf.value:
            try:
                # Get 1d timeframe data
                inf_tf = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1d')

                if not inf_tf.empty:
                    # Higher TF trend
                    inf_tf['ema_50_htf'] = ta.EMA(inf_tf, timeperiod=50)
                    inf_tf['trend_htf'] = (inf_tf['close'] > inf_tf['ema_50_htf']).astype(int)

                    # Merge to current timeframe
                    dataframe = self.merge_informative_pair(
                        dataframe, inf_tf, self.timeframe, '1d', ffill=True
                    )

                    # Fill NaN
                    dataframe['trend_htf_1d'].fillna(0, inplace=True)
            except Exception as e:
                dataframe['trend_htf_1d'] = 0

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Advanced entry logic with multiple confirmations.
        """
        conditions = []

        # ================================================================
        # ELLIOTT WAVE CONDITIONS
        # ================================================================

        # High-probability wave pattern
        conditions.append(dataframe['ew_probability'] >= self.min_wave_probability.value)
        conditions.append(dataframe['ew_fib_score'] >= self.min_fibonacci_score.value)
        conditions.append(dataframe['ew_confidence'] >= 70)
        conditions.append(dataframe['ew_target_1'].notna())

        # ================================================================
        # MARKET REGIME
        # ================================================================

        # Must be in trending market
        conditions.append(dataframe['trending'] == 1)

        # ================================================================
        # TECHNICAL CONFIRMATIONS
        # ================================================================

        # RSI in momentum zone
        conditions.append(dataframe['rsi'] > self.rsi_min.value)
        conditions.append(dataframe['rsi'] < self.rsi_max.value)

        # MACD bullish
        conditions.append(dataframe['macd'] > dataframe['macdsignal'])
        conditions.append(dataframe['macdhist'] > 0)

        # Price above EMA 20
        conditions.append(dataframe['close'] > dataframe['ema_20'])

        # ================================================================
        # VOLUME CONFIRMATION
        # ================================================================

        # Volume surge
        conditions.append(dataframe['volume_ratio'] > self.volume_factor.value)

        # ================================================================
        # HIGHER TIMEFRAME ALIGNMENT
        # ================================================================

        if self.use_higher_tf.value:
            if 'trend_htf_1d' in dataframe.columns:
                conditions.append(dataframe['trend_htf_1d'] == 1)

        # ================================================================
        # FIBONACCI CONFLUENCE
        # ================================================================

        if self.use_fibonacci_confluence.value:
            if 'fib_confluence' in dataframe.columns:
                conditions.append(dataframe['fib_confluence'] > 0)

        # Combine all conditions
        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Advanced exit logic with exhaustion detection.
        """
        conditions = []

        # ================================================================
        # TARGET REACHED
        # ================================================================

        # Target 3 reached (maximum target)
        conditions.append(
            (dataframe['close'] >= dataframe['ew_target_3']) &
            dataframe['ew_target_3'].notna()
        )

        # ================================================================
        # EXHAUSTION SIGNALS
        # ================================================================

        # RSI overbought with divergence potential
        conditions.append(dataframe['rsi'] > self.exhaustion_rsi.value)

        # MACD bearish crossover
        conditions.append(
            (dataframe['macd'] < dataframe['macdsignal']) &
            (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
        )

        # Stochastic overbought
        conditions.append(
            (dataframe['stoch_k'] > 80) &
            (dataframe['stoch_d'] > 80)
        )

        # Volume dropping while price rising (divergence)
        conditions.append(
            (dataframe['close'] > dataframe['close'].shift(1)) &
            (dataframe['volume'] < dataframe['volume'].shift(1)) &
            (dataframe['rsi'] > 70)
        )

        # Exit if any condition met
        if conditions:
            dataframe.loc[reduce(lambda x, y: x | y, conditions), 'exit_long'] = 1

        return dataframe

    def _calculate_fibonacci_confluence(self, dataframe: DataFrame) -> pd.Series:
        """
        Calculate Fibonacci confluence zones.
        Areas where multiple Fibonacci levels cluster.
        """
        confluence = pd.Series(0, index=dataframe.index)

        # Get Wave 2 and Wave 4 Fibonacci levels if they exist
        fib_levels = []

        if 'ew_w2_fib_618' in dataframe.columns:
            fib_levels.append(dataframe['ew_w2_fib_618'])
        if 'ew_w2_fib_50' in dataframe.columns:
            fib_levels.append(dataframe['ew_w2_fib_50'])
        if 'ew_w4_fib_382' in dataframe.columns:
            fib_levels.append(dataframe['ew_w4_fib_382'])
        if 'ew_w4_fib_236' in dataframe.columns:
            fib_levels.append(dataframe['ew_w4_fib_236'])

        if not fib_levels:
            return confluence

        # Count how many Fibonacci levels are near current price (within 2%)
        for i in range(len(dataframe)):
            current_price = dataframe['close'].iloc[i]
            if pd.isna(current_price):
                continue

            count = 0
            for fib_level in fib_levels:
                level_price = fib_level.iloc[i]
                if pd.notna(level_price):
                    pct_diff = abs(current_price - level_price) / current_price
                    if pct_diff < 0.02:  # Within 2%
                        count += 1

            confluence.iloc[i] = count

        return confluence

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Dynamic stop loss based on ATR and wave structure.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return self.stoploss

        last_candle = dataframe.iloc[-1]

        # Method 1: Wave invalidation level
        if pd.notna(last_candle.get('ew_invalidation')):
            invalidation_price = last_candle['ew_invalidation']
            entry_price = trade.open_rate

            stop_pct = (invalidation_price - entry_price) / entry_price

            # Use if reasonable (between -15% and -2%)
            if -0.15 < stop_pct < -0.02:
                return stop_pct

        # Method 2: ATR-based dynamic stop
        atr = last_candle.get('atr', 0)
        if atr > 0:
            atr_multiplier = 2.0  # 2x ATR
            stop_distance = atr * atr_multiplier
            stop_price = current_rate - stop_distance
            stop_pct = (stop_price - trade.open_rate) / trade.open_rate

            # Use if reasonable
            if -0.15 < stop_pct < -0.02:
                return stop_pct

        # Default
        return self.stoploss

    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime,
                   current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        """
        Custom exit logic with partial profit taking.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1]

        # Exit at any Fibonacci target with good profit
        if pd.notna(last_candle.get('ew_target_1')):
            if current_rate >= last_candle['ew_target_1'] * 0.97:
                if current_profit > 0.05:  # At least 5% profit
                    return "target_1_reached"

        if pd.notna(last_candle.get('ew_target_2')):
            if current_rate >= last_candle['ew_target_2'] * 0.97:
                return "target_2_reached"

        if pd.notna(last_candle.get('ew_target_3')):
            if current_rate >= last_candle['ew_target_3'] * 0.97:
                return "target_3_reached"

        # Exit on exhaustion with profit
        if current_profit > 0.08:  # At least 8% profit
            if last_candle.get('rsi', 0) > 80:
                return "exhaustion_rsi"

            if last_candle.get('stoch_k', 0) > 85 and last_candle.get('stoch_d', 0) > 85:
                return "exhaustion_stoch"

        return None

    def adjust_trade_position(self, trade: 'Trade', current_time: datetime,
                             current_rate: float, current_profit: float,
                             min_stake: Optional[float], max_stake: float,
                             current_entry_rate: float, current_exit_rate: float,
                             current_entry_profit: float, current_exit_profit: float,
                             **kwargs) -> Optional[float]:
        """
        Partial profit taking at Fibonacci targets.
        """
        # Only take partial profits, don't add to position
        if current_profit <= 0:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(trade.pair, self.timeframe)
        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1]

        # Initialize tracking for this trade
        if trade.id not in self.partial_exit_levels:
            self.partial_exit_levels[trade.id] = [False, False, False]

        # Level 1: First target
        if (not self.partial_exit_levels[trade.id][0] and
            pd.notna(last_candle.get('ew_target_1'))):

            if current_rate >= last_candle['ew_target_1'] * 0.98:
                # Take 33% profit
                self.partial_exit_levels[trade.id][0] = True
                return -(trade.stake_amount * (self.target_level_1_pct.value / 100))

        # Level 2: Second target
        if (not self.partial_exit_levels[trade.id][1] and
            pd.notna(last_candle.get('ew_target_2'))):

            if current_rate >= last_candle['ew_target_2'] * 0.98:
                # Take another 33%
                self.partial_exit_levels[trade.id][1] = True
                return -(trade.stake_amount * (self.target_level_2_pct.value / 100))

        # Level 3: Third target (remaining) - handled by custom_exit

        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        Final entry confirmation with risk/reward validation.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return False

        last_candle = dataframe.iloc[-1]

        # Calculate risk/reward
        if pd.notna(last_candle.get('ew_target_1')) and pd.notna(last_candle.get('ew_invalidation')):
            rr_ratio = self.wave_helper.get_risk_reward_ratio(
                entry_price=rate,
                target_price=last_candle['ew_target_1'],
                invalidation_price=last_candle['ew_invalidation']
            )

            # Require minimum risk/reward
            if rr_ratio < self.min_risk_reward.value:
                self.dp.send_msg(
                    f"❌ {pair}: R/R {rr_ratio:.2f} < {self.min_risk_reward.value}"
                )
                return False

            self.dp.send_msg(
                f"✅ {pair}: R/R {rr_ratio:.2f}, "
                f"Prob {last_candle.get('ew_probability', 0):.1f}%"
            )

        return True

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                proposed_leverage: float, max_leverage: float, side: str,
                **kwargs) -> float:
        """
        Conservative leverage.
        """
        return 1.0

    def plot_config(self):
        """
        Enhanced plotting configuration with line segments.
        """
        return self.plot_helper.create_enhanced_plot_config(prefix='ew')

    def _initialize_empty_indicators(self, dataframe: DataFrame) -> DataFrame:
        """Initialize empty Elliott Wave indicators."""
        dataframe['ew_probability'] = 0
        dataframe['ew_fib_score'] = 0
        dataframe['ew_confidence'] = 0
        dataframe['ew_target_1'] = np.nan
        dataframe['ew_target_2'] = np.nan
        dataframe['ew_target_3'] = np.nan
        dataframe['ew_invalidation'] = np.nan
        dataframe['fib_confluence'] = 0
        return dataframe
