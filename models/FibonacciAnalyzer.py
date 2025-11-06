"""
Fibonacci Analyzer for Elliott Wave Analysis

This module calculates Fibonacci ratios and relationships between waves
to validate wave patterns and calculate price targets.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from models.MonoWave import MonoWave, MonoWaveUp, MonoWaveDown


class FibonacciAnalyzer:
    """
    Analyzes Fibonacci relationships between waves to validate patterns
    and calculate probability scores.
    """

    # Standard Fibonacci ratios
    FIBONACCI_RATIOS = {
        'retracement': [0.236, 0.382, 0.500, 0.618, 0.786, 0.854],
        'extension': [1.000, 1.236, 1.382, 1.618, 2.000, 2.618, 3.618, 4.236],
        'projection': [0.618, 1.000, 1.618, 2.618]
    }

    # Tolerance for Fibonacci ratio matching (5%)
    TOLERANCE = 0.05

    def __init__(self):
        self.wave_relationships = {}

    def analyze_wave_2_retracement(self, wave1: MonoWave, wave2: MonoWave) -> Dict:
        """
        Analyze Wave 2 retracement of Wave 1.

        Expected: 50%, 61.8%, 76.4% (78.6%), or 85.4%

        Returns:
            Dict with ratio, closest_fib, deviation, and quality score
        """
        wave1_length = wave1.length
        wave2_length = wave2.length

        if wave1_length == 0:
            return {'ratio': 0, 'matches': [], 'quality': 0}

        retracement_ratio = wave2_length / wave1_length

        # Expected ranges for Wave 2
        expected_ratios = [0.382, 0.500, 0.618, 0.786, 0.854]

        matches = self._find_matching_ratios(retracement_ratio, expected_ratios)
        quality = self._calculate_quality_score(matches)

        return {
            'ratio': round(retracement_ratio, 4),
            'matches': matches,
            'quality': quality,
            'ideal_range': (0.50, 0.618),
            'in_ideal_range': 0.50 <= retracement_ratio <= 0.618
        }

    def analyze_wave_3_extension(self, wave1: MonoWave, wave2: MonoWave, wave3: MonoWave) -> Dict:
        """
        Analyze Wave 3 extension relative to Wave 1.

        Expected: 1.618x, 2.0x, 2.618x, or 3.236x of Wave 1

        Returns:
            Dict with ratio, matches, and quality score
        """
        wave1_length = wave1.length
        wave3_length = wave3.length

        if wave1_length == 0:
            return {'ratio': 0, 'matches': [], 'quality': 0}

        extension_ratio = wave3_length / wave1_length

        # Expected ratios for Wave 3
        expected_ratios = [1.000, 1.618, 2.000, 2.618, 3.236]

        matches = self._find_matching_ratios(extension_ratio, expected_ratios)
        quality = self._calculate_quality_score(matches)

        # Also check Wave 3 vs Wave 1-2 distance
        wave1_2_distance = wave1.high - wave2.low if isinstance(wave1, MonoWaveUp) else wave2.high - wave1.low
        wave3_vs_12 = wave3_length / wave1_2_distance if wave1_2_distance > 0 else 0

        matches_vs_12 = self._find_matching_ratios(wave3_vs_12, [1.618, 2.000, 2.618])

        return {
            'ratio': round(extension_ratio, 4),
            'matches': matches,
            'quality': quality,
            'wave3_vs_wave12': round(wave3_vs_12, 4),
            'matches_vs_12': matches_vs_12,
            'ideal_range': (1.618, 2.618),
            'in_ideal_range': 1.618 <= extension_ratio <= 2.618
        }

    def analyze_wave_4_retracement(self, wave3: MonoWave, wave4: MonoWave) -> Dict:
        """
        Analyze Wave 4 retracement of Wave 3.

        Expected: 14.6%, 23.6%, 38.2%, or max 50%

        Returns:
            Dict with ratio, matches, and quality score
        """
        wave3_length = wave3.length
        wave4_length = wave4.length

        if wave3_length == 0:
            return {'ratio': 0, 'matches': [], 'quality': 0}

        retracement_ratio = wave4_length / wave3_length

        # Expected ratios for Wave 4
        expected_ratios = [0.146, 0.236, 0.382, 0.500]

        matches = self._find_matching_ratios(retracement_ratio, expected_ratios)
        quality = self._calculate_quality_score(matches)

        return {
            'ratio': round(retracement_ratio, 4),
            'matches': matches,
            'quality': quality,
            'ideal_range': (0.236, 0.382),
            'in_ideal_range': 0.236 <= retracement_ratio <= 0.382,
            'exceeds_50_percent': retracement_ratio > 0.50
        }

    def analyze_wave_5_projection(self, wave1: MonoWave, wave3: MonoWave,
                                   wave4: MonoWave, wave5: MonoWave) -> Dict:
        """
        Analyze Wave 5 projection using multiple methods.

        Methods:
        1. Wave 5 = Wave 1 (equality)
        2. Wave 5 = 0.618 * Wave 1
        3. Wave 5 = 0.618 * (Wave 1 to Wave 3 distance)
        4. Wave 5 inverse retracement of Wave 4 (1.236-1.618)

        Returns:
            Dict with multiple ratios and matches
        """
        wave1_length = wave1.length
        wave3_length = wave3.length
        wave4_length = wave4.length
        wave5_length = wave5.length

        results = {}

        # Method 1: Wave 5 vs Wave 1
        if wave1_length > 0:
            wave5_vs_1 = wave5_length / wave1_length
            matches_1 = self._find_matching_ratios(wave5_vs_1, [0.618, 1.000, 1.618])
            results['wave5_vs_wave1'] = {
                'ratio': round(wave5_vs_1, 4),
                'matches': matches_1,
                'quality': self._calculate_quality_score(matches_1)
            }

        # Method 2: Wave 5 vs Wave 1-3 distance
        if isinstance(wave1, MonoWaveUp):
            wave1_3_distance = wave3.high - wave1.low
        else:
            wave1_3_distance = wave1.high - wave3.low

        if wave1_3_distance > 0:
            wave5_vs_13 = wave5_length / wave1_3_distance
            matches_13 = self._find_matching_ratios(wave5_vs_13, [0.382, 0.618, 1.000])
            results['wave5_vs_wave13'] = {
                'ratio': round(wave5_vs_13, 4),
                'matches': matches_13,
                'quality': self._calculate_quality_score(matches_13)
            }

        # Method 3: Wave 5 as inverse retracement of Wave 4
        if wave4_length > 0:
            wave5_vs_4 = wave5_length / wave4_length
            matches_4 = self._find_matching_ratios(wave5_vs_4, [1.236, 1.382, 1.618, 2.000])
            results['wave5_inverse_wave4'] = {
                'ratio': round(wave5_vs_4, 4),
                'matches': matches_4,
                'quality': self._calculate_quality_score(matches_4)
            }

        # Overall quality
        total_quality = sum(r.get('quality', 0) for r in results.values())
        avg_quality = total_quality / len(results) if results else 0

        results['overall_quality'] = avg_quality

        return results

    def analyze_corrective_abc(self, waveA: MonoWave, waveB: MonoWave,
                                waveC: MonoWave) -> Dict:
        """
        Analyze corrective ABC pattern Fibonacci relationships.

        Wave B: 50%, 61.8%, 76.4%, or 85.4% of Wave A
        Wave C: 61.8%, 100%, 123.6%, or 161.8% of Wave A

        Returns:
            Dict with ratios and quality scores
        """
        waveA_length = waveA.length
        waveB_length = waveB.length
        waveC_length = waveC.length

        results = {}

        # Wave B vs Wave A
        if waveA_length > 0:
            waveB_vs_A = waveB_length / waveA_length
            matches_B = self._find_matching_ratios(waveB_vs_A, [0.382, 0.500, 0.618, 0.786, 0.854])
            results['waveB_vs_waveA'] = {
                'ratio': round(waveB_vs_A, 4),
                'matches': matches_B,
                'quality': self._calculate_quality_score(matches_B)
            }

        # Wave C vs Wave A
        if waveA_length > 0:
            waveC_vs_A = waveC_length / waveA_length
            matches_C = self._find_matching_ratios(waveC_vs_A, [0.618, 1.000, 1.236, 1.618, 2.618])
            results['waveC_vs_waveA'] = {
                'ratio': round(waveC_vs_A, 4),
                'matches': matches_C,
                'quality': self._calculate_quality_score(matches_C),
                'ideal_range': (1.000, 1.618),
                'in_ideal_range': 1.000 <= waveC_vs_A <= 1.618
            }

        # Overall quality
        total_quality = sum(r.get('quality', 0) for r in results.values())
        avg_quality = total_quality / len(results) if results else 0

        results['overall_quality'] = avg_quality

        return results

    def _find_matching_ratios(self, actual_ratio: float,
                              expected_ratios: List[float]) -> List[Dict]:
        """
        Find which expected Fibonacci ratios the actual ratio matches.

        Returns:
            List of dicts with matched ratio, deviation, and score
        """
        matches = []

        for expected in expected_ratios:
            deviation = abs(actual_ratio - expected)
            relative_deviation = deviation / expected if expected > 0 else float('inf')

            if relative_deviation <= self.TOLERANCE:
                score = 1.0 - (relative_deviation / self.TOLERANCE)
                matches.append({
                    'fibonacci_ratio': expected,
                    'deviation': round(deviation, 4),
                    'relative_deviation': round(relative_deviation, 4),
                    'score': round(score, 4)
                })

        return sorted(matches, key=lambda x: x['score'], reverse=True)

    def _calculate_quality_score(self, matches: List[Dict]) -> float:
        """
        Calculate quality score based on Fibonacci matches.

        Returns:
            Quality score from 0 to 1
        """
        if not matches:
            return 0.0

        # Best match gets full weight, others get partial
        best_score = matches[0]['score']

        # Bonus for multiple matches
        bonus = min(0.2, len(matches) * 0.05)

        return min(1.0, best_score + bonus)

    def calculate_fibonacci_levels(self, start_price: float, end_price: float,
                                   level_type: str = 'retracement') -> Dict[str, float]:
        """
        Calculate Fibonacci retracement or extension levels.

        Args:
            start_price: Starting price point
            end_price: Ending price point
            level_type: 'retracement' or 'extension'

        Returns:
            Dict of Fibonacci levels with their price values
        """
        diff = end_price - start_price
        levels = {}

        ratios = self.FIBONACCI_RATIOS.get(level_type, self.FIBONACCI_RATIOS['retracement'])

        if level_type == 'retracement':
            for ratio in ratios:
                levels[f'{ratio:.3f}'] = end_price - (diff * ratio)
        else:  # extension
            for ratio in ratios:
                levels[f'{ratio:.3f}'] = start_price + (diff * ratio)

        return levels

    def analyze_impulse_wave_pattern(self, waves: List[MonoWave]) -> Dict:
        """
        Comprehensive Fibonacci analysis of a 5-wave impulse pattern.

        Args:
            waves: List of 5 MonoWaves [wave1, wave2, wave3, wave4, wave5]

        Returns:
            Complete Fibonacci analysis with quality scores
        """
        if len(waves) != 5:
            raise ValueError("Impulse pattern requires exactly 5 waves")

        wave1, wave2, wave3, wave4, wave5 = waves

        analysis = {
            'wave2_retracement': self.analyze_wave_2_retracement(wave1, wave2),
            'wave3_extension': self.analyze_wave_3_extension(wave1, wave2, wave3),
            'wave4_retracement': self.analyze_wave_4_retracement(wave3, wave4),
            'wave5_projection': self.analyze_wave_5_projection(wave1, wave3, wave4, wave5)
        }

        # Calculate overall Fibonacci quality score (0-100)
        scores = [
            analysis['wave2_retracement']['quality'] * 100,
            analysis['wave3_extension']['quality'] * 100,
            analysis['wave4_retracement']['quality'] * 100,
            analysis['wave5_projection']['overall_quality'] * 100
        ]

        analysis['overall_fibonacci_score'] = round(sum(scores) / len(scores), 2)
        analysis['fibonacci_confirmations'] = sum(1 for s in scores if s >= 70)

        return analysis

    def analyze_corrective_pattern(self, waves: List[MonoWave]) -> Dict:
        """
        Comprehensive Fibonacci analysis of a 3-wave corrective pattern.

        Args:
            waves: List of 3 MonoWaves [waveA, waveB, waveC]

        Returns:
            Complete Fibonacci analysis with quality scores
        """
        if len(waves) != 3:
            raise ValueError("Corrective pattern requires exactly 3 waves")

        waveA, waveB, waveC = waves

        analysis = self.analyze_corrective_abc(waveA, waveB, waveC)

        # Calculate overall score
        scores = [v.get('quality', 0) * 100 for k, v in analysis.items()
                 if isinstance(v, dict) and 'quality' in v]

        if scores:
            analysis['overall_fibonacci_score'] = round(sum(scores) / len(scores), 2)
            analysis['fibonacci_confirmations'] = sum(1 for s in scores if s >= 70)
        else:
            analysis['overall_fibonacci_score'] = 0
            analysis['fibonacci_confirmations'] = 0

        return analysis
