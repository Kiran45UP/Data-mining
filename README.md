# StockMind Data Mining Platform

A comprehensive full-stack platform for fundamental stock analysis, unsupervised machine learning pattern discovery, and quantitative strategy backtesting.

## Tech Stack
- **Backend:** FastAPI (Python), yfinance, scikit-learn, mlxtend, statsmodels, SQLAlchemy (SQLite)
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts

## Setup Instructions

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   The backend will run on `http://localhost:8000`. The SQLite database will be created automatically on the first run.

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be accessible at `http://localhost:5173`.

## Features
1. **Fundamental Analysis:** Search any stock ticker to view its key ratios and historical financial statements.
2. **Pattern Discovery:** 
   - K-Means Clustering on financial metrics.
   - Apriori Association Rules mining to find patterns between price changes and volume spikes.
   - Isolation Forest anomaly detection for abnormal price movements.
3. **Strategy Backtesting:** Test quantitative trading strategies (SMA Crossover, RSI) against historical price data with dynamic parameters and visual results.
