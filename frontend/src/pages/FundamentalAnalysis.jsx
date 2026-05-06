import { useState } from 'react';
import { Search, TrendingUp, TrendingDown, DollarSign, Building2, Globe } from 'lucide-react';
import { getFundamental, getStatements } from '../services/api';
import TickerMultiSelect from '../components/TickerMultiSelect';

const FundamentalAnalysis = () => {
  const [tickers, setTickers] = useState(['AAPL']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [data, setData] = useState(null);
  const [statements, setStatements] = useState(null);
  const [activeTab, setActiveTab] = useState('income');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (tickers.length === 0) {
      setError('Please add at least one ticker.');
      return;
    }

    const tickerToLoad = tickers[0].trim().toUpperCase();
    if (!tickerToLoad) {
      setError('Please add at least one ticker.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const fundData = await getFundamental(tickerToLoad);
      const stmtData = await getStatements(tickerToLoad);
      setData(fundData);
      setStatements(stmtData);
    } catch (err) {
      setError(err.message);
      setData(null);
      setStatements(null);
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (val, isPercent = false, isCurrency = false) => {
    if (val === null || val === undefined) return 'N/A';
    if (isPercent) return `${(val * 100).toFixed(2)}%`;
    if (isCurrency) {
      if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
      if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
      return `$${val.toLocaleString()}`;
    }
    return typeof val === 'number' ? val.toFixed(2) : val;
  };

  const MetricCard = ({ title, value, isGood, isPercent, isCurrency }) => {
    const formatted = formatValue(value, isPercent, isCurrency);
    const colorClass = formatted === 'N/A' ? 'text-gray-400' 
      : isGood === undefined ? 'text-white'
      : isGood ? 'text-green-400' : 'text-red-400';

    return (
      <div className="card p-5 bg-dark-surface/50 border-gray-800/50 hover:border-gray-700 transition-colors">
        <p className="text-sm text-gray-400 mb-1">{title}</p>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-mono font-bold ${colorClass}`}>
            {formatted}
          </span>
          {isGood !== undefined && formatted !== 'N/A' && (
            isGood ? <TrendingUp className="w-4 h-4 text-green-400" /> : <TrendingDown className="w-4 h-4 text-red-400" />
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Search Bar */}
      <div className="card p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold mb-1">Stock Fundamentals</h2>
          <p className="text-sm text-gray-400">Search any ticker to view key metrics and financials.</p>
        </div>
        <form onSubmit={handleSearch} className="flex flex-col gap-4 w-full md:w-[560px]">
          <TickerMultiSelect
            label="Tickers"
            items={tickers}
            setItems={setTickers}
            placeholder="Type or select a ticker"
            helperText="Use the dropdown or enter a ticker code and press Add. The first selected ticker will be analyzed."
            required
          />
          <button type="submit" disabled={loading} className="btn-primary whitespace-nowrap self-start">
            {loading ? 'Searching...' : 'Analyze'}
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 flex items-center gap-3">
          <TrendingDown className="w-5 h-5" /> {error}
        </div>
      )}

      {data && (
        <div className="space-y-6 animate-fade-in">
          {/* Company Header */}
          <div className="card p-6 border-t-4 border-t-accent">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h1 className="text-3xl font-bold text-white">{data.name} <span className="text-gray-500 text-xl font-normal ml-2">{data.ticker}</span></h1>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                  <span className="flex items-center gap-1"><Building2 className="w-4 h-4"/> {data.sector || 'Unknown'}</span>
                  <span className="flex items-center gap-1"><Globe className="w-4 h-4"/> Market Cap: {formatValue(data.market_cap, false, true)}</span>
                </div>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-300 leading-relaxed line-clamp-3 hover:line-clamp-none cursor-pointer transition-all">
              {data.description}
            </p>
          </div>

          {/* Key Metrics Grid */}
          <h3 className="text-lg font-semibold text-gray-200 pl-1">Key Ratios</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard title="P/E Ratio" value={data.pe_ratio} isGood={data.pe_ratio > 0 && data.pe_ratio < 25} />
            <MetricCard title="EPS (TTM)" value={data.eps} isGood={data.eps > 0} />
            <MetricCard title="Return on Equity" value={data.roe} isPercent isGood={data.roe > 0.15} />
            <MetricCard title="Debt to Equity" value={data.debt_equity} isGood={data.debt_equity < 100} />
            <MetricCard title="Free Cash Flow" value={data.fcf} isCurrency isGood={data.fcf > 0} />
            <MetricCard title="Net Margin" value={data.net_margin} isPercent isGood={data.net_margin > 0.1} />
            <MetricCard title="Revenue Growth" value={data.revenue_growth} isPercent isGood={data.revenue_growth > 0} />
            <MetricCard title="Dividend Yield" value={data.dividend_yield} isPercent isGood={data.dividend_yield > 0} />
          </div>

          {/* Financial Statements */}
          {statements && (
            <div className="card overflow-hidden">
              <div className="flex border-b border-gray-800">
                <button
                  className={`flex-1 py-4 text-center font-medium transition-colors ${activeTab === 'income' ? 'text-accent border-b-2 border-accent bg-accent/5' : 'text-gray-400 hover:text-gray-200 hover:bg-dark-surfaceHover'}`}
                  onClick={() => setActiveTab('income')}
                >
                  Income Statement
                </button>
                <button
                  className={`flex-1 py-4 text-center font-medium transition-colors ${activeTab === 'balance' ? 'text-secondary border-b-2 border-secondary bg-secondary/5' : 'text-gray-400 hover:text-gray-200 hover:bg-dark-surfaceHover'}`}
                  onClick={() => setActiveTab('balance')}
                >
                  Balance Sheet
                </button>
              </div>
              
              <div className="p-0 overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-300">
                  <thead className="text-xs uppercase bg-dark-surfaceHover text-gray-400 border-b border-gray-800">
                    <tr>
                      <th className="px-6 py-4 font-semibold">Metric</th>
                      {(activeTab === 'income' ? statements.income_statement : statements.balance_sheet)?.map((col, idx) => (
                        <th key={idx} className="px-6 py-4 font-semibold">{col.Date}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/50">
                    {(() => {
                      const dataArr = activeTab === 'income' ? statements.income_statement : statements.balance_sheet;
                      if (!dataArr || dataArr.length === 0) return <tr><td colSpan="4" className="p-6 text-center text-gray-500">No data available</td></tr>;
                      
                      const keys = Object.keys(dataArr[0]).filter(k => k !== 'Date');
                      return keys.map((key, i) => (
                        <tr key={i} className="hover:bg-dark-surfaceHover/50 transition-colors">
                          <td className="px-6 py-3 font-medium text-gray-200">{key}</td>
                          {dataArr.map((col, idx) => (
                            <td key={idx} className="px-6 py-3 font-mono">
                              {col[key] === null ? '-' : formatValue(col[key], false, true)}
                            </td>
                          ))}
                        </tr>
                      ));
                    })()}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
      
      {!data && !loading && !error && (
        <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-800 rounded-xl text-gray-500">
          <Search className="w-12 h-12 mb-3 text-gray-600" />
          <p>Search for a ticker to see fundamental data</p>
        </div>
      )}
    </div>
  );
};

export default FundamentalAnalysis;
