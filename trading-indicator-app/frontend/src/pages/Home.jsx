import React, { useState, useEffect } from 'react';
import { analyzeTicker, checkApiStatus } from '../api';
import SignalCard from '../components/SignalCard';
import RiskRewardCard from '../components/RiskRewardCard';
import CapitalUsageCard from '../components/CapitalUsageCard';

function Home() {
  const [ticker, setTicker] = useState('');
  const [timeframe, setTimeframe] = useState('1d');
  const [period, setPeriod] = useState('1y');
  const [capital, setCapital] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [analysisData, setAnalysisData] = useState(null);
  
  // Check API status on load
  useEffect(() => {
    const checkStatus = async () => {
      try {
        await checkApiStatus();
        setApiStatus('connected');
      } catch (error) {
        setApiStatus('disconnected');
      }
    };
    
    checkStatus();
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const data = await analyzeTicker(ticker, timeframe, period, parseFloat(capital));
      setAnalysisData(data);
      setLoading(false);
    } catch (error) {
      setError(error.message);
      setLoading(false);
    }
  };
  
  return (
    <>
      <main className="container mx-auto px-4 py-6">
        {apiStatus !== 'connected' && (
          <div className="mb-6 p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700">
            <p className="font-bold">Backend API {apiStatus}</p>
            <p>Make sure the Python backend is running on http://localhost:8000</p>
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Analyze Stock</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ticker Symbol
                </label>
                <input
                  type="text"
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  placeholder="AAPL"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timeframe
                </label>
                <select
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                >
                  <option value="1d">Daily</option>
                  <option value="1h">Hourly</option>
                  <option value="1wk">Weekly</option>
                  <option value="1mo">Monthly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Period
                </label>
                <select
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <option value="1mo">1 Month</option>
                  <option value="3mo">3 Months</option>
                  <option value="6mo">6 Months</option>
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="5y">5 Years</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capital ($)
                </label>
                <input
                  type="number"
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={capital}
                  onChange={(e) => setCapital(e.target.value)}
                  placeholder="10000"
                  min="100"
                />
              </div>
            </div>
            
            <div className="mt-4">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
                disabled={loading || !ticker}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </form>
          
          {error && (
            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </div>
        
        {analysisData && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <SignalCard data={analysisData} />
            <RiskRewardCard data={analysisData} />
            <CapitalUsageCard data={analysisData} />
          </div>
        )}
      </main>
    </>
  );
}

export default Home;
