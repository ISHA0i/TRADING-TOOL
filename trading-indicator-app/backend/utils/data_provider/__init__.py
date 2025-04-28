"""
Data provider package for market data
"""
from .yahoo_provider import YahooFinanceProvider

# Default provider
default_provider = YahooFinanceProvider()

# Export functions that use the default provider
def get_market_data(ticker, timeframe='1d', period='1y'):
    """Get market data using default provider"""
    return default_provider.get_market_data(ticker, timeframe, period)

def get_symbol_info(ticker):
    """Get symbol info using default provider"""
    return default_provider.get_symbol_info(ticker)

def get_multiple_symbols(tickers, timeframe='1d', period='1mo'):
    """Get multiple symbols data using default provider"""
    return default_provider.get_multiple_symbols(tickers, timeframe, period) 