import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path to allow imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_fetcher import fetch_price_history

def run_association_rules(tickers: List[str], min_support: float, min_confidence: float) -> Dict[str, Any]:
    """Mine association rules based on daily price/volume events."""
    if not tickers:
        return {"rules": [], "total_rules": 0, "error": "No tickers provided"}
        
    all_events = pd.DataFrame()
    
    # 1. Fetch data & 2. Build binary event matrix
    for ticker in tickers:
        hist = fetch_price_history(ticker, period="1y")
        if hist is None or len(hist) < 21:
            continue
            
        events = pd.DataFrame(index=hist.index)
        
        # price_up: close > open
        events[f"{ticker}_price_up"] = hist['Close'] > hist['Open']
        
        # volume_spike: volume > rolling_mean_20 * 1.5
        vol_ma = hist['Volume'].rolling(window=20).mean()
        events[f"{ticker}_volume_spike"] = hist['Volume'] > (vol_ma * 1.5)
        
        # high_volatility: abs(daily_return) > 0.02
        daily_ret = hist['Close'].pct_change()
        events[f"{ticker}_high_vol"] = daily_ret.abs() > 0.02
        
        # Join into all_events
        if all_events.empty:
            all_events = events
        else:
            all_events = all_events.join(events, how='outer')
            
    if all_events.empty:
        return {"rules": [], "total_rules": 0, "message": "Failed to fetch data or calculate events for the provided tickers."}
        
    # Drop rows with NaNs (from rolling mean)
    all_events = all_events.dropna()
    
    # Convert to boolean for apriori
    all_events = all_events.astype(bool)
    
    if len(all_events.columns) == 0:
        return {"rules": [], "total_rules": 0, "message": "No valid event columns generated."}
        
    try:
        # 3. Run apriori
        frequent_itemsets = apriori(all_events, min_support=min_support, use_colnames=True)
        
        if frequent_itemsets.empty:
            return {"rules": [], "total_rules": 0, "message": f"No frequent itemsets found with min_support={min_support}"}
            
        # Run association_rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        if rules.empty:
            return {"rules": [], "total_rules": 0, "message": f"No rules found with min_confidence={min_confidence}"}
            
        # 4. Format results
        formatted_rules = []
        for _, row in rules.iterrows():
            formatted_rules.append({
                "antecedents": list(row['antecedents']),
                "consequents": list(row['consequents']),
                "support": float(row['support']),
                "confidence": float(row['confidence']),
                "lift": float(row['lift'])
            })
            
        # Sort by lift descending
        formatted_rules = sorted(formatted_rules, key=lambda x: x['lift'], reverse=True)
            
        return {
            "rules": formatted_rules,
            "total_rules": len(formatted_rules)
        }
    except Exception as e:
        return {"rules": [], "total_rules": 0, "error": f"Error running association rules: {str(e)}"}
