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
        "take_profit": None,
        "patterns": [],
        "divergences": []
    }
    
    # Add signals based on indicators
    signals = check_trend_signals(df, signals)
    signals = check_oscillator_signals(df, signals)
    signals = check_volatility_signals(df, signals)
    signals = check_volume_signals(df, signals)
    signals = check_pattern_signals(df, signals)
    signals = check_divergence_signals(df, signals)
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
    
    # Ichimoku Cloud signals
    if latest['Close'] > latest['ICHIMOKU_spanA'] and latest['Close'] > latest['ICHIMOKU_spanB']:
        signals['reasons'].append("Price above Ichimoku Cloud (bullish)")
        signals['confidence'] += 0.2
    elif latest['Close'] < latest['ICHIMOKU_spanA'] and latest['Close'] < latest['ICHIMOKU_spanB']:
        signals['reasons'].append("Price below Ichimoku Cloud (bearish)")
        signals['confidence'] -= 0.2
    
    # Supertrend signals
    if latest['SUPERTREND'] < latest['Close']:
        signals['reasons'].append("Supertrend bullish")
        signals['confidence'] += 0.15
    else:
        signals['reasons'].append("Supertrend bearish")
        signals['confidence'] -= 0.15
    
    return signals

def check_oscillator_signals(df, signals):
    """Check for oscillator-based signals"""
    latest = df.iloc[-1]
    
    # RSI signals with multiple timeframes
    rsi_signals = []
    for period in [7, 14, 21]:
        rsi = latest[f'RSI{period}']
        if rsi < 30:
            rsi_signals.append(f"RSI{period} oversold at {rsi:.2f} (bullish)")
            signals['confidence'] += 0.1
        elif rsi > 70:
            rsi_signals.append(f"RSI{period} overbought at {rsi:.2f} (bearish)")
            signals['confidence'] -= 0.1
    signals['reasons'].extend(rsi_signals)
    
    # Stochastic signals
    if latest['STOCH_K'] < 20 and latest['STOCH_D'] < 20:
        signals['reasons'].append("Stochastic oversold (bullish)")
        signals['confidence'] += 0.15
    elif latest['STOCH_K'] > 80 and latest['STOCH_D'] > 80:
        signals['reasons'].append("Stochastic overbought (bearish)")
        signals['confidence'] -= 0.15
    
    # Williams %R
    if latest['WILLR'] < -80:
        signals['reasons'].append(f"Williams %R oversold at {latest['WILLR']:.2f} (bullish)")
        signals['confidence'] += 0.1
    elif latest['WILLR'] > -20:
        signals['reasons'].append(f"Williams %R overbought at {latest['WILLR']:.2f} (bearish)")
        signals['confidence'] -= 0.1
    
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
    
    # Keltner Channel signals
    if latest['Close'] < latest['KC_lower']:
        signals['reasons'].append("Price below Keltner Channel (potential reversal - bullish)")
        signals['confidence'] += 0.1
    elif latest['Close'] > latest['KC_upper']:
        signals['reasons'].append("Price above Keltner Channel (potential reversal - bearish)")
        signals['confidence'] -= 0.1
    
    return signals

def check_volume_signals(df, signals):
    """Check for volume-based signals"""
    latest = df.iloc[-1]
    
    # Volume confirmation with multiple timeframes
    volume_signals = []
    
    # Short-term volume analysis (5-period)
    short_term_volume = df['Volume'].iloc[-5:]
    short_term_avg = short_term_volume.mean()
    short_term_std = short_term_volume.std()
    
    # Short-term volume spike detection
    if latest['Volume'] > short_term_avg + (2 * short_term_std):
        volume_signals.append("Strong short-term volume spike (2+ standard deviations)")
        signals['confidence'] *= 1.4
    elif latest['Volume'] > short_term_avg + short_term_std:
        volume_signals.append("Moderate short-term volume spike (1+ standard deviation)")
        signals['confidence'] *= 1.2
    
    # Short-term volume trend
    short_term_trend = np.polyfit(range(5), short_term_volume, 1)[0]
    if short_term_trend > 0:
        volume_signals.append(f"Short-term volume trending up (slope: {short_term_trend:.2f})")
        signals['confidence'] += 0.1
    
    # Medium-term volume analysis (20-period)
    medium_term_volume = df['Volume'].iloc[-20:]
    medium_term_avg = medium_term_volume.mean()
    medium_term_std = medium_term_volume.std()
    
    # Medium-term volume trend
    medium_term_trend = np.polyfit(range(20), medium_term_volume, 1)[0]
    if medium_term_trend > 0:
        volume_signals.append(f"Medium-term volume trending up (slope: {medium_term_trend:.2f})")
        signals['confidence'] += 0.15
    
    # Volume trend convergence/divergence
    if short_term_trend > 0 and medium_term_trend > 0:
        volume_signals.append("Volume trends converging (bullish)")
        signals['confidence'] += 0.2
    elif short_term_trend < 0 and medium_term_trend < 0:
        volume_signals.append("Volume trends converging (bearish)")
        signals['confidence'] -= 0.2
    
    # Volume momentum
    volume_momentum = (latest['Volume'] - df['Volume'].iloc[-5]) / df['Volume'].iloc[-5]
    if volume_momentum > 0.5:  # 50% increase in volume
        volume_signals.append(f"Strong volume momentum ({volume_momentum:.1%} increase)")
        signals['confidence'] *= 1.3
    
    # OBV trend with multiple timeframes
    obv_short_trend = float(df['OBV'].iloc[-5:].mean() > df['OBV'].iloc[-10:-5].mean())
    obv_medium_trend = float(df['OBV'].iloc[-20:].mean() > df['OBV'].iloc[-40:-20].mean())
    obv_slope = (df['OBV'].iloc[-1] - df['OBV'].iloc[-5]) / 5
    
    if obv_short_trend > 0 and obv_medium_trend > 0 and obv_slope > 0:
        volume_signals.append("OBV trending up in both short and medium term")
        signals['confidence'] += 0.25
    elif obv_short_trend == 0 and obv_medium_trend == 0 and obv_slope < 0:
        volume_signals.append("OBV trending down in both short and medium term")
        signals['confidence'] -= 0.25
    
    # Chaikin Money Flow with trend confirmation
    cmf_short_trend = float(df['CMF'].iloc[-5:].mean() > df['CMF'].iloc[-10:-5].mean())
    cmf_medium_trend = float(df['CMF'].iloc[-20:].mean() > df['CMF'].iloc[-40:-20].mean())
    
    if latest['CMF'] > 0.1 and cmf_short_trend > 0 and cmf_medium_trend > 0:
        volume_signals.append(f"Strong buying pressure with increasing CMF in both timeframes: {latest['CMF']:.2f}")
        signals['confidence'] += 0.3
    elif latest['CMF'] < -0.1 and cmf_short_trend == 0 and cmf_medium_trend == 0:
        volume_signals.append(f"Strong selling pressure with decreasing CMF in both timeframes: {latest['CMF']:.2f}")
        signals['confidence'] -= 0.3
    
    # Volume Weighted MACD confirmation
    vmacd_short_trend = float(df['VMACD'].iloc[-5:].mean() > df['VMACD'].iloc[-10:-5].mean())
    vmacd_medium_trend = float(df['VMACD'].iloc[-20:].mean() > df['VMACD'].iloc[-40:-20].mean())
    
    if latest['VMACD'] > latest['VMACD_signal'] and latest['VMACD_hist'] > 0 and vmacd_short_trend > 0 and vmacd_medium_trend > 0:
        volume_signals.append("Volume-weighted MACD bullish in both timeframes")
        signals['confidence'] += 0.2
    elif latest['VMACD'] < latest['VMACD_signal'] and latest['VMACD_hist'] < 0 and vmacd_short_trend == 0 and vmacd_medium_trend == 0:
        volume_signals.append("Volume-weighted MACD bearish in both timeframes")
        signals['confidence'] -= 0.2
    
    # Add all volume signals to reasons
    signals['reasons'].extend(volume_signals)
    
    # Add volume metrics to signals for position sizing
    signals['volume_metrics'] = {
        'short_term_trend': float(short_term_trend),
        'medium_term_trend': float(medium_term_trend),
        'volume_momentum': float(volume_momentum),
        'obv_trend': bool(obv_short_trend and obv_medium_trend),
        'cmf_trend': bool(cmf_short_trend and cmf_medium_trend),
        'vmacd_trend': bool(vmacd_short_trend and vmacd_medium_trend)
    }
    
    return signals

def check_pattern_signals(df, signals):
    """Check for candlestick and chart patterns"""
    latest = df.iloc[-1]
    
    # Candlestick patterns - handle possible NaN or None values
    if latest.get('CDL_HAMMER', 0) != 0:
        signals['patterns'].append("Hammer pattern (bullish)" if latest['CDL_HAMMER'] > 0 else "Inverted Hammer pattern (bearish)")
        signals['confidence'] += 0.2 if latest['CDL_HAMMER'] > 0 else -0.2
    
    if latest.get('CDL_ENGULFING', 0) != 0:
        signals['patterns'].append("Bullish Engulfing pattern" if latest['CDL_ENGULFING'] > 0 else "Bearish Engulfing pattern")
        signals['confidence'] += 0.25 if latest['CDL_ENGULFING'] > 0 else -0.25
    
    if latest.get('CDL_MORNING_STAR', 0) > 0:
        signals['patterns'].append("Morning Star pattern (bullish)")
        signals['confidence'] += 0.3
    
    if latest.get('CDL_EVENING_STAR', 0) > 0:
        signals['patterns'].append("Evening Star pattern (bearish)")
        signals['confidence'] -= 0.3
    
    # Doji pattern
    if latest.get('CDL_DOJI', 0) > 0:
        signals['patterns'].append("Doji pattern (indecision)")
        # Reduce confidence since Doji indicates uncertainty
        signals['confidence'] *= 0.9
    
    # Fibonacci levels
    current_price = latest['Close']
    for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
        fib_key = f'FIB_{level}'
        if fib_key in latest and pd.notna(latest[fib_key]):
            fib_level = latest[fib_key]
            if abs(current_price - fib_level) / current_price < 0.01:  # Within 1% of level
                signals['reasons'].append(f"Price near Fibonacci {level*100}% level")
    
    return signals

def check_divergence_signals(df, signals):
    """Check for indicator divergences"""
    # RSI divergence
    if len(df) >= 14:
        rsi = df['RSI14'].iloc[-14:]
        price = df['Close'].iloc[-14:]
        
        # Bullish divergence
        if (price.iloc[-1] < price.iloc[-8] and rsi.iloc[-1] > rsi.iloc[-8]) or \
           (price.iloc[-1] < price.iloc[-4] and rsi.iloc[-1] > rsi.iloc[-4]):
            signals['divergences'].append("Bullish RSI divergence")
            signals['confidence'] += 0.25
        
        # Bearish divergence
        if (price.iloc[-1] > price.iloc[-8] and rsi.iloc[-1] < rsi.iloc[-8]) or \
           (price.iloc[-1] > price.iloc[-4] and rsi.iloc[-1] < rsi.iloc[-4]):
            signals['divergences'].append("Bearish RSI divergence")
            signals['confidence'] -= 0.25
    
    # MACD divergence
    if len(df) >= 26:
        macd = df['MACD'].iloc[-26:]
        price = df['Close'].iloc[-26:]
        
        # Bullish divergence
        if (price.iloc[-1] < price.iloc[-13] and macd.iloc[-1] > macd.iloc[-13]) or \
           (price.iloc[-1] < price.iloc[-6] and macd.iloc[-1] > macd.iloc[-6]):
            signals['divergences'].append("Bullish MACD divergence")
            signals['confidence'] += 0.25
        
        # Bearish divergence
        if (price.iloc[-1] > price.iloc[-13] and macd.iloc[-1] < macd.iloc[-13]) or \
           (price.iloc[-1] > price.iloc[-6] and macd.iloc[-1] < macd.iloc[-6]):
            signals['divergences'].append("Bearish MACD divergence")
            signals['confidence'] -= 0.25
    
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