"""
Test Elliott Wave Analyzer with Simulated XRP/USDT data

This script demonstrates:
- Using realistic crypto data for Elliott Wave Analysis
- Running Enhanced Elliott Wave Analysis
- Creating detailed visualizations with probability scores
- Calculating Fibonacci-based price targets

NOTE: Since live data fetching is not available, we'll use BTC data as a proxy
      or generate synthetic XRP-like price movements.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer
from models.helpers import save_chart_as_image


def generate_xrp_like_data(base_price=0.5, num_candles=500):
    """
    Generate synthetic XRP/USDT-like price data with realistic patterns.

    Args:
        base_price: Base price for XRP (default: $0.5)
        num_candles: Number of 4-hour candles to generate

    Returns:
        DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    print(f"Generating synthetic XRP/USDT data...")
    print(f"Base Price: ${base_price}, Candles: {num_candles}")

    np.random.seed(42)  # For reproducibility

    # Start date
    start_date = datetime.now() - timedelta(hours=4 * num_candles)

    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []

    price = base_price

    for i in range(num_candles):
        # Date
        current_date = start_date + timedelta(hours=4 * i)
        dates.append(current_date)

        # Generate price movement with trend component
        # Create Elliott Wave-like patterns
        trend_component = 0.0002 * np.sin(i / 20) + 0.0001 * np.sin(i / 50)
        random_component = np.random.normal(0, 0.015)

        # Price movement
        price_change = price * (trend_component + random_component)
        open_price = price
        close_price = price + price_change

        # Generate high and low
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.01)))

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)

        # Generate volume
        volume = np.random.uniform(1000000, 10000000)
        volumes.append(volume)

        # Update price for next candle
        price = close_price

    df = pd.DataFrame({
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    })

    print(f"✓ Generated {len(df)} candles")
    print(f"  Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
    print(f"  Price range: ${df['Low'].min():.4f} - ${df['High'].max():.4f}")
    print()

    return df


def load_btc_as_sample():
    """Load existing BTC data for demonstration."""
    print("Loading BTC data as sample...")
    df = pd.read_csv('data/btc-usd_1d.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"✓ Loaded {len(df)} candles")
    print(f"  Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
    print(f"  Price range: ${df['Low'].min():.2f} - ${df['High'].max():.2f}")
    print()
    return df


def create_detailed_plot(df, analyzer, best_candidate, targets_info=None, symbol="XRP/USDT"):
    """
    Create a comprehensive Elliott Wave analysis plot with annotations.

    Args:
        df: Price DataFrame
        analyzer: EnhancedWaveAnalyzer instance
        best_candidate: Best wave candidate found
        targets_info: Optional price targets information
        symbol: Trading pair symbol for title
    """
    print("Creating detailed plot...")

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'Elliott Wave Analysis - {symbol}', 'Probability Breakdown'),
        vertical_spacing=0.1
    )

    # Add OHLC candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol
        ),
        row=1, col=1
    )

    # Add Elliott Wave pattern lines
    pattern = best_candidate.pattern
    fig.add_trace(
        go.Scatter(
            x=pattern.dates,
            y=pattern.values,
            text=pattern.labels,
            mode='lines+markers+text',
            name='Elliott Waves',
            textposition='top center',
            textfont=dict(size=14, color='white', family='Arial Black'),
            line=dict(color='rgb(255, 215, 0)', width=4),
            marker=dict(size=12, color='rgb(255, 215, 0)', symbol='circle')
        ),
        row=1, col=1
    )

    # Add price targets if available
    if targets_info and 'targets' in targets_info:
        targets = targets_info['targets']
        current_price = analyzer.get_current_price()

        for target in targets['targets']:
            # Determine color based on target level
            if target['level'] == 'conservative':
                color = 'cyan'
            elif target['level'] == 'moderate':
                color = 'yellow'
            else:
                color = 'orange'

            # Add horizontal line for each target
            fig.add_hline(
                y=target['price'],
                line_dash="dash",
                line_color=color,
                annotation_text=f"{target['level'].upper()}: ${target['price']:.4f}",
                annotation_position="right",
                row=1, col=1
            )

    # Add probability breakdown bar chart
    prob_scores = best_candidate.probability_analysis['scores']
    categories = ['Rules', 'Fibonacci', 'Guidelines', 'Structure']
    scores = [
        prob_scores['rules_compliance']['score'],
        prob_scores['fibonacci_ratios']['score'],
        prob_scores['guidelines']['score'],
        prob_scores['structure_quality']['score']
    ]

    colors = ['green' if s >= 70 else 'yellow' if s >= 50 else 'red' for s in scores]

    fig.add_trace(
        go.Bar(
            x=categories,
            y=scores,
            text=[f"{s:.1f}%" for s in scores],
            textposition='outside',
            marker_color=colors,
            name='Probability Scores'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title={
            'text': f"<b>{symbol} Elliott Wave Analysis</b><br>" +
                   f"<span style='font-size:14px'>Overall Probability: {best_candidate.probability:.1f}% " +
                   f"({best_candidate.probability_analysis['category']})</span><br>" +
                   f"<span style='font-size:12px'>Wave Options: {best_candidate.wave_options}</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=900,
        showlegend=True,
        template='plotly_dark',
        hovermode='x unified'
    )

    # Update axes
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
    fig.update_yaxes(title_text="Score (%)", range=[0, 110], row=2, col=1)

    # Remove rangeslider
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

    # Save the plot
    if not os.path.exists("images"):
        os.mkdir("images")

    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./images/{symbol.replace('/', '_')}_Elliott_Wave_{timestamp}.png"

    try:
        fig.write_image(filename, width=1920, height=1080)
        print(f"✓ Plot saved to: {filename}")
    except Exception as e:
        print(f"⚠ Could not save as PNG: {e}")
        html_filename = f"./images/{symbol.replace('/', '_')}_Elliott_Wave_{timestamp}.html"
        fig.write_html(html_filename)
        print(f"✓ Plot saved as HTML to: {html_filename}")

    return fig


def print_detailed_analysis(best_candidate, targets_info, current_price):
    """Print comprehensive analysis report."""
    print("\n" + "=" * 80)
    print("DETAILED ELLIOTT WAVE ANALYSIS REPORT")
    print("=" * 80)

    # Overall Assessment
    print(f"\n📊 OVERALL ASSESSMENT:")
    print(f"   Probability Score: {best_candidate.probability:.1f}%")
    print(f"   Category: {best_candidate.probability_analysis['category']}")
    print(f"   Wave Type: {best_candidate.wave_type.upper()}")
    print(f"   Wave Configuration: {best_candidate.wave_options}")

    # Probability Breakdown
    print(f"\n📈 PROBABILITY BREAKDOWN:")
    scores = best_candidate.probability_analysis['scores']

    print(f"   Rules Compliance: {scores['rules_compliance']['score']:.1f}%")
    if 'violations' in scores['rules_compliance'] and scores['rules_compliance']['violations']:
        print(f"      Violations:")
        for violation in scores['rules_compliance']['violations']:
            print(f"         ✗ {violation}")
    else:
        print(f"      ✓ All Elliott Wave rules satisfied")

    print(f"\n   Fibonacci Ratios: {scores['fibonacci_ratios']['score']:.1f}%")
    fib_details = scores['fibonacci_ratios']['details']

    if 'wave2_retracement' in fib_details:
        w2 = fib_details['wave2_retracement']
        print(f"      Wave 2 Retracement: {w2['ratio']:.3f} (Quality: {w2['quality']*100:.0f}%)")
        if w2.get('matches'):
            matches_str = ', '.join([f"{m['fibonacci_ratio']:.3f}" for m in w2['matches'][:3]])
            print(f"         Matches: {matches_str}")

    if 'wave3_extension' in fib_details:
        w3 = fib_details['wave3_extension']
        print(f"      Wave 3 Extension: {w3['ratio']:.3f} (Quality: {w3['quality']*100:.0f}%)")
        if w3.get('matches'):
            matches_str = ', '.join([f"{m['fibonacci_ratio']:.3f}" for m in w3['matches'][:3]])
            print(f"         Matches: {matches_str}")

    if 'wave4_retracement' in fib_details:
        w4 = fib_details['wave4_retracement']
        print(f"      Wave 4 Retracement: {w4['ratio']:.3f} (Quality: {w4['quality']*100:.0f}%)")

    print(f"\n   Guidelines: {scores['guidelines']['score']:.1f}%")
    if 'details' in scores['guidelines']:
        for detail in scores['guidelines']['details']:
            print(f"      • {detail}")

    print(f"\n   Structure Quality: {scores['structure_quality']['score']:.1f}%")

    # Price Targets
    if targets_info and 'targets' in targets_info:
        print(f"\n🎯 PRICE TARGETS:")
        targets = targets_info['targets']
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Direction: {targets['direction']}")
        print(f"   Base Price: ${targets['base_price']:.4f}")
        print()

        for target in targets['targets']:
            prob_str = f"{target.get('probability', 0)*100:.0f}%"
            distance = target['price'] - current_price
            distance_pct = (distance / current_price) * 100

            print(f"   {target['level'].upper()}:")
            print(f"      Target Price: ${target['price']:.4f}")
            print(f"      Distance: ${distance:.4f} ({distance_pct:+.2f}%)")
            print(f"      Ratio: {target['ratio']}")
            print(f"      Probability: {prob_str}")
            if 'description' in target:
                print(f"      Description: {target['description']}")
            print()

    # Wave Details
    print(f"\n📏 WAVE MEASUREMENTS:")
    pattern = best_candidate.pattern
    waves = list(pattern.waves.values())

    for i, wave in enumerate(waves):
        wave_label = wave.label
        wave_length = wave.length
        duration = wave.duration

        # Get start/end points based on wave direction
        points = wave.points
        start_price = points[0]
        end_price = points[1]

        print(f"   Wave {wave_label}:")
        print(f"      Start: {wave.date_start} @ ${start_price:.4f}")
        print(f"      End: {wave.date_end} @ ${end_price:.4f}")
        print(f"      Length: ${wave_length:.4f}")
        print(f"      Duration: {duration} candles")
        print()

    print("=" * 80)


def main():
    """Main execution function."""
    print("\n" + "=" * 80)
    print("ELLIOTT WAVE ANALYZER - CRYPTO ANALYSIS DEMO")
    print("=" * 80 + "\n")

    # Use existing BTC data as sample (more realistic than synthetic)
    print("Using BTC data for demonstration...")
    df = load_btc_as_sample()
    symbol = "BTC/USD (Sample)"

    # Save data
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # Initialize analyzer
    print("Initializing Enhanced Wave Analyzer...")
    analyzer = EnhancedWaveAnalyzer(
        df,
        verbose=False,
        min_probability=50.0  # Accept patterns with 50%+ probability
    )

    # Set combinatorial limits
    analyzer.set_combinatorial_limits(n_impulse=15, n_correction=12)
    print()

    # Find the lowest point for impulse wave analysis
    idx_start = np.argmin(np.array(list(df['Low'])))
    print(f"Starting analysis from index {idx_start} (lowest point)")
    print(f"  Date: {df.iloc[idx_start]['Date']}")
    print(f"  Price: ${df.iloc[idx_start]['Low']:.2f}")
    print()

    # Find best impulse patterns
    print("Searching for impulse wave patterns...")
    print("(This may take 30-60 seconds depending on data size)")
    impulse_candidates = analyzer.find_best_impulse_waves(idx_start, max_results=5)

    if not impulse_candidates:
        print("\n⚠ No valid impulse patterns found. Trying corrective patterns...")

        # Try corrective waves from highest point
        idx_high = np.argmax(np.array(list(df['High'])))
        print(f"Starting corrective analysis from index {idx_high} (highest point)")
        print(f"  Date: {df.iloc[idx_high]['Date']}")
        print(f"  Price: ${df.iloc[idx_high]['High']:.2f}")
        print()

        correction_candidates = analyzer.find_best_corrective_waves(idx_high, max_results=5)

        if not correction_candidates:
            print("\n❌ No valid wave patterns found.")
            print("Try adjusting:")
            print("  - Different starting point")
            print("  - Lower min_probability threshold")
            print("  - More data (increase limit)")
            return

        candidates = correction_candidates
        wave_type = 'correction'
        idx_for_targets = idx_high
    else:
        candidates = impulse_candidates
        wave_type = 'impulse'
        idx_for_targets = idx_start

    # Display found patterns
    print(f"\n✓ Found {len(candidates)} valid {wave_type} patterns:\n")

    for i, candidate in enumerate(candidates, 1):
        print(f"Pattern #{i}:")
        print(f"  Probability: {candidate.probability:.1f}% ({candidate.probability_analysis['category']})")
        print(f"  Wave Options: {candidate.wave_options}")
        print()

    # Analyze best pattern
    best_candidate = candidates[0]
    current_price = analyzer.get_current_price()

    # Get price targets
    print("Calculating price targets...")
    targets_info = analyzer.find_wave_with_targets(
        idx_for_targets,
        wave_type=wave_type,
        current_price=current_price
    )

    # Print detailed analysis
    print_detailed_analysis(best_candidate, targets_info, current_price)

    # Create detailed plot
    fig = create_detailed_plot(df, analyzer, best_candidate, targets_info, symbol)

    print("\n✓ Analysis complete!")
    print("\nCheck the 'images' folder for the detailed chart.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
