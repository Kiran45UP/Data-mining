import { NavLink } from 'react-router-dom';
import { LayoutDashboard, LineChart, Network, ActivitySquare } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/fundamental', label: 'Fundamental Analysis', icon: LineChart },
    { path: '/patterns', label: 'Pattern Discovery', icon: Network },
    { path: '/backtest', label: 'Strategy Backtesting', icon: ActivitySquare },
  ];

  return (
    <div className="w-64 bg-dark-surface border-r border-gray-800 flex flex-col transition-all duration-300">
      <div className="h-16 flex items-center px-6 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <ActivitySquare className="w-8 h-8 text-accent" />
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-accent to-secondary">
            Datamining Platform
          </span>
        </div>
      </div>
      
      <nav className="flex-1 py-6 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-[rgba(0,212,255,0.1)] to-[rgba(124,58,237,0.1)] text-accent border border-accent/20 shadow-[0_0_10px_rgba(0,212,255,0.1)]'
                  : 'text-gray-400 hover:bg-dark-surfaceHover hover:text-gray-200'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 text-center">
          Powered by yfinance & FastAPI
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
