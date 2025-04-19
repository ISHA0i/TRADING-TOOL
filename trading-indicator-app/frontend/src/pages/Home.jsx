import React, { useState, useEffect } from 'react';
import { analyzeTicker, checkApiStatus, getUSStocks } from '../api';
import SignalCard from '../components/SignalCard';
import RiskRewardCard from '../components/RiskRewardCard';
import CapitalUsageCard from '../components/CapitalUsageCard';

// Predefined lists
const FOREX_PAIRS = [
  "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
  "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP",
  "EUR/JPY", "GBP/JPY", "AUD/JPY", "NZD/JPY"
];

const MAJOR_INDICES = [
  { symbol: "^GSPC", name: "S&P 500" },
  { symbol: "^DJI", name: "Dow Jones" },
  { symbol: "^IXIC", name: "NASDAQ" },
  { symbol: "^FTSE", name: "FTSE 100" },
  { symbol: "^BSESN", name: "BSE SENSEX" },
  { symbol: "^NSEI", name: "NIFTY 50" },
  { symbol: "^NSEBANK", name: "NIFTY BANK" },
  { symbol: "^CNXIT", name: "NIFTY IT" },
  { symbol: "^CNXAUTO", name: "NIFTY AUTO" },
  { symbol: "^N225", name: "Nikkei 225" },
  { symbol: "^HSI", name: "Hang Seng" },
  { symbol: "^GDAXI", name: "DAX" },
  { symbol: "^FCHI", name: "CAC 40" }
];

const MAJOR_INDIAN_STOCKS = [
  { symbol: "RELIANCE.NS", name: "Reliance Industries" },
  { symbol: "TCS.NS", name: "Tata Consultancy Services" },
  { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
  { symbol: "INFY.NS", name: "Infosys" },
  { symbol: "HINDUNILVR.NS", name: "Hindustan Unilever" },
  { symbol: "ICICIBANK.NS", name: "ICICI Bank" },
  { symbol: "SBIN.NS", name: "State Bank of India" },
  { symbol: "BHARTIARTL.NS", name: "Bharti Airtel" },
  { symbol: "ITC.NS", name: "ITC Limited" },
  { symbol: "KOTAKBANK.NS", name: "Kotak Mahindra Bank" }
];

const CRYPTO_PAIRS = [
  "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD",
  "ADA-USD", "DOGE-USD", "SOL-USD", "DOT-USD",
  "MATIC-USD", "LINK-USD"
];

function Home() {
  const [symbolType, setSymbolType] = useState('stock');
  const [ticker, setTicker] = useState('');
  const [timeframe, setTimeframe] = useState('1d');
  const [period, setPeriod] = useState('1y');
  const [capital, setCapital] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [analysisData, setAnalysisData] = useState(null);
  const [customSymbol, setCustomSymbol] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60); // in seconds
  const [marketRegion, setMarketRegion] = useState('us'); // Add market region state
  const [usStocks, setUSStocks] = useState({ popular: [], sp500: [] });
  const [loadingStocks, setLoadingStocks] = useState(false);

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

  // Fetch US stocks when market region changes to US
  useEffect(() => {
    const fetchUSStocks = async () => {
      if (marketRegion === 'us' && symbolType === 'stock' && usStocks.popular.length === 0) {
        setLoadingStocks(true);
        try {
          const data = await getUSStocks();
          setUSStocks(data);
        } catch (error) {
          console.error('Error fetching US stocks:', error);
          setError('Failed to load US stocks list');
        }
        setLoadingStocks(false);
      }
    };

    fetchUSStocks();
  }, [marketRegion, symbolType]);

  // Auto-refresh effect
  useEffect(() => {
    let intervalId;
    
    if (autoRefresh && (ticker || customSymbol)) {
      intervalId = setInterval(async () => {
        try {
          const symbolToAnalyze = ticker === 'custom' ? customSymbol : ticker;
          const data = await analyzeTicker(symbolToAnalyze, timeframe, period, parseFloat(capital));
          setAnalysisData(data);
        } catch (error) {
          console.error('Auto-refresh error:', error);
        }
      }, refreshInterval * 1000);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, ticker, customSymbol, timeframe, period, capital, refreshInterval]);

  const handleSymbolSelect = (e) => {
    const value = e.target.value;
    setTicker(value);
    if (value === 'custom') {
      setCustomSymbol('');
    }
  };

  const handleCustomSymbolChange = (e) => {
    setCustomSymbol(e.target.value.toUpperCase());
    setTicker('custom');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Use custom symbol if selected, otherwise use the selected ticker
      const symbolToAnalyze = ticker === 'custom' ? customSymbol : ticker;
      const data = await analyzeTicker(symbolToAnalyze, timeframe, period, parseFloat(capital));
      setAnalysisData(data);
      setLoading(false);
    } catch (error) {
      setError(error.message);
      setLoading(false);
    }
  };

  const getSymbolOptions = () => {
    switch (symbolType) {
      case 'stock':
        if (marketRegion === 'india') {
          return MAJOR_INDIAN_STOCKS.map(stock => (
            <option key={stock.symbol} value={stock.symbol}>{stock.name} ({stock.symbol})</option>
          ));
        } else if (marketRegion === 'us') {
          return (
            <>
              <optgroup label="Popular Stocks">
                {usStocks.popular.map(stock => (
                  <option key={stock.symbol} value={stock.symbol}>{stock.name} ({stock.symbol})</option>
                ))}
              </optgroup>
              {usStocks.sp500.length > 0 && (
                <optgroup label="S&P 500 Components">
                  {usStocks.sp500.map(stock => (
                    <option key={stock.symbol} value={stock.symbol}>{stock.name}</option>
                  ))}
                </optgroup>
              )}
            </>
          );
        }
        return [];
      case 'forex':
        return FOREX_PAIRS.map(pair => (
          <option key={pair} value={pair}>{pair}</option>
        ));
      case 'index':
        return MAJOR_INDICES.map(index => (
          <option key={index.symbol} value={index.symbol}>{index.name} ({index.symbol})</option>
        ));
      case 'crypto':
        return CRYPTO_PAIRS.map(pair => (
          <option key={pair} value={pair}>{pair}</option>
        ));
      default:
        return []; // For stocks, we'll use the custom input
    }
  };
  
  return (
    <>
      <main className="container mx-auto px-4 py-6">
        {apiStatus !== 'connected' && (
          <div className="mb-6 p-4 bg-dark-surface border-l-4 border-dark-error text-dark-text">
            <p className="font-bold">Backend API {apiStatus}</p>
            <p>Make sure the Python backend is running on http://localhost:8000</p>
          </div>
        )}
        
        <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-dark-primary">Analyze Market</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Symbol Type Selection */}
              <div>
                <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                  Market Type
                </label>
                <select
                  className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                  value={symbolType}
                  onChange={(e) => {
                    setSymbolType(e.target.value);
                    setTicker('');
                    setCustomSymbol('');
                    if (e.target.value !== 'stock') {
                      setMarketRegion('us');
                    }
                  }}
                >
                  <option value="stock">Stocks</option>
                  <option value="forex">Forex</option>
                  <option value="crypto">Crypto</option>
                  <option value="index">Indices</option>
                </select>
              </div>

              {/* Market Region Selection for Stocks */}
              {symbolType === 'stock' && (
                <div>
                  <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                    Market Region
                  </label>
                  <select
                    className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                    value={marketRegion}
                    onChange={(e) => {
                      setMarketRegion(e.target.value);
                      setTicker('');
                      setCustomSymbol('');
                    }}
                  >
                    <option value="us">US Market</option>
                    <option value="india">Indian Market</option>
                  </select>
                </div>
              )}

              {/* Symbol Selection */}
              <div className={symbolType === 'stock' ? 'lg:col-span-2' : ''}>
                <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                  {symbolType === 'stock' ? 'Stock Symbol' : symbolType === 'forex' ? 'Currency Pair' : symbolType === 'crypto' ? 'Cryptocurrency' : 'Index'}
                </label>
                {symbolType === 'stock' ? (
                  <div className="flex gap-2">
                    <select
                      className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary disabled:opacity-50"
                      value={ticker}
                      onChange={handleSymbolSelect}
                      disabled={loadingStocks}
                    >
                      <option value="">
                        {loadingStocks ? 'Loading stocks...' : 'Select a stock or enter custom symbol'}
                      </option>
                      {getSymbolOptions()}
                    </select>
                    <div className="relative flex-1">
                      <input
                        type="text"
                        className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                        value={customSymbol}
                        onChange={handleCustomSymbolChange}
                        placeholder={marketRegion === 'india' ? "Custom symbol (e.g., TATAMOTORS.NS)" : "Custom symbol (e.g., AAPL)"}
                      />
                    </div>
                  </div>
                ) : (
                  <select
                    className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                    value={ticker}
                    onChange={handleSymbolSelect}
                    required
                  >
                    <option value="">Select {symbolType === 'forex' ? 'a pair' : symbolType === 'crypto' ? 'a cryptocurrency' : 'an index'}</option>
                    {getSymbolOptions()}
                  </select>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                  Timeframe
                </label>
                <select
                  className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                >
                  <option value="1m">1 Minute</option>
                  <option value="5m">5 Minutes</option>
                  <option value="15m">15 Minutes</option>
                  <option value="30m">30 Minutes</option>
                  <option value="1h">1 Hour</option>
                  <option value="1d">Daily</option>
                  <option value="1wk">Weekly</option>
                  <option value="1mo">Monthly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                  Period
                </label>
                <select
                  className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <option value="1d">1 Day</option>
                  <option value="5d">5 Days</option>
                  <option value="1mo">1 Month</option>
                  <option value="3mo">3 Months</option>
                  <option value="6mo">6 Months</option>
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="5y">5 Years</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                  Capital ($)
                </label>
                <input
                  type="number"
                  className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                  value={capital}
                  onChange={(e) => setCapital(e.target.value)}
                  placeholder="10000"
                  min="100"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="autoRefresh"
                  className="rounded bg-dark-surface-2 border-dark-border text-dark-primary focus:ring-dark-primary"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
                <label htmlFor="autoRefresh" className="text-sm text-dark-text-secondary">
                  Auto-refresh
                </label>
              </div>
              
              {autoRefresh && (
                <div>
                  <label className="block text-sm font-medium text-dark-text-secondary mb-1">
                    Refresh Interval (seconds)
                  </label>
                  <select
                    className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary"
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  >
                    <option value="5">5 seconds</option>
                    <option value="10">10 seconds</option>
                    <option value="30">30 seconds</option>
                    <option value="60">1 minute</option>
                    <option value="300">5 minutes</option>
                  </select>
                </div>
              )}
            </div>
            
            <div className="mt-4">
              <button
                type="submit"
                className="bg-dark-primary hover:bg-opacity-90 text-dark-text py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading || (!ticker && !customSymbol)}
              >
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </form>
          
          {error && (
            <div className="mt-4 p-3 bg-dark-surface-2 border border-dark-error rounded-md text-dark-error">
              {error}
            </div>
          )}
        </div>
        
        {analysisData && (
          <>
            <div className="mb-4 flex justify-between items-center text-dark-text-secondary">
              <div>
                {autoRefresh && (
                  <span>
                    Auto-refreshing every {refreshInterval} seconds
                  </span>
                )}
              </div>
              <div>
                Last updated: {new Date().toLocaleTimeString()}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <SignalCard data={analysisData} />
              <RiskRewardCard data={analysisData} symbolType={symbolType} />
              <CapitalUsageCard data={analysisData} symbolType={symbolType} />
            </div>
          </>
        )}
      </main>
    </>
  );
}

export default Home;
