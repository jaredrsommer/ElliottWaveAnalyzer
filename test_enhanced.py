"""
Quick test of enhanced Elliott Wave analyzer functionality
"""

import pandas as pd
import numpy as np
from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer

print("Testing Enhanced Elliott Wave Analyzer")
print("=" * 70)

# Load data
print("\n1. Loading data...")
try:
    df = pd.read_csv('data/btc-usd_1d.csv')
    print(f"   ✓ Loaded {len(df)} candles")
except Exception as e:
    print(f"   ✗ Error loading data: {e}")
    exit(1)

# Create analyzer
print("\n2. Creating analyzer...")
try:
    analyzer = EnhancedWaveAnalyzer(df, verbose=False, min_probability=60.0)
    analyzer.set_combinatorial_limits(n_impulse=10, n_correction=10)
    print(f"   ✓ Analyzer created with 60% minimum probability")
except Exception as e:
    print(f"   ✗ Error creating analyzer: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Find starting point
print("\n3. Finding analysis starting point...")
try:
    idx_start = np.argmin(np.array(list(df['Low'])))
    print(f"   ✓ Starting from index {idx_start}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test impulse detection
print("\n4. Testing impulse wave detection...")
try:
    candidates = analyzer.find_best_impulse_waves(idx_start, max_results=3)
    if candidates:
        print(f"   ✓ Found {len(candidates)} impulse patterns")
        best = candidates[0]
        print(f"   ✓ Best pattern probability: {best.probability:.1f}%")
    else:
        print(f"   ⚠ No impulse patterns found (may need to adjust parameters)")
except Exception as e:
    print(f"   ✗ Error in impulse detection: {e}")
    import traceback
    traceback.print_exc()

# Test target calculation
print("\n5. Testing price target calculation...")
try:
    current_price = analyzer.get_current_price()
    print(f"   ✓ Current price: ${current_price:.2f}")

    analysis = analyzer.find_wave_with_targets(idx_start, wave_type='impulse', current_price=current_price)
    if analysis['found']:
        print(f"   ✓ Found wave pattern with targets")
        if 'targets' in analysis:
            num_targets = len(analysis['targets']['targets'])
            print(f"   ✓ Calculated {num_targets} price targets")
        else:
            print(f"   ⚠ Pattern found but no targets available")
    else:
        print(f"   ⚠ No pattern found for target calculation")
except Exception as e:
    print(f"   ✗ Error in target calculation: {e}")
    import traceback
    traceback.print_exc()

# Test variation analysis
print("\n6. Testing segment variation analysis...")
try:
    variation = analyzer.analyze_segment_variations(idx_start, wave_type='impulse', min_probability=60.0)
    if variation['found']:
        print(f"   ✓ Found {variation['total_candidates']} candidate patterns")
        print(f"   ✓ Best probability: {variation['best_candidate'].probability:.1f}%")
    else:
        print(f"   ⚠ No variations found")
except Exception as e:
    print(f"   ✗ Error in variation analysis: {e}")
    import traceback
    traceback.print_exc()

# Test report generation
print("\n7. Testing report generation...")
try:
    report = analyzer.create_analysis_report(idx_start, wave_type='impulse')
    if report:
        print(f"   ✓ Generated analysis report ({len(report)} characters)")
    else:
        print(f"   ⚠ Empty report generated")
except Exception as e:
    print(f"   ✗ Error in report generation: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Testing Complete!")
print("=" * 70)
