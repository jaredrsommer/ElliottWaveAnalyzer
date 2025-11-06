"""
Historical Wave Labeler - Complete Elliott Wave Annotation

This module iterates through all OHLCV data and labels every identifiable
Elliott Wave segment throughout the entire historical dataset.

Unlike the trading-focused analyzers that find the "best" current pattern,
this tool comprehensively annotates ALL waves in the data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer, WaveCandidate
from models.ProbabilityScorer import ProbabilityScorer
from models.FibonacciAnalyzer import FibonacciAnalyzer


class WaveLabel:
    """Represents a labeled wave segment in historical data."""

    def __init__(self, wave_type: str, label: str, start_idx: int, end_idx: int,
                 start_price: float, end_price: float, probability: float,
                 parent_pattern_idx: int = None):
        self.wave_type = wave_type  # 'impulse' or 'correction'
        self.label = label  # '1', '2', '3', '4', '5' or 'A', 'B', 'C'
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.start_price = start_price
        self.end_price = end_price
        self.probability = probability
        self.parent_pattern_idx = parent_pattern_idx

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'wave_type': self.wave_type,
            'label': self.label,
            'start_idx': self.start_idx,
            'end_idx': self.end_idx,
            'start_price': self.start_price,
            'end_price': self.end_price,
            'probability': self.probability,
            'length': abs(self.end_price - self.start_price),
            'direction': 'up' if self.end_price > self.start_price else 'down'
        }

    def __repr__(self):
        return (f"WaveLabel({self.label}, {self.start_idx}->{self.end_idx}, "
                f"${self.start_price:.2f}->${self.end_price:.2f}, "
                f"prob={self.probability:.1f}%)")


class HistoricalWaveLabeler:
    """
    Comprehensively label all Elliott Wave patterns in historical OHLCV data.

    This class iterates through the entire dataset and identifies all possible
    wave segments, creating a complete annotation of Elliott Wave patterns.
    """

    def __init__(self, df: pd.DataFrame, min_probability: float = 60.0,
                 overlap_strategy: str = 'highest_probability'):
        """
        Initialize Historical Wave Labeler.

        Args:
            df: DataFrame with OHLCV data
            min_probability: Minimum probability for valid patterns
            overlap_strategy: How to handle overlapping patterns
                - 'highest_probability': Keep highest probability pattern
                - 'all': Keep all patterns (may overlap)
                - 'non_overlapping': Keep non-overlapping patterns only
        """
        self.df = df
        self.min_probability = min_probability
        self.overlap_strategy = overlap_strategy

        self.analyzer = EnhancedWaveAnalyzer(df, verbose=False,
                                             min_probability=min_probability)

        # Storage for labeled waves
        self.all_patterns: List[Dict] = []
        self.all_wave_labels: List[WaveLabel] = []
        self.labeled_dataframe: Optional[pd.DataFrame] = None

    def label_all_waves(self, scan_step: int = 5, max_patterns_per_start: int = 3,
                       label_impulse: bool = True, label_correction: bool = True) -> Dict:
        """
        Scan entire dataset and label all Elliott Wave patterns.

        Args:
            scan_step: How many candles to step forward for each scan
            max_patterns_per_start: Max patterns to find from each starting point
            label_impulse: Whether to label impulse patterns
            label_correction: Whether to label corrective patterns

        Returns:
            Dict with complete labeling results
        """
        print(f"🔍 Starting comprehensive wave labeling...")
        print(f"   Dataset: {len(self.df)} candles")
        print(f"   Scan step: {scan_step}")
        print(f"   Min probability: {self.min_probability}%")
        print(f"   Overlap strategy: {self.overlap_strategy}")
        print()

        # Scan through all possible starting points
        total_scans = (len(self.df) - 50) // scan_step

        for scan_num, idx_start in enumerate(range(0, len(self.df) - 50, scan_step), 1):
            if scan_num % 10 == 0 or scan_num == 1:
                progress = (scan_num / total_scans) * 100
                print(f"   Progress: {progress:.1f}% ({scan_num}/{total_scans} scans)")

            # Find impulse patterns from this starting point
            if label_impulse:
                impulse_candidates = self.analyzer.find_best_impulse_waves(
                    idx_start, max_results=max_patterns_per_start
                )

                for candidate in impulse_candidates:
                    self._add_pattern_to_results(candidate, 'impulse', idx_start)

            # Find corrective patterns from this starting point
            if label_correction:
                correction_candidates = self.analyzer.find_best_corrective_waves(
                    idx_start, max_results=max_patterns_per_start
                )

                for candidate in correction_candidates:
                    self._add_pattern_to_results(candidate, 'correction', idx_start)

        print(f"\n✓ Scanning complete!")
        print(f"   Found {len(self.all_patterns)} total patterns")

        # Process patterns based on overlap strategy
        self._process_overlaps()

        # Create labeled dataframe
        self.labeled_dataframe = self._create_labeled_dataframe()

        print(f"\n✓ Labeling complete!")
        print(f"   Unique wave segments: {len(self.all_wave_labels)}")
        print(f"   Average probability: {np.mean([w.probability for w in self.all_wave_labels]):.1f}%")

        return {
            'total_patterns': len(self.all_patterns),
            'total_wave_labels': len(self.all_wave_labels),
            'impulse_patterns': sum(1 for p in self.all_patterns if p['type'] == 'impulse'),
            'correction_patterns': sum(1 for p in self.all_patterns if p['type'] == 'correction'),
            'avg_probability': np.mean([w.probability for w in self.all_wave_labels]),
            'labeled_dataframe': self.labeled_dataframe
        }

    def _add_pattern_to_results(self, candidate: WaveCandidate,
                                wave_type: str, start_idx: int):
        """Add a pattern candidate to results."""
        pattern_dict = {
            'type': wave_type,
            'probability': candidate.probability,
            'start_idx': start_idx,
            'end_idx': candidate.pattern.idx_end,
            'wave_options': candidate.wave_options,
            'pattern': candidate.pattern,
            'analysis': candidate.probability_analysis
        }

        self.all_patterns.append(pattern_dict)

    def _process_overlaps(self):
        """Process overlapping patterns based on strategy."""
        print(f"\n📊 Processing overlaps with strategy: '{self.overlap_strategy}'...")

        if self.overlap_strategy == 'all':
            # Keep all patterns, extract all waves
            for i, pattern_dict in enumerate(self.all_patterns):
                self._extract_waves_from_pattern(pattern_dict, i)

        elif self.overlap_strategy == 'highest_probability':
            # Group patterns by overlapping regions, keep highest probability
            filtered_patterns = self._filter_by_highest_probability()
            for i, pattern_dict in enumerate(filtered_patterns):
                self._extract_waves_from_pattern(pattern_dict, i)

        elif self.overlap_strategy == 'non_overlapping':
            # Keep only non-overlapping patterns
            non_overlapping = self._get_non_overlapping_patterns()
            for i, pattern_dict in enumerate(non_overlapping):
                self._extract_waves_from_pattern(pattern_dict, i)

        print(f"   Extracted {len(self.all_wave_labels)} wave segments")

    def _filter_by_highest_probability(self) -> List[Dict]:
        """Keep only highest probability patterns in overlapping regions."""
        if not self.all_patterns:
            return []

        # Sort by probability (highest first)
        sorted_patterns = sorted(self.all_patterns,
                                key=lambda x: x['probability'],
                                reverse=True)

        kept_patterns = []
        used_ranges = []

        for pattern in sorted_patterns:
            start = pattern['start_idx']
            end = pattern['end_idx']

            # Check if this pattern overlaps significantly with any kept pattern
            overlaps = False
            for used_start, used_end in used_ranges:
                overlap = self._calculate_overlap(start, end, used_start, used_end)
                if overlap > 0.5:  # More than 50% overlap
                    overlaps = True
                    break

            if not overlaps:
                kept_patterns.append(pattern)
                used_ranges.append((start, end))

        print(f"   Filtered from {len(self.all_patterns)} to {len(kept_patterns)} patterns")
        return kept_patterns

    def _get_non_overlapping_patterns(self) -> List[Dict]:
        """Get strictly non-overlapping patterns."""
        if not self.all_patterns:
            return []

        # Sort by start index
        sorted_patterns = sorted(self.all_patterns,
                                key=lambda x: (x['start_idx'], -x['probability']))

        kept_patterns = []
        last_end = -1

        for pattern in sorted_patterns:
            if pattern['start_idx'] >= last_end:
                kept_patterns.append(pattern)
                last_end = pattern['end_idx']

        print(f"   Filtered from {len(self.all_patterns)} to {len(kept_patterns)} non-overlapping")
        return kept_patterns

    def _calculate_overlap(self, start1: int, end1: int,
                          start2: int, end2: int) -> float:
        """Calculate overlap ratio between two ranges."""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start >= overlap_end:
            return 0.0

        overlap_length = overlap_end - overlap_start
        range1_length = end1 - start1

        if range1_length == 0:
            return 0.0

        return overlap_length / range1_length

    def _extract_waves_from_pattern(self, pattern_dict: Dict, pattern_idx: int):
        """Extract individual wave labels from a pattern."""
        pattern = pattern_dict['pattern']
        wave_type = pattern_dict['type']
        probability = pattern_dict['probability']

        for wave_num, wave in pattern.waves.items():
            label = wave.label if hasattr(wave, 'label') else wave_num.replace('wave', '')

            wave_label = WaveLabel(
                wave_type=wave_type,
                label=label,
                start_idx=wave.idx_start,
                end_idx=wave.idx_end,
                start_price=wave.low if hasattr(wave, 'low') else 0,
                end_price=wave.high if hasattr(wave, 'high') else 0,
                probability=probability,
                parent_pattern_idx=pattern_idx
            )

            self.all_wave_labels.append(wave_label)

    def _create_labeled_dataframe(self) -> pd.DataFrame:
        """Create a dataframe with wave labels."""
        df_labeled = self.df.copy()

        # Initialize label columns
        df_labeled['wave_label'] = ''
        df_labeled['wave_type'] = ''
        df_labeled['wave_probability'] = np.nan
        df_labeled['wave_start'] = False
        df_labeled['wave_end'] = False

        # Add each wave label
        for wave_label in self.all_wave_labels:
            # Mark the range with this wave
            start = wave_label.start_idx
            end = wave_label.end_idx

            if start < len(df_labeled) and end < len(df_labeled):
                # Mark start and end points
                df_labeled.loc[start, 'wave_start'] = True
                df_labeled.loc[end, 'wave_end'] = True

                # Add label at the end point
                current_label = df_labeled.loc[end, 'wave_label']
                if current_label:
                    df_labeled.loc[end, 'wave_label'] = f"{current_label},{wave_label.label}"
                else:
                    df_labeled.loc[end, 'wave_label'] = wave_label.label

                df_labeled.loc[end, 'wave_type'] = wave_label.wave_type
                df_labeled.loc[end, 'wave_probability'] = wave_label.probability

        return df_labeled

    def get_wave_summary(self) -> pd.DataFrame:
        """Get a summary DataFrame of all labeled waves."""
        if not self.all_wave_labels:
            return pd.DataFrame()

        wave_data = [wave.to_dict() for wave in self.all_wave_labels]
        df_summary = pd.DataFrame(wave_data)

        # Add date information if available
        if 'Date' in self.df.columns:
            df_summary['start_date'] = df_summary['start_idx'].apply(
                lambda x: self.df.iloc[x]['Date'] if x < len(self.df) else None
            )
            df_summary['end_date'] = df_summary['end_idx'].apply(
                lambda x: self.df.iloc[x]['Date'] if x < len(self.df) else None
            )

        return df_summary.sort_values('start_idx')

    def get_pattern_summary(self) -> pd.DataFrame:
        """Get a summary DataFrame of all identified patterns."""
        if not self.all_patterns:
            return pd.DataFrame()

        pattern_data = []
        for pattern in self.all_patterns:
            pattern_data.append({
                'type': pattern['type'],
                'probability': pattern['probability'],
                'start_idx': pattern['start_idx'],
                'end_idx': pattern['end_idx'],
                'duration': pattern['end_idx'] - pattern['start_idx'],
                'wave_options': str(pattern['wave_options'])
            })

        df_summary = pd.DataFrame(pattern_data)

        # Add date information
        if 'Date' in self.df.columns:
            df_summary['start_date'] = df_summary['start_idx'].apply(
                lambda x: self.df.iloc[x]['Date'] if x < len(self.df) else None
            )
            df_summary['end_date'] = df_summary['end_idx'].apply(
                lambda x: self.df.iloc[x]['Date'] if x < len(self.df) else None
            )

        return df_summary.sort_values('probability', ascending=False)

    def export_labels_to_csv(self, filename: str):
        """Export wave labels to CSV file."""
        df_summary = self.get_wave_summary()
        df_summary.to_csv(filename, index=False)
        print(f"✓ Exported {len(df_summary)} wave labels to {filename}")

    def export_patterns_to_csv(self, filename: str):
        """Export pattern summary to CSV file."""
        df_summary = self.get_pattern_summary()
        df_summary.to_csv(filename, index=False)
        print(f"✓ Exported {len(df_summary)} patterns to {filename}")

    def get_statistics(self) -> Dict:
        """Get statistics about the labeled waves."""
        if not self.all_wave_labels:
            return {}

        df_waves = self.get_wave_summary()

        stats = {
            'total_waves': len(self.all_wave_labels),
            'impulse_waves': sum(1 for w in self.all_wave_labels if w.wave_type == 'impulse'),
            'correction_waves': sum(1 for w in self.all_wave_labels if w.wave_type == 'correction'),
            'avg_probability': df_waves['probability'].mean(),
            'median_probability': df_waves['probability'].median(),
            'avg_wave_length': df_waves['length'].mean(),
            'wave_label_counts': df_waves['label'].value_counts().to_dict(),
            'direction_counts': df_waves['direction'].value_counts().to_dict()
        }

        return stats

    def print_report(self):
        """Print a comprehensive report of the labeling."""
        print("\n" + "=" * 70)
        print("HISTORICAL WAVE LABELING REPORT")
        print("=" * 70)

        stats = self.get_statistics()

        print(f"\nDataset Information:")
        print(f"  Total Candles: {len(self.df)}")
        print(f"  Date Range: {self.df.iloc[0]['Date']} to {self.df.iloc[-1]['Date']}")

        print(f"\nWave Patterns Found:")
        print(f"  Total Patterns: {len(self.all_patterns)}")
        print(f"  Impulse Patterns: {sum(1 for p in self.all_patterns if p['type'] == 'impulse')}")
        print(f"  Correction Patterns: {sum(1 for p in self.all_patterns if p['type'] == 'correction')}")

        print(f"\nWave Segments Labeled:")
        print(f"  Total Segments: {stats.get('total_waves', 0)}")
        print(f"  Impulse Waves: {stats.get('impulse_waves', 0)}")
        print(f"  Correction Waves: {stats.get('correction_waves', 0)}")

        print(f"\nQuality Metrics:")
        print(f"  Average Probability: {stats.get('avg_probability', 0):.1f}%")
        print(f"  Median Probability: {stats.get('median_probability', 0):.1f}%")

        if 'wave_label_counts' in stats:
            print(f"\nWave Label Distribution:")
            for label, count in sorted(stats['wave_label_counts'].items()):
                print(f"  Wave {label}: {count} occurrences")

        print("\n" + "=" * 70)
