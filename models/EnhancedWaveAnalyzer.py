"""
Enhanced Wave Analyzer with Probability Scoring and Target Calculation

This module provides a comprehensive Elliott Wave analysis system that:
- Detects wave patterns with probability scoring
- Calculates Fibonacci-based price targets
- Supports multiple timeframes
- Provides segment length variation analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from models.MonoWave import MonoWaveUp, MonoWaveDown
from models.WavePattern import WavePattern
from models.WaveRules import Impulse, Correction, LeadingDiagonal, TDWave
from models.WaveOptions import WaveOptionsGenerator5, WaveOptionsGenerator3
from models.FibonacciAnalyzer import FibonacciAnalyzer
from models.ProbabilityScorer import ProbabilityScorer
from models.TargetCalculator import TargetCalculator
from models.WaveCycle import WaveCycle


class WaveCandidate:
    """Represents a wave pattern candidate with probability score."""

    def __init__(self, pattern: WavePattern, probability_analysis: Dict,
                 wave_type: str, wave_options: List[int] = None):
        self.pattern = pattern
        self.probability_analysis = probability_analysis
        self.wave_type = wave_type  # 'impulse', 'correction', 'diagonal'
        self.wave_options = wave_options or []
        self.probability = probability_analysis.get('overall_probability', 0)

    def __repr__(self):
        return f"WaveCandidate({self.wave_type}, prob={self.probability:.1f}%)"

    def __lt__(self, other):
        return self.probability < other.probability


class EnhancedWaveAnalyzer:
    """
    Enhanced Elliott Wave Analyzer with probability scoring,
    target calculation, and multi-timeframe support.
    """

    def __init__(self, df: pd.DataFrame, verbose: bool = False,
                 min_probability: float = 50.0):
        """
        Initialize Enhanced Wave Analyzer.

        Args:
            df: DataFrame with OHLCV data (must have Date, Open, High, Low, Close columns)
            verbose: Print detailed analysis
            min_probability: Minimum probability threshold for valid patterns (default 50%)
        """
        self.df = df
        self.lows = np.array(list(self.df['Low']))
        self.highs = np.array(list(self.df['High']))
        self.dates = np.array(list(self.df['Date']))
        self.verbose = verbose
        self.min_probability = min_probability

        # Analyzers
        self.fib_analyzer = FibonacciAnalyzer()
        self.prob_scorer = ProbabilityScorer()
        self.target_calculator = TargetCalculator()

        # Rules
        self.impulse_rule = Impulse('impulse')
        self.correction_rule = Correction('correction')
        self.diagonal_rule = LeadingDiagonal('leading_diagonal')

        # Wave options generators
        self.__waveoptions_impulse: WaveOptionsGenerator5 = None
        self.__waveoptions_correction: WaveOptionsGenerator3 = None

        self.set_combinatorial_limits()

    def set_combinatorial_limits(self, n_impulse: int = 12, n_correction: int = 12):
        """
        Set limits for wave option combinations.

        Args:
            n_impulse: Maximum skip value for impulse waves (5 waves)
            n_correction: Maximum skip value for corrective waves (3 waves)
        """
        self.__waveoptions_impulse = WaveOptionsGenerator5(n_impulse)
        self.__waveoptions_correction = WaveOptionsGenerator3(n_correction)

        if self.verbose:
            print(f"Impulse combinations: {self.__waveoptions_impulse.number:,}")
            print(f"Correction combinations: {self.__waveoptions_correction.number:,}")

    def find_best_impulse_waves(self, idx_start: int, max_results: int = 10) -> List[WaveCandidate]:
        """
        Find the best impulse wave patterns starting from idx_start.

        Returns patterns sorted by probability score.

        Args:
            idx_start: Starting index in the dataframe
            max_results: Maximum number of results to return

        Returns:
            List of WaveCandidate objects sorted by probability (highest first)
        """
        candidates = []

        for wave_option in self.__waveoptions_impulse.options_sorted:
            waves = self._find_impulsive_wave(idx_start, wave_option.values)

            if waves:
                # Basic rule check first
                wave_pattern = WavePattern(waves, verbose=False)

                if wave_pattern.check_rule(self.impulse_rule):
                    # Calculate probability score
                    prob_analysis = self.prob_scorer.score_impulse_pattern(waves, wave_pattern)

                    if prob_analysis['valid_pattern'] and prob_analysis['overall_probability'] >= self.min_probability:
                        candidate = WaveCandidate(
                            pattern=wave_pattern,
                            probability_analysis=prob_analysis,
                            wave_type='impulse',
                            wave_options=wave_option.values
                        )
                        candidates.append(candidate)

                        if self.verbose:
                            print(f"Found impulse: {wave_option.values}, prob={candidate.probability:.1f}%")

        # Sort by probability (highest first) and return top N
        candidates.sort(reverse=True)
        return candidates[:max_results]

    def find_best_corrective_waves(self, idx_start: int, max_results: int = 10) -> List[WaveCandidate]:
        """
        Find the best corrective wave patterns starting from idx_start.

        Returns patterns sorted by probability score.

        Args:
            idx_start: Starting index in the dataframe
            max_results: Maximum number of results to return

        Returns:
            List of WaveCandidate objects sorted by probability (highest first)
        """
        candidates = []

        for wave_option in self.__waveoptions_correction.options_sorted:
            waves = self._find_corrective_wave(idx_start, wave_option.values)

            if waves:
                wave_pattern = WavePattern(waves, verbose=False)

                if wave_pattern.check_rule(self.correction_rule):
                    # Calculate probability score
                    prob_analysis = self.prob_scorer.score_corrective_pattern(waves, wave_pattern)

                    if prob_analysis['valid_pattern'] and prob_analysis['overall_probability'] >= self.min_probability:
                        candidate = WaveCandidate(
                            pattern=wave_pattern,
                            probability_analysis=prob_analysis,
                            wave_type='correction',
                            wave_options=wave_option.values
                        )
                        candidates.append(candidate)

                        if self.verbose:
                            print(f"Found correction: {wave_option.values}, prob={candidate.probability:.1f}%")

        candidates.sort(reverse=True)
        return candidates[:max_results]

    def find_wave_with_targets(self, idx_start: int, wave_type: str = 'impulse',
                               current_price: Optional[float] = None) -> Dict:
        """
        Find wave patterns and calculate price targets.

        Args:
            idx_start: Starting index
            wave_type: 'impulse' or 'correction'
            current_price: Current market price for target calculation

        Returns:
            Dict with best pattern and target analysis
        """
        if wave_type == 'impulse':
            candidates = self.find_best_impulse_waves(idx_start, max_results=1)
        else:
            candidates = self.find_best_corrective_waves(idx_start, max_results=1)

        if not candidates:
            return {
                'found': False,
                'message': f'No valid {wave_type} pattern found meeting {self.min_probability}% probability threshold'
            }

        best_candidate = candidates[0]

        # Get current price if not provided
        if current_price is None:
            last_idx = best_candidate.pattern.idx_end
            if last_idx is not None and last_idx < len(self.df):
                current_price = self.df.iloc[last_idx]['Close']

        result = {
            'found': True,
            'wave_type': wave_type,
            'probability': best_candidate.probability,
            'category': best_candidate.probability_analysis['category'],
            'wave_pattern': best_candidate.pattern,
            'probability_analysis': best_candidate.probability_analysis,
            'wave_options': best_candidate.wave_options
        }

        # Calculate targets for next wave
        if wave_type == 'impulse':
            waves_list = list(best_candidate.pattern.waves.values())
            # Assume we're looking for Wave 5 (most common)
            if len(waves_list) >= 4 and current_price:
                targets = self.target_calculator.calculate_wave_5_targets(
                    waves_list[0], waves_list[1], waves_list[2], waves_list[3],
                    current_price
                )
                result['targets'] = targets

        elif wave_type == 'correction' and current_price:
            waves_list = list(best_candidate.pattern.waves.values())
            if len(waves_list) >= 2:
                targets = self.target_calculator.calculate_wave_C_targets(
                    waves_list[0], waves_list[1], current_price
                )
                result['targets'] = targets

        return result

    def analyze_segment_variations(self, idx_start: int, wave_type: str = 'impulse',
                                  min_probability: float = 60.0) -> Dict:
        """
        Analyze how different segment lengths (wave options) affect probability.

        This provides insight into which wave configurations are most probable.

        Args:
            idx_start: Starting index
            wave_type: 'impulse' or 'correction'
            min_probability: Minimum probability to include in results

        Returns:
            Dict with segment variation analysis
        """
        if wave_type == 'impulse':
            all_candidates = self.find_best_impulse_waves(idx_start, max_results=100)
        else:
            all_candidates = self.find_best_corrective_waves(idx_start, max_results=100)

        # Filter by minimum probability
        filtered = [c for c in all_candidates if c.probability >= min_probability]

        if not filtered:
            return {
                'found': False,
                'message': f'No patterns found with probability >= {min_probability}%'
            }

        # Group by probability ranges
        ranges = {
            '90-100%': [],
            '80-89%': [],
            '70-79%': [],
            '60-69%': [],
            '50-59%': []
        }

        for candidate in filtered:
            prob = candidate.probability
            if prob >= 90:
                ranges['90-100%'].append(candidate)
            elif prob >= 80:
                ranges['80-89%'].append(candidate)
            elif prob >= 70:
                ranges['70-79%'].append(candidate)
            elif prob >= 60:
                ranges['60-69%'].append(candidate)
            else:
                ranges['50-59%'].append(candidate)

        # Prepare summary
        summary = {}
        for range_name, candidates in ranges.items():
            if candidates:
                summary[range_name] = {
                    'count': len(candidates),
                    'wave_options': [c.wave_options for c in candidates],
                    'avg_probability': sum(c.probability for c in candidates) / len(candidates)
                }

        return {
            'found': True,
            'total_candidates': len(filtered),
            'best_candidate': filtered[0],
            'probability_distribution': summary,
            'all_candidates': filtered
        }

    def scan_entire_dataset(self, wave_type: str = 'impulse',
                           min_probability: float = 70.0,
                           step_size: int = 10) -> List[Dict]:
        """
        Scan entire dataset for wave patterns.

        Args:
            wave_type: 'impulse' or 'correction'
            min_probability: Minimum probability threshold
            step_size: Step size for scanning (to reduce computation)

        Returns:
            List of found patterns with their locations
        """
        patterns_found = []

        for idx in range(0, len(self.df) - 50, step_size):  # Need at least 50 bars
            if self.verbose:
                if idx % 100 == 0:
                    print(f"Scanning index {idx}/{len(self.df)}...")

            if wave_type == 'impulse':
                candidates = self.find_best_impulse_waves(idx, max_results=1)
            else:
                candidates = self.find_best_corrective_waves(idx, max_results=1)

            if candidates and candidates[0].probability >= min_probability:
                pattern_info = {
                    'start_idx': idx,
                    'start_date': self.dates[idx],
                    'end_idx': candidates[0].pattern.idx_end,
                    'end_date': self.dates[candidates[0].pattern.idx_end] if candidates[0].pattern.idx_end < len(self.dates) else None,
                    'probability': candidates[0].probability,
                    'wave_type': wave_type,
                    'wave_options': candidates[0].wave_options,
                    'candidate': candidates[0]
                }
                patterns_found.append(pattern_info)

        return patterns_found

    def _find_impulsive_wave(self, idx_start: int, wave_config: list) -> Optional[List]:
        """
        Internal method to find 5-wave impulsive pattern.
        """
        if wave_config is None:
            wave_config = [0, 0, 0, 0, 0]

        wave1 = MonoWaveUp(lows=self.lows, highs=self.highs, dates=self.dates,
                          idx_start=idx_start, skip=wave_config[0])
        wave1.label = '1'
        wave1_end = wave1.idx_end
        if wave1_end is None:
            return False

        wave2 = MonoWaveDown(lows=self.lows, highs=self.highs, dates=self.dates,
                            idx_start=wave1_end, skip=wave_config[1])
        wave2.label = '2'
        wave2_end = wave2.idx_end
        if wave2_end is None:
            return False

        wave3 = MonoWaveUp(lows=self.lows, highs=self.highs, dates=self.dates,
                          idx_start=wave2_end, skip=wave_config[2])
        wave3.label = '3'
        wave3_end = wave3.idx_end
        if wave3_end is None:
            return False

        wave4 = MonoWaveDown(lows=self.lows, highs=self.highs, dates=self.dates,
                            idx_start=wave3_end, skip=wave_config[3])
        wave4.label = '4'
        wave4_end = wave4.idx_end
        if wave4_end is None:
            return False

        # Check for invalidating lows between wave 2 and wave 4
        if wave2.low > np.min(self.lows[wave2.low_idx:wave4.low_idx]):
            return False

        wave5 = MonoWaveUp(lows=self.lows, highs=self.highs, dates=self.dates,
                          idx_start=wave4_end, skip=wave_config[4])
        wave5.label = '5'
        wave5_end = wave5.idx_end
        if wave5_end is None:
            return False

        # Check for invalidating lows between wave 4 and wave 5
        if self.lows[wave4.low_idx:wave5.high_idx].any() and wave4.low > np.min(self.lows[wave4.low_idx:wave5.high_idx]):
            return False

        return [wave1, wave2, wave3, wave4, wave5]

    def _find_corrective_wave(self, idx_start: int, wave_config: list) -> Optional[List]:
        """
        Internal method to find 3-wave corrective pattern.
        """
        if wave_config is None:
            wave_config = [0, 0, 0]

        waveA = MonoWaveDown(lows=self.lows, highs=self.highs, dates=self.dates,
                            idx_start=idx_start, skip=wave_config[0])
        waveA.label = 'A'
        waveA_end = waveA.idx_end
        if waveA_end is None:
            return False

        waveB = MonoWaveUp(lows=self.lows, highs=self.highs, dates=self.dates,
                          idx_start=waveA_end, skip=wave_config[1])
        waveB.label = 'B'
        waveB_end = waveB.idx_end
        if waveB_end is None:
            return False

        waveC = MonoWaveDown(lows=self.lows, highs=self.highs, dates=self.dates,
                            idx_start=waveB_end, skip=wave_config[2])
        waveC.label = 'C'
        waveC_end = waveC.idx_end
        if waveC_end is None:
            return False

        return [waveA, waveB, waveC]

    def get_current_price(self) -> float:
        """Get the most recent close price."""
        return self.df.iloc[-1]['Close']

    def create_analysis_report(self, idx_start: int, wave_type: str = 'impulse') -> str:
        """
        Create a comprehensive text report of wave analysis.

        Args:
            idx_start: Starting index
            wave_type: 'impulse' or 'correction'

        Returns:
            Formatted text report
        """
        current_price = self.get_current_price()
        analysis = self.find_wave_with_targets(idx_start, wave_type, current_price)

        if not analysis['found']:
            return analysis['message']

        report = []
        report.append("=" * 70)
        report.append(f"ELLIOTT WAVE ANALYSIS REPORT - {wave_type.upper()}")
        report.append("=" * 70)
        report.append(f"Overall Probability: {analysis['probability']:.1f}%")
        report.append(f"Category: {analysis['category']}")
        report.append(f"Wave Configuration: {analysis['wave_options']}")
        report.append("")

        # Probability breakdown
        prob_scores = analysis['probability_analysis']['scores']
        report.append("PROBABILITY BREAKDOWN:")
        report.append(f"  Rules Compliance: {prob_scores['rules_compliance']['score']:.0f}%")
        report.append(f"  Fibonacci Ratios: {prob_scores['fibonacci_ratios']['score']:.1f}%")
        report.append(f"  Guidelines: {prob_scores['guidelines']['score']:.1f}%")
        report.append(f"  Structure Quality: {prob_scores['structure_quality']['score']:.1f}%")
        report.append("")

        # Targets
        if 'targets' in analysis:
            targets = analysis['targets']
            report.append("PRICE TARGETS:")
            report.append(f"  Current Price: ${current_price:.2f}")
            report.append(f"  Wave: {targets['wave']}")
            report.append(f"  Direction: {targets['direction']}")
            report.append("")

            for target in targets['targets']:
                report.append(f"  {target['level'].upper()}: ${target['price']:.2f} "
                            f"({target['ratio']}) - Probability: {target.get('probability', 0)*100:.0f}%")
                if 'description' in target:
                    report.append(f"    {target['description']}")

        report.append("=" * 70)

        return "\n".join(report)
