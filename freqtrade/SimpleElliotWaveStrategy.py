"""
Simple Elliott Wave Strategy for Freqtrade

A simplified version of the Enhanced Elliott Wave Strategy for beginners.
Focuses on high-probability Wave 5 entries with clear targets and stops.

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
from typing import Optional
from functools import reduce

from freqtrade.strategy import IStrategy
import talib.abstract as ta

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from freqtrade.elliott_wave_helpers import FreqtradeElliotWaveHelper


class SimpleElliotWaveStrategy(IStrategy):
    """
    Simple Elliott Wave Strategy

    This is a beginner-friendly Elliott Wave strategy that:
    - Enters on high-probability impulse patterns (>75% probability)
    - Exits at first Fibonacci target
    - Uses invalidation level as stop loss
    - No complex optimizations or parameters

    Perfect for:
    - Learning Elliott Wave trading
    - Conservative trading approach
    - Understanding wave pattern behavior
    """

    INTERFACE_VERSION = 3

    # Simple ROI table
    minimal_roi = {
        "0": 0.20,   # 20% target
        "60": 0.10,  # 10% after 1 hour
        "180": 0.05, # 5% after 3 hours
    }

    # Conservative stoploss (will be overridden by wave invalidation)
    stoploss = -0.08  # 8%

    # Enable trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.03
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    # Timeframe - daily works well for Elliott Wave
    timeframe = '1d'

    # Only process new candles
    process_only_new_candles = True

    # Strategy settings
    MIN_PROBABILITY = 75.0  # Only trade high-probability patterns
    MIN_FIB_SCORE = 65.0    # Require good Fibonacci relationships

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.wave_helper = FreqtradeElliotWaveHelper()

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add Elliott Wave indicators to the dataframe.
        """
        # Need enough data for wave analysis
        if len(dataframe) < 60:
            self._initialize_empty_indicators(dataframe)
            return dataframe

        try:
            # Create analyzer with high probability threshold
            analyzer = EnhancedWaveAnalyzer(
                df=dataframe.copy(),
                verbose=False,
                min_probability=self.MIN_PROBABILITY
            )
            analyzer.set_combinatorial_limits(n_impulse=10, n_correction=10)

            # Find the best impulse pattern
            # Start from the lowest point in the visible data
            lowest_idx = dataframe['low'].idxmin()

            current_price = dataframe.iloc[-1]['close']

            analysis = analyzer.find_wave_with_targets(
                idx_start=int(lowest_idx),
                wave_type='impulse',
                current_price=current_price
            )

            if analysis['found'] and analysis['overall_probability'] >= self.MIN_PROBABILITY:
                # Add indicators
                dataframe = self.wave_helper.add_wave_indicators(
                    dataframe, analysis, prefix='ew'
                )
                dataframe = self.wave_helper.mark_wave_points(
                    dataframe, analysis.get('wave_pattern'), prefix='ew'
                )

                # Calculate confidence
                dataframe['ew_confidence'] = self.wave_helper.calculate_confidence_score(
                    dataframe, prefix='ew'
                )

                self.dp.send_msg(
                    f"📈 Elliott Wave found for {metadata['pair']}\n"
                    f"Probability: {analysis['overall_probability']:.1f}%\n"
                    f"Target 1: ${analysis.get('targets', {}).get('targets', [{}])[0].get('price', 0):.2f}"
                )
            else:
                self._initialize_empty_indicators(dataframe)

        except Exception as e:
            self.dp.send_msg(f"⚠️ Error analyzing {metadata['pair']}: {str(e)}")
            self._initialize_empty_indicators(dataframe)

        # Add simple technical indicators
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Simple entry logic: Enter when high-probability Elliott Wave detected.
        """
        dataframe.loc[
            (
                # High probability Elliott Wave
                (dataframe['ew_probability'] >= self.MIN_PROBABILITY) &
                (dataframe['ew_fib_score'] >= self.MIN_FIB_SCORE) &
                (dataframe['ew_confidence'] >= 70) &

                # Have a valid target
                (dataframe['ew_target_1'].notna()) &

                # RSI not overbought
                (dataframe['rsi'] < 70) &
                (dataframe['rsi'] > 35) &

                # Volume confirmation
                (dataframe['volume'] > dataframe['volume_mean'])
            ),
            'enter_long'
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Simple exit logic: Exit at target or when overbought.
        """
        dataframe.loc[
            (
                # Target 1 reached
                (dataframe['close'] >= dataframe['ew_target_1']) |

                # RSI overbought (potential exhaustion)
                (dataframe['rsi'] > 75)
            ),
            'exit_long'
        ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Use Elliott Wave invalidation level as stop loss.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]

            if pd.notna(last_candle.get('ew_invalidation')):
                invalidation_price = last_candle['ew_invalidation']
                entry_price = trade.open_rate

                # Calculate stop as percentage
                stop_pct = (invalidation_price - entry_price) / entry_price

                # Use it if it's reasonable (between -2% and -12%)
                if -0.12 < stop_pct < -0.02:
                    return stop_pct

        return self.stoploss

    def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime,
                   current_rate: float, current_profit: float, **kwargs) -> Optional[str]:
        """
        Exit at Elliott Wave targets.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]

            # Exit at Target 1
            if pd.notna(last_candle.get('ew_target_1')):
                if current_rate >= last_candle['ew_target_1'] * 0.97:
                    return "elliott_wave_target_reached"

        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: datetime,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        Confirm trade has good risk/reward ratio.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]

            # Calculate risk/reward
            if pd.notna(last_candle.get('ew_target_1')) and pd.notna(last_candle.get('ew_invalidation')):
                rr_ratio = self.wave_helper.get_risk_reward_ratio(
                    entry_price=rate,
                    target_price=last_candle['ew_target_1'],
                    invalidation_price=last_candle['ew_invalidation']
                )

                # Require at least 2:1 risk/reward
                if rr_ratio < 2.0:
                    self.dp.send_msg(
                        f"❌ Trade rejected: R/R {rr_ratio:.1f} < 2.0"
                    )
                    return False

                self.dp.send_msg(
                    f"✅ Trade confirmed: R/R {rr_ratio:.1f}"
                )

        return True

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                proposed_leverage: float, max_leverage: float, side: str,
                **kwargs) -> float:
        """
        No leverage for safety.
        """
        return 1.0

    def plot_config(self):
        """
        Simple plotting configuration.
        """
        return {
            'main_plot': {
                'ew_target_1': {'color': 'green', 'type': 'line'},
                'ew_invalidation': {'color': 'red', 'type': 'line'},
                'ew_wave1_high': {'color': 'blue', 'type': 'scatter'},
                'ew_wave3_high': {'color': 'blue', 'type': 'scatter'},
                'ew_wave5_high': {'color': 'blue', 'type': 'scatter'},
            },
            'subplots': {
                "Elliott Wave Probability": {
                    'ew_probability': {'color': 'blue'},
                    'ew_confidence': {'color': 'purple'},
                },
                "RSI": {
                    'rsi': {'color': 'red'},
                },
            }
        }

    def _initialize_empty_indicators(self, dataframe: DataFrame) -> None:
        """
        Initialize empty Elliott Wave indicators.
        """
        dataframe['ew_probability'] = 0
        dataframe['ew_fib_score'] = 0
        dataframe['ew_confidence'] = 0
        dataframe['ew_target_1'] = np.nan
        dataframe['ew_invalidation'] = np.nan
