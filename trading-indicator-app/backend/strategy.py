import pandas as pd
import numpy as np

def generate_signals(data):
    """Generate trading signals based on technical indicators"""
    df = data.copy()
    
    # Get most recent data point
    latest = df.iloc[-1]
    
    # Initialize signals dictionary
    signals = {
        "signal": "NEUTRAL",  # NEUTRAL, BUY, STRONG_BUY, SELL, STRONG_SELL
        "confidence": 0.0,    # 0.0 - 1.0
        "reasons": [],
        "support_levels": [],
        "resistance_levels": [],
        "entry_price": latest['Close'],
        "stop_loss": None,
        "take_profit": None
    }
    
    # Add signals based on indicators
    signals = check_trend_signals(df, signals)
    signals = check_oscillator_signals(df, signals)
    signals = check_volatility_signals(df, signals)
    signals = check_support_resistance(df, signals)
    
    # Calculate final signal and confidence
    signals = calculate_final_signal(signals)
    
    # Calculate stop loss and take profit levels
    signals = calculate_risk_reward_levels(df, signals)
    
    return signals

def check_trend_signals(df, signals):
    """Check for trend-based signals"""
    latest = df.iloc[-1]
    
    # Moving average crossovers
    if latest['EMA9'] > latest['EMA21']:
        signals['reasons'].append("EMA9 crossed above EMA21 (bullish)")
        signals['confidence'] += 0.1
    elif latest['EMA9'] < latest['EMA21']:
        signals['reasons'].append("EMA9 crossed below EMA21 (bearish)")
        signals['confidence'] -= 0.1
    
    # Price vs long-term SMA
    if latest['Close'] > latest['SMA200']:
        signals['reasons'].append("Price above SMA200 (bullish)")
        signals['confidence'] += 0.15
    else:
        signals['reasons'].append("Price below SMA200 (bearish)")
        signals['confidence'] -= 0.15
    
    # MACD signal
    if latest['MACD'] > latest['MACD_signal']:
        signals['reasons'].append("MACD above signal line (bullish)")
        signals['confidence'] += 0.15
    else:
        signals['reasons'].append("MACD below signal line (bearish)")
        signals['confidence'] -= 0.15
    
    # ADX Trend strength
    if latest['ADX'] > 25:
        signals['reasons'].append(f"Strong trend detected (ADX: {latest['ADX']:.2f})")
        # Amplify existing signals if trend is strong
        signals['confidence'] *= 1.2
    
    return signals

def check_oscillator_signals(df, signals):
    """Check for oscillator-based signals"""
    latest = df.iloc[-1]
    
    # RSI signals
    if latest['RSI14'] < 30:
        signals['reasons'].append(f"RSI oversold at {latest['RSI14']:.2f} (bullish)")
        signals['confidence'] += 0.2
    elif latest['RSI14'] > 70:
        signals['reasons'].append(f"RSI overbought at {latest['RSI14']:.2f} (bearish)")
        signals['confidence'] -= 0.2
    
    # Stochastic signals
    if latest['STOCH_K'] < 20 and latest['STOCH_D'] < 20:
        signals['reasons'].append("Stochastic oversold (bullish)")
        signals['confidence'] += 0.15
    elif latest['STOCH_K'] > 80 and latest['STOCH_D'] > 80:
        signals['reasons'].append("Stochastic overbought (bearish)")
        signals['confidence'] -= 0.15
    
    return signals

def check_volatility_signals(df, signals):
    """Check for volatility-based signals"""
    latest = df.iloc[-1]
    
    # Bollinger Band signals
    bb_width = (latest['BB_upper'] - latest['BB_lower']) / latest['BB_middle']
    
    if latest['Close'] < latest['BB_lower']:
        signals['reasons'].append("Price below lower Bollinger Band (potential reversal - bullish)")
        signals['confidence'] += 0.15
    elif latest['Close'] > latest['BB_upper']:
        signals['reasons'].append("Price above upper Bollinger Band (potential reversal - bearish)")
        signals['confidence'] -= 0.15
    
    # Check for Bollinger Band squeeze (low volatility)
    recent = df.iloc[-20:]
    avg_bb_width = ((recent['BB_upper'] - recent['BB_lower']) / recent['BB_middle']).mean()
    
    if bb_width < 0.7 * avg_bb_width:
        signals['reasons'].append("Bollinger Band squeeze detected (breakout pending)")
    
    return signals

def check_support_resistance(df, signals):
    """Identify key support and resistance levels"""
    # Simple method for support/resistance - pivots from last 100 candles
    recent = df.iloc[-100:].copy()
    
    # Find local maxima and minima
    resistance_levels = []
    support_levels = []
    
    for i in range(2, len(recent) - 2):
        if recent.iloc[i]['High'] > recent.iloc[i-1]['High'] and recent.iloc[i]['High'] > recent.iloc[i-2]['High'] and \
           recent.iloc[i]['High'] > recent.iloc[i+1]['High'] and recent.iloc[i]['High'] > recent.iloc[i+2]['High']:
            resistance_levels.append(round(recent.iloc[i]['High'], 2))
            
        if recent.iloc[i]['Low'] < recent.iloc[i-1]['Low'] and recent.iloc[i]['Low'] < recent.iloc[i-2]['Low'] and \
           recent.iloc[i]['Low'] < recent.iloc[i+1]['Low'] and recent.iloc[i]['Low'] < recent.iloc[i+2]['Low']:
            support_levels.append(round(recent.iloc[i]['Low'], 2))
    
    # Filter and sort levels
    resistance_levels = sorted(list(set(resistance_levels)))
    support_levels = sorted(list(set(support_levels)))
    
    # Get recent price
    latest_price = df.iloc[-1]['Close']
    
    # Find nearest levels
    nearest_resistance = [r for r in resistance_levels if r > latest_price][:3]
    nearest_support = [s for s in support_levels if s < latest_price][-3:]
    
    signals['resistance_levels'] = nearest_resistance
    signals['support_levels'] = nearest_support
    
    return signals

def calculate_final_signal(signals):
    """Determine final signal type and normalize confidence"""
    confidence = signals['confidence']
    
    # Normalize confidence to 0-1 range
    confidence = min(max(confidence, -1.0), 1.0)
    confidence_normalized = (confidence + 1) / 2  # Convert from [-1,1] to [0,1]
    
    # Determine signal type based on confidence
    if confidence > 0.5:
        signals['signal'] = "STRONG_BUY"
    elif confidence > 0.1:
        signals['signal'] = "BUY"
    elif confidence < -0.5:
        signals['signal'] = "STRONG_SELL"
    elif confidence < -0.1:
        signals['signal'] = "SELL"
    else:
        signals['signal'] = "NEUTRAL"
    
    # Update confidence
    signals['confidence'] = round(confidence_normalized, 2)
    
    return signals

def calculate_risk_reward_levels(df, signals):
    """Calculate stop loss and take profit levels based on signals and ATR"""
    latest = df.iloc[-1]
    signal_type = signals['signal']
    atr = latest['ATR']
    
    if signal_type in ["BUY", "STRONG_BUY"]:
        # For buy signals
        stop_multiple = 1.5
        target_multiple = 2.0 if signal_type == "BUY" else 3.0
        
        signals['stop_loss'] = round(latest['Close'] - (stop_multiple * atr), 2)
        signals['take_profit'] = round(latest['Close'] + (target_multiple * atr), 2)
        
    elif signal_type in ["SELL", "STRONG_SELL"]:
        # For sell signals
        stop_multiple = 1.5
        target_multiple = 2.0 if signal_type == "SELL" else 3.0
        
        signals['stop_loss'] = round(latest['Close'] + (stop_multiple * atr), 2)
        signals['take_profit'] = round(latest['Close'] - (target_multiple * atr), 2)
    
    return signals 