from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import indicators
import strategy
import capital_manager
from utils import fetch_data

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