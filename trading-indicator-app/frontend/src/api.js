const API_URL = 'http://localhost:8000';

/**
 * Analyze a ticker with the backend API
 * 
 * @param {string} ticker - The ticker symbol
 * @param {string} timeframe - Timeframe for analysis (1d, 1h, etc)
 * @param {string} period - Historical data period (1y, 6mo, etc)
 * @param {number} capital - Available capital amount
 * @returns {Promise} - API response with analysis
 */
export const analyzeTicker = async (ticker, timeframe = '1d', period = '1y', capital = 10000) => {
  try {
    const response = await fetch(`${API_URL}/api/analyze/${ticker}?timeframe=${timeframe}&period=${period}&capital=${capital}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed: ${errorText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

/**
 * Ping the backend API to check if it's running
 * 
 * @returns {Promise} - API response
 */
export const checkApiStatus = async () => {
  try {
    const response = await fetch(`${API_URL}/api`);
    
    if (!response.ok) {
      throw new Error(`API status check failed with status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API status check error:', error);
    throw error;
  }
};