"""
Test the unified strategy validation endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test payload
payload = {
    "ticker": "AAPL",
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 10000,
    "hold_days": 5,
    "modules": {
        "anomaly": {
            "enabled": True,
            "period": "1y",
            "zscore_threshold": 2.0
        },
        "clustering": {"enabled": False},
        "association": {
            "enabled": True,
            "min_support": 0.1,
            "min_confidence": 0.6
        }
    },
    "aggregation_method": "weighted"
}

print("🚀 Testing unified strategy validation endpoint...")
print(f"📤 Sending request to {BASE_URL}/api/backtest/unified-strategy")
print(f"📋 Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/api/backtest/unified-strategy",
        json=payload,
        timeout=60
    )
    
    print(f"\n✅ Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Success! Result keys: {result.keys()}")
        
        # Display metrics
        if 'total_return' in result:
            print(f"\n📊 Performance Metrics:")
            print(f"  Total Return: {result.get('total_return')}%")
            print(f"  Win Rate: {result.get('win_rate')}%")
            print(f"  Total Trades: {result.get('total_trades')}")
            print(f"  Sharpe Ratio: {result.get('sharpe_ratio')}")
            print(f"  Max Drawdown: {result.get('max_drawdown')}%")
        
        if 'error' in result:
            print(f"⚠ Error in result: {result['error']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
    print("Make sure the backend server is running on port 8000")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
