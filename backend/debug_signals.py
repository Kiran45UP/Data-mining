"""
Debug script to trace signal generation and aggregation
"""
import sys
sys.path.insert(0, 'd:\\programme files\\AIML\\Data mining\\stockmind\\backend')

import yfinance as yf
import pandas as pd
from backtesting.signal_converters import (
    AnomalySignalConverter, AssociationSignalConverter, SignalAggregator
)
from mining.anomaly_detection import detect_anomalies
from mining.association_rules import run_association_rules

ticker = "AAPL"
start_date = "2022-01-01"
end_date = "2023-12-31"

print("=" * 80)
print("DEBUGGING SIGNAL GENERATION AND AGGREGATION")
print("=" * 80)

# Step 1: Fetch price data
print("\n1. FETCHING PRICE DATA")
data = yf.download(ticker, start=start_date, end=end_date, progress=False)
print(f"✓ Got {len(data)} rows of price data")
print(f"  Date range: {data.index.min()} to {data.index.max()}")

# Step 2: Anomaly detection
print("\n2. ANOMALY DETECTION")
anomaly_result = detect_anomalies(ticker, period="1y")
print(f"✓ Anomaly detection result keys: {anomaly_result.keys()}")
print(f"  Anomalies found: {anomaly_result.get('anomaly_count')}")
print(f"  Total data points: {anomaly_result.get('total_days')}")

# Step 3: Convert anomaly to signals
print("\n3. ANOMALY SIGNAL CONVERSION")
anomaly_signals = AnomalySignalConverter.convert(anomaly_result, zscore_threshold=2.0)
print(f"✓ Anomaly signals generated: {len(anomaly_signals)}")
if anomaly_signals:
    print(f"  First signal:")
    s = anomaly_signals[0]
    print(f"    Date: {s.date} (type: {type(s.date)})")
    print(f"    Ticker: {s.ticker}")
    print(f"    Signal: {s.signal}")
    print(f"    Confidence: {s.confidence}")
    print(f"  Sample signals:")
    for s in anomaly_signals[:3]:
        print(f"    {s.date}: {s.signal} ({s.confidence:.2f})")

# Step 4: Association rules
print("\n4. ASSOCIATION RULES")
assoc_result = run_association_rules([ticker], min_support=0.1, min_confidence=0.6)
print(f"✓ Association rules result keys: {assoc_result.keys()}")
rules = assoc_result.get('rules', [])
print(f"  Rules found: {len(rules)}")
if rules:
    print(f"  First rule: {rules[0]}")

# Step 5: Convert association to signals
print("\n5. ASSOCIATION SIGNAL CONVERSION")
assoc_signals_dict = AssociationSignalConverter.convert(assoc_result, confidence_threshold=0.6)
total_assoc = sum(len(v) for v in assoc_signals_dict.values())
print(f"✓ Association signals generated: {total_assoc}")
for ticker_key, sigs in assoc_signals_dict.items():
    if sigs:
        print(f"  {ticker_key}: {len(sigs)} signals")
        for s in sigs[:2]:
            print(f"    {s.date}: {s.signal} ({s.confidence:.2f})")

# Step 6: Combine all signals
print("\n6. COMBINING ALL SIGNALS")
all_signals = anomaly_signals + [s for sigs in assoc_signals_dict.values() for s in sigs]
print(f"✓ Total signals: {len(all_signals)}")

# Filter for ticker
ticker_signals = [s for s in all_signals if s.ticker == ticker]
print(f"✓ Signals for {ticker}: {len(ticker_signals)}")

# Step 7: Aggregation
print("\n7. SIGNAL AGGREGATION")
aggregated = SignalAggregator.aggregate_signals(ticker_signals, aggregation_method='weighted')
print(f"✓ Aggregated signals: {len(aggregated)}")
print(f"  Aggregated keys (date, ticker):")
for key in list(aggregated.keys())[:5]:
    print(f"    {key}")

# Step 8: Convert to validator format
print("\n8. CONVERTING TO VALIDATOR FORMAT")
signals_dict = {}
for (date, ticker_key), agg_signal in aggregated.items():
    signals_dict[(date, ticker_key)] = agg_signal
    
print(f"✓ Signals dict for validator: {len(signals_dict)} signals")
print(f"  Date range in signals: {min(k[0] for k in signals_dict.keys())} to {max(k[0] for k in signals_dict.keys())}")
print(f"  Sample signals_dict entries:")
for key in list(signals_dict.keys())[:3]:
    print(f"    {key}: {signals_dict[key]['signal']}")

# Step 9: Check if signals match dates in price data
print("\n9. MATCHING SIGNALS TO PRICE DATA")
price_dates = set(data.index.strftime('%Y-%m-%d'))
signal_dates = set(k[0] for k in signals_dict.keys())
matches = price_dates & signal_dates
print(f"✓ Price data dates: {len(price_dates)}")
print(f"✓ Signal dates: {len(signal_dates)}")
print(f"✓ Matching dates: {len(matches)}")
print(f"  Sample matching dates:")
for date in sorted(list(matches))[:5]:
    print(f"    {date}")

print("\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80)
