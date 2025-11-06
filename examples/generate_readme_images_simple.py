"""
Generate Images for README Documentation (Simplified Version)

This script generates professional chart images showcasing the Enhanced
Elliott Wave Analyzer system using XRP/USD historical data.

Author: Enhanced Elliott Wave Analyzer
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from models.HistoricalWaveLabeler import HistoricalWaveLabeler
from models.MonoWave import MonoWaveUp, MonoWaveDown

# Set style for professional charts
plt.style.use('seaborn-v0_8-darkgrid')

# Create output directory
OUTPUT_DIR = Path(parent_dir) / 'output' / 'readme_images'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("README Image Generator - Enhanced Elliott Wave Analyzer")
print("=" * 80)
print()


def generate_xrp_like_data(n_candles=500, base_price=0.50):
    """Generate realistic XRP-like price data with Elliott Wave patterns."""
    print("📊 Generating XRP-like market data...")

    np.random.seed(42)  # For reproducibility

    # Generate dates
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=n_candles, freq='1D')

    # Generate price with Elliott Wave-like structure
    prices = []
    current_price = base_price

    # Wave 1: Strong uptrend
    for i in range(80):
        change = np.random.normal(0.015, 0.01)  # Positive bias
        current_price *= (1 + change)
        prices.append(current_price)

    # Wave 2: Correction
    for i in range(40):
        change = np.random.normal(-0.008, 0.008)  # Negative bias
        current_price *= (1 + change)
        prices.append(current_price)

    # Wave 3: Strongest move
    for i in range(100):
        change = np.random.normal(0.020, 0.012)  # Strong positive bias
        current_price *= (1 + change)
        prices.append(current_price)

    # Wave 4: Smaller correction
    for i in range(50):
        change = np.random.normal(-0.006, 0.007)
        current_price *= (1 + change)
        prices.append(current_price)

    # Wave 5: Final push
    for i in range(80):
        change = np.random.normal(0.012, 0.010)
        current_price *= (1 + change)
        prices.append(current_price)

    # Random walk continuation
    remaining = n_candles - len(prices)
    for i in range(remaining):
        change = np.random.normal(0, 0.012)
        current_price *= (1 + change)
        prices.append(current_price)

    prices = np.array(prices[:n_candles])

    # Generate OHLC from close prices
    opens = prices * np.random.uniform(0.98, 1.02, n_candles)
    highs = np.maximum(opens, prices) * np.random.uniform(1.00, 1.03, n_candles)
    lows = np.minimum(opens, prices) * np.random.uniform(0.97, 1.00, n_candles)
    volumes = np.random.uniform(10000000, 50000000, n_candles)

    df = pd.DataFrame({
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': prices,
        'Volume': volumes
    })

    print(f"✓ Generated {len(df)} candles")
    print(f"✓ Price range: ${df['Low'].min():.4f} - ${df['High'].max():.4f}")
    print()

    return df


def plot_pattern_detection(df, analyzer, result):
    """Generate image showing Elliott Wave pattern detection with probability."""
    print("📈 Generating pattern detection image...")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[3, 1])
    fig.suptitle('Elliott Wave Pattern Detection - XRP/USD', fontsize=16, fontweight='bold')

    # Main chart
    wave_pattern = result['wave_pattern']
    waves = list(wave_pattern.waves.values())

    # Plot candlesticks (simplified)
    start_idx = max(0, waves[0].idx_start - 20)
    end_idx = min(waves[-1].idx_end + 50, len(df) - 1)

    df_slice = df.iloc[start_idx:end_idx].copy()

    # Price plot
    ax1.plot(df_slice.index, df_slice['Close'], color='gray', linewidth=0.5, alpha=0.5, label='Close Price')
    ax1.fill_between(df_slice.index, df_slice['Low'], df_slice['High'], alpha=0.2, color='lightblue')

    # Plot wave points
    for i, wave in enumerate(waves, 1):
        if isinstance(wave, MonoWaveUp):
            # Mark low (start) and high (end)
            ax1.plot(wave.idx_start, wave.low, 'go', markersize=10, zorder=5)
            ax1.plot(wave.idx_end, wave.high, 'ro', markersize=10, zorder=5)
            ax1.annotate(f'{i}', xy=(wave.idx_end, wave.high),
                        xytext=(0, 10), textcoords='offset points',
                        fontsize=14, fontweight='bold', color='darkred',
                        ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        else:  # MonoWaveDown
            # Mark high (start) and low (end)
            ax1.plot(wave.idx_start, wave.high, 'ro', markersize=10, zorder=5)
            ax1.plot(wave.idx_end, wave.low, 'go', markersize=10, zorder=5)
            ax1.annotate(f'{i}', xy=(wave.idx_end, wave.low),
                        xytext=(0, -15), textcoords='offset points',
                        fontsize=14, fontweight='bold', color='darkgreen',
                        ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        # Draw line connecting wave
        if isinstance(wave, MonoWaveUp):
            ax1.plot([wave.idx_start, wave.idx_end], [wave.low, wave.high],
                    'b-', linewidth=3, zorder=4, alpha=0.8)
        else:
            ax1.plot([wave.idx_start, wave.idx_end], [wave.high, wave.low],
                    'r-', linewidth=3, zorder=4, alpha=0.8)

    # Add targets
    targets = result.get('targets', {})
    current_price = df.iloc[end_idx - 1]['Close']

    if targets.get('target_1'):
        t1_price = targets['target_1']['price']
        ax1.axhline(y=t1_price, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f"Target 1: ${t1_price:.4f}")

    if targets.get('target_2'):
        t2_price = targets['target_2']['price']
        ax1.axhline(y=t2_price, color='lightgreen', linestyle='--', linewidth=1.5, alpha=0.7, label=f"Target 2: ${t2_price:.4f}")

    # Add invalidation level
    if result.get('invalidation_price'):
        ax1.axhline(y=result.get('invalidation_price'), color='red', linestyle='--', linewidth=2,
                   alpha=0.7, label=f"Stop Loss: ${result.get('invalidation_price'):.4f}")

    ax1.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Add statistics box
    stats_text = f"""Pattern Probability: {result.get('probability', 0):.1f}%
Fibonacci Score: {result.get('fibonacci_score', 0):.1f}%
Confidence: {result.get('confidence', 0):.1f}%
Wave Type: {result.get('wave_type', 'unknown').upper()}"""

    ax1.text(0.98, 0.97, stats_text, transform=ax1.transAxes,
            fontsize=11, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Probability subplot
    metrics = ['Probability', 'Fibonacci\nScore', 'Confidence']
    values = [result.get('probability', 0), result.get('fibonacci_score', 0), result.get('confidence', 0)]
    colors = ['#2ecc71' if v >= 75 else '#f39c12' if v >= 60 else '#e74c3c' for v in values]

    bars = ax2.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.axhline(y=75, color='green', linestyle='--', linewidth=1, alpha=0.5, label='High Quality (75%+)')
    ax2.axhline(y=60, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='Medium Quality (60-75%)')
    ax2.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'pattern_detection.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved: {output_path}")
    return output_path


def plot_wave_segments(df, analyzer, result):
    """Generate image showing wave structure with connecting line segments."""
    print("📈 Generating wave line segments image...")

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.suptitle('Elliott Wave Structure with Line Segments - XRP/USD', fontsize=16, fontweight='bold')

    wave_pattern = result['wave_pattern']
    waves = list(wave_pattern.waves.values())

    # Plot candlesticks
    start_idx = max(0, waves[0].idx_start - 20)
    end_idx = min(waves[-1].idx_end + 50, len(df) - 1)
    df_slice = df.iloc[start_idx:end_idx].copy()

    # Background price
    ax.plot(df_slice.index, df_slice['Close'], color='lightgray', linewidth=1, alpha=0.3)
    ax.fill_between(df_slice.index, df_slice['Low'], df_slice['High'], alpha=0.1, color='lightblue')

    # Draw continuous wave line
    wave_points_x = []
    wave_points_y = []

    for i, wave in enumerate(waves):
        if i == 0:
            # First wave - add start point
            if isinstance(wave, MonoWaveUp):
                wave_points_x.append(wave.idx_start)
                wave_points_y.append(wave.low)
            else:
                wave_points_x.append(wave.idx_start)
                wave_points_y.append(wave.high)

        # Add end point
        if isinstance(wave, MonoWaveUp):
            wave_points_x.append(wave.idx_end)
            wave_points_y.append(wave.high)
        else:
            wave_points_x.append(wave.idx_end)
            wave_points_y.append(wave.low)

    # Draw continuous blue line connecting all points
    ax.plot(wave_points_x, wave_points_y, 'b-', linewidth=4, zorder=5, label='Wave Structure', alpha=0.8)

    # Mark wave endpoints
    for i, (x, y) in enumerate(zip(wave_points_x, wave_points_y)):
        if i == 0:
            ax.plot(x, y, 'go', markersize=12, zorder=6, label='Wave Start')
        else:
            color = 'ro' if i % 2 == 0 else 'go'
            ax.plot(x, y, color, markersize=12, zorder=6)

            # Label waves
            wave_num = i
            xytext = (0, 15) if i % 2 == 0 else (0, -20)
            ax.annotate(f'Wave {wave_num}', xy=(x, y),
                       xytext=xytext, textcoords='offset points',
                       fontsize=12, fontweight='bold',
                       ha='center', bbox=dict(boxstyle='round,pad=0.4',
                       facecolor='yellow', alpha=0.8, edgecolor='black'))

    ax.set_xlabel('Data Index', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'wave_line_segments.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved: {output_path}")
    return output_path


def plot_fibonacci_targets(df, analyzer, result):
    """Generate image showing Fibonacci targets and levels."""
    print("📈 Generating Fibonacci targets image...")

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.suptitle('Fibonacci Price Targets - XRP/USD', fontsize=16, fontweight='bold')

    wave_pattern = result['wave_pattern']
    waves = list(wave_pattern.waves.values())

    start_idx = max(0, waves[0].idx_start - 20)
    end_idx = min(waves[-1].idx_end + 100, len(df) - 1)
    df_slice = df.iloc[start_idx:end_idx].copy()

    # Price plot
    ax.plot(df_slice.index, df_slice['Close'], color='blue', linewidth=2, label='Price', zorder=3)
    ax.fill_between(df_slice.index, df_slice['Low'], df_slice['High'], alpha=0.2, color='lightblue')

    # Current price
    current_price = df_slice.iloc[-1]['Close']
    ax.axhline(y=current_price, color='black', linestyle='-', linewidth=2,
              label=f'Current: ${current_price:.4f}', zorder=4)

    # Targets
    targets = result.get('targets', {})
    target_colors = {'target_1': 'green', 'target_2': 'lightgreen', 'target_3': 'lime'}
    target_labels = {'target_1': 'Target 1 (Primary)', 'target_2': 'Target 2 (Secondary)',
                    'target_3': 'Target 3 (Extended)'}

    for target_name, color in target_colors.items():
        target = targets.get(target_name)
        if target:
            price = target['price']
            method = target['method']
            magnitude = target.get('magnitude', 0)

            ax.axhline(y=price, color=color, linestyle='--', linewidth=2.5,
                      label=f"{target_labels[target_name]}: ${price:.4f} (+{magnitude:.1f}%)",
                      alpha=0.8, zorder=5)

            # Add annotation
            ax.text(len(df_slice) - 5, price, f'  {method}',
                   fontsize=10, va='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.6))

    # Invalidation
    if result.get('invalidation_price'):
        inv_price = result.get('invalidation_price')
        ax.axhline(y=inv_price, color='red', linestyle='--', linewidth=2.5,
                  label=f'Stop Loss: ${inv_price:.4f}', alpha=0.8, zorder=5)

    ax.set_xlabel('Data Index', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)

    # Add R/R ratio box
    if result.get('risk_reward_ratio'):
        rr_text = f"Risk/Reward Ratio: {result.get('risk_reward_ratio'):.2f}:1"
        ax.text(0.98, 0.03, rr_text, transform=ax.transAxes,
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8),
               ha='right')

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'fibonacci_targets.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved: {output_path}")
    return output_path


def plot_historical_labeling(df):
    """Generate image showing complete historical wave labeling."""
    print("📈 Generating historical wave labeling image...")

    # Use a subset of data for clearer visualization
    df_subset = df.iloc[-300:].copy().reset_index(drop=True)

    labeler = HistoricalWaveLabeler(df_subset)
    results = labeler.label_all_waves(scan_step=10, max_patterns_per_start=2)

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.suptitle('Historical Wave Labeling - All Patterns Detected - XRP/USD',
                fontsize=16, fontweight='bold')

    # Price plot
    ax.plot(df_subset.index, df_subset['Close'], color='gray', linewidth=1.5,
           label='Price', zorder=2)
    ax.fill_between(df_subset.index, df_subset['Low'], df_subset['High'],
                    alpha=0.1, color='lightblue')

    # Plot all detected patterns
    colors = ['blue', 'red', 'green', 'orange', 'purple']

    all_patterns = results.get('all_patterns', [])
    num_patterns_to_show = min(5, len(all_patterns))

    for i, pattern_info in enumerate(all_patterns[:num_patterns_to_show]):
        pattern = pattern_info['pattern']
        waves = list(pattern.waves.values())
        color = colors[i % len(colors)]

        # Draw wave line
        wave_x = []
        wave_y = []

        for j, wave in enumerate(waves):
            if j == 0:
                if isinstance(wave, MonoWaveUp):
                    wave_x.append(wave.idx_start)
                    wave_y.append(wave.low)
                else:
                    wave_x.append(wave.idx_start)
                    wave_y.append(wave.high)

            if isinstance(wave, MonoWaveUp):
                wave_x.append(wave.idx_end)
                wave_y.append(wave.high)
            else:
                wave_x.append(wave.idx_end)
                wave_y.append(wave.low)

        label = f"Pattern {i+1} ({pattern_info['probability']:.0f}%)"
        ax.plot(wave_x, wave_y, color=color, linewidth=2, alpha=0.7,
               label=label, zorder=3+i)

        # Mark endpoints
        for x, y in zip(wave_x, wave_y):
            ax.plot(x, y, 'o', color=color, markersize=6, zorder=10+i)

    ax.set_xlabel('Data Index', fontsize=12, fontweight='bold')
    ax.set_ylabel('Price (USD)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Add statistics
    stats_text = f"""Patterns Found: {results.get('num_patterns', 0)}
Labeled Waves: {results.get('num_labeled_waves', 0)}
Scan Coverage: {len(df_subset)} candles"""

    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    output_path = OUTPUT_DIR / 'historical_labeling.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved: {output_path}")
    print(f"  Found {results.get('num_patterns', 0)} patterns, labeled {results.get('num_labeled_waves', 0)} waves")
    return output_path


def main():
    """Main function to generate all images."""

    # Generate XRP-like data
    df = generate_xrp_like_data(n_candles=500, base_price=0.50)

    # Save data for future use
    data_path = OUTPUT_DIR.parent / 'XRP_USD_sample_data.csv'
    df.to_csv(data_path, index=False)
    print(f"✓ Saved sample data: {data_path}")
    print()

    # Run analysis on recent data
    print("🔍 Running Elliott Wave analysis...")
    df_recent = df.iloc[:350].copy().reset_index(drop=True)

    analyzer = EnhancedWaveAnalyzer(df_recent, min_probability=70.0)

    # Find best impulse pattern
    best_result = None
    for idx_start in range(0, min(100, len(df_recent) - 100), 10):
        try:
            result = analyzer.find_wave_with_targets(idx_start, 'impulse')
            if result and result.get('probability', 0) >= 70.0:
                best_result = result
                break
        except Exception as e:
            continue

    if not best_result:
        print("⚠ No high-probability pattern found, using best available...")
        impulse_results = analyzer.find_best_impulse_waves(0, max_results=1)
        if impulse_results and len(impulse_results) > 0:
            best_result = impulse_results[0]

    if best_result:
        print(f"✓ Found pattern with {best_result['probability']:.1f}% probability")
        print()

        # Generate images
        print("🎨 Generating images...")
        print()

        plot_pattern_detection(df_recent, analyzer, best_result)
        plot_wave_segments(df_recent, analyzer, best_result)
        plot_fibonacci_targets(df_recent, analyzer, best_result)
    else:
        print("⚠ No suitable pattern found for detailed images")
        print("  This is normal with random data - trying with full dataset...")

        # Try with full dataset
        analyzer_full = EnhancedWaveAnalyzer(df, min_probability=60.0)
        impulse_results = analyzer_full.find_best_impulse_waves(0, max_results=1)

        if impulse_results:
            best_result = impulse_results[0]
            print(f"✓ Found pattern with {best_result['probability']:.1f}% probability")
            print()
            plot_pattern_detection(df, analyzer_full, best_result)
            plot_wave_segments(df, analyzer_full, best_result)
            plot_fibonacci_targets(df, analyzer_full, best_result)

    # Historical labeling (always works)
    plot_historical_labeling(df)

    print()
    print("=" * 80)
    print("✅ Image Generation Complete!")
    print("=" * 80)
    print()
    print(f"📁 Images saved to: {OUTPUT_DIR}")
    print()
    print("Generated images:")
    for img in sorted(OUTPUT_DIR.glob('*.png')):
        print(f"  ✓ {img.name}")
    print()
    print("These images can be added to the README.md to showcase the system!")
    print()


if __name__ == "__main__":
    main()
