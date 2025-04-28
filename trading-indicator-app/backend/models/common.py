"""
Common models used across the application
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from enum import Enum


class TimeFrame(str, Enum):
    """Time frame for analysis"""
    MIN_1 = "1m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"


class Period(str, Enum):
    """Historical data period"""
    DAY_1 = "1d"
    DAY_5 = "5d"
    MONTH_1 = "1mo"
    MONTH_3 = "3mo"
    MONTH_6 = "6mo"
    YEAR_1 = "1y"
    YEAR_2 = "2y"
    YEAR_5 = "5y"
    MAX = "max"


class SignalType(str, Enum):
    """Trading signal type"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WEAK_BUY = "WEAK_BUY"
    NEUTRAL = "NEUTRAL"
    WEAK_SELL = "WEAK_SELL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class SymbolInfo(BaseModel):
    """Symbol information"""
    symbol: str = Field(..., description="Symbol")
    name: str = Field(..., description="Human-readable name")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc."
            }
        }


class OHLCV(BaseModel):
    """Open-High-Low-Close-Volume data"""
    date: str = Field(..., description="Date in ISO format")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2023-01-01T00:00:00.000Z",
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 152.5,
                "volume": 10000000
            }
        }


class MarketRegime(BaseModel):
    """Market regime information"""
    type: str = Field(..., description="Regime type (trending, ranging, volatile)")
    trend_strength: Optional[float] = Field(0.0, description="Trend strength (0-1)")
    volatility: str = Field(..., description="Volatility level (low, medium, high)")
    adx: Optional[float] = Field(None, description="ADX value")
    volatility_value: Optional[float] = Field(None, description="Volatility value")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "trending",
                "trend_strength": 0.75,
                "volatility": "medium"
            }
        }


class SignalMetrics(BaseModel):
    """Trading signal component metrics"""
    trend_score: Optional[float] = Field(0.0, description="Trend analysis score (-1 to 1)")
    momentum_score: Optional[float] = Field(0.0, description="Momentum score (-1 to 1)")
    volatility_score: Optional[float] = Field(0.0, description="Volatility score (-1 to 1)")
    volume_score: Optional[float] = Field(0.0, description="Volume analysis score (-1 to 1)")
    pattern_score: Optional[float] = Field(0.0, description="Chart pattern score (-1 to 1)")
    support_resistance_score: Optional[float] = Field(0.0, description="Support/resistance score (-1 to 1)")
    
    class Config:
        schema_extra = {
            "example": {
                "trend_score": 0.7,
                "momentum_score": 0.5,
                "volatility_score": 0.2,
                "volume_score": 0.6,
                "pattern_score": 0.3,
                "support_resistance_score": 0.4
            }
        }


class ValidationInfo(BaseModel):
    """Signal validation information"""
    original_signal: str = Field(..., description="Original signal before validation")
    original_confidence: float = Field(..., description="Original confidence before validation")
    adjusted_confidence: Optional[float] = Field(None, description="Adjusted confidence after validation")
    regime_compatibility: Optional[float] = Field(None, description="Market regime compatibility (0-1)")
    warning_flags: List[str] = Field(default_factory=list, description="Warning flags raised during validation")
    
    class Config:
        schema_extra = {
            "example": {
                "original_signal": "STRONG_BUY",
                "original_confidence": 0.85,
                "adjusted_confidence": 0.75,
                "regime_compatibility": 0.8,
                "warning_flags": ["Signal in volatile market - reduced confidence"]
            }
        } 