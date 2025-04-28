"""
Market regime detection utilities
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def detect_market_regime(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect market regime from price data
    
    Args:
        data (pd.DataFrame): Market data with OHLCV and indicators
        
    Returns:
        dict: Market regime information
    """
    try:
        if data.empty or len(data) < 20:
            logger.warning("Insufficient data for market regime detection")
            return {
                "type": "unknown",
                "trend_strength": 0,
                "volatility": "unknown"
            }
        
        # Calculate ADX if not already calculated
        if 'ADX' not in data.columns:
            adx = calculate_adx(data)
        else:
            adx = data['ADX']
        
        # Get the most recent ADX value
        latest_adx = adx.iloc[-1] if not adx.empty and not pd.isna(adx.iloc[-1]) else 0
        
        # Calculate volatility (standard deviation of returns)
        returns = data['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * (252 ** 0.5)  # Annualized
        
        # Calculate trend direction using moving averages
        if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
            ma_diff = data['SMA_20'] - data['SMA_50']
            trend_direction = 1 if ma_diff.iloc[-1] > 0 else -1
        else:
            # Use basic price difference
            price_diff = data['Close'].diff(20)
            trend_direction = 1 if price_diff.iloc[-1] > 0 else -1
        
        # Determine regime type
        trend_strength = min(1.0, latest_adx / 100) if latest_adx > 0 else 0
        
        if latest_adx > 25:
            regime_type = "trending"
        elif volatility > returns.rolling(20).std().mean() * 1.5:
            regime_type = "volatile"
        else:
            regime_type = "ranging"
        
        # Determine volatility level
        if volatility > 0.3:
            volatility_level = "high"
        elif volatility > 0.15:
            volatility_level = "medium"
        else:
            volatility_level = "low"
        
        return {
            "type": regime_type,
            "trend_strength": trend_strength,
            "trend_direction": trend_direction,
            "volatility": volatility_level,
            "adx": latest_adx,
            "volatility_value": volatility
        }
        
    except Exception as e:
        logger.error(f"Error detecting market regime: {str(e)}")
        return {
            "type": "unknown",
            "trend_strength": 0,
            "volatility": "unknown",
            "error": str(e)
        }


def calculate_adx(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX)
    
    Args:
        data (pd.DataFrame): Market data with OHLCV columns
        period (int): ADX calculation period
        
    Returns:
        pd.Series: ADX values
    """
    try:
        # Calculate +DM, -DM, and TR
        high_diff = data['High'].diff()
        low_diff = data['Low'].diff().multiply(-1)
        
        # Calculate Directional Movement
        plus_dm = pd.Series(0.0, index=data.index)
        minus_dm = pd.Series(0.0, index=data.index)
        
        # +DM
        condition1 = (high_diff > low_diff) & (high_diff > 0)
        plus_dm[condition1] = high_diff[condition1]
        
        # -DM
        condition2 = (low_diff > high_diff) & (low_diff > 0)
        minus_dm[condition2] = low_diff[condition2]
        
        # Calculate True Range
        tr1 = data['High'] - data['Low']
        tr2 = (data['High'] - data['Close'].shift(1)).abs()
        tr3 = (data['Low'] - data['Close'].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Smooth the indicators
        smoothed_plus_dm = plus_dm.rolling(period).sum()
        smoothed_minus_dm = minus_dm.rolling(period).sum()
        smoothed_tr = tr.rolling(period).sum()
        
        # Calculate +DI and -DI
        plus_di = 100 * (smoothed_plus_dm / smoothed_tr)
        minus_di = 100 * (smoothed_minus_dm / smoothed_tr)
        
        # Calculate DX
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        
        # Calculate ADX
        adx = dx.rolling(period).mean()
        
        return adx
        
    except Exception as e:
        logger.error(f"Error calculating ADX: {str(e)}")
        return pd.Series(dtype=float)


def detect_trend_change(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect changes in trend direction
    
    Args:
        data (pd.DataFrame): Market data with OHLCV and indicators
        
    Returns:
        dict: Trend change information
    """
    try:
        if data.empty or len(data) < 30:
            return {"trend_change": False}
        
        # Check for moving average crossovers
        has_crossover = False
        crossover_type = None
        
        if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
            # Get current and previous relationship
            current = data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1]
            previous = data['SMA_20'].iloc[-2] > data['SMA_50'].iloc[-2]
            
            # Detect crossover
            if current and not previous:
                has_crossover = True
                crossover_type = "bullish"
            elif not current and previous:
                has_crossover = True
                crossover_type = "bearish"
        
        # Check for higher highs/higher lows (for uptrend)
        price_data = data['Close'].tail(30)
        
        # Identify local maxima and minima
        peaks = []
        troughs = []
        
        for i in range(1, len(price_data) - 1):
            if price_data.iloc[i] > price_data.iloc[i-1] and price_data.iloc[i] > price_data.iloc[i+1]:
                peaks.append((i, price_data.iloc[i]))
            elif price_data.iloc[i] < price_data.iloc[i-1] and price_data.iloc[i] < price_data.iloc[i+1]:
                troughs.append((i, price_data.iloc[i]))
        
        # Need at least 2 peaks/troughs to identify a trend
        if len(peaks) >= 2 and len(troughs) >= 2:
            # Check if we have higher highs and higher lows (uptrend)
            higher_highs = peaks[-1][1] > peaks[-2][1]
            higher_lows = troughs[-1][1] > troughs[-2][1]
            
            # Check if we have lower highs and lower lows (downtrend)
            lower_highs = peaks[-1][1] < peaks[-2][1]
            lower_lows = troughs[-1][1] < troughs[-2][1]
            
            if higher_highs and higher_lows:
                trend_direction = "uptrend"
            elif lower_highs and lower_lows:
                trend_direction = "downtrend"
            else:
                trend_direction = "sideways"
        else:
            trend_direction = "undefined"
        
        return {
            "trend_change": has_crossover,
            "crossover_type": crossover_type,
            "trend_direction": trend_direction
        }
        
    except Exception as e:
        logger.error(f"Error detecting trend change: {str(e)}")
        return {"trend_change": False, "error": str(e)} 