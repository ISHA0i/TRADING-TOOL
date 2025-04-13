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
        "risk_reward_ratio": 0.0
    }
    
    signal_strength = signals["confidence"]
    signal_type = signals["signal"]
    stop_loss = signals["stop_loss"]
    take_profit = signals["take_profit"]
    
    # Skip if neutral signal or missing stop loss
    if signal_type == "NEUTRAL" or stop_loss is None:
        return capital_plan
    
    # Adjust risk percentage based on signal strength
    if signal_type in ["STRONG_BUY", "STRONG_SELL"]:
        # More confident signals can risk slightly more
        capital_plan["risk_percent"] = min(1.5, 1.0 + signal_strength)
    else:
        # Less confident signals risk less
        capital_plan["risk_percent"] = max(0.5, signal_strength)
    
    # Calculate dollar risk amount (max we're willing to lose)
    risk_amount = capital * (capital_plan["risk_percent"] / 100)
    
    # Calculate price risk (distance to stop loss)
    if signal_type in ["BUY", "STRONG_BUY"]:
        price_risk_per_unit = current_price - stop_loss
    else:  # SELL or STRONG_SELL
        price_risk_per_unit = stop_loss - current_price
    
    # Calculate position size based on risk
    if price_risk_per_unit > 0:
        position_size_units = risk_amount / price_risk_per_unit
        position_size_usd = position_size_units * current_price
    else:
        # Fallback if stop loss is invalid
        position_size_usd = capital * 0.02  # Default to 2% of capital
        position_size_units = position_size_usd / current_price
    
    # Apply maximum position constraint
    max_position_usd = capital * (capital_plan["max_position_size_percent"] / 100)
    if position_size_usd > max_position_usd:
        position_size_usd = max_position_usd
        position_size_units = position_size_usd / current_price
    
    # Calculate potential profit and stop loss
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
    
    # Calculate risk/reward ratio
    risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
    
    # Update capital plan
    capital_plan.update({
        "position_size_usd": round(position_size_usd, 2),
        "position_size_units": round(position_size_units, 4),
        "stop_loss_usd": round(potential_loss, 2),
        "potential_profit_usd": round(potential_profit, 2),
        "risk_reward_ratio": round(risk_reward_ratio, 2)
    })
    
    return capital_plan 