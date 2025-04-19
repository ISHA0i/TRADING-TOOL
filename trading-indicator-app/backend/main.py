from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from typing import Optional, List
import logging
import traceback
import json
import numpy as np
from utils.fetch_data import get_forex_pairs, get_major_indices, get_major_indian_stocks, get_sp500_tickers

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import indicators
    import strategy
    import capital_manager
    from utils import fetch_data
except ImportError as e:
    logger.error(f"Import error: {e}")
    print("Using mock implementations for demo purposes")
    # Create mock implementations for demo purposes
    class MockModule:
        def calculate_all(self, data):
            return data
        
        def generate_signals(self, data):
            return {
                "signal": "BUY",
                "confidence": 0.75,
                "reasons": ["Mock reason 1", "Mock reason 2"],
                "support_levels": [100, 95, 90],
                "resistance_levels": [110, 120, 130],
                "entry_price": 105.0,
                "stop_loss": 95.0,
                "take_profit": 120.0
            }
        
        def calculate_position(self, signals, capital, current_price):
            return {
                "total_capital": capital,
                "risk_percent": 1.0,
                "max_position_size_percent": 10.0,
                "position_size_usd": capital * 0.1,
                "position_size_units": (capital * 0.1) / current_price,
                "stop_loss_usd": capital * 0.01,
                "potential_profit_usd": capital * 0.02,
                "risk_reward_ratio": 2.0
            }
        
        def get_market_data(self, ticker, timeframe, period):
            import pandas as pd
            import numpy as np
            # Create mock data
            dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
            data = pd.DataFrame({
                'Date': dates,
                'Open': np.linspace(100, 105, 100) + np.random.normal(0, 1, 100),
                'High': np.linspace(105, 110, 100) + np.random.normal(0, 1, 100),
                'Low': np.linspace(95, 100, 100) + np.random.normal(0, 1, 100),
                'Close': np.linspace(100, 105, 100) + np.random.normal(0, 1, 100),
                'Volume': np.random.randint(1000, 10000, 100)
            })
            return data
    
    # Create mock modules
    indicators = MockModule()
    strategy = MockModule()
    capital_manager = MockModule()
    fetch_data = MockModule()

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        try:
            import numpy as np
            import pandas as pd
            
            if isinstance(obj, (float, np.floating)):
                # Convert NaN, inf, -inf to None
                if np.isnan(obj) or not np.isfinite(obj):
                    return None
                return float(obj)
            elif isinstance(obj, (int, np.integer)):
                return int(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return [self.default(x) for x in obj.tolist()]
            elif isinstance(obj, pd.Series):
                return [self.default(x) for x in obj.values]
            elif isinstance(obj, pd.DataFrame):
                # Convert DataFrame to records, handling NaN values
                return obj.replace({np.nan: None}).to_dict('records')
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            
            # Let the base class handle anything else
            return super().default(obj)
            
        except Exception as e:
            # If all else fails, convert to None
            if isinstance(obj, (float, np.floating)) and (np.isnan(obj) or not np.isfinite(obj)):
                return None
            try:
                return str(obj)
            except:
                return None

# Create a custom JSONResponse class that uses our encoder
from starlette.responses import JSONResponse

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=NumpyJSONEncoder,
        ).encode("utf-8")

# Create the main FastAPI app
app = FastAPI(
    title="Trading Indicator API",
    default_response_class=CustomJSONResponse
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock symbol to analyze")
    timeframe: str = Field(default="1d", description="Time frame for analysis (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")
    period: str = Field(default="1y", description="Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)")
    capital: float = Field(default=10000.0, description="Available capital for trading")

@app.get("/")
async def root():
    return {"message": "Trading Indicator API is running"}

@app.get("/api")
async def api_root():
    """Root endpoint for API status check"""
    return {"status": "ok", "message": "Trading Indicator API is running"}

@app.get("/api/analyze/{ticker}")
@app.post("/api/analyze/{ticker}")
async def analyze_ticker(
    ticker: str,
    timeframe: str = Query(default="1d", description="Time frame for analysis"),
    period: str = Query(default="1y", description="Historical data period"),
    capital: float = Query(default=10000.0, description="Available capital")
):
    try:
        logger.info(f"Analyzing {ticker} with timeframe={timeframe}, period={period}, capital={capital}")
        
        # Fetch market data
        data = fetch_data.get_market_data(ticker, timeframe, period)
        if data.empty:
            logger.error(f"No data found for ticker {ticker}")
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}. Please verify the symbol and try again."
            )
        
        # Pre-process data to handle NaN values
        data = data.replace([np.inf, -np.inf], np.nan)
        data = data.ffill().bfill()  # Updated to use recommended methods
        
        # Calculate technical indicators
        try:
            logger.debug(f"Calculating indicators for {ticker}")
            indicators_data = indicators.calculate_all(data)
            if indicators_data is None:
                raise ValueError("Indicator calculation returned None")
                
            # Clean up any remaining NaN values after indicator calculation
            indicators_data = indicators_data.replace([np.inf, -np.inf], np.nan)
            indicators_data = indicators_data.ffill().bfill()  # Updated to use recommended methods
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating technical indicators: {str(e)}"
            )
        
        # Generate trading signals
        try:
            logger.debug(f"Generating signals for {ticker}")
            signals = strategy.generate_signals(indicators_data)
            if signals is None:
                raise ValueError("Signal generation returned None")
            
            # Clean up any NaN values in signals
            signals = {k: (None if isinstance(v, float) and (np.isnan(v) or not np.isfinite(v)) else v) 
                      for k, v in signals.items()}
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating trading signals: {str(e)}"
            )
        
        # Calculate risk and position sizing
        try:
            logger.debug(f"Calculating position size for {ticker}")
            capital_plan = capital_manager.calculate_position(
                signals, capital, float(indicators_data.iloc[-1]['Close'])
            )
            if capital_plan is None:
                raise ValueError("Position calculation returned None")
                
            # Clean up any NaN values in capital plan
            capital_plan = {k: (None if isinstance(v, float) and (np.isnan(v) or not np.isfinite(v)) else v) 
                          for k, v in capital_plan.items()}
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calculating position size: {str(e)}"
            )
        
        # Prepare the response with cleaned data
        response = {
            "ticker": ticker,
            "last_price": float(indicators_data.iloc[-1]['Close']),
            "signals": signals,
            "capital_plan": capital_plan,
            "historical_data": indicators_data.tail(50).replace({np.nan: None}).to_dict('records')
        }
        
        logger.info(f"Successfully analyzed {ticker}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing {ticker}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while analyzing {ticker}: {str(e)}"
        )

@app.get("/api/forex/pairs")
async def get_available_forex_pairs():
    """Get list of available forex pairs"""
    try:
        pairs = get_forex_pairs()
        return {"pairs": pairs}
    except Exception as e:
        logger.error(f"Error getting forex pairs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting forex pairs: {str(e)}"
        )

@app.get("/api/indices")
async def get_available_indices():
    """Get list of major stock indices"""
    try:
        indices = get_major_indices()
        return {"indices": indices}
    except Exception as e:
        logger.error(f"Error getting indices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting indices: {str(e)}"
        )

@app.get("/api/indian-stocks")
async def get_available_indian_stocks():
    """Get list of major Indian stocks"""
    try:
        stocks = get_major_indian_stocks()
        return {"stocks": stocks}
    except Exception as e:
        logger.error(f"Error getting Indian stocks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting Indian stocks: {str(e)}"
        )

@app.get("/api/us-stocks")
async def get_available_us_stocks():
    """Get list of major US stocks and S&P 500 components"""
    try:
        # First get some popular US stocks that we want to show at the top
        popular_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
            {"symbol": "V", "name": "Visa Inc."},
            {"symbol": "WMT", "name": "Walmart Inc."}
        ]
        
        # Then get S&P 500 components
        sp500_tickers = get_sp500_tickers()
        sp500_stocks = [{"symbol": ticker, "name": ticker} for ticker in sp500_tickers 
                       if not any(ps["symbol"] == ticker for ps in popular_stocks)]
        
        return {
            "popular": popular_stocks,
            "sp500": sp500_stocks
        }
    except Exception as e:
        logger.error(f"Error getting US stocks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting US stocks: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")