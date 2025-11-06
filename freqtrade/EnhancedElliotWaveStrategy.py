"""
Enhanced Elliott Wave Strategy for Freqtrade

This strategy uses the Enhanced Elliott Wave Analyzer to identify high-probability
wave patterns and trade based on Fibonacci targets and probability scoring.

Author: Enhanced Elliott Wave Analyzer
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import models
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import numpy as np
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Dict, List, Optional

from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import talib.abstract as ta

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from freqtrade.elliott_wave_helpers import FreqtradeElliotWaveHelper


class EnhancedElliotWaveStrategy(IStrategy):
    """
    Enhanced Elliott Wave Strategy

    This strategy identifies Elliott Wave patterns with probability scoring
    and trades based on high-probability setups with Fibonacci targets.

    Entry Logic:
    - Find impulse wave patterns with probability >= min_wave_probability
    - Fibonacci score >= min_fibonacci_score
    - Enter on Wave 4 completion expecting Wave 5
    - Or enter after completed 12345 + ABC correction expecting new impulse

    Exit Logic:
    - Take profit at Fibonacci targets (Wave 5 projections)
    - Stop loss at invalidation level (Wave 1 high for impulse)
    - Trailing stop to protect profits

    Risk Management:
    - Position sizing based on invalidation distance
    - Risk/Reward ratio minimum 1.5:1
    - Maximum 2% risk per trade
    """

    # Strategy metadata
    INTERFACE_VERSION = 3

    # Minimal ROI designed for Elliott Wave targets
    minimal_roi = {
        "0": 0.15,   # 15% profit target
        "30": 0.10,  # 10% after 30 minutes
        "60": 0.05,  # 5% after 1 hour
        "120": 0.02  # 2% after 2 hours
    }

    # Stoploss
    stoploss = -0.05  # 5% hard stop (will be overridden by dynamic stop)

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.02  # Start trailing at 2% profit
    trailing_stop_positive_offset = 0.03  # Trail by 3%
    trailing_only_offset_is_reached = True

    # Timeframe
    timeframe = '1h'

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Strategy parameters
    min_wave_probability = DecimalParameter(60.0, 90.0, default=70.0, space='buy',
                                           decimals=1, optimize=True,
                                           load=True)

    min_fibonacci_score = DecimalParameter(50.0, 85.0, default=60.0, space='buy',
                                          decimals=1, optimize=True,
                                          load=True)

    target_level = IntParameter(1, 3, default=2, space='sell', optimize=True, load=True)

    use_volume_confirmation = IntParameter(0, 1, default=1, space='buy', optimize=False)

    # Wave analysis settings
    wave_combinatorial_limit = 12
    wave_scan_window = 100  # How many candles to look back

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.wave_helper = FreqtradeElliotWaveHelper()
        self.last_analysis_candle = 0

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached.
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate Elliott Wave indicators on the dataframe.

        This is the main function that integrates the Enhanced Wave Analyzer
        with Freqtrade.
        """
        self.dp.send_msg(f"Analyzing Elliott Waves for {metadata['pair']}...")

        # Only run analysis if we have enough data
        if len(dataframe) < 50:
            return dataframe

        try:
            # Create Enhanced Wave Analyzer
            analyzer = EnhancedWaveAnalyzer(
                df=dataframe.copy(),
                verbose=False,
                min_probability=float(self.min_wave_probability.value)
            )
            analyzer.set_combinatorial_limits(
                n_impulse=self.wave_combinatorial_limit,
                n_correction=self.wave_combinatorial_limit
            )

            # Scan for wave patterns
            # Look for impulse starting from various points
            scan_step = max(5, len(dataframe) // 20)  # Scan ~20 points
            start_points = range(0, min(len(dataframe) - 50, self.wave_scan_window), scan_step)

            best_impulse = None
            best_probability = 0

            for idx_start in start_points:
                try:
                    current_price = dataframe.iloc[-1]['close']

                    # Find impulse wave with targets
                    analysis = analyzer.find_wave_with_targets(
                        idx_start=idx_start,
                        wave_type='impulse',
                        current_price=current_price
                    )

                    if analysis['found']:
                        prob = analysis['overall_probability']
                        if prob > best_probability:
                            best_probability = prob
                            best_impulse = analysis

                except Exception as e:
                    # Continue scanning even if one point fails
                    continue

            # Add best found pattern to indicators
            if best_impulse:
                dataframe = self.wave_helper.add_wave_indicators(
                    dataframe, best_impulse, prefix='ew'
                )
                dataframe = self.wave_helper.mark_wave_points(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )
                dataframe = self.wave_helper.add_wave_labels(
                    dataframe, best_impulse.get('wave_pattern'), prefix='ew'
                )

                # Calculate confidence score
                dataframe['ew_confidence'] = self.wave_helper.calculate_confidence_score(
                    dataframe, prefix='ew'
                )

                self.dp.send_msg(
                    f"Found Elliott Wave pattern for {metadata['pair']}: "
                    f"Probability {best_probability:.1f}%"
                )
            else:
                # Initialize empty indicators
                dataframe['ew_probability'] = 0
                dataframe['ew_fib_score'] = 0
                dataframe['ew_confidence'] = 0
                dataframe['ew_target_1'] = np.nan
                dataframe['ew_target_2'] = np.nan
                dataframe['ew_target_3'] = np.nan

        except Exception as e:
            self.dp.send_msg(f"Error in Elliott Wave analysis: {str(e)}")
            # Initialize empty indicators on error
            dataframe['ew_probability'] = 0
            dataframe['ew_fib_score'] = 0
            dataframe['ew_confidence'] = 0

        # Add standard technical indicators for confirmation
        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_mean']

        # RSI for additional confirmation
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # MACD for trend confirmation
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # ATR for volatility
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on Elliott Wave analysis, populate the entry signal.

        Entry Conditions:
        1. High-probability Elliott Wave pattern detected
        2. Fibonacci score meets minimum threshold
        3. Valid target available
        4. RSI not overbought (< 70)
        5. Volume confirmation (optional)
        6. MACD bullish
        """
        conditions = []

        # Core Elliott Wave conditions
        conditions.append(dataframe['ew_probability'] >= self.min_wave_probability.value)
        conditions.append(dataframe['ew_fib_score'] >= self.min_fibonacci_score.value)
        conditions.append(dataframe['ew_target_1'].notna())

        # Technical confirmations
        conditions.append(dataframe['rsi'] < 70)  # Not overbought
        conditions.append(dataframe['rsi'] > 40)  # Not oversold (want momentum)

        # MACD bullish
        conditions.append(dataframe['macd'] > dataframe['macdsignal'])

        # Volume confirmation (optional)
        if self.use_volume_confirmation.value:
            conditions.append(dataframe['volume_ratio'] > 1.0)

        # Additional safety: ensure we have enough volatility (ATR-based)
        conditions.append(dataframe['atr'] > 0)  # Basic sanity check

        # Combine all conditions
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on Elliott Wave targets and invalidation levels, populate exit signal.

        Exit Conditions:
        1. Price reaches Fibonacci target
        2. RSI overbought (> 75) - potential Wave 5 exhaustion
        3. MACD bearish divergence
        4. Pattern invalidation level reached
        """
        conditions = []

        # Target reached (using selected target level)
        target_col = f'ew_target_{self.target_level.value}'
        if target_col in dataframe.columns:
            conditions.append(dataframe['close'] >= dataframe[target_col])

        # RSI overbought (Wave 5 exhaustion)
        conditions.append(dataframe['rsi'] > 75)

        # MACD bearish crossover
        conditions.append(
            (dataframe['macd'] < dataframe['macdsignal']) &
            (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
        )

        # Exit if any condition is met
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, conditions),
                'exit_long'
            ] = 1

        return dataframe

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        Additional entry confirmation based on risk/reward ratio.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return False

        last_candle = dataframe.iloc[-1]

        # Check if we have a target and invalidation level
        if pd.notna(last_candle.get('ew_target_1')) and pd.notna(last_candle.get('ew_invalidation')):
            # Calculate risk/reward ratio
            rr_ratio = self.wave_helper.get_risk_reward_ratio(
                entry_price=rate,
                target_price=last_candle['ew_target_1'],
                invalidation_price=last_candle['ew_invalidation']
            )

            # Only enter if risk/reward is favorable (minimum 1.5:1)
            if rr_ratio < 1.5:
                self.dp.send_msg(
                    f"Trade rejected for {pair}: "
                    f"Risk/Reward ratio {rr_ratio:.2f} below minimum 1.5"
                )
                return False

        return True

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss based on Elliott Wave invalidation level.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return self.stoploss

        last_candle = dataframe.iloc[-1]

        # If we have an invalidation level, use it as stop loss
        if pd.notna(last_candle.get('ew_invalidation')):
            invalidation_price = last_candle['ew_invalidation']
            entry_price = trade.open_rate

            # Calculate stop loss as percentage from entry
            stop_loss_pct = (invalidation_price - entry_price) / entry_price

            # Ensure stop loss is negative and not too tight
            if stop_loss_pct < 0 and stop_loss_pct > -0.15:  # Max 15% stop
                return stop_loss_pct

        # Default to configured stoploss
        return self.stoploss

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                proposed_leverage: float, max_leverage: float, side: str,
                **kwargs) -> float:
        """
        Conservative leverage for Elliott Wave strategy.
        """
        # Use 1x leverage (no leverage) for safety
        return 1.0

    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime,
                   current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        """
        Custom exit logic based on Elliott Wave targets.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) < 1:
            return None

        last_candle = dataframe.iloc[-1]

        # Exit at Target 1 with high confidence
        if pd.notna(last_candle.get('ew_target_1')):
            if current_rate >= last_candle['ew_target_1'] * 0.98:  # Within 2% of target
                return "target_1_reached"

        # Exit at Target 2 (partial exit could be implemented)
        if pd.notna(last_candle.get('ew_target_2')):
            if current_rate >= last_candle['ew_target_2'] * 0.98:
                return "target_2_reached"

        # Exit at Target 3 (maximum target)
        if pd.notna(last_candle.get('ew_target_3')):
            if current_rate >= last_candle['ew_target_3'] * 0.98:
                return "target_3_reached"

        # Exit if Wave 5 exhaustion signals
        if last_candle.get('rsi', 0) > 80 and current_profit > 0.05:
            return "wave5_exhaustion"

        return None

    def plot_config(self):
        """
        Configure plotting for Freqtrade.
        """
        plot_config = {
            'main_plot': {
                # Wave targets
                'ew_target_1': {'color': 'green', 'type': 'line'},
                'ew_target_2': {'color': 'lightgreen', 'type': 'line'},
                'ew_target_3': {'color': 'lime', 'type': 'line'},
                'ew_invalidation': {'color': 'red', 'type': 'line'},

                # Wave points
                'ew_wave1_high': {'color': 'blue', 'type': 'scatter'},
                'ew_wave2_low': {'color': 'orange', 'type': 'scatter'},
                'ew_wave3_high': {'color': 'blue', 'type': 'scatter'},
                'ew_wave4_low': {'color': 'orange', 'type': 'scatter'},
                'ew_wave5_high': {'color': 'blue', 'type': 'scatter'},
            },
            'subplots': {
                "Elliott Wave Scores": {
                    'ew_probability': {'color': 'blue'},
                    'ew_fib_score': {'color': 'green'},
                    'ew_confidence': {'color': 'purple'},
                },
                "RSI": {
                    'rsi': {'color': 'red'},
                },
                "MACD": {
                    'macd': {'color': 'blue'},
                    'macdsignal': {'color': 'orange'},
                },
            }
        }
        return plot_config


# Helper function for reduce
from functools import reduce
