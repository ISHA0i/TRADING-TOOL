def calculate_position(signals, capital, current_price):
    """
    Calculate position size, risk management, and capital allocation with enhanced accuracy
    """
    # Initialize capital management plan with added metrics
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
        "market_conditions": {},
        "regime_adjustments": {}
    }
    
    signal_strength = signals["confidence"]
    signal_type = signals["signal"]
    stop_loss = signals["stop_loss"]
    take_profit = signals["take_profit"]
    validation = signals.get("validation", {})
    market_regime = signals.get("market_regime", {})
    
    # Skip if neutral signal or missing stop loss
    if signal_type == "NEUTRAL" or stop_loss is None:
        return capital_plan

    # Adjust risk based on market regime
    regime_type = market_regime.get('type', 'unknown')
    regime_volatility = market_regime.get('volatility', 'normal')
    regime_confidence = market_regime.get('confidence', 0.5)
    
    # Store regime adjustments for transparency
    capital_plan['regime_adjustments'] = {
        'type': regime_type,
        'volatility': regime_volatility,
        'base_adjustment': 0.0,
        'volatility_adjustment': 0.0
    }
    
    # Adjust base risk percent based on regime
    if regime_type == 'trending' and regime_confidence > 0.7:
        capital_plan["risk_percent"] = 1.2  # Increase risk in strong trends
        capital_plan['regime_adjustments']['base_adjustment'] = 0.2
    elif regime_type == 'ranging':
        capital_plan["risk_percent"] = 0.8  # Reduce risk in ranging markets
        capital_plan['regime_adjustments']['base_adjustment'] = -0.2
    elif regime_type == 'volatile':
        capital_plan["risk_percent"] = 0.6  # Significantly reduce risk in volatile markets
        capital_plan['regime_adjustments']['base_adjustment'] = -0.4
    
    # Further adjust based on volatility
    if regime_volatility == 'high':
        capital_plan["risk_percent"] *= 0.8
        capital_plan['regime_adjustments']['volatility_adjustment'] = -0.2
    elif regime_volatility == 'low':
        capital_plan["risk_percent"] *= 1.2
        capital_plan['regime_adjustments']['volatility_adjustment'] = 0.2
    
    # Adjust position size based on validation metrics
    if validation:
        adjusted_confidence = validation.get('adjusted_confidence', signal_strength)
        regime_compatibility = validation.get('regime_compatibility', 0)
        historical_accuracy = validation.get('historical_accuracy', 0)
        
        # Reduce position size if validation shows concerns
        if adjusted_confidence < signal_strength:
            size_adjustment = adjusted_confidence / max(signal_strength, 0.1)
            capital_plan["max_position_size_percent"] *= size_adjustment
        
        # Adjust based on historical accuracy
        if historical_accuracy < 0:
            capital_plan["risk_percent"] *= (1 + historical_accuracy)  # Reduce risk for poor historical performance
    
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
    
    # Calculate Kelly Criterion with validation-adjusted confidence
    win_probability = validation.get('adjusted_confidence', signal_strength)
    risk_amount = abs(current_price - stop_loss)
    reward_amount = abs(take_profit - current_price)
    
    if risk_amount > 0:
        win_loss_ratio = reward_amount / risk_amount
        kelly = (win_probability * (win_loss_ratio + 1) - 1) / win_loss_ratio
        kelly = max(0, min(kelly, 0.5))  # Cap Kelly at 50%
        capital_plan["kelly_criterion"] = round(kelly, 4)
    
    # Calculate dollar risk amount with adjusted risk percentage
    risk_amount = capital * (capital_plan["risk_percent"] / 100)
    
    # Calculate position size based on risk
    if signal_type in ["BUY", "STRONG_BUY"]:
        price_risk = current_price - stop_loss
        if price_risk > 0:
            position_size_units = risk_amount / price_risk
            position_size_usd = position_size_units * current_price
    else:  # SELL or STRONG_SELL
        price_risk = stop_loss - current_price
        if price_risk > 0:
            position_size_units = risk_amount / price_risk
            position_size_usd = position_size_units * current_price
    
    # Apply Kelly criterion to position size
    position_size_usd *= kelly
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
    else:  # SELL or STRONG_SELL
        stop_loss_usd = position_size_units * stop_loss
        take_profit_usd = position_size_units * take_profit
        potential_loss = stop_loss_usd - position_size_usd
        potential_profit = position_size_usd - take_profit_usd
    
    # Calculate risk metrics
    risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
    portfolio_risk = (potential_loss / capital) * 100
    
    # Store market conditions
    market_conditions = {
        'regime_type': regime_type,
        'volatility': regime_volatility,
        'trend_strength': market_regime.get('trend_strength', 0),
        'historical_accuracy': validation.get('historical_accuracy', 0),
        'volume_profile': validation.get('volume_profile_score', 0),
        'warning_flags': validation.get('warning_flags', [])
    }
    
    # Update capital plan
    capital_plan.update({
        "position_size_usd": round(position_size_usd, 2),
        "position_size_units": round(position_size_units, 8 if is_crypto else 4),
        "stop_loss_usd": round(potential_loss, 2),
        "potential_profit_usd": round(potential_profit, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 2),
        "portfolio_risk": round(portfolio_risk, 2),
        "volatility_adjusted_size": round(capital_plan["max_position_size_percent"], 2),
        "market_conditions": market_conditions
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

def calculate_position_size(total_capital, risk_per_trade, entry_price, stop_loss, take_profit, market_regime):
    """
    Calculate optimal position size based on risk parameters and market conditions
    
    Args:
        total_capital: Total available capital
        risk_per_trade: Maximum risk per trade as decimal (e.g., 0.01 for 1%)
        entry_price: Entry price of the position
        stop_loss: Stop loss price
        take_profit: Take profit price
        market_regime: Market regime information
        
    Returns:
        Dictionary with position sizing information
    """
    # Base risk amount
    max_risk_amount = total_capital * risk_per_trade
    
    # Calculate risk per unit
    risk_per_unit = abs(entry_price - stop_loss)
    if risk_per_unit == 0:
        return None
    
    # Calculate potential reward per unit
    reward_per_unit = abs(take_profit - entry_price)
    
    # Base position size calculation
    base_position_units = max_risk_amount / risk_per_unit
    
    # Adjust position size based on market regime
    regime_type = market_regime.get('type', 'unknown')
    regime_confidence = market_regime.get('confidence', 0.5)
    volatility = market_regime.get('volatility', 'normal')
    
    # Position size multiplier based on market conditions
    position_multiplier = 1.0
    
    # Adjust for regime type
    if regime_type == 'trending' and regime_confidence > 0.7:
        position_multiplier *= 1.2  # Increase size in strong trends
    elif regime_type == 'ranging':
        position_multiplier *= 0.8  # Reduce size in ranging markets
    elif regime_type == 'volatile':
        position_multiplier *= 0.6  # Significantly reduce size in volatile markets
    
    # Adjust for volatility
    if volatility == 'high':
        position_multiplier *= 0.7
    elif volatility == 'low':
        position_multiplier *= 1.1
    
    # Apply Kelly Criterion adjustment
    win_rate = 0.5  # Default to neutral
    if regime_confidence > 0.7:
        win_rate = 0.65  # Higher win rate in high-confidence setups
    
    risk_reward_ratio = reward_per_unit / risk_per_unit if risk_per_unit > 0 else 0
    kelly_fraction = win_rate - ((1 - win_rate) / risk_reward_ratio) if risk_reward_ratio > 0 else 0
    kelly_fraction = max(0, min(kelly_fraction, 0.5))  # Cap at 50% of Kelly
    
    # Final position size calculation
    adjusted_position_units = base_position_units * position_multiplier * kelly_fraction
    
    # Maximum position size constraints
    max_position_percent = 0.1  # 10% of capital maximum
    max_position_size = total_capital * max_position_percent
    position_size_usd = min(adjusted_position_units * entry_price, max_position_size)
    final_position_units = position_size_usd / entry_price
    
    # Calculate actual risk and potential profit
    actual_risk_usd = final_position_units * risk_per_unit
    potential_profit_usd = final_position_units * reward_per_unit
    
    return {
        "total_capital": total_capital,
        "risk_percent": risk_per_trade * 100,
        "max_position_size_percent": max_position_percent * 100,
        "position_size_usd": position_size_usd,
        "position_size_units": final_position_units,
        "stop_loss_usd": actual_risk_usd,
        "potential_profit_usd": potential_profit_usd,
        "risk_reward_ratio": risk_reward_ratio,
        "kelly_criterion": kelly_fraction,
        "position_multiplier": position_multiplier,
        "regime_adjustments": {
            "type": regime_type,
            "confidence": regime_confidence,
            "volatility": volatility,
            "size_adjustment": ((position_multiplier - 1) * 100)
        }
    }