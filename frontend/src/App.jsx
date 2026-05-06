import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './pages/Dashboard';
import FundamentalAnalysis from './pages/FundamentalAnalysis';
import PatternDiscovery from './pages/PatternDiscovery';
import Backtesting from './pages/Backtesting';

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-dark-bg text-white">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden relative">
          <Topbar />
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-dark-bg p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/fundamental" element={<FundamentalAnalysis />} />
              <Route path="/patterns" element={<PatternDiscovery />} />
              <Route path="/backtest" element={<Backtesting />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
