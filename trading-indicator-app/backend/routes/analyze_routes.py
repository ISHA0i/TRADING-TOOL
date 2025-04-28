"""
API routes for market analysis
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging
import datetime
import pandas as pd
import numpy as np

from models.analyze_request import AnalyzeRequest, ForexAnalyzeRequest, CryptoAnalyzeRequest
from models.analyze_response import AnalyzeResponse, ForexAnalyzeResponse
from controller.indicators_controller import IndicatorsController
from controller.strategy_controller import StrategyController
from controller.capital_manager_controller import CapitalManagerController
from controller.signal_validator_controller import SignalValidatorController
from utils.data_provider import get_market_data, get_symbol_info

logger = logging.getLogger(__name__)

# Initialize controllers
indicators_controller = IndicatorsController()
strategy_controller = StrategyController()
capital_manager_controller = CapitalManagerController()
signal_validator_controller = SignalValidatorController()

# Create router
router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/analyze/{ticker}", response_model=AnalyzeResponse)
@router.post("/analyze/{ticker}", response_model=AnalyzeResponse)
async def analyze_ticker(
    ticker: str,
    timeframe: str = Query(default="1d", description="Time frame for analysis"),
    period: str = Query(default="1y", description="Historical data period"),
    capital: float = Query(default=10000.0, description="Available capital")
):
    """
    Analyze a ticker and generate trading signals
    """
    try:
        logger.info(f"Analyzing {ticker} with timeframe={timeframe}, period={period}, capital={capital}")
        
        # Get market data
        data = get_market_data(ticker, timeframe, period)
        if data.empty:
            logger.error(f"No data found for ticker {ticker}")
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}. Please verify the symbol and try again."
            )
        
        # Ensure the data doesn't have NaN values that would cause issues
        data = data.ffill().bfill()  # Forward and backward fill to handle NaN values
        
        # Get symbol info
        symbol_info = get_symbol_info(ticker)
        
        # Default fallback values
        last_price = float(data['Close'].iloc[-1])
        default_signals = {
            "signal": "NEUTRAL",
            "confidence": 0.5,
            "reasons": ["Could not generate reliable signals based on available data"],
            "signal_metrics": {
                "trend_score": 0.0,
                "momentum_score": 0.0,
                "volatility_score": 0.0,
                "volume_score": 0.0,
                "pattern_score": 0.0,
                "support_resistance_score": 0.0
            },
            "market_regime": {
                "type": "unknown",
                "trend_strength": 0.0,
                "volatility": "unknown"
            },
            "entry_price": last_price,
            "stop_loss": last_price * 0.95,  # Default 5% below current price
            "take_profit": last_price * 1.1  # Default 10% above current price
        }
        
        # Calculate indicators
        try:
            indicators_data = indicators_controller.calculate_all(data)
            if indicators_data is None:
                logger.error("Indicator calculation returned None")
                indicators_data = data.copy()  # Use original data as fallback
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            indicators_data = data.copy()  # Use original data as fallback
        
        # Generate signals
        try:
            signals = strategy_controller.generate_signals(indicators_data)
            if not signals or "signal" not in signals:
                logger.error("Strategy controller returned invalid signals")
                signals = default_signals
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            signals = default_signals
        
        # Validate signals
        try:
            validated_signals = signal_validator_controller.validate_signal(signals, indicators_data)
            if not validated_signals or "signal" not in validated_signals:
                logger.error("Signal validation returned invalid signals")
                validated_signals = signals
        except Exception as e:
            logger.error(f"Error validating signals: {str(e)}")
            validated_signals = signals
        
        # Calculate position sizing
        default_position = {
            "total_capital": capital,
            "risk_percent": 0.02,  # Default 2%
            "risk_amount": capital * 0.02,
            "max_position_size_percent": 0.2,
            "position_size_dollars": capital * 0.1,  # Default 10%
            "position_size_units": (capital * 0.1) / last_price if last_price > 0 else 0,
            "entry_price": last_price,
            "stop_loss_price": last_price * 0.95,
            "take_profit_price": last_price * 1.1,
            "potential_profit_dollars": capital * 0.01,  # Default 1%
            "risk_reward_ratio": 2.0
        }
        
        try:
            position = capital_manager_controller.calculate_position(validated_signals, capital, last_price)
            if not position or "position_size_dollars" not in position:
                logger.error("Capital manager returned invalid position data")
                position = default_position
        except Exception as e:
            logger.error(f"Error calculating position: {str(e)}")
            position = default_position
        
        # Calculate pyramiding levels (optional)
        default_pyramiding = {"pyramiding_enabled": False}
        try:
            pyramiding = capital_manager_controller.calculate_pyramiding_levels(validated_signals, capital, last_price)
            if not pyramiding:
                logger.error("Capital manager returned invalid pyramiding data")
                pyramiding = default_pyramiding
        except Exception as e:
            logger.error(f"Error calculating pyramiding levels: {str(e)}")
            pyramiding = default_pyramiding
        
        # Analyze capital efficiency
        default_capital_efficiency = {
            "expected_value": 0.0,
            "capital_usage_percent": 0.0,
            "estimated_win_rate": 0.5,
            "kelly_criterion": 0.0,
            "optimal_position_percent": 0.10,
            "position_vs_optimal": 0.0
        }
        
        try:
            capital_efficiency = capital_manager_controller.analyze_capital_efficiency(validated_signals, position)
            if not capital_efficiency or not isinstance(capital_efficiency, dict):
                logger.error("Capital manager returned invalid capital efficiency data")
                capital_efficiency = default_capital_efficiency
            elif "error" in capital_efficiency:
                logger.warning(f"Capital efficiency calculation warning: {capital_efficiency['error']}")
        except Exception as e:
            logger.error(f"Error analyzing capital efficiency: {str(e)}")
            capital_efficiency = default_capital_efficiency
        
        # Sanitize response to handle NaN values before returning
        response = {
            "ticker": ticker,
            "timeframe": timeframe,
            "period": period,
            "last_price": float(last_price) if not np.isnan(last_price) else 0.0,
            "last_updated": datetime.datetime.now().isoformat(),
            "signals": _sanitize_nan_values(validated_signals),
            "position": _sanitize_nan_values(position),
            "pyramiding": _sanitize_nan_values(pyramiding),
            "capital_efficiency": _sanitize_nan_values(capital_efficiency)
        }
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing ticker: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

def _sanitize_nan_values(data):
    """
    Recursively sanitize a dictionary or list to replace NaN, infinity, and other 
    problematic values with appropriate defaults to ensure JSON serialization works properly.
    """
    # List of field names that require a float value (not None)
    required_float_fields = [
        'momentum_score', 'volatility_score', 'trend_strength',
        'risk_amount', 'position_size_dollars', 'position_size_units', 'potential_profit_dollars'
    ]
    
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            # If this is a field that needs a float value, use 0.0 instead of None
            if k in required_float_fields:
                if v is None or (isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v))):
                    result[k] = 0.0
                else:
                    result[k] = _sanitize_nan_values(v)
            else:
                result[k] = _sanitize_nan_values(v)
        return result
    elif isinstance(data, list):
        return [_sanitize_nan_values(item) for item in data]
    elif isinstance(data, (float, np.floating)):
        if np.isnan(data) or np.isinf(data) or abs(data) < 1e-10:
            return 0.0  # Use 0.0 as default for NaN/Inf numeric values to avoid None
        return float(data)
    elif isinstance(data, (int, np.integer)):
        return int(data)
    elif isinstance(data, np.bool_):
        return bool(data)
    else:
        return data

@router.post("/analyze/forex/{pair}", response_model=ForexAnalyzeResponse)
async def analyze_forex(
    pair: str,
    request: ForexAnalyzeRequest
):
    """
    Analyze a forex pair and generate trading signals
    """
    try:
        # Extract request parameters
        ticker = pair if pair else request.ticker
        timeframe = request.timeframe.value
        period = request.period.value
        capital = request.capital
        
        # Get base and quote currencies
        base_currency = request.base_currency
        quote_currency = request.quote_currency
        
        if not base_currency or not quote_currency:
            # Try to extract from ticker
            if '/' in ticker:
                parts = ticker.split('/')
                base_currency = parts[0]
                quote_currency = parts[1]
            else:
                # Default values
                base_currency = ticker[:3]
                quote_currency = ticker[3:]
        
        # Get basic analysis
        response = await analyze_ticker(ticker, timeframe, period, capital)
        
        # Add forex-specific fields
        response["base_currency"] = base_currency
        response["quote_currency"] = quote_currency
        
        # Calculate pip value (standard 0.0001 for most pairs)
        pip_value = 0.0001 * response["position"]["position_size_units"] * 10
        response["pip_value"] = pip_value
        
        # Calculate position in lots (standard lot = 100,000 units)
        response["position_in_lots"] = response["position"]["position_size_units"] / 100000
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing forex pair: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) 