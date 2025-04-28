"""
Analysis request models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from .common import TimeFrame, Period


class AnalyzeRequest(BaseModel):
    """
    Request model for market analysis
    """
    ticker: str = Field(..., description="Stock/forex/crypto symbol to analyze")
    timeframe: TimeFrame = Field(default=TimeFrame.DAY_1, description="Time frame for analysis")
    period: Period = Field(default=Period.YEAR_1, description="Historical data period")
    capital: float = Field(default=10000.0, description="Available capital for trading")
    
    @validator('capital')
    def capital_must_be_positive(cls, v):
        """Validate capital is positive"""
        if v <= 0:
            raise ValueError('Capital must be positive')
        return v
    
    @validator('ticker')
    def ticker_must_not_be_empty(cls, v):
        """Validate ticker is not empty"""
        if not v or not v.strip():
            raise ValueError('Ticker must not be empty')
        return v.strip().upper()
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "1d",
                "period": "1y",
                "capital": 10000.0
            }
        }


class ForexAnalyzeRequest(AnalyzeRequest):
    """
    Request model for forex pair analysis
    """
    base_currency: Optional[str] = Field(None, description="Base currency")
    quote_currency: Optional[str] = Field(None, description="Quote currency")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "EUR/USD",
                "timeframe": "1h",
                "period": "3mo",
                "capital": 10000.0,
                "base_currency": "EUR",
                "quote_currency": "USD"
            }
        }


class CryptoAnalyzeRequest(AnalyzeRequest):
    """
    Request model for cryptocurrency analysis
    """
    exchange: Optional[str] = Field(None, description="Cryptocurrency exchange")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "BTC-USD",
                "timeframe": "1d",
                "period": "1y",
                "capital": 10000.0,
                "exchange": "binance"
            }
        }


class BacktestRequest(AnalyzeRequest):
    """
    Request model for backtesting
    """
    start_date: Optional[str] = Field(None, description="Start date for backtest (ISO format)")
    end_date: Optional[str] = Field(None, description="End date for backtest (ISO format)")
    strategy: str = Field(default="default", description="Strategy to backtest")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "1d",
                "period": "5y",
                "capital": 10000.0,
                "start_date": "2020-01-01",
                "end_date": "2021-12-31",
                "strategy": "trend_following"
            }
        } 