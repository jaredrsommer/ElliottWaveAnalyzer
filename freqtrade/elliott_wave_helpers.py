"""
Freqtrade Integration Helper for Enhanced Elliott Wave Analyzer

This module provides helper functions to convert Elliott Wave analysis
into Freqtrade-compatible indicators and signals.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FreqtradeElliotWaveHelper:
    """
    Helper class to integrate Enhanced Elliott Wave Analyzer with Freqtrade.
    """

    @staticmethod
    def add_wave_indicators(dataframe: pd.DataFrame,
                           wave_analysis: Dict,
                           prefix: str = 'ew') -> pd.DataFrame:
        """
        Add Elliott Wave analysis results as indicators to Freqtrade dataframe.

        Args:
            dataframe: Freqtrade dataframe
            wave_analysis: Wave analysis from EnhancedWaveAnalyzer
            prefix: Prefix for indicator columns (default: 'ew')

        Returns:
            Dataframe with added indicators
        """
        # Initialize all indicators to NaN
        dataframe[f'{prefix}_probability'] = np.nan
        dataframe[f'{prefix}_wave_type'] = ''
        dataframe[f'{prefix}_target_1'] = np.nan
        dataframe[f'{prefix}_target_2'] = np.nan
        dataframe[f'{prefix}_target_3'] = np.nan
        dataframe[f'{prefix}_invalidation'] = np.nan
        dataframe[f'{prefix}_fib_score'] = np.nan
        dataframe[f'{prefix}_pattern_quality'] = ''

        if not wave_analysis.get('found', False):
            return dataframe

        # Get pattern details
        probability = wave_analysis.get('overall_probability', 0)
        pattern = wave_analysis.get('wave_pattern')

        if pattern is None:
            return dataframe

        # Mark the wave pattern on the dataframe
        start_idx = pattern.idx_start
        end_idx = pattern.idx_end

        if end_idx is not None and end_idx < len(dataframe):
            # Set probability across the pattern range
            dataframe.loc[start_idx:end_idx, f'{prefix}_probability'] = probability
            dataframe.loc[start_idx:end_idx, f'{prefix}_wave_type'] = wave_analysis.get('wave_type', '')

            # Set pattern quality category
            category = wave_analysis.get('category', '')
            dataframe.loc[start_idx:end_idx, f'{prefix}_pattern_quality'] = category

            # Add Fibonacci score
            fib_score = wave_analysis['probability_analysis']['scores']['fibonacci_ratios']['score']
            dataframe.loc[start_idx:end_idx, f'{prefix}_fib_score'] = fib_score

            # Add targets if available
            if 'targets' in wave_analysis:
                targets = wave_analysis['targets']['targets']

                # Get top 3 most probable targets
                sorted_targets = sorted(targets, key=lambda x: x.get('probability', 0), reverse=True)

                if len(sorted_targets) >= 1:
                    dataframe.loc[end_idx:, f'{prefix}_target_1'] = sorted_targets[0]['price']
                if len(sorted_targets) >= 2:
                    dataframe.loc[end_idx:, f'{prefix}_target_2'] = sorted_targets[1]['price']
                if len(sorted_targets) >= 3:
                    dataframe.loc[end_idx:, f'{prefix}_target_3'] = sorted_targets[2]['price']

                # Add invalidation level if present
                for target in targets:
                    if target.get('level') == 'invalidation':
                        dataframe.loc[end_idx:, f'{prefix}_invalidation'] = target['price']
                        break

        return dataframe

    @staticmethod
    def mark_wave_points(dataframe: pd.DataFrame,
                        wave_pattern,
                        prefix: str = 'ew') -> pd.DataFrame:
        """
        Mark individual wave endpoints on the dataframe for plotting.

        Args:
            dataframe: Freqtrade dataframe
            wave_pattern: WavePattern object
            prefix: Prefix for columns

        Returns:
            Dataframe with wave point markers
        """
        # Initialize wave point columns
        for i in range(1, 6):
            dataframe[f'{prefix}_wave{i}_high'] = np.nan
            dataframe[f'{prefix}_wave{i}_low'] = np.nan

        if wave_pattern is None:
            return dataframe

        # Mark each wave's high and low points
        for wave_num, wave in wave_pattern.waves.items():
            # Extract number from wave_num (e.g., 'wave1' -> 1)
            num = wave_num.replace('wave', '')

            if hasattr(wave, 'high_idx') and wave.high_idx < len(dataframe):
                dataframe.loc[wave.high_idx, f'{prefix}_wave{num}_high'] = wave.high

            if hasattr(wave, 'low_idx') and wave.low_idx < len(dataframe):
                dataframe.loc[wave.low_idx, f'{prefix}_wave{num}_low'] = wave.low

        return dataframe

    @staticmethod
    def generate_entry_signal(dataframe: pd.DataFrame,
                             min_probability: float = 70.0,
                             min_fib_score: float = 60.0,
                             wave_type: str = 'impulse',
                             prefix: str = 'ew') -> pd.Series:
        """
        Generate entry signals based on Elliott Wave analysis.

        Args:
            dataframe: Freqtrade dataframe with wave indicators
            min_probability: Minimum pattern probability
            min_fib_score: Minimum Fibonacci score
            wave_type: Type of wave to look for
            prefix: Indicator prefix

        Returns:
            Boolean series indicating entry signals
        """
        conditions = []

        # Check if probability meets threshold
        conditions.append(dataframe[f'{prefix}_probability'] >= min_probability)

        # Check if Fibonacci score meets threshold
        conditions.append(dataframe[f'{prefix}_fib_score'] >= min_fib_score)

        # Check wave type
        conditions.append(dataframe[f'{prefix}_wave_type'] == wave_type)

        # Check that we have a valid target
        conditions.append(dataframe[f'{prefix}_target_1'].notna())

        # Combine all conditions
        if conditions:
            entry_signal = pd.Series(np.ones(len(dataframe), dtype=bool), index=dataframe.index)
            for condition in conditions:
                entry_signal = entry_signal & condition
            return entry_signal
        else:
            return pd.Series(np.zeros(len(dataframe), dtype=bool), index=dataframe.index)

    @staticmethod
    def generate_exit_signal(dataframe: pd.DataFrame,
                            target_level: int = 1,
                            use_invalidation: bool = True,
                            prefix: str = 'ew') -> Tuple[pd.Series, pd.Series]:
        """
        Generate exit signals based on targets and invalidation levels.

        Args:
            dataframe: Freqtrade dataframe with wave indicators
            target_level: Which target to use (1, 2, or 3)
            use_invalidation: Whether to exit on invalidation
            prefix: Indicator prefix

        Returns:
            Tuple of (profit_target_reached, stop_loss_hit) boolean series
        """
        profit_exit = pd.Series(np.zeros(len(dataframe), dtype=bool), index=dataframe.index)
        stop_exit = pd.Series(np.zeros(len(dataframe), dtype=bool), index=dataframe.index)

        target_col = f'{prefix}_target_{target_level}'

        # Exit when target is reached (price >= target for long)
        if target_col in dataframe.columns:
            profit_exit = (dataframe['close'] >= dataframe[target_col]) & dataframe[target_col].notna()

        # Exit when invalidation level is hit
        if use_invalidation and f'{prefix}_invalidation' in dataframe.columns:
            stop_exit = (dataframe['close'] <= dataframe[f'{prefix}_invalidation']) & \
                       dataframe[f'{prefix}_invalidation'].notna()

        return profit_exit, stop_exit

    @staticmethod
    def calculate_confidence_score(dataframe: pd.DataFrame,
                                   prefix: str = 'ew') -> pd.Series:
        """
        Calculate overall confidence score combining multiple factors.

        Args:
            dataframe: Freqtrade dataframe with wave indicators
            prefix: Indicator prefix

        Returns:
            Series with confidence scores (0-100)
        """
        confidence = pd.Series(np.zeros(len(dataframe)), index=dataframe.index)

        prob_col = f'{prefix}_probability'
        fib_col = f'{prefix}_fib_score'

        if prob_col in dataframe.columns and fib_col in dataframe.columns:
            # Weighted average: 60% probability, 40% Fibonacci score
            confidence = (dataframe[prob_col] * 0.6 + dataframe[fib_col] * 0.4)
            confidence = confidence.fillna(0)

        return confidence

    @staticmethod
    def add_wave_labels(dataframe: pd.DataFrame,
                       wave_pattern,
                       prefix: str = 'ew') -> pd.DataFrame:
        """
        Add wave labels (1, 2, 3, 4, 5 or A, B, C) for plotting.

        Args:
            dataframe: Freqtrade dataframe
            wave_pattern: WavePattern object
            prefix: Prefix for columns

        Returns:
            Dataframe with wave labels
        """
        dataframe[f'{prefix}_label'] = ''

        if wave_pattern is None:
            return dataframe

        # Add labels at wave endpoints
        for wave_num, wave in wave_pattern.waves.items():
            label = wave.label if hasattr(wave, 'label') else wave_num.replace('wave', '')

            # Place label at the endpoint (high for up waves, low for down waves)
            if hasattr(wave, 'high_idx') and hasattr(wave, 'low_idx'):
                # Determine if it's an up wave or down wave
                if wave.high > wave.low:  # Up wave - label at high
                    if wave.high_idx < len(dataframe):
                        dataframe.loc[wave.high_idx, f'{prefix}_label'] = label
                else:  # Down wave - label at low
                    if wave.low_idx < len(dataframe):
                        dataframe.loc[wave.low_idx, f'{prefix}_label'] = label

        return dataframe

    @staticmethod
    def create_plot_config(prefix: str = 'ew') -> Dict:
        """
        Create Freqtrade plotting configuration for Elliott Wave indicators.

        Args:
            prefix: Indicator prefix

        Returns:
            Dict with plot configuration
        """
        return {
            'main_plot': {},
            'subplots': {
                "Elliott Wave Probability": {
                    f'{prefix}_probability': {'color': 'blue', 'type': 'line'},
                    f'{prefix}_fib_score': {'color': 'green', 'type': 'line'},
                },
                "Confidence Score": {
                    f'{prefix}_confidence': {'color': 'purple', 'type': 'line'},
                }
            }
        }

    @staticmethod
    def format_analysis_summary(wave_analysis: Dict) -> str:
        """
        Format wave analysis into a readable summary string.

        Args:
            wave_analysis: Wave analysis dictionary

        Returns:
            Formatted summary string
        """
        if not wave_analysis.get('found', False):
            return "No valid Elliott Wave pattern found"

        summary = []
        summary.append(f"Elliott Wave {wave_analysis['wave_type'].upper()}")
        summary.append(f"Probability: {wave_analysis['overall_probability']:.1f}%")
        summary.append(f"Category: {wave_analysis['category']}")

        if 'targets' in wave_analysis:
            summary.append("\nTargets:")
            for i, target in enumerate(wave_analysis['targets']['targets'][:3], 1):
                summary.append(f"  T{i}: ${target['price']:.2f} ({target.get('probability', 0)*100:.0f}%)")

        return "\n".join(summary)

    @staticmethod
    def get_risk_reward_ratio(entry_price: float,
                             target_price: float,
                             invalidation_price: float) -> float:
        """
        Calculate risk/reward ratio for a trade.

        Args:
            entry_price: Entry price
            target_price: Target price
            invalidation_price: Stop loss / invalidation price

        Returns:
            Risk/reward ratio
        """
        if entry_price == invalidation_price:
            return 0.0

        reward = abs(target_price - entry_price)
        risk = abs(entry_price - invalidation_price)

        if risk == 0:
            return 0.0

        return reward / risk

    @staticmethod
    def calculate_position_size(account_balance: float,
                               risk_percent: float,
                               entry_price: float,
                               stop_loss_price: float) -> float:
        """
        Calculate position size based on account risk.

        Args:
            account_balance: Total account balance
            risk_percent: Percentage of account to risk (e.g., 1.0 for 1%)
            entry_price: Entry price
            stop_loss_price: Stop loss price

        Returns:
            Position size in base currency
        """
        if entry_price == stop_loss_price:
            return 0.0

        risk_amount = account_balance * (risk_percent / 100)
        price_difference = abs(entry_price - stop_loss_price)

        if price_difference == 0:
            return 0.0

        position_size = risk_amount / price_difference

        return position_size
