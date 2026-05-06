# Unified Signals - Quick Start Guide

## What Changed

The Backtesting page now shows **only Unified Signals** - simplified and focused on what works.

Removed:
- ❌ Technical Strategies (SMA/RSI)
- ❌ Combined Rules (complex AND/OR logic)

Kept:
- ✅ Unified Signals (simple multi-module validation)

---

## How to Use

### Step 1: Select Ticker
- Choose a stock ticker (e.g., AAPL, MSFT, GOOGL)

### Step 2: Set Date Range
- **Start Date**: When to begin validation
- **End Date**: When to end validation
- Recommended: 1-2 years of data for good results

### Step 3: Set Capital & Hold Days
- **Capital**: Starting money for backtesting (default $10,000)
- **Hold Days**: How many days to hold each trade (default 5)

### Step 4: Select Modules

Enable one or both modules:

#### Module 1: Z-Score Anomaly
- Detects unusual price movements
- **Threshold**: How extreme to consider anomalous
  - Default: 2.0 (standard deviations)
  - Lower = more sensitive (more trades)
  - Higher = less sensitive (fewer trades)
- **Logic**:
  - BUY when price is extremely low
  - SELL when price is extremely high

#### Module 2: Association Rules
- Finds price/volume patterns
- **Min Confidence**: How reliable the pattern should be
  - Default: 0.6 (60% confidence)
  - Higher = more reliable signals
  - Lower = more signals (but less accurate)

### Step 5: Choose Aggregation Method

How to combine signals if both modules are enabled:

1. **Weighted Average** (Default)
   - Each module's confidence is weighted
   - Best overall results

2. **Majority Vote**
   - Signal type that appears most wins
   - Simpler logic

3. **Unanimous**
   - Both must agree
   - Very conservative, fewer trades

### Step 6: Run Validation

Click "Validate Strategy" button.

---

## Understanding Results

### Key Metrics

| Metric | Meaning | Target |
|--------|---------|--------|
| **Total Return %** | Overall profit/loss | Positive is good |
| **Win Rate %** | % of profitable trades | >50% is good |
| **Avg Return %** | Average profit per trade | Higher is better |
| **Max Gain** | Best single trade | Higher is better |
| **Max Loss** | Worst single trade | Less negative is better |
| **Total Trades** | Number of completed trades | More data points |
| **Sharpe Ratio** | Risk-adjusted return | >1.0 is good |
| **Max Drawdown %** | Worst peak-to-trough decline | Lower is better |
| **Final Equity** | Ending account value | Higher is better |

### Charts

**Equity Curve**: Shows how your account balance changes over time
- Up = making money
- Down = losing money
- Flat = no trades

### Trade Log

Shows every buy/sell:
- Date, Action (BUY/SELL), Price, Shares
- Days Held, P&L (profit/loss), Return %

---

## Simple Usage Examples

### Example 1: Quick Test
```
Ticker: AAPL
Date: 2023-01-01 to 2023-12-31
Capital: $10,000
Hold Days: 5
Modules: Anomaly only (threshold 2.0)
Result: See how anomaly-based trading performed
```

### Example 2: Pattern Detection
```
Ticker: MSFT
Date: 2022-01-01 to 2024-01-01
Capital: $10,000
Hold Days: 3
Modules: Association Rules only (confidence 0.6)
Result: See how pattern-based trading performed
```

### Example 3: Combined Signals
```
Ticker: GOOGL
Date: 2022-06-01 to 2024-01-01
Capital: $20,000
Hold Days: 10
Modules: Both enabled
Aggregation: Weighted Average
Result: See combined results with weighted aggregation
```

---

## Tips & Tricks

1. **Start Simple**
   - Enable just Anomaly first
   - See if it works for your stock
   - Then try Association Rules
   - Finally, try both together

2. **Adjust Thresholds**
   - Low threshold = more signals = more trades = more risk
   - High threshold = fewer signals = fewer trades = less data
   - Balance between having enough trades to analyze

3. **Different Time Periods**
   - Try different date ranges
   - Markets behave differently in different periods
   - Bull market vs Bear market

4. **Compare Results**
   - Run same strategy multiple times with different settings
   - See which threshold works best for your stock
   - Note the win rate and average return

---

## Common Issues & Solutions

### "No Results Generated"
- Enable at least one module (Anomaly or Association)
- Check dates are valid and have data

### "No Trades Executed"
- Signals exist but conditions weren't met
- Try lowering threshold or confidence
- Use different date range with more volatility

### "All Losing Trades"
- Module might not be suitable for this stock
- Try different aggregation method
- Adjust hold days (more days might help)

### "Very Few Trades"
- Threshold or confidence too high
- Lower the threshold to get more signals
- Or just accept fewer, higher-quality signals

---

## Next Steps

1. ✅ Test with a familiar stock (AAPL, MSFT)
2. ✅ Compare module results individually
3. ✅ Try combined approach with weighted average
4. ✅ Adjust thresholds based on results
5. ✅ Note settings that work well

---

## Questions?

The system is simple:
- Select modules ✓
- Set thresholds ✓
- Run validation ✓
- See results ✓

That's it! No complex rules, no confusing options.
