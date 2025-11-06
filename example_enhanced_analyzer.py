"""
Example: Enhanced Elliott Wave Analyzer with Probability Scoring

This example demonstrates the new enhanced features:
- Probability scoring for wave patterns
- Fibonacci ratio analysis
- Price target calculation
- Segment length variation analysis
"""

import pandas as pd
import numpy as np
from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from models.helpers import plot_pattern

# Load data
print("Loading data...")
df = pd.read_csv('data/btc-usd_1d.csv')
print(f"Loaded {len(df)} candles")
print(f"Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
print()

# Find the lowest point to start analysis
idx_start = np.argmin(np.array(list(df['Low'])))
print(f"Starting analysis from index {idx_start} (lowest point)")
print(f"Date: {df.iloc[idx_start]['Date']}, Price: ${df.iloc[idx_start]['Low']:.2f}")
print()

# ============================================================================
# EXAMPLE 1: Find Best Impulse Wave with Probability Scoring
# ============================================================================
print("=" * 80)
print("EXAMPLE 1: Finding Best Impulse Wave Patterns")
print("=" * 80)

# Create analyzer with minimum probability threshold of 60%
analyzer = EnhancedWaveAnalyzer(df, verbose=False, min_probability=60.0)
analyzer.set_combinatorial_limits(n_impulse=15, n_correction=12)

# Find top 5 impulse patterns
print("\nSearching for impulse patterns (this may take a moment)...")
impulse_candidates = analyzer.find_best_impulse_waves(idx_start, max_results=5)

if impulse_candidates:
    print(f"\nFound {len(impulse_candidates)} valid impulse patterns:")
    print()

    for i, candidate in enumerate(impulse_candidates, 1):
        print(f"Pattern #{i}:")
        print(f"  Probability: {candidate.probability:.1f}%")
        print(f"  Category: {candidate.probability_analysis['category']}")
        print(f"  Wave Options: {candidate.wave_options}")

        # Show detailed scores
        scores = candidate.probability_analysis['scores']
        print(f"  Rules Compliance: {scores['rules_compliance']['score']:.0f}%")
        print(f"  Fibonacci Score: {scores['fibonacci_ratios']['score']:.1f}%")
        print(f"  Guidelines Score: {scores['guidelines']['score']:.1f}%")
        print(f"  Structure Score: {scores['structure_quality']['score']:.1f}%")
        print()

    # Plot the best pattern
    best_pattern = impulse_candidates[0]
    print(f"Plotting best pattern (Probability: {best_pattern.probability:.1f}%)...")
    plot_pattern(df, best_pattern.pattern, title=f"Best Impulse - {best_pattern.probability:.1f}% Probability")
else:
    print("No valid impulse patterns found meeting the probability threshold.")

print()

# ============================================================================
# EXAMPLE 2: Price Target Calculation
# ============================================================================
print("=" * 80)
print("EXAMPLE 2: Price Target Calculation")
print("=" * 80)

current_price = analyzer.get_current_price()
print(f"Current Price: ${current_price:.2f}")
print()

# Find wave pattern with targets
analysis = analyzer.find_wave_with_targets(idx_start, wave_type='impulse', current_price=current_price)

if analysis['found']:
    print(f"Wave Pattern Found!")
    print(f"Probability: {analysis['probability']:.1f}%")
    print(f"Category: {analysis['category']}")
    print()

    if 'targets' in analysis:
        targets = analysis['targets']
        print(f"PRICE TARGETS FOR {targets['wave']}:")
        print(f"Direction: {targets['direction']}")
        print(f"Base Price: ${targets['base_price']:.2f}")
        print()

        for target in targets['targets']:
            print(f"  {target['level'].upper()}:")
            print(f"    Price: ${target['price']:.2f}")
            print(f"    Ratio: {target['ratio']}")
            print(f"    Probability: {target.get('probability', 0)*100:.0f}%")
            print(f"    Description: {target.get('description', 'N/A')}")

            # Show magnitude if available
            if 'magnitudes' in targets:
                mag = next((m for m in targets['magnitudes'] if m['level'] == target['level']), None)
                if mag:
                    print(f"    Distance: ${mag['distance']:.2f} ({mag['distance_pct']:.2f}%)")
                    print(f"    Status: {mag['status']}")
            print()

print()

# ============================================================================
# EXAMPLE 3: Segment Length Variation Analysis
# ============================================================================
print("=" * 80)
print("EXAMPLE 3: Segment Length Variation Analysis")
print("=" * 80)

print("\nAnalyzing how different wave configurations affect probability...")
variation_analysis = analyzer.analyze_segment_variations(
    idx_start,
    wave_type='impulse',
    min_probability=60.0
)

if variation_analysis['found']:
    print(f"\nTotal patterns found: {variation_analysis['total_candidates']}")
    print()

    best = variation_analysis['best_candidate']
    print(f"Best Pattern:")
    print(f"  Wave Options: {best.wave_options}")
    print(f"  Probability: {best.probability:.1f}%")
    print()

    print("Probability Distribution:")
    for range_name, data in variation_analysis['probability_distribution'].items():
        print(f"\n  {range_name}: {data['count']} patterns")
        print(f"    Average Probability: {data['avg_probability']:.1f}%")
        print(f"    Wave Options Examples:")
        for opts in data['wave_options'][:3]:  # Show first 3
            print(f"      {opts}")

print()

# ============================================================================
# EXAMPLE 4: Comprehensive Analysis Report
# ============================================================================
print("=" * 80)
print("EXAMPLE 4: Comprehensive Analysis Report")
print("=" * 80)

report = analyzer.create_analysis_report(idx_start, wave_type='impulse')
print(report)
print()

# ============================================================================
# EXAMPLE 5: Corrective Wave Analysis
# ============================================================================
print("=" * 80)
print("EXAMPLE 5: Corrective Wave Analysis")
print("=" * 80)

# Find the highest point for corrective analysis
idx_high = np.argmax(np.array(list(df['High'])))
print(f"Starting corrective analysis from index {idx_high} (highest point)")
print(f"Date: {df.iloc[idx_high]['Date']}, Price: ${df.iloc[idx_high]['High']:.2f}")
print()

correction_candidates = analyzer.find_best_corrective_waves(idx_high, max_results=3)

if correction_candidates:
    print(f"Found {len(correction_candidates)} corrective patterns:")
    print()

    for i, candidate in enumerate(correction_candidates, 1):
        print(f"Pattern #{i}:")
        print(f"  Probability: {candidate.probability:.1f}%")
        print(f"  Wave Options: {candidate.wave_options}")

        # Get Fibonacci analysis
        fib_details = candidate.probability_analysis['scores']['fibonacci_ratios']['details']
        if 'waveC_vs_waveA' in fib_details:
            ratio = fib_details['waveC_vs_waveA']['ratio']
            print(f"  Wave C / Wave A: {ratio:.3f}")

        print()
else:
    print("No valid corrective patterns found.")

print()

# ============================================================================
# EXAMPLE 6: Fibonacci Analysis Details
# ============================================================================
print("=" * 80)
print("EXAMPLE 6: Detailed Fibonacci Analysis")
print("=" * 80)

if impulse_candidates:
    best = impulse_candidates[0]
    fib_analysis = best.probability_analysis['scores']['fibonacci_ratios']['details']

    print("Wave 2 Analysis:")
    wave2_data = fib_analysis['wave2_retracement']
    print(f"  Retracement Ratio: {wave2_data['ratio']:.3f}")
    print(f"  Quality Score: {wave2_data['quality']*100:.1f}%")
    print(f"  In Ideal Range (50-61.8%): {wave2_data['in_ideal_range']}")
    if wave2_data['matches']:
        print(f"  Fibonacci Matches:")
        for match in wave2_data['matches']:
            print(f"    {match['fibonacci_ratio']:.3f} (score: {match['score']:.2f})")
    print()

    print("Wave 3 Analysis:")
    wave3_data = fib_analysis['wave3_extension']
    print(f"  Extension Ratio: {wave3_data['ratio']:.3f}")
    print(f"  Quality Score: {wave3_data['quality']*100:.1f}%")
    print(f"  In Ideal Range (1.618-2.618): {wave3_data['in_ideal_range']}")
    if wave3_data['matches']:
        print(f"  Fibonacci Matches:")
        for match in wave3_data['matches']:
            print(f"    {match['fibonacci_ratio']:.3f} (score: {match['score']:.2f})")
    print()

    print("Wave 4 Analysis:")
    wave4_data = fib_analysis['wave4_retracement']
    print(f"  Retracement Ratio: {wave4_data['ratio']:.3f}")
    print(f"  Quality Score: {wave4_data['quality']*100:.1f}%")
    print(f"  In Ideal Range (23.6-38.2%): {wave4_data['in_ideal_range']}")
    print()

    print(f"Overall Fibonacci Score: {fib_analysis['overall_fibonacci_score']:.1f}%")
    print(f"Fibonacci Confirmations: {fib_analysis['fibonacci_confirmations']}")

print()
print("=" * 80)
print("Analysis Complete!")
print("=" * 80)
