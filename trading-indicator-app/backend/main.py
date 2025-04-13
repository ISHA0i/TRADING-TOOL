from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
try:
    import indicators
    import strategy
    import capital_manager
    from utils import fetch_data
except ImportError as e:
    print(f"Import error: {e}")
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

app = FastAPI(title="Trading Indicator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str
    timeframe: str = "1d"
    period: str = "1y"
    capital: float = 10000.0

@app.get("/")
async def root():
    return {"message": "Trading Indicator API is running"}

@app.post("/analyze")
async def analyze_ticker(request: AnalysisRequest):
    try:
        # Fetch market data
        data = fetch_data.get_market_data(request.ticker, request.timeframe, request.period)
        
        # Calculate technical indicators
        indicators_data = indicators.calculate_all(data)
        
        # Generate trading signals
        signals = strategy.generate_signals(indicators_data)
        
        # Calculate risk and position sizing
        capital_plan = capital_manager.calculate_position(
            signals, request.capital, data.iloc[-1]['Close']
        )
        
        return {
            "ticker": request.ticker,
            "last_price": float(data.iloc[-1]['Close']),
            "signals": signals,
            "capital_plan": capital_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 