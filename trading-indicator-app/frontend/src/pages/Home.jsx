import React, { useState, useEffect } from 'react';
import { analyzeTicker, checkApiStatus, getUSStocks, getForexPairs, getMajorIndices, getIndianStocks, getCryptoPairs, getMarketData } from '../api';
import SignalCard from '../components/SignalCard';
import RiskRewardCard from '../components/RiskRewardCard';
import CapitalUsageCard from '../components/CapitalUsageCard';

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
  const [forexPairs, setForexPairs] = useState([]);
  const [indices, setIndices] = useState([]);
  const [indianStocks, setIndianStocks] = useState([]);
  const [cryptoPairs, setCryptoPairs] = useState([]);
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [loadingSymbols, setLoadingSymbols] = useState(false);
  const [dataProvider, setDataProvider] = useState('yfinance'); // Default to yfinance
  const [retryingConnection, setRetryingConnection] = useState(false);

  // Check API status on load with retry logic
  useEffect(() => {
    checkBackendStatus();
  }, []);

  // Function to check backend status with clearer error reporting
  const checkBackendStatus = async () => {
    setApiStatus('checking');
    setRetryingConnection(true);
    
    try {
      console.log('Checking API connection...');
      await checkApiStatus();
      setApiStatus('connected');
      setError(null); // Clear any previous connection errors
      console.log('API connection successful');
    } catch (error) {
      console.error('API connection failed:', error);
      setApiStatus('disconnected');
      setError(`Unable to connect to the backend server. ${error.message}`);
    } finally {
      setRetryingConnection(false);
    }
  };

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

  // Fetch Indian stocks when market region changes to India
  useEffect(() => {
    const fetchIndianStocks = async () => {
      if (marketRegion === 'india' && symbolType === 'stock' && indianStocks.length === 0) {
        setLoadingStocks(true);
        try {
          const data = await getIndianStocks();
          setIndianStocks(data);
        } catch (error) {
          console.error('Error fetching Indian stocks:', error);
          setError('Failed to load Indian stocks list');
        }
        setLoadingStocks(false);
      }
    };

    fetchIndianStocks();
  }, [marketRegion, symbolType]);

  // Fetch forex pairs when symbol type changes to forex
  useEffect(() => {
    const fetchForexPairs = async () => {
      if (symbolType === 'forex' && forexPairs.length === 0) {
        setLoadingSymbols(true);
        try {
          const data = await getForexPairs();
          setForexPairs(data);
        } catch (error) {
          console.error('Error fetching forex pairs:', error);
          setError('Failed to load forex pairs list');
        }
        setLoadingSymbols(false);
      }
    };

    fetchForexPairs();
  }, [symbolType]);

  // Fetch indices when symbol type changes to index
  useEffect(() => {
    const fetchIndices = async () => {
      if (symbolType === 'index' && indices.length === 0) {
        setLoadingSymbols(true);
        try {
          const data = await getMajorIndices();
          setIndices(data);
        } catch (error) {
          console.error('Error fetching indices:', error);
          setError('Failed to load indices list');
        }
        setLoadingSymbols(false);
      }
    };

    fetchIndices();
  }, [symbolType]);

  // Fetch crypto pairs when symbol type changes to crypto
  useEffect(() => {
    const fetchCryptoPairs = async () => {
      if (symbolType === 'crypto' && cryptoPairs.length === 0) {
        setLoadingSymbols(true);
        try {
          const data = await getCryptoPairs();
          setCryptoPairs(data);
        } catch (error) {
          console.error('Error fetching crypto pairs:', error);
          setError('Failed to load cryptocurrency list');
        }
        setLoadingSymbols(false);
      }
    };

    fetchCryptoPairs();
  }, [symbolType]);
  
  // Auto-refresh effect with data provider
  useEffect(() => {
    let intervalId;
    
    if (autoRefresh && (ticker || customSymbol)) {
      intervalId = setInterval(async () => {
        const symbolToAnalyze = ticker === 'custom' ? customSymbol : ticker;
        console.log(`Auto-refreshing ${symbolToAnalyze}...`);
        
        try {
          const data = await analyzeTicker(symbolToAnalyze, timeframe, period, parseFloat(capital), symbolType);
          setAnalysisData(data);
          setError(null); // Clear any previous errors on successful refresh
        } catch (error) {
          console.error('Auto-refresh error:', error);
          
          // Handle capital efficiency errors - try to extract partial data
          if (error.message.includes("capital_efficiency") || 
              error.message.includes("division by zero") || 
              error.message.includes("ResponseValidationError")) {
            
            try {
              // Try to parse the error response for any useful data
              const errorBody = error.message.split("body=")[1];
              if (errorBody) {
                const jsonStart = errorBody.indexOf('{');
                if (jsonStart >= 0) {
                  const partialData = JSON.parse(errorBody.substring(jsonStart));
                  
                  // Ensure capital_efficiency exists with an error indicator
                  if (!partialData.capital_efficiency) {
                    partialData.capital_efficiency = { error: "Calculation failed due to division by zero" };
                  }
                  
                  setAnalysisData(partialData);
                  setError("Warning: Capital efficiency calculations failed. Some metrics may not be available.");
                  return;
                }
              }
            } catch (parseError) {
              console.error("Failed to parse partial data from error:", parseError);
            }
          }
          
          // Only show connection errors in the UI (don't disrupt user experience too much)
          if (error.message.includes("Failed to fetch") || error.message.includes("Connection to backend failed")) {
            setError("Auto-refresh failed: Unable to connect to the server");
          }
        }
      }, refreshInterval * 1000);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, ticker, customSymbol, timeframe, period, capital, refreshInterval, symbolType, dataProvider]);

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
      
      console.log(`Analyzing ${symbolToAnalyze} with type ${symbolType}, timeframe=${timeframe}, period=${period}`);
      
      try {
        const data = await analyzeTicker(symbolToAnalyze, timeframe, period, parseFloat(capital), symbolType);
        setAnalysisData(data);
        setLoading(false);
      } catch (error) {
        // Special handling for capital efficiency errors that can still display partial data
        if (error.message.includes("capital_efficiency") || 
            error.message.includes("division by zero") || 
            error.message.includes("ResponseValidationError")) {
          
          console.warn("Capital efficiency calculation failed, but continuing with partial data");
          
          // Try to extract the partial data from the error if available
          let partialData = null;
          try {
            // Try to parse the error response for any useful data
            const errorBody = error.message.split("body=")[1];
            if (errorBody) {
              const jsonStart = errorBody.indexOf('{');
              if (jsonStart >= 0) {
                partialData = JSON.parse(errorBody.substring(jsonStart));
                
                // Ensure capital_efficiency exists with an error indicator
                if (!partialData.capital_efficiency) {
                  partialData.capital_efficiency = { error: "Calculation failed due to division by zero" };
                }
                
                setAnalysisData(partialData);
                setError("Warning: Capital efficiency calculations failed. Some metrics may not be available.");
                setLoading(false);
                return;
              }
            }
          } catch (parseError) {
            console.error("Failed to parse partial data from error:", parseError);
          }
          
          // If we couldn't extract data, show a user-friendly error
          setError("Analysis encountered calculation errors. Try a different symbol or timeframe.");
        } else if (error.message.includes("Failed to fetch") || error.message.includes("Connection to backend failed")) {
          setError("Unable to connect to the analysis server. Please ensure the backend is running and accessible.");
        } else if (error.message.includes("404")) {
          setError(`Symbol "${symbolToAnalyze}" not found. Please check the symbol and try again.`);
        } else if (error.message.includes("yfinance")) {
          setError("Yahoo Finance data retrieval error. Please try a different symbol or check your internet connection.");
        } else {
          setError(`Analysis error: ${error.message}`);
        }
        
        setLoading(false);
      }
    } catch (error) {
      console.error("Unexpected error during analysis:", error);
      setError("An unexpected error occurred. Please try again.");
      setLoading(false);
    }
  };

  const getSymbolOptions = () => {
    // If we're loading, show loading message
    if (loadingSymbols) {
      return [<option key="loading" value="" disabled>Loading symbols...</option>];
    }
    
    switch (symbolType) {
      case 'stock':
        if (marketRegion === 'india') {
          if (indianStocks.length === 0) {
            return [<option key="empty" value="" disabled>No stocks available</option>];
          }
          return indianStocks.map(stock => (
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
        if (forexPairs.length === 0) {
          return [<option key="empty" value="" disabled>No forex pairs available</option>];
        }
        return forexPairs.map(pair => (
          <option key={pair.symbol} value={pair.symbol}>{pair.name}</option>
        ));
      case 'index':
        if (indices.length === 0) {
          return [<option key="empty" value="" disabled>No indices available</option>];
        }
        return indices.map(index => (
          <option key={index.symbol} value={index.symbol}>{index.name} ({index.symbol})</option>
        ));
      case 'crypto':
        if (cryptoPairs.length === 0) {
          return [<option key="empty" value="" disabled>No cryptocurrencies available</option>];
        }
        return cryptoPairs.map(pair => (
          <option key={pair.symbol} value={pair.symbol}>{pair.name}</option>
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
            <div className="flex justify-between items-center">
              <div>
                <p className="font-bold">Backend API {apiStatus}</p>
                <p>Make sure the Python backend is running on http://localhost:8000 or http://127.0.0.1:8000</p>
                <p className="text-xs mt-1">Check your terminal for the correct URL where the backend is running.</p>
              </div>
              <button
                onClick={checkBackendStatus}
                disabled={retryingConnection}
                className="px-4 py-2 bg-dark-primary text-dark-text rounded hover:bg-opacity-90 disabled:opacity-50"
              >
                {retryingConnection ? 'Checking...' : 'Retry Connection'}
              </button>
            </div>
          </div>
        )}
        
        {error && apiStatus === 'connected' && (
          <div className="mb-6 p-4 bg-dark-surface border-l-4 border-dark-warning text-dark-text">
            <p className="font-bold">Warning</p>
            <p>{error}</p>
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
                    className="w-full p-2 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text focus:border-dark-primary focus:ring-dark-primary disabled:opacity-50"
                    value={ticker}
                    onChange={handleSymbolSelect}
                    required
                    disabled={loadingSymbols}
                  >
                    <option value="">
                      {loadingSymbols 
                        ? `Loading ${symbolType === 'forex' ? 'forex pairs' : symbolType === 'crypto' ? 'cryptocurrencies' : 'indices'}...` 
                        : `Select ${symbolType === 'forex' ? 'a pair' : symbolType === 'crypto' ? 'a cryptocurrency' : 'an index'}`}
                    </option>
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

              {/* Add note about data source */}
              <div className="lg:col-span-4 mt-2">
                <div className="text-xs text-dark-text-secondary bg-dark-surface-2 p-2 rounded">
                  <span className="font-semibold">Note:</span> Data for crypto, forex, and US markets is provided by Yahoo Finance (yfinance).
                </div>
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
              <SignalCard data={analysisData} symbolType={symbolType} />
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
