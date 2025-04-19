const API_URL = 'http://localhost:8000';

/**
 * Format ticker symbol based on market type and region
 * @param {string} ticker - Original ticker symbol
 * @returns {string} - Formatted ticker symbol
 */
const formatTickerSymbol = (ticker) => {
  // Already formatted Indian stock
  if (ticker.endsWith('.NS') || ticker.endsWith('.BO')) {
    return ticker;
  }
  
  // Format forex pairs
  if (ticker.includes('/')) {
    return ticker.replace('/', '') + '=X';
  }
  
  // Format indices
  if (ticker.startsWith('^')) {
    return ticker;
  }
  if (ticker.toLowerCase().startsWith('index:')) {
    return '^' + ticker.substring(6);
  }
  
  // Format crypto pairs
  if (ticker.includes('-USD')) {
    return ticker;
  }
  if (ticker.toLowerCase().startsWith('crypto:')) {
    return ticker.substring(7) + '-USD';
  }
  
  return ticker;
};

/**
 * Make an API request with error handling
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} - API response
 */
const apiRequest = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

/**
 * Analyze a ticker with the backend API
 */
export const analyzeTicker = async (ticker, timeframe = '1d', period = '1y', capital = 10000) => {
  const formattedTicker = formatTickerSymbol(ticker);
  return apiRequest(`/api/analyze/${formattedTicker}?timeframe=${timeframe}&period=${period}&capital=${capital}`, {
    method: 'POST'
  });
};

/**
 * Get a list of available forex pairs
 */
export const getForexPairs = async () => {
  return apiRequest('/api/forex/pairs');
};

/**
 * Get a list of major stock indices
 */
export const getMajorIndices = async () => {
  return apiRequest('/api/indices');
};

/**
 * Get a list of major Indian stocks
 */
export const getIndianStocks = async () => {
  return apiRequest('/api/indian-stocks');
};

/**
 * Get a list of major US stocks and S&P 500 components
 */
export const getUSStocks = async () => {
  return apiRequest('/api/us-stocks');
};

/**
 * Ping the backend API to check if it's running
 */
export const checkApiStatus = async () => {
  return apiRequest('/api');
};