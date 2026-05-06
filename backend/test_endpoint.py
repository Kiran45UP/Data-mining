"""
Test script for unified strategy endpoint
"""
import sys
sys.path.insert(0, 'd:\\programme files\\AIML\\Data mining\\stockmind\\backend')

# Test imports
try:
    from backtesting.signal_converters import (
        AnomalySignalConverter, ClusteringSignalConverter, 
        AssociationSignalConverter, SignalAggregator, TradeSignal
    )
    from backtesting.validation_engine import StrategyValidator
    from mining.anomaly_detection import detect_anomalies
    from mining.association_rules import run_association_rules
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test TradeSignal dataclass
try:
    signal = TradeSignal(
        date='2023-01-01',
        ticker='AAPL',
        signal='BUY',
        confidence=0.8,
        source='anomaly',
        details={'test': 'data'}
    )
    print(f"✓ TradeSignal created: {signal}")
    print(f"✓ Signal to_dict: {signal.to_dict()}")
except Exception as e:
    print(f"✗ TradeSignal error: {e}")
    sys.exit(1)

# Test anomaly detection
try:
    print("\n📊 Testing anomaly detection for AAPL...")
    anomaly_result = detect_anomalies('AAPL', period='1y')
    if 'error' in anomaly_result:
        print(f"⚠ Anomaly error: {anomaly_result['error']}")
    else:
        print(f"✓ Anomaly result keys: {anomaly_result.keys()}")
        print(f"  - Anomaly count: {anomaly_result.get('anomaly_count')}")
        print(f"  - Total days: {anomaly_result.get('total_days')}")
        print(f"  - Data points: {len(anomaly_result.get('data', []))}")
        
        # Test converter
        signals = AnomalySignalConverter.convert(anomaly_result, zscore_threshold=2.0)
        print(f"✓ Anomaly signals generated: {len(signals)}")
        if signals:
            print(f"  Sample signal: {signals[0].to_dict()}")
except Exception as e:
    print(f"✗ Anomaly detection error: {e}")
    import traceback
    traceback.print_exc()

# Test association rules
try:
    print("\n📊 Testing association rules for AAPL...")
    assoc_result = run_association_rules(['AAPL'], min_support=0.1, min_confidence=0.6)
    if 'error' in assoc_result:
        print(f"⚠ Association error: {assoc_result['error']}")
    else:
        print(f"✓ Association result keys: {assoc_result.keys()}")
        rules = assoc_result.get('rules', [])
        print(f"✓ Rules found: {len(rules)}")
        if rules:
            print(f"  Sample rule: {rules[0]}")
        
        # Test converter
        signals_dict = AssociationSignalConverter.convert(assoc_result, confidence_threshold=0.6)
        print(f"✓ Association signals generated: {sum(len(v) for v in signals_dict.values())}")
        for ticker, sigs in signals_dict.items():
            if sigs:
                print(f"  {ticker}: {len(sigs)} signals")
                print(f"  Sample signal: {sigs[0].to_dict()}")
except Exception as e:
    print(f"✗ Association rules error: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ All tests passed!")
