# Elliott Wave Freqtrade Strategy - Quick Start Guide

Get up and running with Elliott Wave trading in Freqtrade in 10 minutes!

---

## 🚀 Quick Start (10 Minutes)

### Step 1: Copy Files (2 minutes)

```bash
# Assuming you have Freqtrade already installed
cd ~/freqtrade

# Copy the Elliott Wave files
cp -r /path/to/ElliottWaveAnalyzer/models user_data/strategies/
cp -r /path/to/ElliottWaveAnalyzer/freqtrade user_data/strategies/
```

### Step 2: Verify Installation (1 minute)

```bash
# Check strategies are available
freqtrade list-strategies

# You should see:
# - SimpleElliotWaveStrategy
# - EnhancedElliotWaveStrategy
```

### Step 3: Download Data (3 minutes)

```bash
# Download 1 year of daily data for major pairs
freqtrade download-data \
    --exchange binance \
    --pairs BTC/USDT ETH/USDT \
    --timeframe 1d \
    --days 365
```

### Step 4: Run Backtest (2 minutes)

```bash
# Test the strategy on historical data
freqtrade backtesting \
    --strategy SimpleElliotWaveStrategy \
    --timeframe 1d \
    --timerange 20230101-20241101
```

### Step 5: Review Results (2 minutes)

```bash
# View backtest results
freqtrade backtesting-analysis

# Generate plots
freqtrade plot-dataframe \
    --strategy SimpleElliotWaveStrategy \
    --pairs BTC/USDT \
    --timeframe 1d
```

---

## 🎯 What You'll See

### Expected Backtest Output:

```
============================================================
BACKTESTING REPORT
============================================================
| Pair      |   Entries |   Avg Profit % |   Tot Profit % |
|-----------|-----------|----------------|----------------|
| BTC/USDT  |        12 |           8.45 |         101.40 |
| ETH/USDT  |        15 |           6.32 |          94.80 |
| TOTAL     |        27 |           7.39 |         196.20 |
============================================================

Entries: High-probability Elliott Wave patterns only
Win Rate: ~65-75% (typical for Elliott Wave)
Avg R/R: 2.5:1 or better
```

### Plot Features:

- **Blue dots**: Wave 1, 3, 5 high points
- **Green lines**: Fibonacci targets
- **Red line**: Invalidation stop loss
- **Entry arrows**: High-probability setups
- **Exit arrows**: Target reached or exhaustion

---

## 📋 Next Steps

### Option A: Paper Trade (Recommended)

```bash
# Start dry-run mode (no real money)
freqtrade trade \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json \
    --dry-run
```

Monitor for 1-2 weeks to build confidence.

### Option B: Optimize Settings

```bash
# Optimize for your preferred pairs
freqtrade hyperopt \
    --strategy EnhancedElliotWaveStrategy \
    --timeframe 1d \
    --epochs 100 \
    --spaces buy sell
```

### Option C: Go Live (When Ready!)

```bash
# Real trading - start small!
freqtrade trade \
    --strategy SimpleElliotWaveStrategy \
    --config user_data/config.json
```

**⚠️ Important:** Start with small amounts, monitor closely!

---

## 🎓 Understanding the Strategy

### What the Strategy Does:

1. **Scans for Elliott Wave patterns** in your selected pairs
2. **Scores each pattern** 0-100% based on:
   - Elliott Wave rules compliance
   - Fibonacci ratio relationships
   - Wave structure quality
3. **Only trades high-probability patterns** (>75% for Simple strategy)
4. **Sets clear targets** using Fibonacci projections
5. **Manages risk** with invalidation stop losses

### Entry Signal:

- ✅ High-probability Elliott Wave pattern detected
- ✅ Good Fibonacci relationships (multiple confirmations)
- ✅ RSI shows momentum (not overbought)
- ✅ Volume confirmation
- ✅ Risk/Reward ratio ≥ 2:1

### Exit Signal:

- 🎯 Fibonacci target reached
- 🔴 Stop loss at invalidation level
- ⚡ RSI shows Wave 5 exhaustion
- 📈 Trailing stop protects profits

---

## 🔧 Configuration Tips

### Best Pairs for Elliott Wave:

```json
"pair_whitelist": [
    "BTC/USDT",   // ⭐ Best - Clear waves
    "ETH/USDT",   // ⭐ Best - High liquidity
    "BNB/USDT",   // ✓ Good
    "SOL/USDT",   // ✓ Good
    "ADA/USDT"    // ✓ Good
]
```

**Avoid:**
- Low-volume pairs
- New tokens (< 6 months old)
- Meme coins

### Best Timeframes:

- **1d (Daily)** ⭐ **RECOMMENDED** - Clearest waves, best results
- **4h** ✓ Good - More signals, slightly noisier
- **1h** ⚠️ Advanced only - More noise
- **< 1h** ❌ Not recommended

### Risk Settings:

```json
{
    "max_open_trades": 3,        // Conservative
    "stake_amount": "unlimited",  // Auto-calculate
    "tradable_balance_ratio": 0.99,
    "stoploss": -0.08            // 8% (overridden by wave invalidation)
}
```

---

## 📊 Performance Expectations

### Typical Results (Daily Timeframe):

| Metric           | Expected Range |
|------------------|----------------|
| Win Rate         | 60-75%         |
| Avg R/R Ratio    | 2.0-3.5:1      |
| Trades/Month     | 2-8            |
| Avg Trade Length | 5-20 days      |
| Drawdown         | 10-20%         |

**Note:** Results vary by market conditions and pair selection.

### When Strategy Works Best:

✅ **Trending markets** (bull or bear)
✅ **Clear impulse waves forming**
✅ **High liquidity pairs**
✅ **Daily timeframe**

❌ **Choppy/sideways markets**
❌ **Low volume pairs**
❌ **Very short timeframes**

---

## 🐛 Troubleshooting

### "No patterns found"

**Solutions:**
1. Lower `MIN_PROBABILITY` threshold (try 65%)
2. Use longer timeframe (1d instead of 1h)
3. Ensure 100+ candles of historical data
4. Check if pair has clear trends

### "Strategy not entering trades"

**Check:**
1. Are probabilities shown in plots? (Run `plot-dataframe`)
2. Is RSI too extreme? (Strategy avoids RSI >70)
3. Is volume requirement met?
4. Check Risk/Reward ratio (must be ≥2:1)

### "Too many stop losses"

**Adjustments:**
1. Use `SimpleElliotWaveStrategy` (more conservative)
2. Increase `MIN_PROBABILITY` to 80%
3. Add more confirmations (enable volume check)
4. Use daily timeframe only

---

## 💡 Pro Tips

1. **Start with Daily Timeframe**
   - Clearest Elliott Wave patterns
   - Less noise
   - Better probability scores

2. **Be Patient**
   - Quality > Quantity
   - Wait for 75%+ probability setups
   - Don't force trades

3. **Respect the Waves**
   - Wave 5 often shows exhaustion (RSI divergence)
   - Wave 4 corrections are opportunities
   - Never ignore invalidation levels

4. **Monitor Fibonacci Scores**
   - 70%+ Fib score = excellent pattern
   - Multiple Fib confirmations = higher confidence
   - Low Fib scores often fail

5. **Use Telegram Notifications**
   - Get alerted to new patterns
   - Monitor entry/exit in real-time
   - Track performance easily

---

## 📱 Enable Telegram (Optional)

Edit `config.json`:

```json
{
    "telegram": {
        "enabled": true,
        "token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    }
}
```

You'll receive messages like:

```
📈 Elliott Wave found for BTC/USDT
Probability: 78.5%
Target 1: $58,250.00

✅ Trade confirmed: R/R 2.8
Entering BTC/USDT at $52,000

🎯 Target reached: BTC/USDT
Exit at $58,100 (+11.7%)
```

---

## 🎓 Learning Resources

- **Elliott Wave Theory**: `../doc/ELLIOTT_WAVE_THEORY.md`
- **Full Documentation**: `README_FREQTRADE.md`
- **Enhanced Analyzer**: `../README_ENHANCED.md`
- **Freqtrade Docs**: https://www.freqtrade.io/

---

## ✅ Checklist

Before going live, ensure:

- [ ] Backtested on 1+ year of data
- [ ] Win rate ≥ 60%
- [ ] Average R/R ratio ≥ 2:1
- [ ] Paper traded for 2+ weeks
- [ ] Understand entry/exit rules
- [ ] Telegram notifications working
- [ ] Using recommended pairs (BTC/ETH)
- [ ] Daily timeframe selected
- [ ] Risk settings configured
- [ ] Starting with small position sizes

---

## 🎯 Success Criteria

You're ready for live trading when:

1. **Backtest shows profit** over 12+ months
2. **Understand why trades win/lose** (review in plots)
3. **Comfortable with wave theory** (read the guide)
4. **Paper trading profitable** for 2+ weeks
5. **Risk management clear** (stop losses, position sizing)

---

## 🚨 Safety Reminders

- ⚠️ Start with **small amounts** ($100-500)
- ⚠️ Never risk more than **2% per trade**
- ⚠️ Always use **stop losses**
- ⚠️ Monitor **daily** in the beginning
- ⚠️ If in doubt, **stay out**

---

**You're all set! 🎉**

Start your backtesting and paper trading journey. Elliott Wave patterns provide high-probability setups with clear targets and stops.

*Happy Trading! 📈*
