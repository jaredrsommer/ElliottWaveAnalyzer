# Elliott Wave Analyzer - Freqtrade Integration

Complete guide to using the Enhanced Elliott Wave Analyzer as a Freqtrade strategy with custom indicators and plotting.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Strategy Overview](#strategy-overview)
5. [Configuration](#configuration)
6. [Backtesting](#backtesting)
7. [Live Trading](#live-trading)
8. [Plotting](#plotting)
9. [Optimization](#optimization)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This integration provides two Freqtrade strategies based on the Enhanced Elliott Wave Analyzer:

### **1. EnhancedElliotWaveStrategy** (Advanced)
Full-featured strategy with:
- Hyperopt-optimizable parameters
- Multiple Fibonacci targets
- Dynamic stop loss based on invalidation levels
- Volume and RSI confirmations
- Custom risk management
- Trailing stops

**Best for:** Experienced traders, optimization, multi-timeframe analysis

### **2. SimpleElliotWaveStrategy** (Beginner-Friendly)
Simplified strategy with:
- Fixed parameters (no optimization needed)
- Single target approach
- Clear entry/exit rules
- 2:1 minimum risk/reward
- Easy to understand logic

**Best for:** Beginners, learning Elliott Wave, conservative trading

---

## 🚀 Installation

### Prerequisites

1. **Freqtrade installed** (version 2023.x or later)
   ```bash
   # If not installed, follow: https://www.freqtrade.io/en/stable/installation/
   ```

2. **Python 3.9+**

### Step 1: Copy Files to Freqtrade

```bash
# Navigate to your Freqtrade directory
cd ~/freqtrade

# Create user_data/strategies directory if it doesn't exist
mkdir -p user_data/strategies

# Copy the Enhanced Elliott Wave Analyzer
cp -r /path/to/ElliottWaveAnalyzer/models user_data/strategies/
cp -r /path/to/ElliottWaveAnalyzer/freqtrade user_data/strategies/

# Verify files are copied
ls user_data/strategies/freqtrade/
# Should show: EnhancedElliotWaveStrategy.py, SimpleElliotWaveStrategy.py, elliott_wave_helpers.py
```

### Step 2: Install Dependencies

```bash
# Activate Freqtrade virtual environment
source .venv/bin/activate

# Install required packages
pip install numpy pandas numba matplotlib

# Verify installation
python -c "from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer; print('✓ Installation successful')"
```

---

## 🏁 Quick Start

### 1. Choose Your Strategy

**For Beginners:**
```bash
freqtrade list-strategies
# Look for: SimpleElliotWaveStrategy
```

**For Advanced Users:**
```bash
freqtrade list-strategies
# Look for: EnhancedElliotWaveStrategy
```

### 2. Test with Dry-Run

```bash
# Start dry-run (paper trading)
freqtrade trade \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json \
    --dry-run
```

### 3. Download Data for Backtesting

```bash
# Download historical data
freqtrade download-data \
    --exchange binance \
    --pairs BTC/USDT ETH/USDT \
    --timeframe 1d \
    --days 365
```

### 4. Run Quick Backtest

```bash
# Backtest the strategy
freqtrade backtesting \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json \
    --timeframe 1d \
    --timerange 20230101-20241101
```

---

## 📊 Strategy Overview

### EnhancedElliotWaveStrategy

#### Entry Conditions ✅
1. **Elliott Wave Pattern Detected**
   - Probability ≥ 70% (adjustable)
   - Fibonacci score ≥ 60% (adjustable)
   - Valid Fibonacci target available

2. **Technical Confirmations**
   - RSI between 40-70 (momentum but not overbought)
   - MACD bullish (above signal line)
   - Volume > 20-period average (optional)

3. **Risk Management**
   - Risk/Reward ratio ≥ 1.5:1
   - Clear invalidation level exists

#### Exit Conditions 🚪
1. **Profit Targets**
   - Target 1, 2, or 3 reached (configurable)
   - Within 2% of Fibonacci target

2. **Exhaustion Signals**
   - RSI > 75 (Wave 5 exhaustion)
   - MACD bearish crossover

3. **Stop Loss**
   - Elliott Wave invalidation level
   - Or fixed 5% hard stop

4. **Trailing Stop**
   - Activates at 2% profit
   - Trails by 3%

### SimpleElliotWaveStrategy

#### Entry Conditions ✅
1. **High-Probability Pattern**
   - Probability ≥ 75% (fixed)
   - Fibonacci score ≥ 65% (fixed)
   - Confidence ≥ 70%

2. **Simple Confirmations**
   - RSI 35-70
   - Volume above average

3. **Risk/Reward**
   - Minimum 2:1 ratio required

#### Exit Conditions 🚪
1. **Target 1 reached** (within 3%)
2. **RSI > 75** (exhaustion)
3. **Stop at invalidation level**

---

## ⚙️ Configuration

### Basic config.json

Create or modify `user_data/config.json`:

```json
{
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "dry_run": true,
    "cancel_open_orders_on_exit": false,

    "exchange": {
        "name": "binance",
        "key": "YOUR_API_KEY",
        "secret": "YOUR_API_SECRET",
        "ccxt_config": {},
        "ccxt_async_config": {},
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT"
        ],
        "pair_blacklist": []
    },

    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1,
        "price_last_balance": 0.0,
        "check_depth_of_market": {
            "enabled": false,
            "bids_to_ask_delta": 1
        }
    },

    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },

    "pairlists": [
        {
            "method": "StaticPairList"
        }
    ],

    "telegram": {
        "enabled": false,
        "token": "YOUR_TELEGRAM_TOKEN",
        "chat_id": "YOUR_TELEGRAM_CHAT_ID"
    },

    "api_server": {
        "enabled": true,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "verbosity": "info",
        "jwt_secret_key": "YOUR_SECRET_KEY",
        "CORS_origins": [],
        "username": "freqtrade",
        "password": "YOUR_PASSWORD"
    },

    "bot_name": "elliott_wave_bot",
    "initial_state": "running",
    "force_entry_enable": false,
    "internals": {
        "process_throttle_secs": 5
    }
}
```

### Strategy-Specific Settings

#### For EnhancedElliotWaveStrategy

```python
# In the strategy file, adjust these parameters:

min_wave_probability = 70.0  # Minimum Elliott Wave probability
min_fibonacci_score = 60.0   # Minimum Fibonacci score
target_level = 2             # Which target to use (1, 2, or 3)
use_volume_confirmation = 1  # Enable volume check
```

#### For SimpleElliotWaveStrategy

```python
# In the strategy file:

MIN_PROBABILITY = 75.0  # High probability patterns only
MIN_FIB_SCORE = 65.0    # Good Fibonacci relationships
```

---

## 🔬 Backtesting

### Basic Backtest

```bash
freqtrade backtesting \
    --strategy SimpleElliotWaveStrategy \
    --timeframe 1d \
    --timerange 20230101-20241101 \
    --stake-amount unlimited
```

### Detailed Backtest with Breakdown

```bash
freqtrade backtesting \
    --strategy EnhancedElliotWaveStrategy \
    --timeframe 1d \
    --timerange 20230101-20241101 \
    --breakdown day month \
    --export trades \
    --export-filename user_data/backtest_results/elliott_wave_results.json
```

### Backtest Multiple Timeframes

```bash
# 1-day timeframe (recommended for Elliott Wave)
freqtrade backtesting --strategy SimpleElliotWaveStrategy --timeframe 1d

# 4-hour timeframe
freqtrade backtesting --strategy SimpleElliotWaveStrategy --timeframe 4h

# 1-hour timeframe
freqtrade backtesting --strategy SimpleElliotWaveStrategy --timeframe 1h
```

### Analyze Results

```bash
# Show backtest results
freqtrade backtesting-show

# Plot results
freqtrade plot-dataframe \
    --strategy SimpleElliotWaveStrategy \
    --timeframe 1d \
    --timerange 20230101-20231231
```

---

## 📈 Live Trading

### Start Live Trading

⚠️ **WARNING:** Always test thoroughly in dry-run mode first!

```bash
# Dry-run (paper trading)
freqtrade trade \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json \
    --dry-run

# Live trading (REAL MONEY)
freqtrade trade \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json
```

### Recommended Pairs

Elliott Wave works best on:
- **Major cryptocurrencies:** BTC/USDT, ETH/USDT
- **Large-cap altcoins:** BNB/USDT, ADA/USDT, SOL/USDT
- **Liquid pairs:** High volume pairs

Avoid:
- Low-volume pairs
- New/unestablished tokens
- Extremely volatile meme coins

### Recommended Timeframes

- **1d (daily):** Best for Elliott Wave clarity
- **4h:** Good for shorter-term patterns
- **1h:** More signals but potentially lower quality
- **< 1h:** Not recommended (noise)

---

## 🎨 Plotting

### Generate Plots

```bash
# Plot with Elliott Wave indicators
freqtrade plot-dataframe \
    --strategy EnhancedElliotWaveStrategy \
    --pairs BTC/USDT \
    --timeframe 1d \
    --timerange 20230101-20231231 \
    --indicators1 ew_target_1 ew_target_2 ew_invalidation \
    --indicators2 ew_probability ew_fib_score
```

### View in Browser

After plotting:
```bash
# Open the HTML file
# Location: user_data/plot/freqtrade-plot-BTC_USDT-1d.html

# Or use Python HTTP server
cd user_data/plot
python -m http.server 8888
# Visit: http://localhost:8888
```

### Plot Features

The strategies include custom plotting that shows:

**Main Chart:**
- Wave points (1, 2, 3, 4, 5 marked)
- Target lines (Target 1, 2, 3 in green)
- Invalidation level (red line)
- Entry/exit signals

**Subplots:**
- Elliott Wave Probability (0-100%)
- Fibonacci Score (0-100%)
- Confidence Score (0-100%)
- RSI indicator
- MACD indicator

---

## 🔧 Optimization (Hyperopt)

### Optimize EnhancedElliotWaveStrategy

```bash
freqtrade hyperopt \
    --strategy EnhancedElliotWaveStrategy \
    --hyperopt-loss SharpeHyperOptLoss \
    --timeframe 1d \
    --timerange 20230101-20241001 \
    --spaces buy sell \
    --epochs 100
```

### Optimizable Parameters

**Buy Space:**
- `min_wave_probability`: 60.0 - 90.0
- `min_fibonacci_score`: 50.0 - 85.0
- `use_volume_confirmation`: 0 or 1

**Sell Space:**
- `target_level`: 1, 2, or 3

### View Optimization Results

```bash
# Show best results
freqtrade hyperopt-show

# Show specific epoch
freqtrade hyperopt-show -n 50

# Export results
freqtrade hyperopt-show --print-json > hyperopt_results.json
```

---

## 🔍 Monitoring & Debugging

### Check Strategy Status

```bash
# Show current trades
freqtrade show_trades

# Show strategy performance
freqtrade backtesting-analysis

# View logs
tail -f logs/freqtrade.log
```

### Enable Debug Logging

In `config.json`:
```json
{
    "verbosity": 3,
    "logfile": "logs/freqtrade.log"
}
```

### View Elliott Wave Analysis

The strategy sends messages via Telegram (if configured) showing:
- Pattern probability
- Fibonacci scores
- Target prices
- Risk/Reward ratios

---

## ❓ Troubleshooting

### Issue: No Elliott Wave patterns found

**Solutions:**
1. Check timeframe - use 1d or 4h
2. Ensure enough historical data (100+ candles)
3. Lower `min_wave_probability` threshold
4. Check if pair has clear trends

### Issue: Strategy not entering trades

**Check:**
1. Are Elliott Wave indicators populated? (Check plots)
2. Is RSI in acceptable range?
3. Is volume confirmation required but not met?
4. Check Risk/Reward ratio requirements

### Issue: Import errors

```bash
# Verify installation
python -c "from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
pip install numpy pandas numba matplotlib --force-reinstall
```

### Issue: Slow performance

**Optimizations:**
1. Reduce `wave_combinatorial_limit` (default: 12 → try 8)
2. Reduce `wave_scan_window` (default: 100 → try 50)
3. Use higher timeframes (1d instead of 1h)
4. Reduce number of pairs

### Issue: Frequent stops/invalidations

**Adjustments:**
1. Increase `min_wave_probability` (more selective)
2. Use `SimpleElliotWaveStrategy` (more conservative)
3. Add more confirmations (RSI, MACD)
4. Increase minimum Risk/Reward ratio

---

## 📚 Additional Resources

### Documentation
- [Freqtrade Documentation](https://www.freqtrade.io/)
- [Elliott Wave Theory Guide](../doc/ELLIOTT_WAVE_THEORY.md)
- [Enhanced Analyzer README](../README_ENHANCED.md)

### Example Commands Cheat Sheet

```bash
# Backtest
freqtrade backtesting --strategy SimpleElliotWaveStrategy --timeframe 1d

# Dry-run
freqtrade trade --strategy SimpleElliotWaveStrategy --dry-run

# Plot
freqtrade plot-dataframe --strategy SimpleElliotWaveStrategy --pairs BTC/USDT

# Hyperopt
freqtrade hyperopt --strategy EnhancedElliotWaveStrategy --epochs 100

# Show trades
freqtrade show_trades

# Status
freqtrade status
```

---

## 🎓 Strategy Tips

### For Best Results:

1. **Use Daily Timeframe**
   - Elliott Wave patterns clearer
   - Less noise
   - Better probability scores

2. **Trade Major Pairs**
   - BTC/USDT, ETH/USDT
   - High liquidity
   - Clear wave structures

3. **Be Patient**
   - Wait for high-probability setups (75%+)
   - Don't force trades
   - Quality over quantity

4. **Respect Risk Management**
   - Always use stop losses
   - Honor invalidation levels
   - Never override Risk/Reward minimums

5. **Monitor Fibonacci Scores**
   - Higher Fib scores = better patterns
   - Look for multiple Fibonacci confirmations
   - 70%+ Fib score is excellent

6. **Understand Wave Psychology**
   - Wave 5 often shows RSI divergence
   - Wave 3 typically strongest
   - Wave 4 rarely overlaps Wave 1

---

## 🚀 Next Steps

1. **Start with Backtesting**
   ```bash
   freqtrade backtesting --strategy SimpleElliotWaveStrategy --timeframe 1d
   ```

2. **Analyze Results**
   - Check win rate
   - Review Risk/Reward ratios
   - Identify best-performing pairs

3. **Paper Trade (Dry-Run)**
   ```bash
   freqtrade trade --strategy SimpleElliotWaveStrategy --dry-run
   ```

4. **Optimize (Optional)**
   ```bash
   freqtrade hyperopt --strategy EnhancedElliotWaveStrategy
   ```

5. **Go Live (Carefully!)**
   - Start with small amounts
   - Monitor closely
   - Build confidence gradually

---

## 📞 Support

For issues or questions:
- Review this documentation
- Check [Freqtrade Documentation](https://www.freqtrade.io/)
- Review Elliott Wave Theory guide
- Check strategy logs for errors

---

**Built with ❤️ for Elliott Wave traders**

*Happy Trading! 📈*
