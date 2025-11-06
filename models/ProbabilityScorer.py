"""
Probability Scorer for Elliott Wave Patterns

This module scores wave patterns based on:
- Strict Elliott Wave rules compliance
- Guideline adherence
- Fibonacci ratio relationships
- Wave structure quality
- Technical indicators
"""

import numpy as np
from typing import Dict, List, Optional
from models.MonoWave import MonoWave, MonoWaveUp, MonoWaveDown
from models.WavePattern import WavePattern
from models.WaveRules import WaveRule, Impulse, Correction
from models.FibonacciAnalyzer import FibonacciAnalyzer


class ProbabilityScorer:
    """
    Calculates probability scores for Elliott Wave patterns based on
    multiple factors including rules, guidelines, and Fibonacci relationships.
    """

    def __init__(self):
        self.fib_analyzer = FibonacciAnalyzer()

        # Scoring weights
        self.weights = {
            'rules_compliance': 0.40,  # 40% - Must be 100% for valid pattern
            'fibonacci_ratios': 0.30,  # 30% - Fibonacci relationships
            'guidelines': 0.20,         # 20% - Elliott Wave guidelines
            'structure_quality': 0.10   # 10% - Wave structure quality
        }

    def score_impulse_pattern(self, waves: List[MonoWave],
                              wave_pattern: WavePattern = None) -> Dict:
        """
        Calculate comprehensive probability score for a 5-wave impulse pattern.

        Args:
            waves: List of 5 MonoWaves
            wave_pattern: Optional WavePattern object

        Returns:
            Dict with detailed scoring breakdown and overall probability
        """
        if len(waves) != 5:
            raise ValueError("Impulse pattern requires exactly 5 waves")

        wave1, wave2, wave3, wave4, wave5 = waves

        scores = {}

        # 1. Rules Compliance (40% weight)
        rules_score = self._score_impulse_rules(waves, wave_pattern)
        scores['rules_compliance'] = rules_score

        # If rules are not satisfied, pattern is invalid
        if rules_score['score'] < 100:
            return {
                'valid_pattern': False,
                'overall_probability': 0,
                'scores': scores,
                'rule_violations': rules_score['violations']
            }

        # 2. Fibonacci Ratios (30% weight)
        fib_analysis = self.fib_analyzer.analyze_impulse_wave_pattern(waves)
        scores['fibonacci_ratios'] = {
            'score': fib_analysis['overall_fibonacci_score'],
            'confirmations': fib_analysis['fibonacci_confirmations'],
            'details': fib_analysis
        }

        # 3. Guidelines Adherence (20% weight)
        guidelines_score = self._score_impulse_guidelines(waves)
        scores['guidelines'] = guidelines_score

        # 4. Structure Quality (10% weight)
        structure_score = self._score_wave_structure(waves)
        scores['structure_quality'] = structure_score

        # Calculate overall probability
        overall_prob = (
            (rules_score['score'] / 100) * self.weights['rules_compliance'] +
            (scores['fibonacci_ratios']['score'] / 100) * self.weights['fibonacci_ratios'] +
            (guidelines_score['score'] / 100) * self.weights['guidelines'] +
            (structure_score['score'] / 100) * self.weights['structure_quality']
        ) * 100

        # Categorize probability
        category = self._categorize_probability(overall_prob)

        return {
            'valid_pattern': True,
            'overall_probability': round(overall_prob, 2),
            'category': category,
            'scores': scores,
            'summary': self._generate_summary(overall_prob, scores)
        }

    def score_corrective_pattern(self, waves: List[MonoWave],
                                 wave_pattern: WavePattern = None) -> Dict:
        """
        Calculate comprehensive probability score for a 3-wave corrective pattern.

        Args:
            waves: List of 3 MonoWaves
            wave_pattern: Optional WavePattern object

        Returns:
            Dict with detailed scoring breakdown and overall probability
        """
        if len(waves) != 3:
            raise ValueError("Corrective pattern requires exactly 3 waves")

        waveA, waveB, waveC = waves

        scores = {}

        # 1. Rules Compliance (40% weight)
        rules_score = self._score_corrective_rules(waves, wave_pattern)
        scores['rules_compliance'] = rules_score

        if rules_score['score'] < 100:
            return {
                'valid_pattern': False,
                'overall_probability': 0,
                'scores': scores,
                'rule_violations': rules_score['violations']
            }

        # 2. Fibonacci Ratios (30% weight)
        fib_analysis = self.fib_analyzer.analyze_corrective_pattern(waves)
        scores['fibonacci_ratios'] = {
            'score': fib_analysis['overall_fibonacci_score'],
            'confirmations': fib_analysis['fibonacci_confirmations'],
            'details': fib_analysis
        }

        # 3. Guidelines Adherence (20% weight)
        guidelines_score = self._score_corrective_guidelines(waves)
        scores['guidelines'] = guidelines_score

        # 4. Structure Quality (10% weight)
        structure_score = self._score_wave_structure(waves)
        scores['structure_quality'] = structure_score

        # Calculate overall probability
        overall_prob = (
            (rules_score['score'] / 100) * self.weights['rules_compliance'] +
            (scores['fibonacci_ratios']['score'] / 100) * self.weights['fibonacci_ratios'] +
            (guidelines_score['score'] / 100) * self.weights['guidelines'] +
            (structure_score['score'] / 100) * self.weights['structure_quality']
        ) * 100

        category = self._categorize_probability(overall_prob)

        return {
            'valid_pattern': True,
            'overall_probability': round(overall_prob, 2),
            'category': category,
            'scores': scores,
            'summary': self._generate_summary(overall_prob, scores)
        }

    def _score_impulse_rules(self, waves: List[MonoWave],
                            wave_pattern: WavePattern = None) -> Dict:
        """
        Score compliance with strict impulse wave rules.

        Returns:
            Dict with score (0 or 100) and violations list
        """
        wave1, wave2, wave3, wave4, wave5 = waves
        violations = []

        # Rule 1: Wave 2 cannot retrace more than 100% of Wave 1
        if isinstance(wave1, MonoWaveUp):
            if wave2.low <= wave1.low:
                violations.append("Wave 2 retraced more than 100% of Wave 1")
        else:
            if wave2.high >= wave1.high:
                violations.append("Wave 2 retraced more than 100% of Wave 1")

        # Rule 2: Wave 3 cannot be the shortest
        if wave3.length < wave1.length and wave3.length < wave5.length:
            violations.append("Wave 3 is the shortest wave")

        # Rule 3: Wave 4 cannot overlap Wave 1
        if isinstance(wave1, MonoWaveUp):
            if wave4.low <= wave1.high:
                violations.append("Wave 4 overlaps Wave 1 (not a diagonal)")
        else:
            if wave4.high >= wave1.low:
                violations.append("Wave 4 overlaps Wave 1 (not a diagonal)")

        score = 100 if len(violations) == 0 else 0

        return {
            'score': score,
            'violations': violations,
            'rules_checked': 3
        }

    def _score_corrective_rules(self, waves: List[MonoWave],
                                wave_pattern: WavePattern = None) -> Dict:
        """
        Score compliance with corrective wave rules.

        Returns:
            Dict with score (0 or 100) and violations list
        """
        waveA, waveB, waveC = waves
        violations = []

        # Rule 1: Wave B should not significantly exceed Wave A starting point
        # (allowing for expanded flat up to 123.6%)
        if isinstance(waveA, MonoWaveDown):
            waveB_retracement = waveB.length / waveA.length if waveA.length > 0 else 0
            if waveB_retracement > 1.40:  # Allow some tolerance beyond 123.6%
                violations.append(f"Wave B retracement too large: {waveB_retracement:.2f}")

        # Rule 2: Wave C should move beyond or near Wave A endpoint
        # (minimum 60% of Wave A for running flat)
        if waveA.length > 0:
            waveC_ratio = waveC.length / waveA.length
            if waveC_ratio < 0.50:
                violations.append(f"Wave C too short relative to Wave A: {waveC_ratio:.2f}")

        score = 100 if len(violations) == 0 else 0

        return {
            'score': score,
            'violations': violations,
            'rules_checked': 2
        }

    def _score_impulse_guidelines(self, waves: List[MonoWave]) -> Dict:
        """
        Score adherence to Elliott Wave guidelines for impulse patterns.

        Guidelines checked:
        1. Wave 3 extension (typically 1.618x Wave 1)
        2. Alternation between Wave 2 and Wave 4
        3. Wave equality (Wave 1 and 5 when Wave 3 extends)
        4. Wave proportions

        Returns:
            Dict with score (0-100) and details
        """
        wave1, wave2, wave3, wave4, wave5 = waves
        guideline_scores = []
        details = []

        # Guideline 1: Wave 3 is typically the longest/strongest
        if wave3.length >= wave1.length and wave3.length >= wave5.length:
            guideline_scores.append(100)
            details.append("Wave 3 is longest (ideal)")
        elif wave3.length >= max(wave1.length, wave5.length) * 0.9:
            guideline_scores.append(70)
            details.append("Wave 3 is near longest")
        else:
            guideline_scores.append(40)
            details.append("Wave 3 is not the longest")

        # Guideline 2: Wave 3 extension
        wave3_ratio = wave3.length / wave1.length if wave1.length > 0 else 0
        if 1.50 <= wave3_ratio <= 2.70:
            guideline_scores.append(100)
            details.append(f"Wave 3 extension ideal: {wave3_ratio:.2f}x")
        elif 1.20 <= wave3_ratio <= 3.20:
            guideline_scores.append(70)
            details.append(f"Wave 3 extension acceptable: {wave3_ratio:.2f}x")
        else:
            guideline_scores.append(40)
            details.append(f"Wave 3 extension weak: {wave3_ratio:.2f}x")

        # Guideline 3: Alternation - Wave 2 and Wave 4 differ in depth
        wave2_retracement = wave2.length / wave1.length if wave1.length > 0 else 0
        wave4_retracement = wave4.length / wave3.length if wave3.length > 0 else 0

        retracement_diff = abs(wave2_retracement - wave4_retracement)
        if retracement_diff > 0.20:
            guideline_scores.append(100)
            details.append("Strong alternation between Wave 2 and 4")
        elif retracement_diff > 0.10:
            guideline_scores.append(70)
            details.append("Moderate alternation between Wave 2 and 4")
        else:
            guideline_scores.append(40)
            details.append("Weak alternation between Wave 2 and 4")

        # Guideline 4: Wave equality (when Wave 3 extends, Wave 1 ≈ Wave 5)
        if wave3.length > wave1.length * 1.3:  # Wave 3 is extended
            wave5_vs_1 = wave5.length / wave1.length if wave1.length > 0 else 0
            if 0.85 <= wave5_vs_1 <= 1.15:
                guideline_scores.append(100)
                details.append(f"Wave 1 and 5 equality: {wave5_vs_1:.2f}")
            elif 0.70 <= wave5_vs_1 <= 1.30:
                guideline_scores.append(70)
                details.append(f"Wave 1 and 5 near equality: {wave5_vs_1:.2f}")
            else:
                guideline_scores.append(40)
                details.append(f"Wave 1 and 5 not equal: {wave5_vs_1:.2f}")
        else:
            guideline_scores.append(50)
            details.append("Wave 3 not extended (equality N/A)")

        # Guideline 5: Time proportionality
        wave2_duration = wave2.duration
        wave4_duration = wave4.duration
        if wave2_duration > 0 and wave4_duration > 0:
            duration_ratio = max(wave2_duration, wave4_duration) / min(wave2_duration, wave4_duration)
            if duration_ratio <= 3:
                guideline_scores.append(100)
                details.append("Time proportionality good")
            elif duration_ratio <= 6:
                guideline_scores.append(70)
                details.append("Time proportionality acceptable")
            else:
                guideline_scores.append(40)
                details.append("Time proportionality poor")

        avg_score = sum(guideline_scores) / len(guideline_scores) if guideline_scores else 0

        return {
            'score': round(avg_score, 2),
            'guidelines_met': sum(1 for s in guideline_scores if s >= 70),
            'total_guidelines': len(guideline_scores),
            'details': details
        }

    def _score_corrective_guidelines(self, waves: List[MonoWave]) -> Dict:
        """
        Score adherence to corrective wave guidelines.

        Returns:
            Dict with score and details
        """
        waveA, waveB, waveC = waves
        guideline_scores = []
        details = []

        # Guideline 1: Wave C relationship to Wave A
        waveC_vs_A = waveC.length / waveA.length if waveA.length > 0 else 0
        if 0.90 <= waveC_vs_A <= 1.70:
            guideline_scores.append(100)
            details.append(f"Wave C vs A ideal: {waveC_vs_A:.2f}")
        elif 0.60 <= waveC_vs_A <= 2.70:
            guideline_scores.append(70)
            details.append(f"Wave C vs A acceptable: {waveC_vs_A:.2f}")
        else:
            guideline_scores.append(40)
            details.append(f"Wave C vs A weak: {waveC_vs_A:.2f}")

        # Guideline 2: Wave B retracement
        waveB_vs_A = waveB.length / waveA.length if waveA.length > 0 else 0
        if 0.38 <= waveB_vs_A <= 0.80:
            guideline_scores.append(100)
            details.append(f"Wave B retracement ideal: {waveB_vs_A:.2f}")
        elif 0.20 <= waveB_vs_A <= 1.00:
            guideline_scores.append(70)
            details.append(f"Wave B retracement acceptable: {waveB_vs_A:.2f}")
        else:
            guideline_scores.append(40)
            details.append(f"Wave B retracement unusual: {waveB_vs_A:.2f}")

        # Guideline 3: Time proportionality
        if waveA.duration > 0:
            waveC_time_ratio = waveC.duration / waveA.duration
            if 0.5 <= waveC_time_ratio <= 2.0:
                guideline_scores.append(100)
                details.append("Time proportionality good")
            elif 0.3 <= waveC_time_ratio <= 5.0:
                guideline_scores.append(70)
                details.append("Time proportionality acceptable")
            else:
                guideline_scores.append(40)
                details.append("Time proportionality poor")

        avg_score = sum(guideline_scores) / len(guideline_scores) if guideline_scores else 0

        return {
            'score': round(avg_score, 2),
            'guidelines_met': sum(1 for s in guideline_scores if s >= 70),
            'total_guidelines': len(guideline_scores),
            'details': details
        }

    def _score_wave_structure(self, waves: List[MonoWave]) -> Dict:
        """
        Score the quality of wave structure.

        Factors:
        - Clear pivot points
        - Reasonable wave sizes
        - Duration proportionality

        Returns:
            Dict with score and details
        """
        structure_scores = []
        details = []

        # Check for reasonable wave sizes (no wave is too small)
        lengths = [w.length for w in waves]
        avg_length = sum(lengths) / len(lengths)
        min_length = min(lengths)

        if min_length > avg_length * 0.15:
            structure_scores.append(100)
            details.append("All waves have substantial size")
        elif min_length > avg_length * 0.08:
            structure_scores.append(70)
            details.append("Wave sizes acceptable")
        else:
            structure_scores.append(40)
            details.append("Some waves very small")

        # Check duration proportionality
        durations = [w.duration for w in waves if w.duration > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)

            if min_duration > avg_duration * 0.1:
                structure_scores.append(100)
                details.append("Wave durations well-proportioned")
            elif min_duration > avg_duration * 0.05:
                structure_scores.append(70)
                details.append("Wave durations acceptable")
            else:
                structure_scores.append(40)
                details.append("Some waves very brief")

        avg_score = sum(structure_scores) / len(structure_scores) if structure_scores else 50

        return {
            'score': round(avg_score, 2),
            'details': details
        }

    def _categorize_probability(self, probability: float) -> str:
        """
        Categorize probability score into quality tiers.

        Returns:
            String category
        """
        if probability >= 90:
            return "VERY HIGH - Excellent Elliott Wave pattern"
        elif probability >= 75:
            return "HIGH - Strong Elliott Wave pattern"
        elif probability >= 60:
            return "MODERATE - Valid but weak pattern"
        elif probability >= 50:
            return "LOW - Questionable pattern"
        else:
            return "VERY LOW - Poor pattern quality"

    def _generate_summary(self, overall_prob: float, scores: Dict) -> str:
        """
        Generate human-readable summary of the analysis.

        Returns:
            Summary string
        """
        summary_parts = []

        summary_parts.append(f"Overall Probability: {overall_prob:.1f}%")

        if scores.get('rules_compliance', {}).get('score', 0) == 100:
            summary_parts.append("✓ All Elliott Wave rules satisfied")
        else:
            violations = scores.get('rules_compliance', {}).get('violations', [])
            summary_parts.append(f"✗ Rule violations: {', '.join(violations)}")

        fib_score = scores.get('fibonacci_ratios', {}).get('score', 0)
        fib_confirms = scores.get('fibonacci_ratios', {}).get('confirmations', 0)
        summary_parts.append(f"Fibonacci Score: {fib_score:.1f}% ({fib_confirms} confirmations)")

        guide_score = scores.get('guidelines', {}).get('score', 0)
        guide_met = scores.get('guidelines', {}).get('guidelines_met', 0)
        guide_total = scores.get('guidelines', {}).get('total_guidelines', 0)
        summary_parts.append(f"Guidelines: {guide_met}/{guide_total} met ({guide_score:.1f}%)")

        return " | ".join(summary_parts)
