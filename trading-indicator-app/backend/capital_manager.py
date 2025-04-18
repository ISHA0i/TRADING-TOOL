def calculate_position(signals, capital, current_price):
    """
    Calculate position size, risk management, and capital allocation
    
    Args:
        signals: Dictionary containing signal data
        capital: Total capital available
        current_price: Current asset price
        
    Returns:
        Dictionary with position sizing and risk management details
    """
    # Initialize capital management plan
    capital_plan = {
        "total_capital": capital,
        "risk_percent": 1.0,  # Default risk 1% of total capital
        "max_position_size_percent": 10.0,  # Default max position size 10% of capital
        "position_size_usd": 0.0,
        "position_size_units": 0.0,
        "stop_loss_usd": 0.0,
        "potential_profit_usd": 0.0,
        "risk_reward_ratio": 0.0,
        "kelly_criterion": 0.0,
        "volatility_adjusted_size": 0.0,
        "portfolio_risk": 0.0,
        "market_conditions": {}
    }
    
    signal_strength = signals["confidence"]
    signal_type = signals["signal"]
    stop_loss = signals["stop_loss"]
    take_profit = signals["take_profit"]
    
    # Skip if neutral signal or missing stop loss
    if signal_type == "NEUTRAL" or stop_loss is None:
        return capital_plan

    # Check if this is a crypto asset by looking for BTC price
    is_crypto = "bitcoin_price" in signals
    
    # For crypto assets, adjust risk based on market conditions
    if is_crypto:
        # Reduce position size for highly volatile crypto assets
        if signals.get("volatility_adjusted_size", 0) > 2.0:
            capital_plan["max_position_size_percent"] = 5.0  # Reduce max position size
        
        # Check BTC correlation for risk adjustment
        if any("correlation with BTC" in reason for reason in signals.get("reasons", [])):
            capital_plan["risk_percent"] = 0.75  # Reduce risk for highly correlated assets
    
    # Calculate market conditions with safe division
    bb_upper = signals.get('BB_upper', current_price)
    bb_lower = signals.get('BB_lower', current_price)
    bb_range = bb_upper - bb_lower
    
    # Safe calculation of BB position with fallback to 0.5 for zero range
    if bb_range != 0:
        bb_position = (current_price - bb_lower) / bb_range
    else:
        bb_position = 0.5  # Neutral position when range is zero
    
    market_conditions = {
        'rsi': signals.get('RSI14', 50),
        'macd_hist': signals.get('MACD_hist', 0),
        'bb_position': bb_position,
        'volume_ratio': signals.get('volume_ratio', 1.0),
        'obv_trend': 1 if signals.get('OBV_trend', False) else -1,
        'cmf': signals.get('CMF', 0)
    }
    capital_plan['market_conditions'] = market_conditions
    
    # Calculate dynamic position size
    volatility = signals.get('ATR', 0)
    trend_strength = signals.get('ADX', 0)
    position_size_percent = calculate_dynamic_position_size(
        capital, volatility, trend_strength, signal_strength, market_conditions, is_crypto
    )
    
    # Calculate Kelly Criterion
    win_probability = signal_strength
    win_loss_ratio = 2.0
    kelly = (win_probability * (win_loss_ratio + 1) - 1) / win_loss_ratio
    kelly = max(0, min(kelly, 0.5))
    capital_plan["kelly_criterion"] = round(kelly, 4)
    
    # Apply Kelly to position size
    position_size_percent *= kelly
    
    # Calculate dollar risk amount
    risk_amount = capital * (capital_plan["risk_percent"] / 100)
    
    # Calculate price risk
    if signal_type in ["BUY", "STRONG_BUY"]:
        price_risk_per_unit = current_price - stop_loss
    else:
        price_risk_per_unit = stop_loss - current_price
    
    # Calculate position size
    if price_risk_per_unit > 0:
        position_size_units = risk_amount / price_risk_per_unit
        position_size_usd = position_size_units * current_price
    else:
        position_size_usd = capital * 0.02
        position_size_units = position_size_usd / current_price
    
    # Apply maximum position constraint
    max_position_usd = capital * (capital_plan["max_position_size_percent"] / 100)
    if position_size_usd > max_position_usd:
        position_size_usd = max_position_usd
        position_size_units = position_size_usd / current_price
    
    # Calculate potential profit/loss
    if signal_type in ["BUY", "STRONG_BUY"]:
        stop_loss_usd = position_size_units * stop_loss
        take_profit_usd = position_size_units * take_profit
        potential_loss = position_size_usd - stop_loss_usd
        potential_profit = take_profit_usd - position_size_usd
    else:
        stop_loss_usd = position_size_units * stop_loss
        take_profit_usd = position_size_units * take_profit
        potential_loss = stop_loss_usd - position_size_usd
        potential_profit = position_size_usd - take_profit_usd
    
    # Calculate risk metrics
    risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
    portfolio_risk = (potential_loss / capital) * 100
    
    # Update capital plan
    capital_plan.update({
        "position_size_usd": round(position_size_usd, 2),
        "position_size_units": round(position_size_units, 8 if is_crypto else 4),  # More decimals for crypto
        "stop_loss_usd": round(potential_loss, 2),
        "potential_profit_usd": round(potential_profit, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 2),
        "portfolio_risk": round(portfolio_risk, 2),
        "volatility_adjusted_size": round(position_size_percent * 100, 2)
    })
    
    return capital_plan

def calculate_trailing_stop(current_price, entry_price, atr, signal_type):
    """
    Calculate trailing stop loss levels
    
    Args:
        current_price: Current asset price
        entry_price: Entry price of the position
        atr: Average True Range
        signal_type: Type of signal (BUY/SELL)
        
    Returns:
        Trailing stop loss level
    """
    # Base trailing stop distance
    base_distance = atr * 1.5
    
    # Adjust trailing stop based on profit
    if signal_type in ["BUY", "STRONG_BUY"]:
        profit = current_price - entry_price
        if profit > atr * 2:  # If profit is more than 2 ATR
            trailing_stop = current_price - (atr * 1.0)  # Tighten stop
        else:
            trailing_stop = current_price - base_distance
    else:  # SELL or STRONG_SELL
        profit = entry_price - current_price
        if profit > atr * 2:
            trailing_stop = current_price + (atr * 1.0)
        else:
            trailing_stop = current_price + base_distance
    
    return round(trailing_stop, 2)

def calculate_dynamic_position_size(capital, volatility, trend_strength, signal_confidence, market_conditions, is_crypto=False):
    """
    Calculate dynamic position size based on market conditions
    
    Args:
        capital: Total capital available
        volatility: Current market volatility (ATR)
        trend_strength: Strength of the trend (ADX)
        signal_confidence: Confidence in the signal
        market_conditions: Dictionary containing market condition metrics
        is_crypto: Boolean indicating if the asset is a cryptocurrency
        
    Returns:
        Dynamic position size as percentage of capital
    """
    # Base position size - lower for crypto
    base_size = 0.01 if is_crypto else 0.02  # 1% for crypto, 2% for others
    
    # Market condition factors
    volatility_factor = calculate_volatility_factor(volatility, capital, is_crypto)
    trend_factor = calculate_trend_factor(trend_strength)
    confidence_factor = calculate_confidence_factor(signal_confidence)
    market_phase_factor = calculate_market_phase_factor(market_conditions)
    volume_factor = calculate_volume_factor(market_conditions)
    
    # For crypto, add extra risk adjustments
    if is_crypto:
        # Reduce position size during high volatility periods
        if volatility_factor < 0.7:
            base_size *= 0.75
        
        # Reduce position size during weekends (typically lower volume)
        from datetime import datetime
        if datetime.now().weekday() in [5, 6]:  # Weekend
            base_size *= 0.8
    
    # Calculate final position size
    position_size = base_size * volatility_factor * trend_factor * confidence_factor * market_phase_factor * volume_factor
    
    # Apply maximum position constraint (stricter for crypto)
    max_size = 0.05 if is_crypto else 0.1  # 5% for crypto, 10% for others
    return min(max_size, position_size)

def calculate_volatility_factor(volatility, capital, is_crypto=False):
    """Calculate position size adjustment based on volatility"""
    # Normalize volatility relative to capital
    normalized_volatility = volatility / capital
    
    # Stricter thresholds for crypto
    if is_crypto:
        if normalized_volatility > 0.1:  # Very high volatility
            return 0.3
        elif normalized_volatility > 0.05:  # High volatility
            return 0.5
        elif normalized_volatility > 0.02:  # Medium volatility
            return 0.7
        else:  # Low volatility
            return 1.0
    else:
        if normalized_volatility > 0.05:  # Very high volatility
            return 0.5
        elif normalized_volatility > 0.02:  # High volatility
            return 0.7
        elif normalized_volatility > 0.01:  # Medium volatility
            return 0.9
        else:  # Low volatility
            return 1.0

def calculate_trend_factor(trend_strength):
    """Calculate position size adjustment based on trend strength"""
    # Stronger trend = larger position size
    if trend_strength > 40:  # Very strong trend
        return 1.5
    elif trend_strength > 25:  # Strong trend
        return 1.2
    elif trend_strength > 15:  # Moderate trend
        return 1.0
    else:  # Weak or no trend
        return 0.8

def calculate_confidence_factor(signal_confidence):
    """Calculate position size adjustment based on signal confidence"""
    # Higher confidence = larger position size
    if signal_confidence > 0.8:  # Very high confidence
        return 1.3
    elif signal_confidence > 0.6:  # High confidence
        return 1.1
    elif signal_confidence > 0.4:  # Moderate confidence
        return 1.0
    else:  # Low confidence
        return 0.7

def calculate_market_phase_factor(market_conditions):
    """Calculate position size adjustment based on market phase"""
    # Get market phase indicators
    rsi = market_conditions.get('rsi', 50)
    macd_hist = market_conditions.get('macd_hist', 0)
    bb_position = market_conditions.get('bb_position', 0.5)
    
    # Determine market phase
    if rsi < 30 or rsi > 70:  # Overbought/oversold
        return 0.7
    elif (rsi > 40 and rsi < 60) and abs(macd_hist) < 0.5:  # Range-bound
        return 0.8
    elif (rsi > 50 and macd_hist > 0) or (rsi < 50 and macd_hist < 0):  # Trending
        return 1.2
    else:  # Transition phase
        return 1.0

def calculate_volume_factor(market_conditions):
    """Calculate position size adjustment based on volume conditions"""
    # Get volume indicators
    volume_ratio = market_conditions.get('volume_ratio', 1.0)
    obv_trend = market_conditions.get('obv_trend', 0)
    cmf = market_conditions.get('cmf', 0)
    
    # Calculate volume factor
    if volume_ratio > 2.0 and obv_trend > 0 and cmf > 0.1:  # Strong volume confirmation
        return 1.3
    elif volume_ratio > 1.5 and (obv_trend > 0 or cmf > 0):  # Good volume confirmation
        return 1.1
    elif volume_ratio < 0.8 or (obv_trend < 0 and cmf < 0):  # Weak volume
        return 0.7
    else:  # Neutral volume
        return 1.0

def calculate_portfolio_risk(positions, total_capital):
    """
    Calculate total portfolio risk
    
    Args:
        positions: List of current positions
        total_capital: Total portfolio capital
        
    Returns:
        Portfolio risk metrics
    """
    total_risk = 0
    max_drawdown = 0
    position_risks = []
    
    for position in positions:
        risk_amount = position.get('stop_loss_usd', 0)
        total_risk += risk_amount
        position_risks.append({
            'symbol': position.get('symbol'),
            'risk_percent': (risk_amount / total_capital) * 100
        })
    
    portfolio_risk_percent = (total_risk / total_capital) * 100
    
    return {
        'total_risk_usd': round(total_risk, 2),
        'portfolio_risk_percent': round(portfolio_risk_percent, 2),
        'position_risks': position_risks,
        'max_drawdown': round(max_drawdown, 2)
    }