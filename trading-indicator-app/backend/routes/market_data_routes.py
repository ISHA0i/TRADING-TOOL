"""
API routes for market data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from utils.data_provider import get_market_data, get_symbol_info
from models.common import SymbolInfo

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["market-data"])

# Define commonly used symbols
FOREX_PAIRS = [
    {"symbol": "EUR/USD", "name": "Euro/US Dollar"},
    {"symbol": "GBP/USD", "name": "British Pound/US Dollar"},
    {"symbol": "USD/JPY", "name": "US Dollar/Japanese Yen"},
    {"symbol": "USD/CHF", "name": "US Dollar/Swiss Franc"},
    {"symbol": "USD/CAD", "name": "US Dollar/Canadian Dollar"},
    {"symbol": "AUD/USD", "name": "Australian Dollar/US Dollar"},
    {"symbol": "NZD/USD", "name": "New Zealand Dollar/US Dollar"},
    {"symbol": "EUR/GBP", "name": "Euro/British Pound"},
    {"symbol": "EUR/JPY", "name": "Euro/Japanese Yen"},
    {"symbol": "GBP/JPY", "name": "British Pound/Japanese Yen"}
]

MAJOR_INDICES = [
    {"symbol": "^GSPC", "name": "S&P 500"},
    {"symbol": "^DJI", "name": "Dow Jones Industrial Average"},
    {"symbol": "^IXIC", "name": "NASDAQ Composite"},
    {"symbol": "^FTSE", "name": "FTSE 100"},
    {"symbol": "^BSESN", "name": "BSE SENSEX"},
    {"symbol": "^NSEI", "name": "NIFTY 50"},
    {"symbol": "^NSEBANK", "name": "NIFTY BANK"},
    {"symbol": "^N225", "name": "Nikkei 225"},
    {"symbol": "^HSI", "name": "Hang Seng"},
    {"symbol": "^GDAXI", "name": "DAX"}
]

MAJOR_INDIAN_STOCKS = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
    {"symbol": "INFY.NS", "name": "Infosys"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
    {"symbol": "SBIN.NS", "name": "State Bank of India"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
    {"symbol": "ITC.NS", "name": "ITC Limited"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"}
]

POPULAR_US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "V", "name": "Visa Inc."},
    {"symbol": "WMT", "name": "Walmart Inc."}
]

CRYPTO_PAIRS = [
    {"symbol": "BTC-USD", "name": "Bitcoin/US Dollar"},
    {"symbol": "ETH-USD", "name": "Ethereum/US Dollar"},
    {"symbol": "BNB-USD", "name": "Binance Coin/US Dollar"},
    {"symbol": "XRP-USD", "name": "XRP/US Dollar"},
    {"symbol": "ADA-USD", "name": "Cardano/US Dollar"},
    {"symbol": "DOGE-USD", "name": "Dogecoin/US Dollar"},
    {"symbol": "SOL-USD", "name": "Solana/US Dollar"},
    {"symbol": "DOT-USD", "name": "Polkadot/US Dollar"},
    {"symbol": "MATIC-USD", "name": "Polygon/US Dollar"},
    {"symbol": "LINK-USD", "name": "Chainlink/US Dollar"}
]


@router.get("/forex/pairs", response_model=List[SymbolInfo])
async def get_available_forex_pairs():
    """Get list of available forex pairs"""
    try:
        return FOREX_PAIRS
    except Exception as e:
        logger.error(f"Error fetching forex pairs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching forex pairs: {str(e)}")


@router.get("/indices", response_model=List[SymbolInfo])
async def get_available_indices():
    """Get list of available market indices"""
    try:
        return MAJOR_INDICES
    except Exception as e:
        logger.error(f"Error fetching indices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching indices: {str(e)}")


@router.get("/indian-stocks", response_model=List[SymbolInfo])
async def get_available_indian_stocks():
    """Get list of available Indian stocks"""
    try:
        return MAJOR_INDIAN_STOCKS
    except Exception as e:
        logger.error(f"Error fetching Indian stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Indian stocks: {str(e)}")


@router.get("/us-stocks")
async def get_available_us_stocks():
    """Get list of available US stocks (popular and S&P 500)"""
    try:
        # In a production environment, this would fetch the actual S&P 500 components
        # For simplicity, we're returning a predefined list
        return {
            "popular": POPULAR_US_STOCKS,
            "sp500": []  # This would be populated with actual S&P 500 components
        }
    except Exception as e:
        logger.error(f"Error fetching US stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching US stocks: {str(e)}")


@router.get("/crypto", response_model=List[SymbolInfo])
async def get_available_crypto():
    """Get list of available cryptocurrencies"""
    try:
        return CRYPTO_PAIRS
    except Exception as e:
        logger.error(f"Error fetching cryptocurrencies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching cryptocurrencies: {str(e)}")


@router.get("/market-data/{ticker}")
async def get_historical_data(
    ticker: str,
    timeframe: str = Query(default="1d", description="Time frame for data"),
    period: str = Query(default="1mo", description="Historical period")
):
    """Get historical market data for a symbol"""
    try:
        data = get_market_data(ticker, timeframe, period)
        if data.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {ticker}"
            )
        
        # Convert to list of dictionaries for JSON response
        data = data.reset_index()
        data['Date'] = data['Date'].astype(str)  # Convert dates to strings
        
        # Convert DataFrame to list of dictionaries
        data_list = data.to_dict(orient='records')
        
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "period": period,
            "data": data_list
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


@router.get("/symbol-info/{ticker}")
async def get_symbol_info_endpoint(ticker: str):
    """Get information about a symbol"""
    try:
        info = get_symbol_info(ticker)
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"No information found for {ticker}"
            )
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching symbol info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching symbol info: {str(e)}") 