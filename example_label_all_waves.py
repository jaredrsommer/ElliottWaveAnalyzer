"""
Example: Label ALL Elliott Wave Segments in Historical Data

This example demonstrates how to iterate through entire OHLCV datasets
and label EVERY identifiable Elliott Wave pattern and segment.

Unlike the trading-focused examples that find "current" patterns,
this creates a comprehensive historical annotation of all waves.
"""

import pandas as pd
import numpy as np
from models.HistoricalWaveLabeler import HistoricalWaveLabeler

print("=" * 80)
print("COMPREHENSIVE HISTORICAL ELLIOTT WAVE LABELING")
print("=" * 80)
print()

# Load data
print("Step 1: Loading data...")
df = pd.read_csv('data/btc-usd_1d.csv')
print(f"✓ Loaded {len(df)} candles")
print(f"  Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
print()

# Create Historical Wave Labeler
print("Step 2: Creating Historical Wave Labeler...")
labeler = HistoricalWaveLabeler(
    df=df,
    min_probability=60.0,  # Minimum 60% probability
    overlap_strategy='highest_probability'  # Keep best patterns in overlapping regions
)
print("✓ Labeler created")
print()

# ============================================================================
# COMPREHENSIVE LABELING - This iterates through ALL data
# ============================================================================
print("Step 3: Scanning and labeling ALL waves in dataset...")
print("(This may take a few minutes for large datasets)")
print()

results = labeler.label_all_waves(
    scan_step=5,  # Check every 5 candles
    max_patterns_per_start=2,  # Keep top 2 patterns from each start point
    label_impulse=True,  # Label impulse patterns (12345)
    label_correction=True  # Label corrective patterns (ABC)
)

print()
print("=" * 80)
print("LABELING COMPLETE!")
print("=" * 80)
print()

# ============================================================================
# VIEW RESULTS
# ============================================================================
print("Step 4: Analyzing results...")
print()

print(f"📊 Summary:")
print(f"  Total patterns found: {results['total_patterns']}")
print(f"  Impulse patterns: {results['impulse_patterns']}")
print(f"  Correction patterns: {results['correction_patterns']}")
print(f"  Total wave segments labeled: {results['total_wave_labels']}")
print(f"  Average probability: {results['avg_probability']:.1f}%")
print()

# ============================================================================
# GET DETAILED STATISTICS
# ============================================================================
print("Step 5: Getting detailed statistics...")
print()

stats = labeler.get_statistics()

print(f"Wave Type Distribution:")
print(f"  Impulse waves: {stats['impulse_waves']}")
print(f"  Correction waves: {stats['correction_waves']}")
print()

print(f"Wave Label Occurrences:")
for label in ['1', '2', '3', '4', '5', 'A', 'B', 'C']:
    count = stats['wave_label_counts'].get(label, 0)
    print(f"  Wave {label}: {count} occurrences")
print()

print(f"Quality Metrics:")
print(f"  Average probability: {stats['avg_probability']:.1f}%")
print(f"  Median probability: {stats['median_probability']:.1f}%")
print(f"  Average wave length: ${stats['avg_wave_length']:.2f}")
print()

# ============================================================================
# VIEW WAVE SUMMARY
# ============================================================================
print("Step 6: Viewing wave summary...")
print()

wave_summary = labeler.get_wave_summary()
print(f"First 10 labeled waves:")
print(wave_summary.head(10).to_string())
print()

# ============================================================================
# VIEW PATTERN SUMMARY
# ============================================================================
print("Step 7: Viewing pattern summary...")
print()

pattern_summary = labeler.get_pattern_summary()
print(f"Top 10 highest probability patterns:")
print(pattern_summary.head(10)[['type', 'probability', 'start_date', 'end_date', 'duration']].to_string())
print()

# ============================================================================
# GET LABELED DATAFRAME
# ============================================================================
print("Step 8: Getting labeled dataframe...")
print()

labeled_df = labeler.labeled_dataframe
print(f"Labeled dataframe shape: {labeled_df.shape}")
print(f"New columns added: {[col for col in labeled_df.columns if 'wave' in col.lower()]}")
print()

# Show some examples of labeled candles
wave_end_df = labeled_df[labeled_df['wave_end'] == True]
print(f"Candles with wave endings: {len(wave_end_df)}")
print("\nFirst 10 wave endings:")
print(wave_end_df[['Date', 'Close', 'wave_label', 'wave_type', 'wave_probability']].head(10).to_string())
print()

# ============================================================================
# EXPORT RESULTS
# ============================================================================
print("Step 9: Exporting results...")
print()

# Export wave labels to CSV
labeler.export_labels_to_csv('output/all_wave_labels.csv')

# Export pattern summary to CSV
labeler.export_patterns_to_csv('output/all_patterns.csv')

# Export labeled dataframe
labeled_df.to_csv('output/labeled_dataframe.csv', index=False)
print(f"✓ Exported labeled dataframe to output/labeled_dataframe.csv")
print()

# ============================================================================
# PRINT COMPREHENSIVE REPORT
# ============================================================================
print("Step 10: Generating comprehensive report...")
labeler.print_report()

# ============================================================================
# EXAMPLE: Filter waves by criteria
# ============================================================================
print("\n" + "=" * 80)
print("ADVANCED FILTERING EXAMPLES")
print("=" * 80)
print()

# Get only high-probability waves
high_prob_waves = wave_summary[wave_summary['probability'] >= 75.0]
print(f"High-probability waves (≥75%): {len(high_prob_waves)}")
print(f"  Impulse: {len(high_prob_waves[high_prob_waves['wave_type'] == 'impulse'])}")
print(f"  Correction: {len(high_prob_waves[high_prob_waves['wave_type'] == 'correction'])}")
print()

# Get only Wave 3s (typically strongest)
wave3_segments = wave_summary[wave_summary['label'] == '3']
print(f"Wave 3 segments found: {len(wave3_segments)}")
if len(wave3_segments) > 0:
    print(f"  Average probability: {wave3_segments['probability'].mean():.1f}%")
    print(f"  Average length: ${wave3_segments['length'].mean():.2f}")
print()

# Get only Wave 5s (potential exhaustion points)
wave5_segments = wave_summary[wave_summary['label'] == '5']
print(f"Wave 5 segments found: {len(wave5_segments)}")
if len(wave5_segments) > 0:
    print(f"  Average probability: {wave5_segments['probability'].mean():.1f}%")
    print(f"  These could be potential reversal points")
print()

# Get corrective patterns
abc_waves = wave_summary[wave_summary['wave_type'] == 'correction']
print(f"ABC corrective waves: {len(abc_waves)}")
if len(abc_waves) > 0:
    print(f"  Wave A: {len(abc_waves[abc_waves['label'] == 'A'])}")
    print(f"  Wave B: {len(abc_waves[abc_waves['label'] == 'B'])}")
    print(f"  Wave C: {len(abc_waves[abc_waves['label'] == 'C'])}")
print()

# ============================================================================
# EXAMPLE: Use labeled data for analysis
# ============================================================================
print("=" * 80)
print("USING LABELED DATA FOR ANALYSIS")
print("=" * 80)
print()

# Find all complete impulse patterns (has all 5 waves)
impulse_patterns = pattern_summary[pattern_summary['type'] == 'impulse']
print(f"Complete 12345 impulse patterns: {len(impulse_patterns)}")

if len(impulse_patterns) > 0:
    # Show the best impulse pattern
    best_impulse = impulse_patterns.iloc[0]
    print(f"\nBest impulse pattern:")
    print(f"  Probability: {best_impulse['probability']:.1f}%")
    print(f"  Start date: {best_impulse['start_date']}")
    print(f"  End date: {best_impulse['end_date']}")
    print(f"  Duration: {best_impulse['duration']} candles")
    print(f"  Wave options: {best_impulse['wave_options']}")
print()

# Find periods with multiple overlapping patterns (high conviction areas)
wave_density = labeled_df['wave_label'].str.count(',') + (labeled_df['wave_label'] != '').astype(int)
high_density = labeled_df[wave_density > 1]
print(f"Candles with multiple wave labels (high conviction): {len(high_density)}")
if len(high_density) > 0:
    print(f"\nExample high-conviction areas:")
    print(high_density[['Date', 'Close', 'wave_label', 'wave_probability']].head(5).to_string())
print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("✓ ALL waves in the historical dataset have been labeled!")
print()
print("You now have:")
print("  1. Complete wave labels for every segment")
print("  2. Probability scores for each pattern")
print("  3. CSV exports of all waves and patterns")
print("  4. Labeled dataframe with wave information")
print()
print("Use this data to:")
print("  - Visualize historical wave structure")
print("  - Backtest wave-based strategies")
print("  - Identify high-probability setups")
print("  - Study wave behavior patterns")
print("  - Train machine learning models")
print()
print("Files created:")
print("  - output/all_wave_labels.csv")
print("  - output/all_patterns.csv")
print("  - output/labeled_dataframe.csv")
print()
print("=" * 80)
