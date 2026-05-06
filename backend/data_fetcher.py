import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

def fetch_stock_info(ticker: str) -> Dict[str, Any]:
    """Fetch fundamental information for a stock."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "roe": info.get("returnOnEquity"),
            "debt_equity": info.get("debtToEquity"),
            "fcf": info.get("freeCashflow"),
            "net_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "dividend_yield": info.get("dividendYield"),
            "description": info.get("longBusinessSummary")
        }
    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {
            "ticker": ticker,
            "name": None,
            "sector": None,
            "market_cap": None,
            "pe_ratio": None,
            "eps": None,
            "roe": None,
            "debt_equity": None,
            "fcf": None,
            "net_margin": None,
            "revenue_growth": None,
            "dividend_yield": None,
            "description": None
        }

def fetch_price_history(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch price history for a stock."""
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            return None
            
        # In newer yfinance versions with multi-index columns, we might need to flatten it
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            
        return data
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return None

def fetch_financials(ticker: str) -> Dict[str, Any]:
    """Fetch income statement and balance sheet."""
    try:
        stock = yf.Ticker(ticker)
        
        # Get financials and balance sheet, transpose to have dates as rows
        inc_stmt = stock.financials.transpose().reset_index()
        bal_sheet = stock.balance_sheet.transpose().reset_index()
        
        # Convert date column to string for JSON serialization
        if not inc_stmt.empty and 'index' in inc_stmt.columns:
            inc_stmt = inc_stmt.rename(columns={'index': 'Date'})
            inc_stmt['Date'] = inc_stmt['Date'].dt.strftime('%Y-%m-%d')
            
        if not bal_sheet.empty and 'index' in bal_sheet.columns:
            bal_sheet = bal_sheet.rename(columns={'index': 'Date'})
            bal_sheet['Date'] = bal_sheet['Date'].dt.strftime('%Y-%m-%d')
            
        # Take up to 3 years
        inc_stmt_dict = inc_stmt.head(3).to_dict(orient='records') if not inc_stmt.empty else []
        bal_sheet_dict = bal_sheet.head(3).to_dict(orient='records') if not bal_sheet.empty else []
        
        # Clean up NaN values for JSON serialization
        import math
        def clean_dict(d):
            return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in d.items()}
            
        inc_stmt_dict = [clean_dict(d) for d in inc_stmt_dict]
        bal_sheet_dict = [clean_dict(d) for d in bal_sheet_dict]
        
        return {
            "income_statement": inc_stmt_dict,
            "balance_sheet": bal_sheet_dict
        }
    except Exception as e:
        print(f"Error fetching financials for {ticker}: {e}")
        return {
            "income_statement": [],
            "balance_sheet": []
        }
