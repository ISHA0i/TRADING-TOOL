import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_market_data(ticker, timeframe="1d", period="1y"):
    """
    Fetch market data using Yahoo Finance API
    
    Args:
        ticker: Stock/Forex/Crypto/Index symbol (e.g., 'AAPL', 'EURUSD=X', 'BTC-USD', '^GSPC')
        timeframe: Bar timeframe (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        Pandas dataframe with OHLCV data
    """
    try:
        logger.info(f"Fetching data for {ticker} with timeframe={timeframe}, period={period}")
        
        # Format forex pairs correctly
        if "/" in ticker:  # If forex pair is provided with slash (EUR/USD)
            ticker = ticker.replace("/", "") + "=X"
        elif len(ticker) == 6 and not ticker.endswith("=X"):  # If forex pair without slash (EURUSD)
            ticker = ticker + "=X"
            
        # Format indices correctly
        if ticker.lower().startswith("index:"):
            ticker = "^" + ticker[6:]  # Convert "INDEX:GSPC" to "^GSPC"
        
        # Format crypto tickers correctly
        if "-USD" not in ticker:
            # Check if it's a known crypto symbol
            if any(ticker.upper().startswith(c) for c in get_major_cryptos()):
                ticker = ticker.upper() + "-USD"  # Add -USD suffix if missing
            elif ticker.lower().startswith("crypto:"):
                ticker = ticker[7:] + "-USD"  # Convert "CRYPTO:BTC" to "BTC-USD"
        
        # For intraday data, period is limited
        if timeframe in ["1m", "5m", "15m", "30m", "1h"]:
            if period not in ["1d", "5d", "1mo"]:
                period = "5d"
                logger.warning(f"Adjusted period to 5d for intraday timeframe {timeframe}")
        
        # Fetch data
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        if info is None or "regularMarketPrice" not in info:
            logger.error(f"Invalid symbol: {ticker}")
            return pd.DataFrame()
            
        data = ticker_obj.history(period=period, interval=timeframe)
        
        if data.empty:
            logger.error(f"No data returned for {ticker}")
            return pd.DataFrame()
        
        # Rename columns to standard format
        data.columns = [col.title() for col in data.columns]
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Convert Date to datetime 
        data['Date'] = pd.to_datetime(data['Date'])
        
        # For crypto, fetch BTC price if not BTC itself
        if "-USD" in ticker and not ticker.startswith("BTC-"):
            try:
                btc = yf.Ticker("BTC-USD")
                btc_price = btc.history(period="1d").iloc[-1]['Close']
                # Add BTC price as additional info
                data['BTC_Price'] = btc_price
            except Exception as e:
                logger.warning(f"Could not fetch BTC price: {str(e)}")
                data['BTC_Price'] = None
        
        # Select and reorder relevant columns
        columns = ['Date', 'Open', 'High', 'Low', 'Close']
        if 'Volume' in data.columns:
            columns.append('Volume')
        if 'BTC_Price' in data.columns:
            columns.append('BTC_Price')
        
        data = data[columns]
        
        # Handle missing volume data
        if 'Volume' not in data.columns:
            logger.warning(f"No volume data for {ticker}, using 0")
            data['Volume'] = 0
        
        # Remove rows with NaN values
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.dropna()
        
        logger.info(f"Successfully fetched {len(data)} rows of data for {ticker}")
        return data
    
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
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

def get_forex_pairs():
    """
    Get a list of major forex pairs
    
    Returns:
        List of forex pair symbols
    """
    major_pairs = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
        "USD/CAD", "AUD/USD", "NZD/USD", "EUR/GBP",
        "EUR/JPY", "GBP/JPY", "AUD/JPY", "NZD/JPY"
    ]
    return major_pairs

def get_major_indices():
    """
    Get a list of major stock indices
    
    Returns:
        List of index symbols
    """
    indices = [
        "^GSPC",   # S&P 500
        "^DJI",    # Dow Jones
        "^IXIC",   # NASDAQ
        "^FTSE",   # FTSE 100
        "^N225",   # Nikkei 225
        "^HSI",    # Hang Seng
        "^GDAXI",  # DAX
        "^FCHI"    # CAC 40
    ]
    return indices

def get_major_cryptos():
    """
    Get a list of major cryptocurrencies
    
    Returns:
        List of cryptocurrency symbols
    """
    major_cryptos = [
        "BTC",    # Bitcoin
        "ETH",    # Ethereum
        "BNB",    # Binance Coin
        "XRP",    # Ripple
        "ADA",    # Cardano
        "DOGE",   # Dogecoin
        "SOL",    # Solana
        "DOT",    # Polkadot
        "MATIC",  # Polygon
        "LINK",   # Chainlink
        "UNI",    # Uniswap
        "AVAX",   # Avalanche
        "ATOM",   # Cosmos
        "ALGO",   # Algorand
        "FTM"     # Fantom
    ]
    return major_cryptos