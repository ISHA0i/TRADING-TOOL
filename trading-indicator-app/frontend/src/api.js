// Try multiple base URLs to improve connection reliability
const API_URLS = [
  'http://127.0.0.1:8000',
  'http://localhost:8000'
];

// Start with the first URL
let currentUrlIndex = 0;
let API_URL = API_URLS[currentUrlIndex];

/**
 * Format ticker symbol based on market type and region
 * @param {string} ticker - Original ticker symbol
 * @param {string} symbolType - Type of symbol (stock, forex, crypto, index)
 * @returns {string} - Formatted ticker symbol for yfinance
 */
const formatTickerSymbol = (ticker, symbolType = 'stock') => {
  if (!ticker) return ticker;
  
  // Already formatted Indian stock
  if (ticker.endsWith('.NS') || ticker.endsWith('.BO')) {
    return ticker;
  }
  
  // Format forex pairs for yfinance
  if (symbolType === 'forex') {
    if (ticker.includes('/')) {
      return ticker.replace('/', '') + '=X';
    }
    // Add =X suffix if not already present
    return ticker.endsWith('=X') ? ticker : ticker + '=X';
  }
  
  // Format indices
  if (symbolType === 'index' || ticker.startsWith('^')) {
    if (!ticker.startsWith('^')) {
      return '^' + ticker;
    }
    return ticker;
  }
  
  // Format crypto pairs for yfinance
  if (symbolType === 'crypto') {
    if (ticker.includes('-USD')) {
      return ticker;
    }
    if (!ticker.includes('-')) {
      return ticker + '-USD';
    }
    return ticker;
  }
  
  // US market stocks (just return the symbol for yfinance)
  return ticker;
};

/**
 * Switch to the next available API URL
 * @returns {string} - The new API URL
 */
const switchApiUrl = () => {
  currentUrlIndex = (currentUrlIndex + 1) % API_URLS.length;
  API_URL = API_URLS[currentUrlIndex];
  console.log(`Switching to alternative API URL: ${API_URL}`);
  return API_URL;
};

/**
 * Make an API request with better error handling and fallback URLs
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} - API response
 */
const apiRequest = async (endpoint, options = {}) => {
  let attemptCount = 0;
  const maxAttempts = API_URLS.length;
  
  // Add CORS mode
  const fetchOptions = {
    ...options,
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    },
  };
  
  while (attemptCount < maxAttempts) {
    try {
      console.log(`Requesting (attempt ${attemptCount + 1}/${maxAttempts}): ${API_URL}${endpoint}`);
      
      const response = await fetch(`${API_URL}${endpoint}`, fetchOptions);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Server responded with ${response.status}: ${errorText}`);
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      attemptCount++;
      
      // If this is a "Failed to fetch" error and we haven't tried all URLs yet
      if (error.message.includes('Failed to fetch') && attemptCount < maxAttempts) {
        console.warn(`Connection failed with ${API_URL}, trying alternative URL...`);
        switchApiUrl();
        continue; // Try again with the new URL
      }
      
      // Enhance error reporting
      if (error.message.includes('Failed to fetch')) {
        console.error('Connection to backend failed. Please check if the server is running at available URLs:', API_URLS);
        throw new Error(`Connection to backend failed. Please ensure the server is running at ${API_URL} or check your terminal for the correct URL`);
      }
      
      console.error('API request error:', error);
      throw error;
    }
  }
};

/**
 * Analyze a ticker with the backend API
 */
export const analyzeTicker = async (ticker, timeframe = '1d', period = '1y', capital = 10000, symbolType = 'stock') => {
  const formattedTicker = formatTickerSymbol(ticker, symbolType);
  
  // Add data_provider parameter to specify yfinance
  const dataProvider = 'yfinance';
  
  // Different endpoint for forex and crypto
  if (symbolType === 'forex') {
    return apiRequest(`/api/analyze/forex/${formattedTicker}`, {
      method: 'POST',
      body: JSON.stringify({
        ticker: formattedTicker,
        timeframe,
        period,
        capital,
        data_provider: dataProvider
      })
    });
  } else if (symbolType === 'crypto') {
    return apiRequest(`/api/analyze/${formattedTicker}?timeframe=${timeframe}&period=${period}&capital=${capital}&data_provider=${dataProvider}`, {
      method: 'POST'
    });
  } else {
    return apiRequest(`/api/analyze/${formattedTicker}?timeframe=${timeframe}&period=${period}&capital=${capital}&data_provider=${dataProvider}`, {
      method: 'POST'
    });
  }
};

/**
 * Get historical market data
 */
export const getMarketData = async (ticker, timeframe = '1d', period = '1y', symbolType = 'stock') => {
  const formattedTicker = formatTickerSymbol(ticker, symbolType);
  return apiRequest(`/api/market-data/${formattedTicker}?timeframe=${timeframe}&period=${period}&data_provider=yfinance`);
};

/**
 * Get a list of available forex pairs
 */
export const getForexPairs = async () => {
  return apiRequest('/api/forex/pairs?data_provider=yfinance');
};

/**
 * Get a list of major stock indices
 */
export const getMajorIndices = async () => {
  return apiRequest('/api/indices?data_provider=yfinance');
};

/**
 * Get a list of major Indian stocks
 */
export const getIndianStocks = async () => {
  return apiRequest('/api/indian-stocks?data_provider=yfinance');
};

/**
 * Get a list of major US stocks and S&P 500 components
 */
export const getUSStocks = async () => {
  return apiRequest('/api/us-stocks?data_provider=yfinance');
};

/**
 * Get a list of available cryptocurrencies
 */
export const getCryptoPairs = async () => {
  return apiRequest('/api/crypto?data_provider=yfinance');
};

/**
 * Ping the backend API to check if it's running
 */
export const checkApiStatus = async () => {
  return apiRequest('/api');
};