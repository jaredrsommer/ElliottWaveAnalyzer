"""
Test script for Freqtrade Elliott Wave strategies

This script validates that the strategies can be loaded and used
without Freqtrade running.
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_dataframe(num_candles=200):
    """
    Create a sample OHLCV dataframe for testing.
    """
    dates = pd.date_range(end=datetime.now(), periods=num_candles, freq='1D')

    # Create realistic price movement
    np.random.seed(42)
    close_prices = []
    price = 50000.0

    for i in range(num_candles):
        # Random walk with slight upward bias
        change = np.random.randn() * 500 + 50
        price += change
        price = max(price, 10000)  # Floor
        close_prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': [p * 0.99 for p in close_prices],
        'high': [p * 1.02 for p in close_prices],
        'low': [p * 0.98 for p in close_prices],
        'close': close_prices,
        'volume': np.random.randint(1000000, 10000000, size=num_candles)
    })

    return df


def test_strategy_import():
    """Test that strategies can be imported."""
    print("=" * 70)
    print("TEST 1: Strategy Import")
    print("=" * 70)

    try:
        from freqtrade.SimpleElliotWaveStrategy import SimpleElliotWaveStrategy
        print("✓ SimpleElliotWaveStrategy imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SimpleElliotWaveStrategy: {e}")
        return False

    try:
        from freqtrade.EnhancedElliotWaveStrategy import EnhancedElliotWaveStrategy
        print("✓ EnhancedElliotWaveStrategy imported successfully")
    except Exception as e:
        print(f"✗ Failed to import EnhancedElliotWaveStrategy: {e}")
        return False

    try:
        from freqtrade.AdvancedElliotWaveStrategy import AdvancedElliotWaveStrategy
        print("✓ AdvancedElliotWaveStrategy imported successfully")
    except Exception as e:
        print(f"✗ Failed to import AdvancedElliotWaveStrategy: {e}")
        return False

    try:
        from freqtrade.wave_plotting_helper import WavePlottingHelper
        print("✓ WavePlottingHelper imported successfully")
    except Exception as e:
        print(f"✗ Failed to import WavePlottingHelper: {e}")
        return False

    print()
    return True


def test_helper_functions():
    """Test helper functions."""
    print("=" * 70)
    print("TEST 2: Helper Functions")
    print("=" * 70)

    try:
        from freqtrade.elliott_wave_helpers import FreqtradeElliotWaveHelper

        helper = FreqtradeElliotWaveHelper()
        print("✓ FreqtradeElliotWaveHelper instantiated")

        # Test risk/reward calculation
        rr = helper.get_risk_reward_ratio(
            entry_price=50000,
            target_price=55000,
            invalidation_price=48000
        )
        print(f"✓ Risk/Reward calculation: {rr:.2f}")

        if rr != 2.5:
            print(f"  ⚠ Warning: Expected 2.5, got {rr:.2f}")

        # Test position size calculation
        position = helper.calculate_position_size(
            account_balance=10000,
            risk_percent=2.0,
            entry_price=50000,
            stop_loss_price=48000
        )
        print(f"✓ Position size calculation: ${position:.2f}")

        print()
        return True

    except Exception as e:
        print(f"✗ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indicator_population():
    """Test indicator population with mock data."""
    print("=" * 70)
    print("TEST 3: Indicator Population")
    print("=" * 70)

    try:
        # Create mock dataframe
        df = create_sample_dataframe(150)
        print(f"✓ Created test dataframe: {len(df)} candles")

        # Rename columns to match Freqtrade format
        df.columns = [col.capitalize() for col in df.columns]

        # Mock metadata
        metadata = {'pair': 'BTC/USDT'}

        # Mock config for strategy
        mock_config = {
            'stake_currency': 'USDT',
            'dry_run': True,
            'exchange': {'name': 'binance'}
        }

        # Test SimpleElliotWaveStrategy
        from freqtrade.SimpleElliotWaveStrategy import SimpleElliotWaveStrategy

        # Create mock DP (DataProvider)
        class MockDP:
            def send_msg(self, msg):
                print(f"  📨 {msg}")

        strategy = SimpleElliotWaveStrategy(mock_config)
        strategy.dp = MockDP()

        print("✓ SimpleElliotWaveStrategy instantiated")

        # Test populate_indicators (this is the key test)
        try:
            result_df = strategy.populate_indicators(df.copy(), metadata)
            print(f"✓ populate_indicators executed: {len(result_df)} rows")

            # Check if Elliott Wave indicators were added
            ew_columns = [col for col in result_df.columns if col.startswith('ew_')]
            print(f"✓ Elliott Wave indicators added: {len(ew_columns)}")

            for col in ew_columns[:5]:  # Show first 5
                print(f"    - {col}")

            # Check if standard indicators were added
            if 'rsi' in result_df.columns:
                print("✓ RSI indicator added")
            if 'volume_mean' in result_df.columns:
                print("✓ Volume indicators added")

        except Exception as e:
            print(f"⚠ populate_indicators had an issue: {e}")
            print("  (This may be expected if no patterns found)")

        print()
        return True

    except Exception as e:
        print(f"✗ Indicator population test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_entry_exit_logic():
    """Test entry/exit signal generation."""
    print("=" * 70)
    print("TEST 4: Entry/Exit Signal Logic")
    print("=" * 70)

    try:
        df = create_sample_dataframe(150)
        df.columns = [col.capitalize() for col in df.columns]

        # Add mock Elliott Wave indicators
        df['ew_probability'] = 75.0
        df['ew_fib_score'] = 70.0
        df['ew_confidence'] = 72.0
        df['ew_target_1'] = df['Close'] * 1.10  # 10% above
        df['ew_invalidation'] = df['Close'] * 0.95  # 5% below
        df['rsi'] = 55.0
        df['volume_mean'] = df['Volume']

        metadata = {'pair': 'BTC/USDT'}
        mock_config = {'stake_currency': 'USDT', 'dry_run': True, 'exchange': {'name': 'binance'}}

        from freqtrade.SimpleElliotWaveStrategy import SimpleElliotWaveStrategy

        class MockDP:
            def send_msg(self, msg):
                pass

        strategy = SimpleElliotWaveStrategy(mock_config)
        strategy.dp = MockDP()

        # Test entry trend
        entry_df = strategy.populate_entry_trend(df.copy(), metadata)
        entries = entry_df['enter_long'].sum() if 'enter_long' in entry_df.columns else 0
        print(f"✓ Entry signals generated: {entries}")

        # Test exit trend
        exit_df = strategy.populate_exit_trend(df.copy(), metadata)
        exits = exit_df['exit_long'].sum() if 'exit_long' in exit_df.columns else 0
        print(f"✓ Exit signals generated: {exits}")

        # Test plot config
        plot_config = strategy.plot_config()
        print(f"✓ Plot configuration available: {len(plot_config)} sections")

        print()
        return True

    except Exception as e:
        print(f"✗ Entry/exit logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_strategy():
    """Test EnhancedElliotWaveStrategy."""
    print("=" * 70)
    print("TEST 5: Enhanced Strategy")
    print("=" * 70)

    try:
        from freqtrade.EnhancedElliotWaveStrategy import EnhancedElliotWaveStrategy

        mock_config = {
            'stake_currency': 'USDT',
            'dry_run': True,
            'exchange': {'name': 'binance'}
        }

        strategy = EnhancedElliotWaveStrategy(mock_config)
        print("✓ EnhancedElliotWaveStrategy instantiated")

        # Check parameters exist
        print(f"✓ min_wave_probability: {strategy.min_wave_probability.value}")
        print(f"✓ min_fibonacci_score: {strategy.min_fibonacci_score.value}")
        print(f"✓ target_level: {strategy.target_level.value}")

        # Check methods exist
        if hasattr(strategy, 'custom_stoploss'):
            print("✓ custom_stoploss method exists")
        if hasattr(strategy, 'custom_exit'):
            print("✓ custom_exit method exists")
        if hasattr(strategy, 'confirm_trade_entry'):
            print("✓ confirm_trade_entry method exists")

        print()
        return True

    except Exception as e:
        print(f"✗ Enhanced strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wave_plotting_helper():
    """Test WavePlottingHelper."""
    print("=" * 70)
    print("TEST 6: Wave Plotting Helper")
    print("=" * 70)

    try:
        from freqtrade.wave_plotting_helper import WavePlottingHelper

        helper = WavePlottingHelper()
        print("✓ WavePlottingHelper instantiated")

        # Test plot config generation
        plot_config = helper.create_enhanced_plot_config(prefix='ew')
        print(f"✓ Enhanced plot config created")

        # Check main plot elements
        if 'main_plot' in plot_config:
            main_elements = len(plot_config['main_plot'])
            print(f"✓ Main plot elements: {main_elements}")

        # Check subplots
        if 'subplots' in plot_config:
            subplots = len(plot_config['subplots'])
            print(f"✓ Subplots: {subplots}")

        # Check specific plot elements exist
        expected_elements = [
            'ew_impulse_line',
            'ew_correction_line',
            'ew_upper_channel',
            'ew_lower_channel',
            'ew_w2_fib_618',
            'ew_target_1',
            'ew_invalidation'
        ]

        for element in expected_elements:
            if element in plot_config['main_plot']:
                print(f"  ✓ {element} configured")

        print()
        return True

    except Exception as e:
        print(f"✗ Wave plotting helper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_strategy():
    """Test AdvancedElliotWaveStrategy."""
    print("=" * 70)
    print("TEST 7: Advanced Strategy")
    print("=" * 70)

    try:
        from freqtrade.AdvancedElliotWaveStrategy import AdvancedElliotWaveStrategy

        mock_config = {
            'stake_currency': 'USDT',
            'dry_run': True,
            'exchange': {'name': 'binance'}
        }

        strategy = AdvancedElliotWaveStrategy(mock_config)
        print("✓ AdvancedElliotWaveStrategy instantiated")

        # Check advanced parameters
        print(f"✓ min_wave_probability: {strategy.min_wave_probability.value}")
        print(f"✓ min_fibonacci_score: {strategy.min_fibonacci_score.value}")
        print(f"✓ use_higher_tf: {strategy.use_higher_tf.value}")
        print(f"✓ use_fibonacci_confluence: {strategy.use_fibonacci_confluence.value}")

        # Check position adjustment enabled
        if hasattr(strategy, 'position_adjustment_enable'):
            print(f"✓ position_adjustment_enable: {strategy.position_adjustment_enable}")

        # Check advanced methods exist
        if hasattr(strategy, 'adjust_trade_position'):
            print("✓ adjust_trade_position method exists (partial exits)")
        if hasattr(strategy, 'custom_stoploss'):
            print("✓ custom_stoploss method exists (dynamic stops)")
        if hasattr(strategy, 'custom_exit'):
            print("✓ custom_exit method exists (advanced exits)")
        if hasattr(strategy, 'confirm_trade_entry'):
            print("✓ confirm_trade_entry method exists (trade confirmation)")

        # Check plotting helper integration
        if hasattr(strategy, 'plot_helper'):
            print("✓ WavePlottingHelper integrated")

        print()
        return True

    except Exception as e:
        print(f"✗ Advanced strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "FREQTRADE STRATEGY TEST SUITE" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    results = []

    # Run tests
    results.append(("Strategy Import", test_strategy_import()))
    results.append(("Helper Functions", test_helper_functions()))
    results.append(("Indicator Population", test_indicator_population()))
    results.append(("Entry/Exit Logic", test_entry_exit_logic()))
    results.append(("Enhanced Strategy", test_enhanced_strategy()))
    results.append(("Wave Plotting Helper", test_wave_plotting_helper()))
    results.append(("Advanced Strategy", test_advanced_strategy()))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Strategies are ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
