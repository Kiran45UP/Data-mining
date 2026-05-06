import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path to allow imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_fetcher import fetch_stock_info

def run_clustering(tickers: List[str], features: List[str], n_clusters: int) -> Dict[str, Any]:
    """Run K-Means clustering on the given tickers based on selected features."""
    if not tickers or not features:
        return {"error": "Tickers and features must be provided"}
    
    if len(tickers) < n_clusters:
        return {"error": f"Number of tickers ({len(tickers)}) must be >= number of clusters ({n_clusters})"}

    data_list = []
    valid_tickers = []
    
    # 1. Fetch data
    for ticker in tickers:
        info = fetch_stock_info(ticker)
        if info:
            row = [info.get(feature) for feature in features]
            data_list.append(row)
            valid_tickers.append(ticker)
            
    if not valid_tickers:
        return {"error": "Failed to fetch data for the provided tickers."}
        
    # 2. Build feature matrix and fill NaN with column mean
    df = pd.DataFrame(data_list, columns=features)
    df = df.apply(pd.to_numeric, errors='coerce') # Ensure all are numeric
    df = df.fillna(df.mean())
    
    # Check if there are still NaNs (e.g. if an entire column was NaN)
    df = df.fillna(0)
    
    # 3. Normalize
    scaler = StandardScaler()
    try:
        X_scaled = scaler.fit_transform(df)
    except Exception as e:
        return {"error": f"Scaling failed: {e}"}
        
    # 4. Run KMeans
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
    except Exception as e:
        return {"error": f"Clustering failed: {e}"}
        
    # 5. Compute silhouette score (needs >= 2 clusters and >= 2 samples)
    sil_score = None
    if n_clusters > 1 and len(valid_tickers) > 1 and len(set(labels)) > 1:
        sil_score = float(silhouette_score(X_scaled, labels))
        
    # 6. Format results
    clusters = []
    for i, ticker in enumerate(valid_tickers):
        feature_values = {feat: float(df.iloc[i][feat]) if not pd.isna(df.iloc[i][feat]) else None for feat in features}
        clusters.append({
            "ticker": ticker,
            "cluster_id": int(labels[i]),
            "feature_values": feature_values
        })
        
    return {
        "clusters": clusters,
        "silhouette_score": sil_score,
        "cluster_centers": [list(center) for center in kmeans.cluster_centers_],
        "inertia": float(kmeans.inertia_)
    }
