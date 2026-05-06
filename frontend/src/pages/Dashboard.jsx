import { Link } from 'react-router-dom';
import { LineChart, Network, ActivitySquare, Database, Cpu, Zap } from 'lucide-react';

const Dashboard = () => {
  const features = [
    {
      title: 'Fundamental Analysis',
      description: 'Analyze company financials, key ratios, and historical statements to assess intrinsic value.',
      icon: LineChart,
      path: '/fundamental',
      color: 'from-blue-500 to-accent',
    },
    {
      title: 'Pattern Discovery',
      description: 'Utilize unsupervised ML for stock clustering, association rules mining, and anomaly detection.',
      icon: Network,
      path: '/patterns',
      color: 'from-secondary to-purple-500',
    },
    {
      title: 'Strategy Backtesting',
      description: 'Test quantitative trading strategies against historical price data to evaluate performance.',
      icon: ActivitySquare,
      path: '/backtest',
      color: 'from-green-500 to-emerald-400',
    },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-dark-surface to-[#0f172a] border border-gray-800 p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 opacity-10">
          <ActivitySquare className="w-64 h-64 text-accent" />
        </div>
        <div className="relative z-10 max-w-3xl">
          <h1 className="text-4xl font-bold mb-4 text-white">
            Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-secondary">Datamining Platform</span>
          </h1>
          <p className="text-lg text-gray-400 mb-6">
            An advanced data mining platform for fundamental stock analysis, pattern discovery, and quantitative strategy backtesting.
          </p>
          <button className="btn-primary flex items-center gap-2">
            <Zap className="w-4 h-4" /> Get Started
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6 flex items-center gap-4 hover:border-accent/50 transition-colors">
          <div className="p-4 rounded-xl bg-accent/10 text-accent">
            <Cpu className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">Data Mining Techniques</p>
            <h3 className="text-2xl font-bold text-white">3 Active Models</h3>
          </div>
        </div>
        
        <div className="card p-6 flex items-center gap-4 hover:border-secondary/50 transition-colors">
          <div className="p-4 rounded-xl bg-secondary/10 text-secondary">
            <ActivitySquare className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">Strategies Available</p>
            <h3 className="text-2xl font-bold text-white">2 Algorithms</h3>
          </div>
        </div>

        <div className="card p-6 flex items-center gap-4 hover:border-green-500/50 transition-colors">
          <div className="p-4 rounded-xl bg-green-500/10 text-green-500">
            <Database className="w-8 h-8" />
          </div>
          <div>
            <p className="text-sm text-gray-400 font-medium">Data Engine</p>
            <h3 className="text-2xl font-bold text-white">Powered by yfinance</h3>
          </div>
        </div>
      </div>

      {/* Feature Links */}
      <div>
        <h2 className="text-2xl font-semibold mb-6 text-gray-100 flex items-center gap-2">
          Platform Capabilities
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <Link key={idx} to={feature.path} className="group">
              <div className="card p-8 h-full hover:-translate-y-1 hover:shadow-[0_10px_30px_rgba(0,0,0,0.5)] transition-all duration-300 relative overflow-hidden">
                <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${feature.color}`}></div>
                <div className="mb-6 inline-flex p-3 rounded-xl bg-dark-surfaceHover group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-8 h-8 text-gray-200" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-white group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-400 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
