from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import datetime
import json
import pandas as pd

from database import engine, Base, get_db, Stock, PriceHistory, BacktestResult
from data_fetcher import fetch_stock_info, fetch_financials, fetch_price_history
from mining.clustering import run_clustering
from mining.association_rules import run_association_rules
from mining.anomaly_detection import detect_anomalies
from backtesting.strategies import SMAStrategy, RSIStrategy
from backtesting.engine import BacktestEngine
from backtesting.signal_converters import (
    AnomalySignalConverter, ClusteringSignalConverter, 
    AssociationSignalConverter, SignalAggregator
)
from backtesting.validation_engine import StrategyValidator, MultiModuleValidator

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StockMind API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ClusterRequest(BaseModel):
    tickers: List[str]
    features: List[str]
    n_clusters: int

class AssociationRequest(BaseModel):
    tickers: List[str]
    min_support: float
    min_confidence: float

class BacktestRequest(BaseModel):
    ticker: str
    strategy: str
    params: Dict[str, Any]
    start_date: str
    end_date: str
    initial_capital: float


class UnifiedStrategyRequest(BaseModel):
    """Request for unified strategy validation"""
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    hold_days: int = 5
    modules: Dict[str, Any]  # {"anomaly": {config}, "clustering": {config}, "association": {config}}
    aggregation_method: str = "weighted"  # "weighted", "unanimous", "majority"
    custom_rules: Optional[Dict[str, Any]] = None


class CombinedSignalRequest(BaseModel):
    """Request for combined multi-module signals"""
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 10000.0
    hold_days: int = 5
    rule_config: Dict[str, Any]  # {"condition": "AND"/"OR", "requirements": [...]}
    modules: Dict[str, Any]  # Module configurations

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/fundamental/{ticker}")
def get_fundamental(ticker: str, db: Session = Depends(get_db)):
    info = fetch_stock_info(ticker)
    if not info or not info.get("name"):
        raise HTTPException(status_code=404, detail=f"Data for {ticker} not found")
        
    # Save to db
    db_stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not db_stock:
        db_stock = Stock(
            ticker=ticker,
            name=info.get("name"),
            sector=info.get("sector"),
            fetched_at=datetime.datetime.now().isoformat()
        )
        db.add(db_stock)
        db.commit()
        
    return info

@app.get("/api/fundamental/{ticker}/statements")
def get_statements(ticker: str):
    data = fetch_financials(ticker)
    return data

@app.post("/api/patterns/cluster")
def cluster_stocks(req: ClusterRequest):
    result = run_clustering(req.tickers, req.features, req.n_clusters)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/patterns/association")
def association_rules(req: AssociationRequest):
    result = run_association_rules(req.tickers, req.min_support, req.min_confidence)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/api/patterns/anomalies/{ticker}")
def get_anomalies(ticker: str, period: str = Query("1y")):
    result = detect_anomalies(ticker, period)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/api/backtest/strategies")
def list_strategies():
    return {
        "strategies": [
            {
                "id": "sma_crossover",
                "name": "SMA Crossover",
                "description": "Simple Moving Average crossover strategy.",
                "params": [
                    {"name": "fast_period", "type": "int", "default": 20},
                    {"name": "slow_period", "type": "int", "default": 50}
                ]
            },
            {
                "id": "rsi_strategy",
                "name": "RSI Strategy",
                "description": "Relative Strength Index strategy.",
                "params": [
                    {"name": "period", "type": "int", "default": 14},
                    {"name": "overbought", "type": "int", "default": 70},
                    {"name": "oversold", "type": "int", "default": 30}
                ]
            }
        ]
    }

@app.post("/api/backtest/run")
def run_backtest(req: BacktestRequest, db: Session = Depends(get_db)):
    # 1. Fetch data
    # Calculate an appropriate period based on start_date and end_date or just use yf.download with dates
    import yfinance as yf
    try:
        data = yf.download(req.ticker, start=req.start_date, end=req.end_date, progress=False)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No price data found for {req.ticker} between {req.start_date} and {req.end_date}")
            
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
        
    # 2. Instantiate strategy
    strategy = None
    if req.strategy == "sma_crossover":
        strategy = SMAStrategy(
            fast_period=req.params.get("fast_period", 20),
            slow_period=req.params.get("slow_period", 50)
        )
    elif req.strategy == "rsi_strategy":
        strategy = RSIStrategy(
            period=req.params.get("period", 14),
            overbought=req.params.get("overbought", 70),
            oversold=req.params.get("oversold", 30)
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {req.strategy}")
        
    # 3. Run backtest
    engine = BacktestEngine(data, strategy, initial_capital=req.initial_capital)
    result = engine.run()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # 4. Save to db
    db_result = BacktestResult(
        ticker=req.ticker,
        strategy=req.strategy,
        params=json.dumps(req.params),
        total_return=result.get("total_return"),
        sharpe_ratio=result.get("sharpe_ratio"),
        max_drawdown=result.get("max_drawdown"),
        win_rate=result.get("win_rate"),
        trades=json.dumps(result.get("trades", [])),
        run_at=datetime.datetime.now().isoformat()
    )
    db.add(db_result)
    db.commit()
    
    return result


@app.post("/api/backtest/unified-strategy")
def validate_unified_strategy(req: UnifiedStrategyRequest):
    """
    Validate unified strategy using signals from multiple modules
    """
    import yfinance as yf
    
    try:
        # Fetch price data with requested dates
        data = yf.download(req.ticker, start=req.start_date, end=req.end_date, progress=False)
        if data.empty:
            raise Exception(f"No price data for {req.ticker}")
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
        
        # Collect signals from each module
        all_signals = []
        
        # Anomaly Detection - use the price data directly instead of fetching again
        if req.modules.get('anomaly', {}).get('enabled'):
            anomaly_config = req.modules['anomaly']
            
            # Compute anomalies on the existing data
            from sklearn.ensemble import IsolationForest
            import numpy as np
            
            hist = data.reset_index()
            hist.columns = ['Date' if c == 'index' else c for c in hist.columns]
            hist['daily_return'] = hist['Close'].pct_change().fillna(0)
            
            X = hist['daily_return'].values.reshape(-1, 1)
            clf = IsolationForest(contamination=0.05, random_state=42)
            clf.fit(X)
            labels = clf.predict(X)
            scores = clf.decision_function(X)
            
            # Format results
            data_points = []
            for i, idx in enumerate(hist.index):
                is_anomaly = bool(labels[i] == -1)
                data_points.append({
                    "date": hist['Date'].iloc[i].strftime('%Y-%m-%d'),
                    "close": float(hist['Close'].iloc[i]),
                    "daily_return": float(hist['daily_return'].iloc[i]),
                    "is_anomaly": is_anomaly,
                    "anomaly_score": float(scores[i])
                })
            
            anomaly_result = {
                "ticker": req.ticker,
                "data": data_points,
                "anomaly_count": sum(1 for p in data_points if p['is_anomaly']),
                "total_days": len(data_points)
            }
            
            signals = AnomalySignalConverter.convert(
                anomaly_result, 
                zscore_threshold=anomaly_config.get('zscore_threshold', 2.0)
            )
            all_signals.extend(signals)
        
        # Association Rules
        if req.modules.get('association', {}).get('enabled'):
            assoc_config = req.modules['association']
            tickers = [req.ticker]
            
            assoc_result = run_association_rules(
                tickers,
                min_support=assoc_config.get('min_support', 0.1),
                min_confidence=assoc_config.get('min_confidence', 0.6)
            )
            
            if 'error' not in assoc_result and assoc_result.get('rules'):
                # Use the middle date of the period as a representative
                start = pd.Timestamp(req.start_date)
                end = pd.Timestamp(req.end_date)
                mid_date = (start + (end - start) // 2).strftime('%Y-%m-%d')
                
                signals_dict = AssociationSignalConverter.convert(
                    assoc_result, 
                    confidence_threshold=assoc_config.get('min_confidence', 0.6),
                    date=mid_date
                )
                for ticker, signals in signals_dict.items():
                    all_signals.extend(signals)
        
        # Filter for current ticker
        ticker_signals = [s for s in all_signals if s.ticker == req.ticker]
        
        if not ticker_signals:
            return {
                "error": "No signals generated from selected modules",
                "message": "Try enabling different modules or adjusting their thresholds"
            }
        
        # Aggregate signals
        aggregated = SignalAggregator.aggregate_signals(
            ticker_signals,
            aggregation_method=req.aggregation_method
        )
        
        # Convert to validation format
        signals_dict = {}
        for (date, ticker_key), agg_signal in aggregated.items():
            signals_dict[(date, ticker_key)] = agg_signal
        
        # Validate against historical data
        validator = StrategyValidator(data, req.initial_capital)
        result = validator.validate(signals_dict, req.hold_days)
        
        result['modules_used'] = list(req.modules.keys())
        result['aggregation_method'] = req.aggregation_method
        result['aggregated_signals'] = list(aggregated.values())
        
        return result
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=error_msg)


@app.post("/api/backtest/combined-signals")
def validate_combined_signals(req: CombinedSignalRequest):
    """
    Validate trading signals using combined multi-module approach with custom rules
    Example rule_config: {
        "condition": "AND",
        "requirements": [
            {"source": "anomaly", "signal": "BUY", "min_confidence": 0.5},
            {"source": "association", "signal": "BUY", "min_confidence": 0.6}
        ]
    }
    """
    import yfinance as yf
    
    try:
        # Fetch price data
        data = yf.download(req.ticker, start=req.start_date, end=req.end_date, progress=False)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No price data for {req.ticker}")
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
        
        # Collect signals from each module
        all_signals = []
        
        # Anomaly Detection
        if req.modules.get('anomaly', {}).get('enabled'):
            anomaly_config = req.modules['anomaly']
            anomaly_result = detect_anomalies(req.ticker, period=anomaly_config.get('period', '1y'))
            if 'error' not in anomaly_result:
                signals = AnomalySignalConverter.convert(
                    anomaly_result,
                    zscore_threshold=anomaly_config.get('zscore_threshold', 2.0)
                )
                all_signals.extend(signals)
        
        # Clustering
        if req.modules.get('clustering', {}).get('enabled'):
            cluster_config = req.modules['clustering']
            tickers = cluster_config.get('tickers', [req.ticker])
            if tickers:
                cluster_result = run_clustering(
                    tickers,
                    features=cluster_config.get('features', ['pe_ratio', 'market_cap']),
                    n_clusters=cluster_config.get('n_clusters', 3)
                )
                if 'error' not in cluster_result:
                    signals_dict = ClusteringSignalConverter.convert(cluster_result)
                    for ticker, signals in signals_dict.items():
                        all_signals.extend(signals)
        
        # Association Rules
        if req.modules.get('association', {}).get('enabled'):
            assoc_config = req.modules['association']
            tickers = assoc_config.get('tickers', [req.ticker])
            if tickers:
                assoc_result = run_association_rules(
                    tickers,
                    min_support=assoc_config.get('min_support', 0.1),
                    min_confidence=assoc_config.get('min_confidence', 0.6)
                )
                if 'error' not in assoc_result:
                    signals_dict = AssociationSignalConverter.convert(assoc_result)
                    for ticker, signals in signals_dict.items():
                        all_signals.extend(signals)
        
        # Filter for current ticker
        ticker_signals = [s for s in all_signals if s.ticker == req.ticker]
        
        if not ticker_signals:
            return {
                "error": "No signals generated from selected modules"
            }
        
        # Aggregate signals first
        aggregated = SignalAggregator.aggregate_signals(ticker_signals, aggregation_method='weighted')
        
        # Convert to validation format
        signals_dict = {}
        for (date, ticker), agg_signal in aggregated.items():
            signals_dict[(date, ticker)] = agg_signal
        
        # Apply custom rules and validate
        validator = MultiModuleValidator(data)
        result = validator.validate_with_rules(
            signals_dict,
            req.rule_config,
            req.hold_days,
            req.initial_capital
        )
        
        result['rule_config'] = req.rule_config
        result['aggregated_signals'] = list(aggregated.values())
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@app.get("/api/backtest/strategy-templates")
def get_strategy_templates():
    """Get templates for different unified strategies"""
    return {
        "templates": [
            {
                "id": "anomaly_only",
                "name": "Anomaly Detection Strategy",
                "description": "Trades based on price anomalies (z-score)",
                "modules": {
                    "anomaly": {
                        "enabled": True,
                        "period": "1y",
                        "zscore_threshold": 2.0
                    },
                    "clustering": {"enabled": False},
                    "association": {"enabled": False}
                }
            },
            {
                "id": "combined_conservative",
                "name": "Conservative Combined Strategy",
                "description": "Buy only when multiple modules agree",
                "rule_config": {
                    "condition": "AND",
                    "requirements": [
                        {"source": "anomaly", "signal": "BUY", "min_confidence": 0.5},
                        {"source": "association", "signal": "BUY", "min_confidence": 0.6}
                    ]
                }
            },
            {
                "id": "combined_aggressive",
                "name": "Aggressive Combined Strategy",
                "description": "Buy if any module generates strong signal",
                "rule_config": {
                    "condition": "OR",
                    "requirements": [
                        {"source": "anomaly", "signal": "BUY", "min_confidence": 0.7},
                        {"source": "association", "signal": "BUY", "min_confidence": 0.7},
                        {"source": "clustering", "signal": "BUY", "min_confidence": 0.7}
                    ]
                }
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
