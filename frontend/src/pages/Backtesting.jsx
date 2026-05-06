import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Settings2, ActivitySquare, Target, Hash, TrendingUp, TrendingDown } from 'lucide-react';
import { getStrategies, runBacktest } from '../services/api';
import TickerMultiSelect from '../components/TickerMultiSelect';

const Backtesting = () => {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [tickers, setTickers] = useState(['AAPL']);
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate, setEndDate] = useState('2023-12-31');
  const [initialCapital, setInitialCapital] = useState(10000);
  const [params, setParams] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        const data = await getStrategies();
        setStrategies(data.strategies);
        if (data.strategies.length > 0) {
          handleStrategyChange(data.strategies[0].id, data.strategies);
        }
      } catch (err) {
        setError('Failed to load strategies');
      }
    };
    fetchStrategies();
  }, []);

  const handleStrategyChange = (stratId, strats = strategies) => {
    setSelectedStrategy(stratId);
    const strat = strats.find(s => s.id === stratId);
    if (strat) {
      const defaultParams = {};
      strat.params.forEach(p => {
        defaultParams[p.name] = p.default;
      });
      setParams(defaultParams);
    }
  };

  const handleParamChange = (name, value) => {
    setParams({ ...params, [name]: parseFloat(value) });
  };

  const handleRun = async () => {
    if (tickers.length === 0) {
      setError('Please select at least one ticker.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const res = await runBacktest({
        ticker: tickers[0].toUpperCase(),
        strategy: selectedStrategy,
        params,
        start_date: startDate,
        end_date: endDate,
        initial_capital: initialCapital
      });
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const activeStratDef = strategies.find(s => s.id === selectedStrategy);

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
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">
      {/* Strategy Builder Panel */}
      <div className="w-full lg:w-[400px] card p-6 overflow-y-auto flex-shrink-0">
        <h2 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
          <Settings2 className="w-5 h-5 text-accent" /> Strategy Builder
        </h2>

        <div className="space-y-5">
          <div>
            <TickerMultiSelect
              label="Tickers"
              items={tickers}
              setItems={setTickers}
              placeholder="Type or select a ticker"
              helperText="Backtesting uses the first selected ticker when running the simulation."
              required
            />
          </div>

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

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Initial Capital ($)</label>
            <input type="number" className="input-field w-full" value={initialCapital} onChange={(e) => setInitialCapital(parseFloat(e.target.value))} />
          </div>

          <div className="border-t border-gray-800 pt-5">
            <label className="block text-sm font-medium text-gray-400 mb-1">Select Strategy</label>
            <select 
              className="input-field w-full bg-dark-bg"
              value={selectedStrategy}
              onChange={(e) => handleStrategyChange(e.target.value)}
            >
              {strategies.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-2">{activeStratDef?.description}</p>
          </div>

          {activeStratDef?.params.length > 0 && (
            <div className="bg-dark-bg p-4 rounded-lg border border-gray-800">
              <h3 className="text-sm font-semibold text-gray-300 mb-3 border-b border-gray-800 pb-2">Parameters</h3>
              <div className="space-y-3">
                {activeStratDef.params.map(p => (
                  <div key={p.name} className="flex justify-between items-center">
                    <label className="text-sm text-gray-400 capitalize">{p.name.replace('_', ' ')}</label>
                    <input 
                      type="number" 
                      className="input-field w-24 py-1 text-sm text-right"
                      value={params[p.name] !== undefined ? params[p.name] : ''}
                      onChange={(e) => handleParamChange(p.name, e.target.value)}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <button onClick={handleRun} disabled={loading} className="btn-primary w-full flex justify-center items-center gap-2 mt-4">
            {loading ? <ActivitySquare className="w-5 h-5 animate-pulse" /> : <Play className="w-5 h-5" />}
            {loading ? 'Running Simulation...' : 'Run Backtest'}
          </button>
          {error && <p className="text-sm text-red-400 mt-2 text-center">{error}</p>}
        </div>
      </div>

      {/* Results Panel */}
      <div className="flex-1 card p-6 overflow-hidden flex flex-col">
        {!result && !loading && (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <ActivitySquare className="w-20 h-20 mb-4 opacity-30 text-accent" />
            <h3 className="text-xl font-medium text-gray-400">No Results Yet</h3>
            <p className="mt-2">Configure your strategy and run a backtest to view performance.</p>
          </div>
        )}

        {loading && (
          <div className="h-full flex items-center justify-center">
            <div className="text-accent text-xl font-medium animate-pulse">Running quantitative simulation...</div>
          </div>
        )}

        {result && (
          <div className="h-full flex flex-col animate-fade-in overflow-y-auto pr-2">
            <h2 className="text-xl font-bold mb-4 text-white">Backtest Results</h2>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              <MetricCard title="Total Return" value={result.total_return} isPercent icon={ActivitySquare} colorClass={result.total_return >= 0 ? 'text-green-400' : 'text-red-400'} />
              <MetricCard title="Annualized" value={result.annualized_return} isPercent icon={TrendingUp} colorClass="text-accent" />
              <MetricCard title="Win Rate" value={result.win_rate} isPercent icon={Target} colorClass={result.win_rate >= 50 ? 'text-green-400' : 'text-orange-400'} />
              <MetricCard title="Sharpe Ratio" value={result.sharpe_ratio} icon={TrendingUp} colorClass="text-purple-400" />
              <MetricCard title="Max Drawdown" value={result.max_drawdown} isPercent icon={TrendingDown} colorClass="text-red-400" />
              <MetricCard title="Total Trades" value={result.trade_count} icon={Hash} colorClass="text-white" />
            </div>

            {/* Chart */}
            <div className="h-[300px] w-full bg-dark-bg rounded-xl border border-gray-800 p-4 mb-6 flex-shrink-0">
              <h3 className="text-sm font-medium text-gray-400 mb-2">Equity Curve ($)</h3>
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
                  <YAxis domain={['auto', 'auto']} stroke="#9CA3AF" tickFormatter={(v) => `$${v}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                    formatter={(value) => [`$${value}`, 'Equity']}
                  />
                  <Area type="monotone" dataKey="equity" stroke="#00D4FF" fillOpacity={1} fill="url(#colorEquity)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Trade Log */}
            <div className="flex-1 min-h-[200px]">
              <h3 className="text-lg font-bold mb-3 text-white">Trade Log</h3>
              <div className="border border-gray-800 rounded-xl overflow-hidden h-full">
                <div className="overflow-y-auto max-h-[300px]">
                  <table className="w-full text-left text-sm text-gray-300">
                    <thead className="sticky top-0 bg-dark-surface text-xs uppercase text-gray-400 border-b border-gray-800">
                      <tr>
                        <th className="px-4 py-3">Date</th>
                        <th className="px-4 py-3">Action</th>
                        <th className="px-4 py-3 text-right">Price</th>
                        <th className="px-4 py-3 text-right">Shares</th>
                        <th className="px-4 py-3 text-right">P&L</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800 bg-dark-bg">
                      {result.trades.map((t, i) => (
                        <tr key={i} className="hover:bg-dark-surfaceHover">
                          <td className="px-4 py-3">{t.date}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded text-xs font-bold ${t.action === 'BUY' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                              {t.action}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right font-mono">${t.price.toFixed(2)}</td>
                          <td className="px-4 py-3 text-right font-mono">{t.shares}</td>
                          <td className={`px-4 py-3 text-right font-mono font-bold ${t.pnl > 0 ? 'text-green-400' : t.pnl < 0 ? 'text-red-400' : 'text-gray-500'}`}>
                            {t.action === 'SELL' ? `${t.pnl > 0 ? '+' : ''}$${t.pnl.toFixed(2)}` : '-'}
                          </td>
                        </tr>
                      ))}
                      {result.trades.length === 0 && (
                        <tr><td colSpan="5" className="text-center py-6 text-gray-500">No trades executed</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Backtesting;
