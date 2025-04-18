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
        "divergences": [],
        "bitcoin_price": latest.get('BTC_Price')  # Add BTC price for crypto pairs
    }
    
    # Add signals based on indicators
    signals = check_trend_signals(df, signals)
    signals = check_oscillator_signals(df, signals)
    signals = check_volatility_signals(df, signals)
    signals = check_volume_signals(df, signals)
    signals = check_pattern_signals(df, signals)
    signals = check_divergence_signals(df, signals)
    signals = check_support_resistance(df, signals)
    
    # Check for crypto-specific patterns if BTC price is available
    if 'BTC_Price' in df.columns:
        signals = check_crypto_patterns(df, signals)
    
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
    # Get all indicators' states
    trend_score = calculate_trend_score(signals)
    momentum_score = calculate_momentum_score(signals)
    volume_score = calculate_volume_score(signals)
    volatility_score = calculate_volatility_score(signals)
    pattern_score = calculate_pattern_score(signals)
    support_resistance_score = calculate_sr_score(signals)
    
    # Calculate weighted final score
    final_score = (
        trend_score * 0.35 +        # Trend has highest weight
        momentum_score * 0.20 +     # Momentum second
        volume_score * 0.15 +       # Volume confirmation
        volatility_score * 0.10 +   # Volatility context
        pattern_score * 0.10 +      # Pattern recognition
        support_resistance_score * 0.10  # S/R levels
    )
    
    # Normalize final score to -1 to 1 range
    final_score = max(min(final_score, 1.0), -1.0)
    
    # Convert to confidence (0-1 range)
    confidence = (final_score + 1) / 2
    
    # Determine signal type with more granular categories
    if final_score > 0.7:
        signal = "STRONG_BUY"
    elif final_score > 0.3:
        signal = "BUY"
    elif final_score > 0.1:
        signal = "WEAK_BUY"
    elif final_score > -0.1:
        signal = "NEUTRAL"
    elif final_score > -0.3:
        signal = "WEAK_SELL"
    elif final_score > -0.7:
        signal = "SELL"
    else:
        signal = "STRONG_SELL"
    
    # Update signals dictionary
    signals['signal'] = signal
    signals['confidence'] = round(confidence, 2)
    signals['signal_metrics'] = {
        'trend_score': round(trend_score, 2),
        'momentum_score': round(momentum_score, 2),
        'volume_score': round(volume_score, 2),
        'volatility_score': round(volatility_score, 2),
        'pattern_score': round(pattern_score, 2),
        'support_resistance_score': round(support_resistance_score, 2)
    }
    
    return signals

def calculate_trend_score(signals):
    """Calculate trend score from -1 to 1"""
    score = 0
    count = 0
    
    # Moving averages alignment
    if 'EMA9' in signals and 'EMA21' in signals:
        score += 1 if signals['EMA9'] > signals['EMA21'] else -1
        count += 1
    
    if 'Close' in signals and 'SMA200' in signals:
        score += 1 if signals['Close'] > signals['SMA200'] else -1
        count += 1
    
    # MACD direction
    if 'MACD' in signals and 'MACD_signal' in signals:
        score += 1 if signals['MACD'] > signals['MACD_signal'] else -1
        count += 1
    
    # ADX strength modifier
    adx = signals.get('ADX', 0)
    if adx > 25:  # Strong trend
        score *= 1.2
    elif adx < 20:  # Weak trend
        score *= 0.8
    
    return score / max(count, 1)  # Normalize to -1 to 1

def calculate_momentum_score(signals):
    """Calculate momentum score from -1 to 1"""
    score = 0
    count = 0
    
    # RSI signals
    rsi14 = signals.get('RSI14', 50)
    if rsi14 < 30:
        score += 1  # Oversold (bullish)
    elif rsi14 > 70:
        score -= 1  # Overbought (bearish)
    count += 1
    
    # Stochastic signals
    if 'STOCH_K' in signals and 'STOCH_D' in signals:
        k, d = signals['STOCH_K'], signals['STOCH_D']
        if k < 20 and d < 20:
            score += 1  # Oversold
        elif k > 80 and d > 80:
            score -= 1  # Overbought
        count += 1
    
    # Williams %R
    willr = signals.get('WILLR', -50)
    if willr < -80:
        score += 1  # Oversold
    elif willr > -20:
        score -= 1  # Overbought
    count += 1
    
    return score / max(count, 1)

def calculate_volume_score(signals):
    """Calculate volume score from -1 to 1"""
    score = 0
    count = 0
    
    # Volume trend
    if 'volume_metrics' in signals:
        metrics = signals['volume_metrics']
        if metrics.get('obv_trend'):
            score += 1
            count += 1
        if metrics.get('cmf_trend'):
            score += 1
            count += 1
        
        # Volume momentum
        if metrics.get('volume_momentum', 0) > 0.5:
            score += 1
            count += 1
    
    return score / max(count, 1)

def calculate_volatility_score(signals):
    """Calculate volatility score from -1 to 1"""
    score = 0
    count = 0
    
    # Bollinger Bands
    if all(k in signals for k in ['Close', 'BB_upper', 'BB_lower']):
        if signals['Close'] < signals['BB_lower']:
            score += 1  # Potential reversal up
        elif signals['Close'] > signals['BB_upper']:
            score -= 1  # Potential reversal down
        count += 1
    
    # ATR trending
    if 'ATR' in signals:
        atr_ma = signals.get('ATR_MA', signals['ATR'])
        if signals['ATR'] < atr_ma:
            score += 0.5  # Lower volatility (more predictable)
        count += 1
    
    return score / max(count, 1)

def calculate_pattern_score(signals):
    """Calculate pattern score from -1 to 1"""
    score = 0
    count = 0
    
    if 'patterns' in signals:
        for pattern in signals['patterns']:
            if 'bullish' in pattern.lower():
                score += 1
            elif 'bearish' in pattern.lower():
                score -= 1
            count += 1
    
    if 'divergences' in signals:
        for divergence in signals['divergences']:
            if 'bullish' in divergence.lower():
                score += 1
            elif 'bearish' in divergence.lower():
                score -= 1
            count += 1
    
    return score / max(count, 1)

def calculate_sr_score(signals):
    """Calculate support/resistance score from -1 to 1"""
    score = 0
    
    if 'Close' in signals and signals['support_levels'] and signals['resistance_levels']:
        current_price = signals['Close']
        
        # Find nearest support and resistance
        supports = [s for s in signals['support_levels'] if s < current_price]
        resistances = [r for r in signals['resistance_levels'] if r > current_price]
        
        if supports and resistances:
            nearest_support = max(supports)
            nearest_resistance = min(resistances)
            
            # Calculate price position between S/R levels
            range_size = nearest_resistance - nearest_support
            if range_size > 0:
                position = (current_price - nearest_support) / range_size
                
                if position < 0.2:  # Close to support (bullish)
                    score = 1
                elif position > 0.8:  # Close to resistance (bearish)
                    score = -1
                else:  # In the middle of range
                    score = 0.5 - position
    
    return score

def calculate_risk_reward_levels(df, signals):
    """Calculate dynamic stop loss and take profit levels based on technical analysis"""
    latest = df.iloc[-1]
    signal_type = signals['signal']
    atr = latest['ATR']
    
    # Calculate dynamic multipliers based on market conditions
    stop_multiple, target_multiple = calculate_dynamic_multipliers(df, signals, latest)
    
    if signal_type in ["BUY", "STRONG_BUY"]:
        # For buy signals
        signals['stop_loss'] = round(latest['Close'] - (stop_multiple * atr), 2)
        signals['take_profit'] = round(latest['Close'] + (target_multiple * atr), 2)
        
    elif signal_type in ["SELL", "STRONG_SELL"]:
        # For sell signals
        signals['stop_loss'] = round(latest['Close'] + (stop_multiple * atr), 2)
        signals['take_profit'] = round(latest['Close'] - (target_multiple * atr), 2)
    
    return signals

def calculate_dynamic_multipliers(df, signals, latest):
    """Calculate dynamic stop loss and take profit multipliers based on market conditions"""
    # Base multipliers
    base_stop = 1.5
    base_target = 2.0
    
    # Adjust based on trend strength (ADX)
    adx = latest['ADX']
    if adx > 30:  # Strong trend
        base_target *= 1.5
    elif adx < 20:  # Weak trend
        base_stop *= 0.8
        base_target *= 0.8
    
    # Adjust based on volatility
    bb_width = (latest['BB_upper'] - latest['BB_lower']) / latest['BB_middle']
    avg_bb_width = ((df['BB_upper'] - df['BB_lower']) / df['BB_middle']).mean()
    
    if bb_width > avg_bb_width * 1.5:  # High volatility
        base_stop *= 1.2
        base_target *= 1.3
    elif bb_width < avg_bb_width * 0.5:  # Low volatility
        base_stop *= 0.8
        base_target *= 0.8
    
    # Adjust based on RSI extremes
    rsi = latest['RSI14']
    if rsi > 70 or rsi < 30:
        base_target *= 0.8  # More conservative targets in overbought/oversold conditions
    
    # Adjust based on support/resistance proximity
    if signals['support_levels'] and signals['resistance_levels']:
        current_price = latest['Close']
        nearest_support = min([s for s in signals['support_levels'] if s < current_price], default=None)
        nearest_resistance = min([r for r in signals['resistance_levels'] if r > current_price], default=None)
        
        if nearest_support and nearest_resistance:
            price_range = nearest_resistance - nearest_support
            if price_range > 0:
                position_in_range = (current_price - nearest_support) / price_range
                if position_in_range < 0.2:  # Close to support
                    base_target *= 1.2
                elif position_in_range > 0.8:  # Close to resistance
                    base_stop *= 0.8
    
    # Adjust based on market patterns
    if signals['patterns']:
        pattern_adjustments = {
            'Hammer pattern (bullish)': {'target': 1.2, 'stop': 0.9},
            'Inverted Hammer pattern (bearish)': {'target': 1.2, 'stop': 0.9},
            'Morning Star pattern (bullish)': {'target': 1.3, 'stop': 0.8},
            'Evening Star pattern (bearish)': {'target': 1.3, 'stop': 0.8},
            'Doji pattern (indecision)': {'target': 0.8, 'stop': 1.2}
        }
        
        for pattern in signals['patterns']:
            if pattern in pattern_adjustments:
                base_target *= pattern_adjustments[pattern]['target']
                base_stop *= pattern_adjustments[pattern]['stop']
    
    # Adjust based on divergences
    if signals['divergences']:
        for divergence in signals['divergences']:
            if 'Bullish' in divergence:
                base_target *= 1.2
            elif 'Bearish' in divergence:
                base_target *= 0.8
    
    # Adjust based on volume metrics
    volume_metrics = signals.get('volume_metrics', {})
    if volume_metrics.get('obv_trend'):
        base_target *= 1.1
    if volume_metrics.get('cmf_trend'):
        base_target *= 1.1
    
    # Final adjustments based on signal strength
    if signals['signal'] in ['STRONG_BUY', 'STRONG_SELL']:
        base_target *= 1.2
    
    # Ensure minimum and maximum values
    base_stop = max(1.0, min(3.0, base_stop))
    base_target = max(1.5, min(4.0, base_target))
    
    return base_stop, base_target

# Add new crypto-specific function
def check_crypto_patterns(df, signals):
    """Check for cryptocurrency-specific patterns and metrics"""
    latest = df.iloc[-1]
    
    try:
        # Calculate BTC correlation if BTC price is available
        if 'BTC_Price' in df.columns:
            # Get price changes
            df['returns'] = df['Close'].pct_change()
            df['btc_returns'] = df['BTC_Price'].pct_change()
            
            # Calculate rolling correlation with BTC
            correlation = df['returns'].corr(df['btc_returns'])
            
            if abs(correlation) > 0.7:
                signals['reasons'].append(f"Strong correlation with BTC: {correlation:.2f}")
                # Adjust confidence based on BTC trend
                if df['btc_returns'].tail(5).mean() > 0:
                    signals['confidence'] += 0.1
                else:
                    signals['confidence'] -= 0.1
        
        # Check for extreme volume spikes (common in crypto)
        volume_ma = df['Volume'].rolling(window=20).mean()
        current_volume = latest['Volume']
        
        if current_volume > volume_ma.iloc[-1] * 3:
            signals['reasons'].append("Extreme volume spike detected (3x average)")
            signals['confidence'] *= 1.2
        
        # Check for weekend effect (crypto trades 24/7)
        if pd.to_datetime(latest['Date']).weekday() in [5, 6]:  # Weekend
            signals['reasons'].append("Weekend trading period - typically lower volume")
            signals['confidence'] *= 0.9
        
        # Check for potential flash crash recovery
        recent_low = df['Low'].tail(5).min()
        if latest['Close'] > recent_low * 1.1 and latest['Low'] < recent_low * 1.05:
            signals['reasons'].append("Potential flash crash recovery pattern")
            signals['confidence'] += 0.15
        
        # Check for high volatility periods
        atr = df['ATR'].iloc[-1]
        atr_ma = df['ATR'].rolling(window=20).mean().iloc[-1]
        
        if atr > atr_ma * 1.5:
            signals['reasons'].append("High volatility period - use caution")
            signals['confidence'] *= 0.8
        
        # Check for whale activity (large transactions)
        if current_volume * latest['Close'] > volume_ma.iloc[-1] * latest['Close'] * 5:
            signals['reasons'].append("Potential whale activity detected")
            signals['confidence'] *= 1.1
        
    except Exception as e:
        print(f"Error in crypto pattern analysis: {str(e)}")
    
    return signals