import { useLocation } from 'react-router-dom';
import { Bell, Settings, User } from 'lucide-react';

const Topbar = () => {
  const location = useLocation();

  const getTitle = () => {
    switch (location.pathname) {
      case '/': return 'Dashboard';
      case '/fundamental': return 'Fundamental Analysis';
      case '/patterns': return 'Pattern Discovery';
      case '/backtest': return 'Strategy Backtesting';
      default: return 'Datamining Platform';
    }
  };

  return (
    <div className="h-16 bg-dark-surface border-b border-gray-800 flex items-center justify-between px-8 z-10">
      <h1 className="text-xl font-semibold text-gray-100">{getTitle()}</h1>

      <div className="flex items-center gap-4 text-gray-400">
        <button className="p-2 rounded-full hover:bg-dark-surfaceHover transition-colors hover:text-white">
          <Bell className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-full hover:bg-dark-surfaceHover transition-colors hover:text-white">
          <Settings className="w-5 h-5" />
        </button>
        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-accent to-secondary p-[2px]">
          <div className="h-full w-full rounded-full bg-dark-surface flex items-center justify-center">
            <User className="w-4 h-4 text-gray-200" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
