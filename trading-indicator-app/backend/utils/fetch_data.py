import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_market_data(ticker, timeframe="1d", period="1y"):
    """
    Fetch market data using Yahoo Finance API
    
    Args:
        ticker: Stock symbol
        timeframe: Bar timeframe (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        Pandas dataframe with OHLCV data
    """
    try:
        # For intraday data, period is limited
        if timeframe in ["1m", "5m", "15m", "30m", "1h"]:
            if period not in ["1d", "5d", "1mo"]:
                period = "5d"  # Default to 5 days for intraday data
        
        # Fetch data
        data = yf.Ticker(ticker).history(period=period, interval=timeframe)
        
        # Rename columns to standard format
        data.columns = [col.title() for col in data.columns]
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Convert Date to datetime 
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Select and reorder relevant columns
        if 'Volume' in data.columns:
            data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        else:
            # Some data might not have volume
            data = data[['Date', 'Open', 'High', 'Low', 'Close']]
            data['Volume'] = 0
        
        # Remove rows with NaN values - use np.nan explicitly
        data = data.replace([np.nan, None, float('nan')], np.nan)
        data = data.dropna()
        
        return data
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

def get_multiple_tickers(tickers, timeframe="1d", period="1y"):
    """
    Fetch data for multiple tickers
    
    Args:
        tickers: List of ticker symbols
        timeframe: Bar timeframe
        period: Data period
    
    Returns:
        Dictionary of dataframes with ticker as key
    """
    result = {}
    for ticker in tickers:
        result[ticker] = get_market_data(ticker, timeframe, period)
    
    return result

def get_sp500_tickers():
    """
    Get a list of S&P 500 tickers using Yahoo Finance
    
    Returns:
        List of ticker symbols
    """
    try:
        # This is a shortcut to get S&P 500 tickers
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        tickers = sp500['Symbol'].tolist()
        
        # Clean up tickers (remove special characters)
        tickers = [t.replace('.', '-') for t in tickers]
        
        return tickers
    
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {str(e)}")
        return [] 