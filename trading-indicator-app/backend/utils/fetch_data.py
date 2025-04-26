import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from .providers.angel_one_provider import AngelOneProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Angel One provider if credentials are available
angel_one = None
if all(key in os.environ for key in ['ANGEL_API_KEY', 'ANGEL_CLIENT_ID', 'ANGEL_SECRET_KEY', 'ANGEL_TOTP_KEY']):
    angel_one = AngelOneProvider(
        api_key=os.environ['ANGEL_API_KEY'],
        client_id=os.environ['ANGEL_CLIENT_ID'],
        secret_key=os.environ['ANGEL_SECRET_KEY'],
        totp_key=os.environ['ANGEL_TOTP_KEY']
    )

def format_indian_symbol(ticker):
    """
    Format Indian stock symbols for Yahoo Finance
    
    Args:
        ticker: Stock symbol (e.g., 'RELIANCE', 'HDFC', 'TCS')
    
    Returns:
        Formatted ticker symbol
    """
    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return ticker
    
    # Default to NSE if no exchange specified
    return f"{ticker}.NS"

def get_market_data(ticker, timeframe="1d", period="1y"):
    """
    Fetch market data using either Angel One (for Indian stocks) or Yahoo Finance API
    
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
        if "/" in ticker:
            ticker = ticker.replace("/", "") + "=X"
        elif len(ticker) == 6 and not ticker.endswith("=X"):
            ticker = ticker + "=X"
            
        # Format indices correctly
        if ticker.lower().startswith("index:"):
            ticker = "^" + ticker[6:]
        
        # Format Indian stock symbols
        if not any(c in ticker for c in ['^', '=X', '-USD', '.NS', '.BO']):
            ticker = format_indian_symbol(ticker)
        
        # Format crypto tickers correctly
        if "-USD" not in ticker:
            if any(ticker.upper().startswith(c) for c in get_major_cryptos()):
                ticker = ticker.upper() + "-USD"
            elif ticker.lower().startswith("crypto:"):
                ticker = ticker[7:] + "-USD"

        # Use Angel One for Indian stocks if provider is available
        is_indian_stock = ticker.endswith('.NS') or ticker.endswith('.BO')
        if is_indian_stock and angel_one:
            # Convert timeframe to Angel One format
            timeframe_map = {
                "1m": "ONE_MINUTE",
                "5m": "FIVE_MINUTE",
                "15m": "FIFTEEN_MINUTE",
                "30m": "THIRTY_MINUTE",
                "1h": "ONE_HOUR",
                "1d": "ONE_DAY"
            }
            
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "1d":
                start_date = end_date - timedelta(days=1)
            elif period == "5d":
                start_date = end_date - timedelta(days=5)
            elif period == "1mo":
                start_date = end_date - timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - timedelta(days=180)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=365)  # Default to 1 year
                
            # Remove .NS or .BO suffix and format for Angel One
            base_symbol = ticker.replace('.NS', '').replace('.BO', '')
            angel_symbol = angel_one.format_symbol(base_symbol)
            
            # Get data from Angel One
            data = angel_one.get_historical_data(
                symbol=angel_symbol,
                timeframe=timeframe_map.get(timeframe, "ONE_DAY"),
                from_date=start_date,
                to_date=end_date
            )
            
            if not data.empty:
                return data

        # Adjust timeframe for Indian market stocks
        if is_indian_stock and timeframe in ["1m", "5m", "15m", "30m", "1h"]:
            logger.warning(f"Intraday data for Indian stocks might be limited. Adjusting timeframe to 1d")
            timeframe = "1d"
            if period in ["1d", "5d"]:
                period = "1mo"
        
        # Fetch data with error handling and retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ticker_obj = yf.Ticker(ticker)
                
                # First try to get info to validate the symbol
                info = ticker_obj.info
                if info is None or "regularMarketPrice" not in info:
                    logger.error(f"Invalid symbol: {ticker}")
                    return pd.DataFrame()

                # Then fetch historical data
                data = ticker_obj.history(period=period, interval=timeframe)
                
                if data.empty:
                    logger.error(f"No data returned for {ticker}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                        continue
                    return pd.DataFrame()
                
                break  # Success, exit retry loop
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                return pd.DataFrame()
        
        # Post-process the data
        data = data.reset_index()
        data.columns = [col.title() for col in data.columns]
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Handle missing volume data
        if 'Volume' not in data.columns or (data['Volume'] == 0).all():
            logger.warning(f"No volume data for {ticker}, using synthetic volume")
            # Create synthetic volume based on price movement
            price_change = data['Close'].pct_change().abs()
            data['Volume'] = ((price_change + 0.001) * 100000).fillna(50000).astype(int)
        
        # Clean up data
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.dropna()
        
        if len(data) > 0:
            logger.info(f"Successfully fetched {len(data)} rows of data for {ticker}")
            return data
        else:
            logger.error(f"No valid data after processing for {ticker}")
            return pd.DataFrame()
        
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
        "^FCHI",   # CAC 40
        "^BSESN",  # BSE SENSEX
        "^NSEI",   # NIFTY 50
        "^NSEBANK", # NIFTY BANK
        "^CNXIT",  # NIFTY IT
        "^CNXAUTO" # NIFTY AUTO
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

def get_major_indian_stocks():
    """
    Get a list of major Indian stocks from both NSE and BSE
    
    Returns:
        List of stock symbols
    """
    major_stocks = [
        "RELIANCE.NS",  # Reliance Industries
        "TCS.NS",       # Tata Consultancy Services
        "HDFCBANK.NS",  # HDFC Bank
        "INFY.NS",      # Infosys
        "HINDUNILVR.NS",# Hindustan Unilever
        "ICICIBANK.NS", # ICICI Bank
        "SBIN.NS",      # State Bank of India
        "BHARTIARTL.NS",# Bharti Airtel
        "ITC.NS",       # ITC Limited
        "KOTAKBANK.NS", # Kotak Mahindra Bank
        "WIPRO.NS",     # Wipro
        "AXISBANK.NS",  # Axis Bank
        "MARUTI.NS",    # Maruti Suzuki
        "HCLTECH.NS",   # HCL Technologies
        "ASIANPAINT.NS" # Asian Paints
    ]
    return major_stocks