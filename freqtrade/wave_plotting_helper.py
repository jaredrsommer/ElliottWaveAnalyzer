"""
Enhanced Plotting Helper for Freqtrade Elliott Wave Strategies

This module adds visual line segments connecting Elliott Wave points
to make the wave structure clearly visible on Freqtrade charts.
"""

import pandas as pd
import numpy as np
from typing import Dict


class WavePlottingHelper:
    """
    Helper class to create line segments and enhanced visualizations
    for Elliott Wave patterns on Freqtrade charts.
    """

    @staticmethod
    def add_wave_lines(dataframe: pd.DataFrame, wave_pattern,
                      prefix: str = 'ew') -> pd.DataFrame:
        """
        Add line segments connecting Elliott Wave points.

        This creates continuous lines that connect:
        - Wave 1 start → Wave 1 end
        - Wave 1 end → Wave 2 end
        - Wave 2 end → Wave 3 end
        - Wave 3 end → Wave 4 end
        - Wave 4 end → Wave 5 end

        Args:
            dataframe: Freqtrade dataframe
            wave_pattern: WavePattern object
            prefix: Prefix for columns

        Returns:
            Dataframe with wave line columns
        """
        if wave_pattern is None:
            return dataframe

        # Initialize line columns (one for impulse, one for correction)
        dataframe[f'{prefix}_impulse_line'] = np.nan
        dataframe[f'{prefix}_correction_line'] = np.nan

        # Determine if impulse or correction
        is_impulse = len(wave_pattern.waves) == 5

        line_column = f'{prefix}_impulse_line' if is_impulse else f'{prefix}_correction_line'

        # Get wave endpoints
        wave_list = list(wave_pattern.waves.values())

        for i, wave in enumerate(wave_list):
            start_idx = wave.idx_start
            end_idx = wave.idx_end

            if end_idx is None or start_idx >= len(dataframe) or end_idx >= len(dataframe):
                continue

            # Get prices at start and end
            start_price = wave.low if hasattr(wave, 'low') else dataframe.iloc[start_idx]['close']
            end_price = wave.high if hasattr(wave, 'high') else dataframe.iloc[end_idx]['close']

            # If wave goes down, swap prices
            from models.MonoWave import MonoWaveDown
            if isinstance(wave, MonoWaveDown):
                start_price = wave.high if hasattr(wave, 'high') else start_price
                end_price = wave.low if hasattr(wave, 'low') else end_price

            # Create line between start and end
            num_points = end_idx - start_idx + 1
            if num_points > 1:
                line_values = np.linspace(start_price, end_price, num_points)
                dataframe.loc[start_idx:end_idx, line_column] = line_values

        return dataframe

    @staticmethod
    def add_wave_channels(dataframe: pd.DataFrame, wave_pattern,
                         prefix: str = 'ew') -> pd.DataFrame:
        """
        Add Elliott Wave channel lines (trend channels).

        For impulse waves, draws channels:
        - Upper channel: connects Wave 1 high and Wave 3 high
        - Lower channel: connects Wave 2 low and Wave 4 low

        Args:
            dataframe: Freqtrade dataframe
            wave_pattern: WavePattern object
            prefix: Prefix for columns

        Returns:
            Dataframe with channel line columns
        """
        if wave_pattern is None or len(wave_pattern.waves) != 5:
            return dataframe

        dataframe[f'{prefix}_upper_channel'] = np.nan
        dataframe[f'{prefix}_lower_channel'] = np.nan

        waves = list(wave_pattern.waves.values())
        wave1, wave2, wave3, wave4, wave5 = waves

        # Upper channel: Wave 1 high → Wave 3 high, extended to Wave 5
        if hasattr(wave1, 'high_idx') and hasattr(wave3, 'high_idx'):
            x1, y1 = wave1.high_idx, wave1.high
            x2, y2 = wave3.high_idx, wave3.high

            if x2 > x1:
                slope = (y2 - y1) / (x2 - x1)

                # Extend from Wave 1 to Wave 5
                for idx in range(wave1.idx_start, wave5.idx_end + 1):
                    if idx < len(dataframe):
                        channel_value = y1 + slope * (idx - x1)
                        dataframe.loc[idx, f'{prefix}_upper_channel'] = channel_value

        # Lower channel: Wave 2 low → Wave 4 low, extended to Wave 5
        if hasattr(wave2, 'low_idx') and hasattr(wave4, 'low_idx'):
            x1, y1 = wave2.low_idx, wave2.low
            x2, y2 = wave4.low_idx, wave4.low

            if x2 > x1:
                slope = (y2 - y1) / (x2 - x1)

                # Extend from Wave 2 to Wave 5
                for idx in range(wave2.idx_start, wave5.idx_end + 1):
                    if idx < len(dataframe):
                        channel_value = y1 + slope * (idx - x1)
                        dataframe.loc[idx, f'{prefix}_lower_channel'] = channel_value

        return dataframe

    @staticmethod
    def add_fibonacci_levels(dataframe: pd.DataFrame, wave_pattern,
                            prefix: str = 'ew') -> pd.DataFrame:
        """
        Add Fibonacci retracement levels for Wave 2 and Wave 4.

        Args:
            dataframe: Freqtrade dataframe
            wave_pattern: WavePattern object
            prefix: Prefix for columns

        Returns:
            Dataframe with Fibonacci level columns
        """
        if wave_pattern is None or len(wave_pattern.waves) != 5:
            return dataframe

        waves = list(wave_pattern.waves.values())
        wave1, wave2, wave3, wave4, wave5 = waves

        # Wave 2 Fibonacci retracements
        if hasattr(wave1, 'low') and hasattr(wave1, 'high'):
            wave1_range = wave1.high - wave1.low

            # 61.8% retracement level
            fib_618 = wave1.high - (wave1_range * 0.618)
            dataframe[f'{prefix}_w2_fib_618'] = np.nan
            dataframe.loc[wave1.idx_end:wave2.idx_end, f'{prefix}_w2_fib_618'] = fib_618

            # 50% retracement level
            fib_50 = wave1.high - (wave1_range * 0.500)
            dataframe[f'{prefix}_w2_fib_50'] = np.nan
            dataframe.loc[wave1.idx_end:wave2.idx_end, f'{prefix}_w2_fib_50'] = fib_50

        # Wave 4 Fibonacci retracements
        if hasattr(wave3, 'low') and hasattr(wave3, 'high'):
            wave3_range = wave3.high - wave3.low

            # 38.2% retracement level
            fib_382 = wave3.high - (wave3_range * 0.382)
            dataframe[f'{prefix}_w4_fib_382'] = np.nan
            dataframe.loc[wave3.idx_end:wave4.idx_end, f'{prefix}_w4_fib_382'] = fib_382

            # 23.6% retracement level
            fib_236 = wave3.high - (wave3_range * 0.236)
            dataframe[f'{prefix}_w4_fib_236'] = np.nan
            dataframe.loc[wave3.idx_end:wave4.idx_end, f'{prefix}_w4_fib_236'] = fib_236

        return dataframe

    @staticmethod
    def create_enhanced_plot_config(prefix: str = 'ew') -> Dict:
        """
        Create enhanced Freqtrade plotting configuration with line segments.

        Args:
            prefix: Indicator prefix

        Returns:
            Dict with enhanced plot configuration
        """
        return {
            'main_plot': {
                # Wave line segments (makes wave structure visible)
                f'{prefix}_impulse_line': {
                    'color': 'blue',
                    'type': 'line',
                    'width': 2
                },
                f'{prefix}_correction_line': {
                    'color': 'orange',
                    'type': 'line',
                    'width': 2
                },

                # Channel lines
                f'{prefix}_upper_channel': {
                    'color': 'green',
                    'type': 'line',
                    'width': 1,
                    'fill_to': f'{prefix}_lower_channel',
                    'fill_color': 'rgba(0, 255, 0, 0.1)'
                },
                f'{prefix}_lower_channel': {
                    'color': 'green',
                    'type': 'line',
                    'width': 1
                },

                # Fibonacci levels
                f'{prefix}_w2_fib_618': {
                    'color': 'purple',
                    'type': 'line',
                    'width': 1,
                    'dash': 'dash'
                },
                f'{prefix}_w2_fib_50': {
                    'color': 'purple',
                    'type': 'line',
                    'width': 1,
                    'dash': 'dot'
                },
                f'{prefix}_w4_fib_382': {
                    'color': 'purple',
                    'type': 'line',
                    'width': 1,
                    'dash': 'dash'
                },
                f'{prefix}_w4_fib_236': {
                    'color': 'purple',
                    'type': 'line',
                    'width': 1,
                    'dash': 'dot'
                },

                # Target lines
                f'{prefix}_target_1': {
                    'color': 'green',
                    'type': 'line',
                    'width': 2
                },
                f'{prefix}_target_2': {
                    'color': 'lightgreen',
                    'type': 'line',
                    'width': 1
                },
                f'{prefix}_target_3': {
                    'color': 'lime',
                    'type': 'line',
                    'width': 1
                },

                # Invalidation line
                f'{prefix}_invalidation': {
                    'color': 'red',
                    'type': 'line',
                    'width': 2
                },

                # Wave points (markers)
                f'{prefix}_wave1_high': {'color': 'blue', 'type': 'scatter'},
                f'{prefix}_wave2_low': {'color': 'orange', 'type': 'scatter'},
                f'{prefix}_wave3_high': {'color': 'blue', 'type': 'scatter'},
                f'{prefix}_wave4_low': {'color': 'orange', 'type': 'scatter'},
                f'{prefix}_wave5_high': {'color': 'blue', 'type': 'scatter'},
            },
            'subplots': {
                "Elliott Wave Analysis": {
                    f'{prefix}_probability': {
                        'color': 'blue',
                        'fill_to': 0,
                        'fill_color': 'rgba(0, 0, 255, 0.3)'
                    },
                    f'{prefix}_fib_score': {
                        'color': 'green',
                        'fill_to': 0,
                        'fill_color': 'rgba(0, 255, 0, 0.3)'
                    },
                    f'{prefix}_confidence': {'color': 'purple'},
                },
                "RSI": {
                    'rsi': {'color': 'red'},
                },
                "MACD": {
                    'macd': {'color': 'blue'},
                    'macdsignal': {'color': 'orange'},
                    'macdhist': {'color': 'gray', 'type': 'bar'},
                },
            }
        }
