import { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Zap, ActivitySquare, Target, Hash, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { validateUnifiedStrategy } from '../services/api';
import TickerMultiSelect from '../components/TickerMultiSelect';

const Backtesting = () => {
  // State
  const [tickers, setTickers] = useState(['AAPL']);
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [initialCapital, setInitialCapital] = useState(10000);
  const [holdDays, setHoldDays] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  
  // Module configs
  const [anomalyEnabled, setAnomalyEnabled] = useState(true);
  const [anomalyThreshold, setAnomalyThreshold] = useState(2.0);
  
  const [associationEnabled, setAssociationEnabled] = useState(false);
  const [associationConfidence, setAssociationConfidence] = useState(0.6);
  
  const [aggregationMethod, setAggregationMethod] = useState('weighted');
  
  // Run validation
  const handleRun = async () => {
    if (!tickers || tickers.length === 0) {
      setError('Please select a ticker');
      return;
    }
    
    if (!anomalyEnabled && !associationEnabled) {
      setError('Please enable at least one module');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const moduleConfigs = {
        anomaly: {
          enabled: anomalyEnabled,
          period: '1y',
          zscore_threshold: anomalyThreshold
        },
        clustering: { enabled: false },
        association: {
          enabled: associationEnabled,
          min_support: 0.1,
          min_confidence: associationConfidence,
          tickers: [tickers[0].toUpperCase()]
        }
      };
      
      const res = await validateUnifiedStrategy({
        ticker: tickers[0].toUpperCase(),
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital,
        hold_days: holdDays,
        modules: moduleConfigs,
        aggregation_method: aggregationMethod
      });
      
      setResult(res);
    } catch (err) {
      setError(err.message || 'Validation failed');
    } finally {
      setLoading(false);
    }
  };
  
  // Metric card component
  const MetricCard = ({ title, value, icon: Icon, isPercent, isCurrency, colorClass }) => (
    <div className="bg-dark-bg border border-gray-800 p-4 rounded-xl flex items-center gap-4">
      <div className={`p-3 rounded-lg bg-dark-surface ${colorClass}`}>
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <p className="text-sm text-gray-400">{title}</p>
        <h4 className={`text-xl font-bold ${colorClass.includes('text-white') ? 'text-white' : colorClass}`}>
          {isCurrency ? '$' : ''}{value}{isPercent ? '%' : ''}
        </h4>
      </div>
    </div>
  );

  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-6">
      
      {/* LEFT PANEL - CONFIG */}
      <div className="card p-6 h-fit sticky top-24">
        <h2 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-accent" /> Unified Signals
        </h2>
        
        <div className="space-y-5">
          {/* Ticker Selection */}
          <div>
            <TickerMultiSelect
              label="Ticker"
              items={tickers}
              setItems={setTickers}
              placeholder="Select ticker"
              required
            />
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Start Date</label>
              <input type="date" className="input-field w-full text-sm" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">End Date</label>
              <input type="date" className="input-field w-full text-sm" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
          </div>

          {/* Capital & Hold Days */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Capital ($)</label>
              <input type="number" className="input-field w-full text-sm" value={initialCapital} onChange={(e) => setInitialCapital(parseFloat(e.target.value))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Hold Days</label>
              <input type="number" className="input-field w-full text-sm" value={holdDays} onChange={(e) => setHoldDays(parseInt(e.target.value))} min="1" />
            </div>
          </div>

          {/* Modules Section */}
          <div className="border-t border-gray-800 pt-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Modules</h3>
            
            {/* Anomaly Detection */}
            <div className="mb-3 p-3 bg-dark-bg rounded border border-gray-800">
              <label className="flex items-center gap-2 text-sm text-gray-300 mb-2 cursor-pointer">
                <input type="checkbox" checked={anomalyEnabled} onChange={() => setAnomalyEnabled(!anomalyEnabled)} />
                <span>Z-Score Anomaly</span>
              </label>
              {anomalyEnabled && (
                <div className="ml-6 space-y-2">
                  <div>
                    <label className="text-xs text-gray-500">Threshold</label>
                    <input type="number" step="0.5" className="input-field w-full text-xs py-1" value={anomalyThreshold} onChange={(e) => setAnomalyThreshold(parseFloat(e.target.value))} />
                  </div>
                  <p className="text-xs text-gray-500">BUY when z-score &lt; -{anomalyThreshold}</p>
                </div>
              )}
            </div>

            {/* Association Rules */}
            <div className="p-3 bg-dark-bg rounded border border-gray-800">
              <label className="flex items-center gap-2 text-sm text-gray-300 mb-2 cursor-pointer">
                <input type="checkbox" checked={associationEnabled} onChange={() => setAssociationEnabled(!associationEnabled)} />
                <span>Association Rules</span>
              </label>
              {associationEnabled && (
                <div className="ml-6 space-y-2">
                  <div>
                    <label className="text-xs text-gray-500">Min Confidence</label>
                    <input type="number" step="0.05" className="input-field w-full text-xs py-1" value={associationConfidence} onChange={(e) => setAssociationConfidence(parseFloat(e.target.value))} min="0" max="1" />
                  </div>
                  <p className="text-xs text-gray-500">Pattern confidence threshold</p>
                </div>
              )}
            </div>
          </div>

          {/* Aggregation Method */}
          <div className="border-t border-gray-800 pt-4">
            <label className="block text-sm font-medium text-gray-400 mb-2">Aggregation Method</label>
            <select className="input-field w-full text-sm" value={aggregationMethod} onChange={(e) => setAggregationMethod(e.target.value)}>
              <option value="weighted">Weighted Average</option>
              <option value="majority">Majority Vote</option>
              <option value="unanimous">Unanimous</option>
            </select>
            <p className="text-xs text-gray-500 mt-2">How to combine signals from multiple modules</p>
          </div>

          {/* Run Button */}
          <button onClick={handleRun} disabled={loading} className="btn-primary w-full flex justify-center items-center gap-2 mt-4">
            {loading ? <ActivitySquare className="w-5 h-5 animate-pulse" /> : <Play className="w-5 h-5" />}
            {loading ? 'Validating...' : 'Validate Strategy'}
          </button>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500 rounded p-3 flex gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT PANEL - RESULTS */}
      <div className="card p-6 overflow-hidden flex flex-col">
        {!result && !loading && (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <ActivitySquare className="w-20 h-20 mb-4 opacity-30 text-accent" />
            <h3 className="text-xl font-medium text-gray-400">No Results Yet</h3>
            <p className="mt-2 text-center">Configure your modules and run validation to see performance metrics.</p>
          </div>
        )}

        {loading && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <ActivitySquare className="w-16 h-16 text-accent animate-spin mx-auto mb-4" />
              <p className="text-accent text-lg font-medium">Running validation...</p>
            </div>
          </div>
        )}

        {result && (
          <div className="h-full flex flex-col overflow-y-auto pr-2 space-y-6">
            <h2 className="text-2xl font-bold mb-4 text-white">Validation Results</h2>
            
            {result.error ? (
              <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 flex gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-400">{result.error}</p>
                  {result.message && <p className="text-sm text-red-300 mt-1">{result.message}</p>}
                </div>
              </div>
            ) : (
              <>
                {/* Primary Metrics */}
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  <MetricCard title="Total Return" value={result.total_return} isPercent icon={TrendingUp} colorClass={result.total_return >= 0 ? 'text-green-400' : 'text-red-400'} />
                  <MetricCard title="Win Rate" value={result.win_rate} isPercent icon={Target} colorClass={result.win_rate >= 50 ? 'text-green-400' : 'text-orange-400'} />
                  <MetricCard title="Avg Return" value={result.avg_return} isPercent icon={ActivitySquare} colorClass={result.avg_return >= 0 ? 'text-blue-400' : 'text-orange-400'} />
                  <MetricCard title="Max Gain" value={result.max_gain} isCurrency icon={TrendingUp} colorClass="text-green-400" />
                  <MetricCard title="Max Loss" value={result.max_loss} isCurrency icon={TrendingDown} colorClass="text-red-400" />
                  <MetricCard title="Total Trades" value={result.total_trades} icon={Hash} colorClass="text-white" />
                </div>

                {/* Secondary Metrics */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  <div className="bg-dark-bg border border-gray-800 p-3 rounded-lg">
                    <p className="text-xs text-gray-500">Annualized Return</p>
                    <p className="text-lg font-bold text-accent">{result.annualized_return}%</p>
                  </div>
                  <div className="bg-dark-bg border border-gray-800 p-3 rounded-lg">
                    <p className="text-xs text-gray-500">Sharpe Ratio</p>
                    <p className="text-lg font-bold text-purple-400">{result.sharpe_ratio}</p>
                  </div>
                  <div className="bg-dark-bg border border-gray-800 p-3 rounded-lg">
                    <p className="text-xs text-gray-500">Max Drawdown</p>
                    <p className="text-lg font-bold text-red-400">{result.max_drawdown}%</p>
                  </div>
                  <div className="bg-dark-bg border border-gray-800 p-3 rounded-lg">
                    <p className="text-xs text-gray-500">Final Equity</p>
                    <p className="text-lg font-bold text-green-400">${result.final_equity}</p>
                  </div>
                </div>

                {/* Equity Curve Chart */}
                {result.equity_curve && result.equity_curve.length > 0 && (
                  <div className="h-[300px] bg-dark-bg rounded-xl border border-gray-800 p-4">
                    <h3 className="text-sm font-medium text-gray-400 mb-2">Equity Curve</h3>
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={result.equity_curve} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00D4FF" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#00D4FF" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                        <XAxis dataKey="date" stroke="#9CA3AF" tick={{fontSize: 12}} minTickGap={30} />
                        <YAxis stroke="#9CA3AF" tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                        <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }} formatter={(value) => [`$${value.toFixed(0)}`, 'Equity']} />
                        <Area type="monotone" dataKey="equity" stroke="#00D4FF" fillOpacity={1} fill="url(#colorEquity)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Trade Log */}
                <div className="flex-1 min-h-[200px]">
                  <h3 className="text-lg font-bold mb-3 text-white">Trade Log</h3>
                  <div className="border border-gray-800 rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs text-gray-300">
                        <thead className="bg-dark-surface text-xs uppercase text-gray-400 border-b border-gray-800">
                          <tr>
                            <th className="px-4 py-3">Date</th>
                            <th className="px-4 py-3">Action</th>
                            <th className="px-4 py-3 text-right">Price</th>
                            <th className="px-4 py-3 text-right">Shares</th>
                            <th className="px-4 py-3 text-right">Days Held</th>
                            <th className="px-4 py-3 text-right">P&L</th>
                            <th className="px-4 py-3 text-right">Return %</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-800 bg-dark-bg">
                          {result.trades && result.trades.map((t, i) => (
                            <tr key={i} className="hover:bg-dark-surface/50">
                              <td className="px-4 py-3">{t.date}</td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs font-bold ${t.action === 'BUY' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                                  {t.action}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-right font-mono">${t.price?.toFixed(2) || 'N/A'}</td>
                              <td className="px-4 py-3 text-right font-mono">{t.shares || '-'}</td>
                              <td className="px-4 py-3 text-right font-mono">{t.days_held || '-'}</td>
                              <td className={`px-4 py-3 text-right font-mono font-bold ${t.pnl > 0 ? 'text-green-400' : t.pnl < 0 ? 'text-red-400' : 'text-gray-500'}`}>
                                {t.action === 'SELL' ? `${t.pnl > 0 ? '+' : ''}$${t.pnl?.toFixed(2) || '0'}` : '-'}
                              </td>
                              <td className={`px-4 py-3 text-right font-mono font-bold ${t.pnl_percent > 0 ? 'text-green-400' : t.pnl_percent < 0 ? 'text-red-400' : 'text-gray-500'}`}>
                                {t.pnl_percent ? `${t.pnl_percent > 0 ? '+' : ''}${t.pnl_percent.toFixed(2)}%` : '-'}
                              </td>
                            </tr>
                          ))}
                          {(!result.trades || result.trades.length === 0) && (
                            <tr><td colSpan="7" className="text-center py-6 text-gray-500">No trades executed</td></tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Backtesting;
