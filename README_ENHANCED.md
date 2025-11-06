# Enhanced Elliott Wave Analyzer

An advanced Elliott Wave analysis system with probability scoring, Fibonacci-based price target calculation, and multi-timeframe support for OHLCV market data.

## 🎯 Key Features

### ✨ **NEW in Enhanced Version**

- **Probability Scoring System**: Every wave pattern is scored 0-100% based on:
  - Elliott Wave rules compliance (40%)
  - Fibonacci ratio relationships (30%)
  - Guidelines adherence (20%)
  - Wave structure quality (10%)

- **Price Target Calculation**: Automatic calculation of price targets using multiple Fibonacci methods
  - Wave 3 targets: 1.0x, 1.618x, 2.618x Wave 1
  - Wave 4 targets: 23.6%, 38.2%, 50% retracements
  - Wave 5 targets: Multiple projection methods
  - Wave C targets: Equality, 0.618x, 1.618x Wave A

- **Magnitude Analysis**: Real-time distance calculation from current price to all targets
  - Percentage and absolute distance to targets
  - Target status tracking (pending/reached/exceeded)
  - Probability-weighted target recommendations

- **Segment Length Variation Analysis**: Understand how different wave configurations affect probability
  - Compare multiple wave patterns simultaneously
  - Probability distribution across different segment lengths
  - Identify most probable wave structures

- **Comprehensive Fibonacci Analysis**:
  - Wave 2 retracement validation
  - Wave 3 extension analysis
  - Wave 4 retracement validation
  - Wave 5 projection using multiple methods
  - Corrective wave ABC relationships

- **Multi-Timeframe Support**: Analyze any OHLCV dataset regardless of timeframe
  - 1-minute to monthly charts
  - Automatic wave degree classification
  - Timeframe-independent pattern detection

- **Detailed Reporting**: Generate comprehensive analysis reports
  - Probability breakdowns
  - Fibonacci confirmations
  - Price targets with probabilities
  - Guideline compliance details

## 📚 Documentation

- **[Elliott Wave Theory Guide](doc/ELLIOTT_WAVE_THEORY.md)**: Comprehensive Elliott Wave Theory documentation including:
  - Wave rules and guidelines
  - Fibonacci relationships
  - Wave degrees
  - Pattern types
  - Probability assessment

## 🚀 Quick Start

### Installation

```bash
# Python 3.9+ required
pip install -r requirements.txt
```

### Basic Usage

```python
import pandas as pd
from models.EnhancedWaveAnalyzer import EnhancedWaveAnalyzer

# Load your OHLCV data
df = pd.read_csv('data/btc-usd_1d.csv')

# Create analyzer (min_probability = 60% threshold)
analyzer = EnhancedWaveAnalyzer(df, min_probability=60.0)

# Find best impulse wave patterns
idx_start = 0  # Starting index
candidates = analyzer.find_best_impulse_waves(idx_start, max_results=5)

# Print results
for candidate in candidates:
    print(f"Probability: {candidate.probability:.1f}%")
    print(f"Category: {candidate.probability_analysis['category']}")
```

### Calculate Price Targets

```python
# Get current price
current_price = analyzer.get_current_price()

# Find wave with targets
analysis = analyzer.find_wave_with_targets(
    idx_start=0,
    wave_type='impulse',
    current_price=current_price
)

if analysis['found']:
    targets = analysis['targets']
    print(f"Wave: {targets['wave']}")

    for target in targets['targets']:
        print(f"{target['level']}: ${target['price']:.2f}")
        print(f"  Probability: {target['probability']*100:.0f}%")
```

### Analyze Segment Variations

```python
# Understand how different wave configurations affect probability
variation_analysis = analyzer.analyze_segment_variations(
    idx_start=0,
    wave_type='impulse',
    min_probability=60.0
)

print(f"Total patterns found: {variation_analysis['total_candidates']}")
print(f"Best probability: {variation_analysis['best_candidate'].probability:.1f}%")
```

### Generate Comprehensive Report

```python
# Create detailed analysis report
report = analyzer.create_analysis_report(idx_start=0, wave_type='impulse')
print(report)
```

## 📖 Examples

### Example 1: Enhanced Wave Analysis
```bash
python example_enhanced_analyzer.py
```

Demonstrates:
- Finding wave patterns with probability scoring
- Price target calculation
- Segment length variation analysis
- Fibonacci analysis details
- Corrective wave analysis

### Example 2: Original Examples (Still Work!)
```bash
python example_monowave.py           # Basic MonoWave concept
python example_12345_impulsive_wave.py  # Classic impulse detection
```

## 🏗️ Architecture

### Core Components

#### 1. **EnhancedWaveAnalyzer**
Main analysis engine that orchestrates all components.

```python
analyzer = EnhancedWaveAnalyzer(
    df=dataframe,           # OHLCV data
    verbose=False,          # Print detailed logs
    min_probability=60.0    # Minimum probability threshold
)
```

**Key Methods:**
- `find_best_impulse_waves()`: Find impulse patterns with probability scores
- `find_best_corrective_waves()`: Find corrective patterns with scores
- `find_wave_with_targets()`: Find patterns and calculate price targets
- `analyze_segment_variations()`: Analyze different wave configurations
- `create_analysis_report()`: Generate comprehensive text report

#### 2. **FibonacciAnalyzer**
Calculates and validates Fibonacci relationships between waves.

**Features:**
- Wave 2 retracement analysis (38.2%, 50%, 61.8%, 78.6%)
- Wave 3 extension analysis (1.618x, 2.618x)
- Wave 4 retracement analysis (23.6%, 38.2%, 50%)
- Wave 5 projection (multiple methods)
- Corrective ABC relationships

#### 3. **ProbabilityScorer**
Scores wave patterns based on rules, guidelines, and Fibonacci ratios.

**Scoring Breakdown:**
- **Rules Compliance (40%)**: MUST be 100% for valid pattern
- **Fibonacci Ratios (30%)**: Quality of Fibonacci relationships
- **Guidelines (20%)**: Alternation, wave equality, etc.
- **Structure Quality (10%)**: Wave proportions and clarity

**Probability Categories:**
- 90-100%: Very High - Excellent pattern
- 75-89%: High - Strong pattern
- 60-74%: Moderate - Valid but weak
- 50-59%: Low - Questionable
- <50%: Very Low - Poor quality

#### 4. **TargetCalculator**
Calculates price targets using Fibonacci ratios.

**Wave 3 Targets:**
- Minimum: 1.0x Wave 1
- Common: 1.618x Wave 1 (Golden Ratio)
- Extended: 2.618x Wave 1
- Very Extended: 3.618x Wave 1

**Wave 4 Targets:**
- Shallow: 23.6% retracement
- Common: 38.2% retracement
- Deep: 50% retracement
- Invalidation: Wave 1 high

**Wave 5 Targets:**
- Conservative: 0.618x Wave 1
- Equality: 1.0x Wave 1 (most common)
- Fibonacci projection: 0.618x Wave 1-3
- Extended: 1.618x Wave 4

**Wave C Targets:**
- Short: 0.618x Wave A
- Equality: 1.0x Wave A (most common)
- Extended: 1.618x Wave A
- Very Extended: 2.618x Wave A

#### 5. **Original Components** (Still Available)
- **MonoWave**: Basic wave detection (up/down movements)
- **WavePattern**: Chain of waves forming patterns
- **WaveRules**: Rule validation (Impulse, Correction, Diagonal)
- **WaveOptions**: Combinatorial wave configurations

## 📊 Data Requirements

Your DataFrame must contain these columns:
- **Date**: Date/timestamp
- **Open**: Opening price
- **High**: Highest price
- **Low**: Lowest price
- **Close**: Closing price
- **Volume** (optional): Trading volume

Supports any timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M

## 🎯 Use Cases

### Trading Strategy Development
```python
# Find high-probability setups
analyzer.set_combinatorial_limits(n_impulse=15, n_correction=12)
impulses = analyzer.find_best_impulse_waves(idx_start, max_results=10)

# Filter for very high probability (>85%)
high_prob = [c for c in impulses if c.probability >= 85.0]

# Get price targets for entry/exit
for candidate in high_prob:
    # Calculate targets...
    pass
```

### Multi-Timeframe Analysis
```python
# Analyze different timeframes
timeframes = {
    '1h': df_1h,
    '4h': df_4h,
    '1d': df_1d
}

for tf, data in timeframes.items():
    analyzer = EnhancedWaveAnalyzer(data)
    patterns = analyzer.find_best_impulse_waves(0)
    print(f"{tf}: Found {len(patterns)} patterns")
```

### Pattern Scanning
```python
# Scan entire dataset for patterns
patterns = analyzer.scan_entire_dataset(
    wave_type='impulse',
    min_probability=70.0,
    step_size=20
)

print(f"Found {len(patterns)} high-probability patterns")
```

## 🔬 Advanced Features

### Custom Probability Thresholds
```python
# Very conservative (only excellent patterns)
analyzer = EnhancedWaveAnalyzer(df, min_probability=85.0)

# More permissive (include moderate patterns)
analyzer = EnhancedWaveAnalyzer(df, min_probability=50.0)
```

### Segment Length Configuration
```python
# More combinations (slower but more thorough)
analyzer.set_combinatorial_limits(n_impulse=20, n_correction=15)

# Fewer combinations (faster but may miss some patterns)
analyzer.set_combinatorial_limits(n_impulse=8, n_correction=8)
```

### Accessing Detailed Analysis
```python
candidate = impulse_candidates[0]

# Probability breakdown
prob_analysis = candidate.probability_analysis
scores = prob_analysis['scores']

# Fibonacci details
fib_details = scores['fibonacci_ratios']['details']
wave2_analysis = fib_details['wave2_retracement']
wave3_analysis = fib_details['wave3_extension']

# Guidelines details
guidelines = scores['guidelines']['details']
for guideline in guidelines:
    print(guideline)
```

## 📈 Performance Considerations

- **Combinatorial Limits**: Higher limits = more accurate but slower
  - Recommended for backtesting: `n_impulse=15`
  - Recommended for real-time: `n_impulse=10`

- **Probability Threshold**: Higher threshold = fewer but better patterns
  - Conservative: `min_probability=75.0`
  - Balanced: `min_probability=60.0`
  - Permissive: `min_probability=50.0`

- **Step Size**: For scanning, larger step = faster but may miss patterns
  - Thorough: `step_size=5`
  - Balanced: `step_size=10`
  - Fast: `step_size=20`

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

## 📝 Changelog

### Version 2.0 (Enhanced)
- ✨ Added probability scoring system
- ✨ Added Fibonacci analyzer
- ✨ Added price target calculator
- ✨ Added magnitude analysis
- ✨ Added segment variation analysis
- ✨ Added comprehensive reporting
- ✨ Added multi-timeframe support
- 📚 Added Elliott Wave Theory documentation
- 🎯 Enhanced wave detection accuracy
- 🔧 Improved API ergonomics

### Version 1.0 (Original)
- Basic MonoWave detection
- WavePattern validation
- WaveRules implementation
- Impulse and Correction detection

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Ralph Nelson Elliott for Elliott Wave Theory
- Leonardo Fibonacci for Fibonacci sequence
- Original ElliottWaveAnalyzer contributors

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the Elliott Wave Theory guide in `doc/ELLIOTT_WAVE_THEORY.md`

## 🎓 Learning Resources

1. **Start Here**: `doc/ELLIOTT_WAVE_THEORY.md` - Complete Elliott Wave Theory guide
2. **Basic Concepts**: `example_monowave.py` - Understand MonoWaves
3. **Pattern Detection**: `example_12345_impulsive_wave.py` - Classic detection
4. **Enhanced Features**: `example_enhanced_analyzer.py` - New capabilities

## 🔮 Future Enhancements

- [ ] Real-time market data integration
- [ ] Additional corrective pattern types (triangles, flats)
- [ ] Wave degree automatic classification
- [ ] Machine learning probability enhancement
- [ ] Interactive visualization dashboard
- [ ] Alert system for high-probability setups
- [ ] Backtesting framework integration

---

**Built with ❤️ for Elliott Wave traders and analysts**
