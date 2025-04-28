"""
Analysis response models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from .common import MarketRegime, SignalMetrics, ValidationInfo, SignalType


class PositionData(BaseModel):
    """Position sizing information"""
    total_capital: float = Field(..., description="Total available capital")
    risk_percent: float = Field(..., description="Risk percent per trade")
    risk_per_share: Optional[float] = Field(None, description="Risk amount per share/unit")
    risk_amount: Optional[float] = Field(0.0, description="Total risk amount")
    max_position_size_percent: float = Field(..., description="Maximum position size as percent of capital")
    position_size_dollars: Optional[float] = Field(0.0, description="Position size in dollars")
    position_size_units: Optional[float] = Field(0.0, description="Position size in units/shares")
    entry_price: float = Field(..., description="Entry price")
    stop_loss_price: float = Field(..., description="Stop loss price")
    take_profit_price: float = Field(..., description="Take profit price")
    potential_profit_dollars: Optional[float] = Field(0.0, description="Potential profit in dollars")
    risk_reward_ratio: float = Field(..., description="Risk/reward ratio")
    position_adjustment: Optional[float] = Field(None, description="Position size adjustment factor")


class PyramidingLevel(BaseModel):
    """Pyramiding level information"""
    level: int = Field(..., description="Pyramiding level number")
    price: float = Field(..., description="Entry price for this level")
    position_dollars: float = Field(..., description="Position size in dollars")
    position_units: float = Field(..., description="Position size in units/shares")


class PyramidingData(BaseModel):
    """Pyramiding strategy information"""
    pyramiding_enabled: bool = Field(..., description="Whether pyramiding is enabled")
    total_position_dollars: Optional[float] = Field(None, description="Total position size in dollars")
    total_position_percent: Optional[float] = Field(None, description="Total position as percent of capital")
    levels: Optional[List[PyramidingLevel]] = Field(None, description="Pyramiding levels")
    error: Optional[str] = Field(None, description="Error message if any")


class CapitalEfficiency(BaseModel):
    """Capital efficiency analysis"""
    expected_value: Optional[float] = Field(0.0, description="Expected value of the trade")
    capital_usage_percent: Optional[float] = Field(0.0, description="Capital usage as percentage")
    estimated_win_rate: Optional[float] = Field(0.5, description="Estimated win rate")
    kelly_criterion: Optional[float] = Field(0.0, description="Kelly criterion")
    optimal_position_percent: Optional[float] = Field(0.1, description="Optimal position size percent")
    position_vs_optimal: Optional[float] = Field(0.0, description="Actual position vs optimal ratio")
    error: Optional[str] = Field(None, description="Error message if calculation failed")


class SignalAnalysis(BaseModel):
    """Trading signal analysis"""
    signal: SignalType = Field(..., description="Trading signal (STRONG_BUY, BUY, etc.)")
    confidence: float = Field(..., description="Signal confidence (0-1)")
    reasons: List[str] = Field(..., description="Reasons for the signal")
    signal_metrics: Optional[SignalMetrics] = Field(None, description="Component scores for the signal")
    patterns: Optional[List[str]] = Field(None, description="Detected chart patterns")
    divergences: Optional[List[str]] = Field(None, description="Detected divergences")
    market_regime: Optional[MarketRegime] = Field(None, description="Market regime analysis")
    support_levels: Optional[List[float]] = Field(None, description="Support levels")
    resistance_levels: Optional[List[float]] = Field(None, description="Resistance levels")
    entry_price: float = Field(..., description="Recommended entry price")
    stop_loss: float = Field(..., description="Recommended stop loss")
    take_profit: float = Field(..., description="Recommended take profit")
    validation: Optional[ValidationInfo] = Field(None, description="Signal validation information")


class AnalyzeResponse(BaseModel):
    """
    Response model for market analysis
    """
    ticker: str = Field(..., description="Analyzed symbol")
    timeframe: str = Field(..., description="Timeframe used for analysis")
    period: str = Field(..., description="Period used for analysis")
    last_price: float = Field(..., description="Last/current price")
    last_updated: str = Field(..., description="Last updated timestamp")
    signals: SignalAnalysis = Field(..., description="Trading signals and analysis")
    position: PositionData = Field(..., description="Position sizing information")
    pyramiding: Optional[PyramidingData] = Field(None, description="Pyramiding strategy information")
    capital_efficiency: Optional[CapitalEfficiency] = Field(None, description="Capital efficiency analysis")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "1d",
                "period": "1y",
                "last_price": 150.75,
                "last_updated": "2023-01-01T12:00:00.000Z",
                "signals": {
                    "signal": "BUY",
                    "confidence": 0.75,
                    "reasons": [
                        "Strong uptrend identified with price above key moving averages",
                        "Improving momentum with oscillators in bullish territory"
                    ],
                    "signal_metrics": {
                        "trend_score": 0.7,
                        "momentum_score": 0.5,
                        "volatility_score": 0.2,
                        "volume_score": 0.6,
                        "pattern_score": 0.3,
                        "support_resistance_score": 0.4
                    },
                    "market_regime": {
                        "type": "trending",
                        "trend_strength": 0.75,
                        "volatility": "medium"
                    },
                    "entry_price": 150.75,
                    "stop_loss": 145.0,
                    "take_profit": 160.0
                },
                "position": {
                    "total_capital": 10000.0,
                    "risk_percent": 0.02,
                    "risk_per_share": 5.75,
                    "risk_amount": 200.0,
                    "max_position_size_percent": 0.2,
                    "position_size_dollars": 2000.0,
                    "position_size_units": 13.27,
                    "entry_price": 150.75,
                    "stop_loss_price": 145.0,
                    "take_profit_price": 160.0,
                    "potential_profit_dollars": 122.65,
                    "risk_reward_ratio": 2.17
                }
            }
        }


class ForexAnalyzeResponse(AnalyzeResponse):
    """
    Response model for forex pair analysis
    """
    base_currency: str = Field(..., description="Base currency")
    quote_currency: str = Field(..., description="Quote currency")
    pip_value: float = Field(..., description="Pip value")
    position_in_lots: Optional[float] = Field(None, description="Position size in lots")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "EUR/USD",
                "timeframe": "1h",
                "period": "3mo",
                "last_price": 1.0825,
                "last_updated": "2023-01-01T12:00:00.000Z",
                "base_currency": "EUR",
                "quote_currency": "USD",
                "pip_value": 10.0,
                "position_in_lots": 0.2,
                "signals": {
                    "signal": "BUY",
                    "confidence": 0.75,
                    "reasons": [
                        "Strong uptrend identified with price above key moving averages",
                        "Improving momentum with oscillators in bullish territory"
                    ]
                }
            }
        }


class BacktestResponse(BaseModel):
    """
    Response model for backtesting
    """
    ticker: str = Field(..., description="Analyzed symbol")
    timeframe: str = Field(..., description="Timeframe used for backtest")
    start_date: str = Field(..., description="Backtest start date")
    end_date: str = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., description="Initial capital")
    final_capital: float = Field(..., description="Final capital")
    total_return_pct: float = Field(..., description="Total return percentage")
    annualized_return_pct: float = Field(..., description="Annualized return percentage")
    max_drawdown_pct: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate")
    profit_factor: float = Field(..., description="Profit factor")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    total_trades: int = Field(..., description="Total number of trades")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "timeframe": "1d",
                "start_date": "2020-01-01",
                "end_date": "2021-12-31",
                "initial_capital": 10000.0,
                "final_capital": 15250.0,
                "total_return_pct": 52.5,
                "annualized_return_pct": 26.25,
                "max_drawdown_pct": 12.3,
                "win_rate": 0.65,
                "profit_factor": 2.4,
                "sharpe_ratio": 1.8,
                "total_trades": 45
            }
        } 