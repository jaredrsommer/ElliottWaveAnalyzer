"""
Target Calculator for Elliott Wave Analysis

This module calculates price targets and magnitudes for waves in progress
using multiple Fibonacci-based methods.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from models.MonoWave import MonoWave, MonoWaveUp, MonoWaveDown


class TargetCalculator:
    """
    Calculates price targets for Elliott Wave patterns using Fibonacci ratios
    and multiple projection methods.
    """

    def __init__(self):
        self.fibonacci_ratios = {
            'retracement': [0.236, 0.382, 0.500, 0.618, 0.786, 0.854],
            'extension': [1.000, 1.236, 1.382, 1.618, 2.000, 2.618, 3.618],
            'projection': [0.618, 1.000, 1.618, 2.618]
        }

    def calculate_wave_3_targets(self, wave1: MonoWave, wave2: MonoWave,
                                 current_price: Optional[float] = None) -> Dict:
        """
        Calculate Wave 3 price targets.

        Methods:
        1. Wave 3 = 1.618 * Wave 1
        2. Wave 3 = 2.618 * Wave 1
        3. Wave 3 = 1.0 * Wave 1 (minimum)

        Args:
            wave1: Completed Wave 1
            wave2: Completed Wave 2
            current_price: Optional current price for magnitude calculation

        Returns:
            Dict with targets and probabilities
        """
        is_upward = isinstance(wave1, MonoWaveUp)
        wave1_length = wave1.length
        wave2_end = wave2.low if is_upward else wave2.high

        targets = []

        # Target 1: Minimum (1.0 * Wave 1)
        target_min = wave2_end + wave1_length if is_upward else wave2_end - wave1_length
        targets.append({
            'level': 'minimum',
            'price': round(target_min, 2),
            'ratio': '1.0x Wave 1',
            'probability': 0.50,
            'description': 'Minimum Wave 3 target (equals Wave 1)'
        })

        # Target 2: Common (1.618 * Wave 1)
        target_common = wave2_end + (wave1_length * 1.618) if is_upward else wave2_end - (wave1_length * 1.618)
        targets.append({
            'level': 'common',
            'price': round(target_common, 2),
            'ratio': '1.618x Wave 1',
            'probability': 0.70,
            'description': 'Most common Wave 3 target (Golden Ratio)'
        })

        # Target 3: Extended (2.618 * Wave 1)
        target_extended = wave2_end + (wave1_length * 2.618) if is_upward else wave2_end - (wave1_length * 2.618)
        targets.append({
            'level': 'extended',
            'price': round(target_extended, 2),
            'ratio': '2.618x Wave 1',
            'probability': 0.40,
            'description': 'Extended Wave 3 target (strong trend)'
        })

        # Target 4: Very Extended (3.618 * Wave 1)
        target_very_extended = wave2_end + (wave1_length * 3.618) if is_upward else wave2_end - (wave1_length * 3.618)
        targets.append({
            'level': 'very_extended',
            'price': round(target_very_extended, 2),
            'ratio': '3.618x Wave 1',
            'probability': 0.20,
            'description': 'Very extended Wave 3 target (parabolic)'
        })

        result = {
            'wave': 'Wave 3',
            'direction': 'upward' if is_upward else 'downward',
            'targets': targets,
            'base_price': wave2_end,
            'wave1_length': wave1_length
        }

        # Calculate magnitude if current price provided
        if current_price is not None:
            result['current_price'] = current_price
            result['magnitudes'] = self._calculate_magnitudes(current_price, targets, is_upward)

        return result

    def calculate_wave_4_targets(self, wave1: MonoWave, wave2: MonoWave,
                                 wave3: MonoWave, current_price: Optional[float] = None) -> Dict:
        """
        Calculate Wave 4 retracement targets.

        Methods:
        1. Wave 4 = 23.6% retracement of Wave 3
        2. Wave 4 = 38.2% retracement of Wave 3
        3. Wave 4 = 50.0% retracement of Wave 3 (maximum typically)

        Args:
            wave1: Completed Wave 1
            wave2: Completed Wave 2
            wave3: Completed Wave 3
            current_price: Optional current price

        Returns:
            Dict with targets and probabilities
        """
        is_upward = isinstance(wave1, MonoWaveUp)
        wave3_length = wave3.length
        wave3_end = wave3.high if is_upward else wave3.low
        wave1_high = wave1.high if is_upward else wave1.low

        targets = []

        # Target 1: Shallow (23.6% retracement)
        target_shallow = wave3_end - (wave3_length * 0.236) if is_upward else wave3_end + (wave3_length * 0.236)
        targets.append({
            'level': 'shallow',
            'price': round(target_shallow, 2),
            'ratio': '23.6% retracement',
            'probability': 0.60,
            'description': 'Shallow Wave 4 retracement'
        })

        # Target 2: Common (38.2% retracement)
        target_common = wave3_end - (wave3_length * 0.382) if is_upward else wave3_end + (wave3_length * 0.382)
        targets.append({
            'level': 'common',
            'price': round(target_common, 2),
            'ratio': '38.2% retracement',
            'probability': 0.75,
            'description': 'Most common Wave 4 retracement'
        })

        # Target 3: Deep (50% retracement)
        target_deep = wave3_end - (wave3_length * 0.500) if is_upward else wave3_end + (wave3_length * 0.500)
        targets.append({
            'level': 'deep',
            'price': round(target_deep, 2),
            'ratio': '50% retracement',
            'probability': 0.50,
            'description': 'Deep Wave 4 retracement'
        })

        # Add invalidation level (Wave 1 high/low)
        targets.append({
            'level': 'invalidation',
            'price': round(wave1_high, 2),
            'ratio': 'Wave 1 high',
            'probability': 0.0,
            'description': 'INVALIDATION LEVEL - Pattern fails if reached'
        })

        result = {
            'wave': 'Wave 4',
            'direction': 'downward' if is_upward else 'upward',
            'targets': targets,
            'base_price': wave3_end,
            'wave3_length': wave3_length,
            'invalidation_level': wave1_high
        }

        if current_price is not None:
            result['current_price'] = current_price
            result['magnitudes'] = self._calculate_magnitudes(current_price, targets, not is_upward)

        return result

    def calculate_wave_5_targets(self, wave1: MonoWave, wave2: MonoWave,
                                 wave3: MonoWave, wave4: MonoWave,
                                 current_price: Optional[float] = None) -> Dict:
        """
        Calculate Wave 5 price targets using multiple methods.

        Methods:
        1. Wave 5 = Wave 1 (equality)
        2. Wave 5 = 0.618 * Wave 1
        3. Wave 5 = 0.618 * (Wave 1 to Wave 3 distance)
        4. Wave 5 inverse retracement of Wave 4

        Args:
            wave1: Completed Wave 1
            wave2: Completed Wave 2
            wave3: Completed Wave 3
            wave4: Completed Wave 4
            current_price: Optional current price

        Returns:
            Dict with targets and probabilities
        """
        is_upward = isinstance(wave1, MonoWaveUp)
        wave1_length = wave1.length
        wave4_end = wave4.low if is_upward else wave4.high

        targets = []

        # Method 1: Wave 5 = 0.618 * Wave 1
        target_618 = wave4_end + (wave1_length * 0.618) if is_upward else wave4_end - (wave1_length * 0.618)
        targets.append({
            'level': 'conservative',
            'price': round(target_618, 2),
            'ratio': '0.618x Wave 1',
            'probability': 0.65,
            'method': 'Fibonacci ratio of Wave 1',
            'description': 'Conservative Wave 5 target'
        })

        # Method 2: Wave 5 = Wave 1 (equality)
        target_equality = wave4_end + wave1_length if is_upward else wave4_end - wave1_length
        targets.append({
            'level': 'equality',
            'price': round(target_equality, 2),
            'ratio': '1.0x Wave 1',
            'probability': 0.75,
            'method': 'Wave equality',
            'description': 'Wave 5 equals Wave 1 (common when Wave 3 extends)'
        })

        # Method 3: Wave 5 = 0.618 * (Wave 1 to Wave 3)
        if is_upward:
            wave1_to_3_distance = wave3.high - wave1.low
        else:
            wave1_to_3_distance = wave1.high - wave3.low

        target_13_ratio = wave4_end + (wave1_to_3_distance * 0.618) if is_upward else wave4_end - (wave1_to_3_distance * 0.618)
        targets.append({
            'level': 'fibonacci_projection',
            'price': round(target_13_ratio, 2),
            'ratio': '0.618x Wave 1-3',
            'probability': 0.60,
            'method': 'Fibonacci projection from Wave 1-3',
            'description': 'Fibonacci projection target'
        })

        # Method 4: Inverse retracement of Wave 4 (1.618x)
        wave4_length = wave4.length
        target_inverse = wave4_end + (wave4_length * 1.618) if is_upward else wave4_end - (wave4_length * 1.618)
        targets.append({
            'level': 'extended',
            'price': round(target_inverse, 2),
            'ratio': '1.618x Wave 4',
            'probability': 0.50,
            'method': 'Inverse Wave 4 retracement',
            'description': 'Extended Wave 5 target'
        })

        # Sort targets by price
        targets.sort(key=lambda x: x['price'], reverse=is_upward)

        result = {
            'wave': 'Wave 5',
            'direction': 'upward' if is_upward else 'downward',
            'targets': targets,
            'base_price': wave4_end,
            'wave1_length': wave1_length,
            'recommended_target': targets[1] if len(targets) > 1 else targets[0]  # Usually equality
        }

        if current_price is not None:
            result['current_price'] = current_price
            result['magnitudes'] = self._calculate_magnitudes(current_price, targets, is_upward)

        return result

    def calculate_wave_C_targets(self, waveA: MonoWave, waveB: MonoWave,
                                current_price: Optional[float] = None) -> Dict:
        """
        Calculate Wave C targets for corrective patterns.

        Methods:
        1. Wave C = Wave A (equality)
        2. Wave C = 0.618 * Wave A
        3. Wave C = 1.618 * Wave A

        Args:
            waveA: Completed Wave A
            waveB: Completed Wave B
            current_price: Optional current price

        Returns:
            Dict with targets and probabilities
        """
        is_downward = isinstance(waveA, MonoWaveDown)
        waveA_length = waveA.length
        waveB_end = waveB.high if is_downward else waveB.low

        targets = []

        # Target 1: Short (0.618 * Wave A)
        target_short = waveB_end - (waveA_length * 0.618) if is_downward else waveB_end + (waveA_length * 0.618)
        targets.append({
            'level': 'short',
            'price': round(target_short, 2),
            'ratio': '0.618x Wave A',
            'probability': 0.50,
            'description': 'Short Wave C target'
        })

        # Target 2: Equality (1.0 * Wave A)
        target_equality = waveB_end - waveA_length if is_downward else waveB_end + waveA_length
        targets.append({
            'level': 'equality',
            'price': round(target_equality, 2),
            'ratio': '1.0x Wave A',
            'probability': 0.80,
            'description': 'Wave C equals Wave A (most common)'
        })

        # Target 3: Extended (1.618 * Wave A)
        target_extended = waveB_end - (waveA_length * 1.618) if is_downward else waveB_end + (waveA_length * 1.618)
        targets.append({
            'level': 'extended',
            'price': round(target_extended, 2),
            'ratio': '1.618x Wave A',
            'probability': 0.60,
            'description': 'Extended Wave C target'
        })

        # Target 4: Very Extended (2.618 * Wave A)
        target_very_extended = waveB_end - (waveA_length * 2.618) if is_downward else waveB_end + (waveA_length * 2.618)
        targets.append({
            'level': 'very_extended',
            'price': round(target_very_extended, 2),
            'ratio': '2.618x Wave A',
            'probability': 0.30,
            'description': 'Very extended Wave C target'
        })

        result = {
            'wave': 'Wave C',
            'direction': 'downward' if is_downward else 'upward',
            'targets': targets,
            'base_price': waveB_end,
            'waveA_length': waveA_length,
            'recommended_target': targets[1]  # Equality is most common
        }

        if current_price is not None:
            result['current_price'] = current_price
            result['magnitudes'] = self._calculate_magnitudes(current_price, targets, is_downward)

        return result

    def _calculate_magnitudes(self, current_price: float, targets: List[Dict],
                             is_upward: bool) -> List[Dict]:
        """
        Calculate remaining magnitude (distance) from current price to each target.

        Args:
            current_price: Current market price
            targets: List of target dicts
            is_upward: Direction of the wave

        Returns:
            List of magnitude dicts
        """
        magnitudes = []

        for target in targets:
            target_price = target['price']
            distance = target_price - current_price
            distance_pct = (distance / current_price * 100) if current_price > 0 else 0

            # Check if target is in the correct direction
            if is_upward and distance > 0:
                status = 'pending'
            elif not is_upward and distance < 0:
                status = 'pending'
            elif abs(distance) < (current_price * 0.005):  # Within 0.5%
                status = 'reached'
            else:
                status = 'exceeded'

            magnitudes.append({
                'level': target['level'],
                'target_price': target_price,
                'current_price': current_price,
                'distance': round(distance, 2),
                'distance_pct': round(distance_pct, 2),
                'status': status,
                'probability': target.get('probability', 0)
            })

        return magnitudes

    def calculate_all_impulse_targets(self, waves: List[MonoWave],
                                      current_wave: str,
                                      current_price: float) -> Dict:
        """
        Calculate all relevant targets for an impulse pattern in progress.

        Args:
            waves: List of completed waves (1-4 waves depending on current_wave)
            current_wave: Which wave is in progress ('3', '4', or '5')
            current_price: Current market price

        Returns:
            Complete target analysis
        """
        if current_wave == '3':
            if len(waves) < 2:
                raise ValueError("Need at least Wave 1 and 2 to calculate Wave 3 targets")
            return self.calculate_wave_3_targets(waves[0], waves[1], current_price)

        elif current_wave == '4':
            if len(waves) < 3:
                raise ValueError("Need Wave 1, 2, and 3 to calculate Wave 4 targets")
            return self.calculate_wave_4_targets(waves[0], waves[1], waves[2], current_price)

        elif current_wave == '5':
            if len(waves) < 4:
                raise ValueError("Need Wave 1, 2, 3, and 4 to calculate Wave 5 targets")
            return self.calculate_wave_5_targets(waves[0], waves[1], waves[2], waves[3], current_price)

        else:
            raise ValueError(f"Unknown wave: {current_wave}. Must be '3', '4', or '5'")

    def calculate_support_resistance_levels(self, waves: List[MonoWave]) -> Dict:
        """
        Calculate key support and resistance levels from wave structure.

        Args:
            waves: List of waves

        Returns:
            Dict with support and resistance levels
        """
        highs = [w.high for w in waves]
        lows = [w.low for w in waves]

        # Get unique levels
        resistance_levels = sorted(set(highs), reverse=True)
        support_levels = sorted(set(lows))

        return {
            'resistance_levels': [round(r, 2) for r in resistance_levels],
            'support_levels': [round(s, 2) for s in support_levels],
            'major_resistance': round(max(highs), 2) if highs else None,
            'major_support': round(min(lows), 2) if lows else None
        }
