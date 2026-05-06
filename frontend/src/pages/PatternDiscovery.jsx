import { useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ComposedChart, Line, Legend } from 'recharts';
import { Network, Search, AlertTriangle, TrendingUp, Filter } from 'lucide-react';
import { runClustering, runAssociation, getAnomalies } from '../services/api';
import TickerMultiSelect from '../components/TickerMultiSelect';

const COLORS = ['#00D4FF', '#7C3AED', '#10B981', '#F59E0B', '#EF4444', '#3B82F6'];

const PatternDiscovery = () => {
  const [activeTab, setActiveTab] = useState('clustering');

  return (
    <div className="space-y-6">
      <div className="flex gap-4 border-b border-gray-800 pb-2">
        <TabButton id="clustering" icon={Network} label="Clustering" activeTab={activeTab} setActiveTab={setActiveTab} />
        <TabButton id="association" icon={TrendingUp} label="Association Rules" activeTab={activeTab} setActiveTab={setActiveTab} />
        <TabButton id="anomalies" icon={AlertTriangle} label="Anomaly Detection" activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      <div className="animate-fade-in">
        {activeTab === 'clustering' && <ClusteringTab />}
        {activeTab === 'association' && <AssociationTab />}
        {activeTab === 'anomalies' && <AnomaliesTab />}
      </div>
    </div>
  );
};

const TabButton = ({ id, icon: Icon, label, activeTab, setActiveTab }) => (
  <button
    onClick={() => setActiveTab(id)}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
      activeTab === id
        ? 'bg-accent/10 text-accent border border-accent/20'
        : 'text-gray-400 hover:text-gray-200 hover:bg-dark-surfaceHover'
    }`}
  >
    <Icon className="w-5 h-5" />
    {label}
  </button>
);

const ClusteringTab = () => {
  const [tickers, setTickers] = useState(['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'META', 'NVDA']);
  const [features, setFeatures] = useState(['pe_ratio', 'roe']);
  const [nClusters, setNClusters] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const allFeatures = ['pe_ratio', 'roe', 'revenue_growth', 'debt_equity', 'market_cap'];

  const handleRun = async () => {
    setLoading(true);
    setError('');
    try {
      const tickerList = tickers.map((t) => t.trim().toUpperCase()).filter((t) => t);
      const res = await runClustering({ tickers: tickerList, features, n_clusters: nClusters });
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.clusters?.map(c => ({
    ticker: c.ticker,
    cluster: c.cluster_id,
    x: c.feature_values[features[0]],
    y: features.length > 1 ? c.feature_values[features[1]] : 0,
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="card p-6 lg:col-span-1 space-y-6">
        <div>
          <TickerMultiSelect
            label="Tickers"
            items={tickers}
            setItems={setTickers}
            placeholder="Type or select a ticker"
            helperText="Pick tickers from the dropdown or type one and press Add."
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Features</label>
          <div className="space-y-2">
            {allFeatures.map(f => (
              <label key={f} className="flex items-center gap-2 text-gray-300">
                <input
                  type="checkbox"
                  checked={features.includes(f)}
                  onChange={(e) => {
                    if (e.target.checked) setFeatures([...features, f]);
                    else setFeatures(features.filter(feat => feat !== f));
                  }}
                  className="rounded border-gray-600 bg-dark-bg text-accent focus:ring-accent"
                />
                {f.replace('_', ' ').toUpperCase()}
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Number of Clusters</label>
          <input
            type="number"
            min="2"
            max="6"
            className="input-field w-full"
            value={nClusters}
            onChange={(e) => setNClusters(parseInt(e.target.value))}
          />
        </div>

        <button onClick={handleRun} disabled={loading || features.length < 2} className="btn-primary w-full">
          {loading ? 'Running...' : 'Run Clustering'}
        </button>
        {features.length < 2 && <p className="text-xs text-red-400">Select at least 2 features for 2D visualization</p>}
      </div>

      <div className="card p-6 lg:col-span-2 flex flex-col min-h-[500px]">
        {error && <div className="text-red-400 mb-4">{error}</div>}
        
        {!result && !loading && !error && (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
            <Network className="w-16 h-16 mb-4 opacity-50" />
            <p>Configure parameters and run clustering to see results</p>
          </div>
        )}

        {loading && <div className="flex-1 flex items-center justify-center text-accent">Processing...</div>}

        {result && (
          <>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-bold">Cluster Visualization</h3>
              <div className="text-sm px-3 py-1 bg-dark-surfaceHover rounded-full border border-gray-700">
                Silhouette Score: <span className="font-mono text-accent">{result.silhouette_score?.toFixed(3) || 'N/A'}</span>
              </div>
            </div>
            
            <div className="h-[300px] w-full bg-dark-bg rounded-xl border border-gray-800 p-4 mb-6">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                  <XAxis type="number" dataKey="x" name={features[0]} stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} />
                  <YAxis type="number" dataKey="y" name={features[1]} stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }} 
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                    formatter={(value, name, props) => [value, name === 'x' ? features[0] : features[1]]}
                    labelFormatter={() => ''}
                    itemSorter={(item) => item.value}
                  />
                  <Scatter name="Stocks" data={chartData} fill="#8884d8">
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.cluster % COLORS.length]} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-gray-300">
                <thead className="text-xs uppercase bg-dark-surfaceHover text-gray-400 border-b border-gray-800">
                  <tr>
                    <th className="px-4 py-3">Ticker</th>
                    <th className="px-4 py-3">Cluster</th>
                    {features.map(f => <th key={f} className="px-4 py-3">{f}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {result.clusters.map((c, i) => (
                    <tr key={i} className="hover:bg-dark-surfaceHover/50">
                      <td className="px-4 py-3 font-medium text-white">{c.ticker}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 rounded-full text-xs font-bold" style={{backgroundColor: `${COLORS[c.cluster_id % COLORS.length]}33`, color: COLORS[c.cluster_id % COLORS.length]}}>
                          Cluster {c.cluster_id}
                        </span>
                      </td>
                      {features.map(f => (
                        <td key={f} className="px-4 py-3 font-mono">{c.feature_values[f]?.toFixed(2) || 'N/A'}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

const AssociationTab = () => {
  const [tickers, setTickers] = useState(['AAPL', 'MSFT', 'GOOG']);
  const [minSupport, setMinSupport] = useState(0.1);
  const [minConfidence, setMinConfidence] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleRun = async () => {
    setLoading(true);
    setError('');
    try {
      const tickerList = tickers.map((t) => t.trim().toUpperCase()).filter((t) => t);
      const res = await runAssociation({ tickers: tickerList, min_support: minSupport, min_confidence: minConfidence });
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="card p-6 lg:col-span-1 space-y-6">
        <TickerMultiSelect
          label="Tickers"
          items={tickers}
          setItems={setTickers}
          placeholder="Type or select a ticker"
          helperText="Add multiple tickers for association rules mining."
          required
        />
        
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Min Support: {minSupport}</label>
          <input type="range" min="0.01" max="0.5" step="0.01" className="w-full accent-accent" value={minSupport} onChange={(e) => setMinSupport(parseFloat(e.target.value))} />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">Min Confidence: {minConfidence}</label>
          <input type="range" min="0.1" max="1.0" step="0.1" className="w-full accent-accent" value={minConfidence} onChange={(e) => setMinConfidence(parseFloat(e.target.value))} />
        </div>

        <button onClick={handleRun} disabled={loading} className="btn-primary w-full">
          {loading ? 'Mining Rules...' : 'Mine Rules'}
        </button>
      </div>

      <div className="card p-6 lg:col-span-2 min-h-[500px]">
        {error && <div className="text-red-400 mb-4">{error}</div>}
        
        {!result && !loading && !error && (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <Filter className="w-16 h-16 mb-4 opacity-50" />
            <p>Mine association rules to discover relationships between market events.</p>
          </div>
        )}

        {result && (
          <>
            <h3 className="text-lg font-bold mb-4 text-white">Discovered Rules ({result.total_rules})</h3>
            {result.total_rules === 0 ? (
              <p className="text-gray-400 text-center py-8">No rules found. Try lowering thresholds.</p>
            ) : (
              <div className="overflow-y-auto max-h-[600px]">
                <table className="w-full text-left text-sm text-gray-300">
                  <thead className="sticky top-0 bg-dark-surface text-xs uppercase text-gray-400 border-b border-gray-800">
                    <tr>
                      <th className="px-4 py-3">Antecedents</th>
                      <th className="px-4 py-3">Consequents</th>
                      <th className="px-4 py-3">Support</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Lift</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {result.rules.map((r, i) => (
                      <tr key={i} className="hover:bg-dark-surfaceHover">
                        <td className="px-4 py-3 font-medium text-accent">{r.antecedents.join(', ')}</td>
                        <td className="px-4 py-3 font-medium text-secondary">{r.consequents.join(', ')}</td>
                        <td className="px-4 py-3 font-mono">{(r.support * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 font-mono">{(r.confidence * 100).toFixed(1)}%</td>
                        <td className={`px-4 py-3 font-mono font-bold ${r.lift > 1.5 ? 'text-green-400' : ''}`}>
                          {r.lift.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

const AnomaliesTab = () => {
  const [tickers, setTickers] = useState(['TSLA']);
  const [period, setPeriod] = useState('1y');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleRun = async () => {
    if (tickers.length === 0) {
      setError('Please select at least one ticker.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const tickerToLoad = tickers[0].toUpperCase();
      const res = await getAnomalies(tickerToLoad, period);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-6">
      <div className="space-y-4 mb-8">
        <TickerMultiSelect
          label="Tickers"
          items={tickers}
          setItems={setTickers}
          placeholder="Type or select a ticker"
          helperText="Anomaly detection will use the first selected ticker."
          required
        />
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <select className="input-field w-full md:w-32 bg-dark-bg" value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="6mo">6 Months</option>
            <option value="1y">1 Year</option>
            <option value="2y">2 Years</option>
          </select>
          <button onClick={handleRun} disabled={loading} className="btn-primary w-full md:w-auto">
            {loading ? 'Detecting...' : 'Detect Anomalies'}
          </button>
        </div>
      </div>

      {error && <div className="text-red-400 mb-4">{error}</div>}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-dark-bg border border-gray-800 p-4 rounded-xl">
              <p className="text-sm text-gray-400">Total Days</p>
              <h4 className="text-2xl font-bold">{result.total_days}</h4>
            </div>
            <div className="bg-dark-bg border border-gray-800 p-4 rounded-xl">
              <p className="text-sm text-gray-400">Anomalies Detected</p>
              <h4 className="text-2xl font-bold text-red-400">{result.anomaly_count}</h4>
            </div>
            <div className="bg-dark-bg border border-gray-800 p-4 rounded-xl">
              <p className="text-sm text-gray-400">Anomaly Rate</p>
              <h4 className="text-2xl font-bold text-accent">
                {((result.anomaly_count / result.total_days) * 100).toFixed(1)}%
              </h4>
            </div>
          </div>

          <div className="h-[400px] w-full bg-dark-bg rounded-xl border border-gray-800 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={result.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="date" stroke="#9CA3AF" tick={{fontSize: 12}} minTickGap={30} />
                <YAxis dataKey="close" domain={['auto', 'auto']} stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff' }}
                />
                <Legend />
                <Line type="monotone" dataKey="close" stroke="#00D4FF" dot={false} name="Close Price" />
                <Scatter dataKey="close" name="Anomaly" data={result.data.filter(d => d.is_anomaly)} fill="#EF4444" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto max-h-[300px] border border-gray-800 rounded-xl">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="sticky top-0 bg-dark-surfaceHover text-xs uppercase text-gray-400">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Close Price</th>
                  <th className="px-4 py-3">Daily Return</th>
                  <th className="px-4 py-3">Anomaly Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800 bg-dark-bg">
                {result.data.filter(d => d.is_anomaly).map((d, i) => (
                  <tr key={i}>
                    <td className="px-4 py-3 text-white">{d.date}</td>
                    <td className="px-4 py-3 font-mono">${d.close.toFixed(2)}</td>
                    <td className="px-4 py-3 font-mono font-bold text-red-400">{(d.daily_return * 100).toFixed(2)}%</td>
                    <td className="px-4 py-3 font-mono">{d.anomaly_score.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternDiscovery;
