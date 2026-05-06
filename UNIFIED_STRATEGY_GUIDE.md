# Unified Strategy Validation Guide

## Overview
The unified strategy validation system combines signals from multiple mining modules to create more reliable trading signals. This guide covers how to use the three different validation approaches.

## Table of Contents
1. [Technical Strategies](#technical-strategies)
2. [Unified Signals](#unified-signals)
3. [Combined Rules](#combined-rules)
4. [API Reference](#api-reference)

---

## Technical Strategies

Traditional technical analysis strategies (SMA Crossover, RSI Strategy).

**Use Case:** Simple, well-tested strategies based on technical indicators.

**Example Request:**
```json
{
  "ticker": "AAPL",
  "strategy": "sma_crossover",
  "params": {
    "fast_period": 20,
    "slow_period": 50
  },
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000
}
```

---

## Unified Signals

Combines signals from multiple modules with simple aggregation.

**Best for:** Quick validation using multiple data sources with simple rules.

### Module Configurations

#### Anomaly Detection
```json
{
  "enabled": true,
  "period": "1y",
  "zscore_threshold": 2.0
}
```
- `zscore_threshold`: Values above/below this trigger signals
- BUY when z-score < -threshold (price unusually low)
- SELL when z-score > threshold (price unusually high)

#### Clustering
```json
{
  "enabled": true,
  "n_clusters": 3,
  "features": ["pe_ratio", "market_cap"],
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```
- Evaluates cluster quality
- Strong clusters indicate good stocks
- Confidence based on silhouette score

#### Association Rules
```json
{
  "enabled": true,
  "min_support": 0.1,
  "min_confidence": 0.6,
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```
- Mines BUY/SELL patterns from price/volume events
- Uses association confidence as signal strength

### Example Request

```json
{
  "ticker": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000,
  "hold_days": 5,
  "aggregation_method": "weighted",
  "modules": {
    "anomaly": {
      "enabled": true,
      "period": "1y",
      "zscore_threshold": 2.0
    },
    "association": {
      "enabled": true,
      "min_support": 0.1,
      "min_confidence": 0.6,
      "tickers": ["AAPL", "MSFT"]
    },
    "clustering": {
      "enabled": false
    }
  }
}
```

### Aggregation Methods

1. **Weighted Average** (Default)
   - Each signal's confidence is weighted
   - Final signal determined by highest total weight
   - Best for: Most use cases

2. **Majority Vote**
   - Signal type with most votes wins
   - Confidence is average of all signals
   - Best for: When module count varies

3. **Unanimous**
   - All signals must agree
   - Very few trades, but high accuracy
   - Best for: Conservative trading

---

## Combined Rules

Advanced multi-module validation with custom AND/OR logic.

**Best for:** Sophisticated strategies requiring specific combinations of signals.

### Rule Configuration

```json
{
  "condition": "AND",
  "requirements": [
    {
      "source": "anomaly",
      "signal": "BUY",
      "min_confidence": 0.5
    },
    {
      "source": "association",
      "signal": "BUY",
      "min_confidence": 0.6
    }
  ]
}
```

### Example Request

```json
{
  "ticker": "AAPL",
  "start_date": "2022-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000,
  "hold_days": 5,
  "rule_config": {
    "condition": "AND",
    "requirements": [
      {
        "source": "anomaly",
        "signal": "BUY",
        "min_confidence": 0.5
      },
      {
        "source": "association",
        "signal": "BUY",
        "min_confidence": 0.6
      }
    ]
  },
  "modules": {
    "anomaly": {
      "enabled": true,
      "period": "1y",
      "zscore_threshold": 2.0
    },
    "association": {
      "enabled": true,
      "min_support": 0.1,
      "min_confidence": 0.6,
      "tickers": ["AAPL", "MSFT"]
    },
    "clustering": {
      "enabled": false
    }
  }
}
```

### Rule Logic Examples

**Conservative (all must agree):**
```json
{
  "condition": "AND",
  "requirements": [
    {"source": "anomaly", "signal": "BUY", "min_confidence": 0.5},
    {"source": "association", "signal": "BUY", "min_confidence": 0.6}
  ]
}
```
Result: Trade only when BOTH anomaly AND association say BUY

**Aggressive (any strong signal):**
```json
{
  "condition": "OR",
  "requirements": [
    {"source": "anomaly", "signal": "BUY", "min_confidence": 0.8},
    {"source": "association", "signal": "BUY", "min_confidence": 0.8}
  ]
}
```
Result: Trade when EITHER anomaly OR association say strong BUY

---

## API Reference

### POST /api/backtest/unified-strategy
Validate using unified signals with module aggregation.

**Response:**
```json
{
  "total_return": 15.5,
  "annualized_return": 8.2,
  "win_rate": 62.5,
  "total_signals": 8,
  "total_trades": 4,
  "avg_return": 3.87,
  "max_gain": 450.50,
  "max_loss": -125.25,
  "sharpe_ratio": 1.45,
  "max_drawdown": 8.3,
  "equity_curve": [...],
  "trades": [...]
}
```

### POST /api/backtest/combined-signals
Validate using combined multi-module rules.

**Response:** Same as unified-strategy

### GET /api/backtest/strategy-templates
Get preset strategy templates.

**Response:**
```json
{
  "templates": [
    {
      "id": "anomaly_only",
      "name": "Anomaly Detection Strategy",
      "description": "Trades based on price anomalies (z-score)"
    },
    {
      "id": "combined_conservative",
      "name": "Conservative Combined Strategy"
    },
    {
      "id": "combined_aggressive",
      "name": "Aggressive Combined Strategy"
    }
  ]
}
```

---

## Response Metrics Explained

| Metric | Description | Target |
|--------|-------------|--------|
| **Total Return %** | Overall profit/loss as % | Positive is better |
| **Annualized Return %** | Extrapolated annual return | 10-20% is good |
| **Win Rate %** | % of profitable trades | >50% is good |
| **Avg Return %** | Average profit per trade | Higher is better |
| **Max Gain** | Best single trade | Higher is better |
| **Max Loss** | Worst single trade | Less negative is better |
| **Sharpe Ratio** | Risk-adjusted return | >1.0 is good |
| **Max Drawdown %** | Worst peak-to-trough | Lower is better |
| **Total Trades** | Number of completed trades | More data points |

---

## Trading Rules

1. **Entry:** Buy on BUY signal with matching confidence
2. **Exit:** Either when SELL signal appears or after hold_days
3. **Position:** Single position held at a time
4. **Capital Usage:** 95% of available capital per trade
5. **Transaction Costs:** Commission and slippage accounted for

---

## Performance Tips

1. **Validation Setup:**
   - Use 2-3 year historical data for reliable validation
   - Test on different market conditions
   - Compare multiple rule configurations

2. **Module Selection:**
   - Don't enable all modules for every strategy
   - Start simple, add complexity gradually
   - Validate each module independently first

3. **Rule Configuration:**
   - Conservative rules (AND) = fewer trades, higher accuracy
   - Aggressive rules (OR) = more trades, need to monitor
   - Adjust confidence thresholds based on results

---

## Common Mistakes to Avoid

1. ❌ Over-optimization on historical data (curve fitting)
2. ❌ Using too short validation period (<1 year)
3. ❌ Not accounting for transaction costs
4. ❌ Selecting rules that generate zero trades
5. ❌ Ignoring maximum drawdown (risk metric)

---

## Next Steps

1. Start with Technical Strategies for baseline
2. Try Unified Signals with one module enabled
3. Compare with Combined Rules using conservative logic
4. Fine-tune thresholds based on results
5. Validate on out-of-sample data before deployment
