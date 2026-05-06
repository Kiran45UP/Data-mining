import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any
import sys
import os

# Add parent directory to path to allow imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_fetcher import fetch_price_history

def detect_anomalies(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """Detect anomalies in daily returns using Isolation Forest."""
    
    # 1. Fetch price history
    hist = fetch_price_history(ticker, period=period)
    
    if hist is None or hist.empty:
        return {"error": f"Could not fetch data for {ticker}"}
        
    # 2. Compute daily return
    # Fill NaN from pct_change with 0 to keep the same number of rows for joining back
    hist['daily_return'] = hist['Close'].pct_change().fillna(0)
    
    # 3. Fit IsolationForest
    # Reshape for sklearn: expects 2D array
    X = hist['daily_return'].values.reshape(-1, 1)
    
    try:
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(X)
        
        # 4. Predict anomaly labels (-1 = anomaly, 1 = normal)
        labels = clf.predict(X)
        scores = clf.decision_function(X) # lower score means more anomalous
        
        # Format results
        data_points = []
        anomaly_count = 0
        
        for i, date in enumerate(hist.index):
            is_anomaly = bool(labels[i] == -1)
            if is_anomaly:
                anomaly_count += 1
                
            data_points.append({
                "date": date.strftime('%Y-%m-%d'),
                "close": float(hist['Close'].iloc[i]),
                "daily_return": float(hist['daily_return'].iloc[i]),
                "is_anomaly": is_anomaly,
                "anomaly_score": float(scores[i])
            })
            
        return {
            "ticker": ticker,
            "data": data_points,
            "anomaly_count": anomaly_count,
            "total_days": len(data_points)
        }
        
    except Exception as e:
        return {"error": f"Anomaly detection failed: {str(e)}"}
