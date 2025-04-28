"""
Yahoo Finance data provider for market data
"""
import pandas as pd
import numpy as np
import logging
import yfinance as yf
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class YahooFinanceProvider:
    """
    Data provider using Yahoo Finance API
    """
    
    def __init__(self):
        """Initialize Yahoo Finance data provider"""
        logger.info("Initializing YahooFinanceProvider")
    
    def get_market_data(self, ticker: str, timeframe: str = '1d', period: str = '1y') -> pd.DataFrame:
        """
        Get market data from Yahoo Finance
        
        Args:
            ticker (str): Symbol to fetch data for
            timeframe (str): Time frame (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            period (str): Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            
        Returns:
            pd.DataFrame: Market data with OHLCV columns
        """
        try:
            logger.info(f"Fetching market data for {ticker} with timeframe={timeframe}, period={period}")
            
            # Format ticker if needed
            formatted_ticker = self._format_ticker(ticker)
            
            # Get data from yfinance
            data = yf.download(
                tickers=formatted_ticker,
                period=period,
                interval=timeframe,
                auto_adjust=True,
                progress=False
            )
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()
            
            # Rename columns to standard format
            data = data.reset_index()
            data.columns = [str(col).title() for col in data.columns]
            
            # Ensure all required columns are present
            if 'Date' not in data.columns:
                data['Date'] = pd.to_datetime('today')
            
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = 0
            
            # Set index to Date
            data.set_index('Date', inplace=True)
            
            # Handle missing values
            data = data.replace([np.inf, -np.inf], np.nan)
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return pd.DataFrame()
    
    def get_symbol_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get information about a symbol
        
        Args:
            ticker (str): Symbol to get info for
            
        Returns:
            dict: Symbol information
        """
        try:
            # Format ticker if needed
            formatted_ticker = self._format_ticker(ticker)
            
            # Get ticker info
            ticker_obj = yf.Ticker(formatted_ticker)
            info = ticker_obj.info
            
            # Get last price
            hist = ticker_obj.history(period="1d")
            last_price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
            
            # Extract relevant info
            symbol_info = {
                'symbol': ticker,
                'formatted_symbol': formatted_ticker,
                'name': info.get('shortName', info.get('longName', ticker)),
                'last_price': last_price,
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', '')
            }
            
            return symbol_info
            
        except Exception as e:
            logger.error(f"Error getting symbol info: {str(e)}")
            return {
                'symbol': ticker,
                'name': ticker,
                'last_price': 0
            }
    
    def get_multiple_symbols(self, tickers: List[str], timeframe: str = '1d', period: str = '1mo') -> Dict[str, pd.DataFrame]:
        """
        Get market data for multiple symbols
        
        Args:
            tickers (List[str]): List of symbols to fetch data for
            timeframe (str): Time frame (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            period (str): Period to fetch (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of symbol -> market data
        """
        result = {}
        for ticker in tickers:
            result[ticker] = self.get_market_data(ticker, timeframe, period)
        return result
    
    def _format_ticker(self, ticker: str) -> str:
        """Format ticker for Yahoo Finance API"""
        # Already formatted
        if ticker.endswith('.NS') or ticker.endswith('.BO') or ticker.startswith('^') or '-' in ticker:
            return ticker
            
        # Format forex pairs
        if '/' in ticker:
            return ticker.replace('/', '') + '=X'
            
        # Return as is for regular stocks
        return ticker 