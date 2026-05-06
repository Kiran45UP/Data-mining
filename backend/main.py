from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import datetime
import json

from database import engine, Base, get_db, Stock, PriceHistory, BacktestResult
from data_fetcher import fetch_stock_info, fetch_financials, fetch_price_history
from mining.clustering import run_clustering
from mining.association_rules import run_association_rules
from mining.anomaly_detection import detect_anomalies
from backtesting.strategies import SMAStrategy, RSIStrategy
from backtesting.engine import BacktestEngine

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
