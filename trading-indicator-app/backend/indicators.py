import pandas as pd
import numpy as np
# Set numpy NaN value explicitly
np.nan  # Use this instead of NaN
import pandas_ta as ta
from ta.trend import SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator

def calculate_all(df):
    """
    Calculate all technical indicators for the given dataframe
    This is the main function called by the API
    """
    return calculate_indicators(df)  # Call the existing calculate_indicators function

def calculate_indicators(df):
    """
    Calculate technical indicators for the given dataframe
    """
    # Ensure we have the required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Ensure datetime index for calculations
    if not isinstance(df.index, pd.DatetimeIndex):
        if 'Date' in df.columns:
            df = df.set_index('Date')
        else:
            df.index = pd.to_datetime(df.index)
    
    # Sort index to ensure proper calculations
    df = df.sort_index()
    
    # Add basic indicators
    df = add_moving_averages(df)
    df = add_oscillators(df)
    df = add_volatility_indicators(df)
    df = add_trend_indicators(df)
    df = add_volume_indicators(df)
    df = add_pattern_indicators(df)
    
    # Reset index to keep Date as a column
    df = df.reset_index()
    
    return df

def add_moving_averages(df):
    """Add various moving averages to dataframe"""
    # Simple Moving Averages
    df['SMA20'] = ta.sma(df['Close'], length=20)
    df['SMA50'] = ta.sma(df['Close'], length=50)
    df['SMA200'] = ta.sma(df['Close'], length=200)
    
    # Exponential Moving Averages
    df['EMA9'] = ta.ema(df['Close'], length=9)
    df['EMA21'] = ta.ema(df['Close'], length=21)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    
    # Calculate VWAP manually since ta.vwap requires specific datetime index
    df['VWAP'] = calculate_vwap(df)
    
    # MACD with histogram
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['MACD_hist'] = macd['MACDh_12_26_9']
    
    return df

def calculate_vwap(df):
    """Calculate VWAP manually"""
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    volume_traded = df['Volume']
    
    cumulative_tp_vol = (typical_price * volume_traded).cumsum()
    cumulative_vol = volume_traded.cumsum()
    
    return cumulative_tp_vol / cumulative_vol

def add_oscillators(df):
    """Add oscillator indicators to dataframe"""
    # RSI with multiple timeframes
    df['RSI14'] = ta.rsi(df['Close'], length=14)
    df['RSI7'] = ta.rsi(df['Close'], length=7)
    df['RSI21'] = ta.rsi(df['Close'], length=21)
    
    # Stochastic with multiple timeframes
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    df['STOCH_K'] = stoch['STOCHk_14_3_3']
    df['STOCH_D'] = stoch['STOCHd_14_3_3']
    
    # Williams %R
    df['WILLR'] = ta.willr(df['High'], df['Low'], df['Close'], length=14)
    
    # CCI (Commodity Channel Index)
    df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=14)
    
    # Money Flow Index - handle large volume numbers
    try:
        # Convert volume to manageable float64 numbers by scaling
        volume_scaled = df['Volume'].astype('float64') / 1e9  # Scale down volume even more
        # Ensure typical price is also float64
        typical_price = ((df['High'] + df['Low'] + df['Close']) / 3).astype('float64')
        
        # Calculate MFI components
        money_flow = (typical_price * volume_scaled).astype('float64')
        
        # Positive/negative money flow
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0.0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0.0)
        
        # Calculate 14-period sums
        positive_sum = positive_flow.rolling(window=14).sum()
        negative_sum = negative_flow.rolling(window=14).sum()
        
        # Calculate final MFI
        money_ratio = (positive_sum / negative_sum.replace(0, 1e-10)).astype('float64')
        mfi = (100.0 - (100.0 / (1.0 + money_ratio))).astype('float64')
        
        # Clean up any invalid values
        df['MFI'] = mfi.fillna(50.0).replace([np.inf, -np.inf], 50.0).clip(0, 100)
    except Exception as e:
        print(f"Error calculating MFI: {str(e)}")
        df['MFI'] = 50.0  # Neutral value as fallback
    
    return df

def add_volatility_indicators(df):
    """Add volatility indicators to dataframe"""
    # Bollinger Bands with multiple deviations
    bbands = ta.bbands(df['Close'], length=20, std=2)
    df['BB_upper'] = bbands['BBU_20_2.0']
    df['BB_middle'] = bbands['BBM_20_2.0']
    df['BB_lower'] = bbands['BBL_20_2.0']
    
    # Bollinger Bands with 1 standard deviation
    bbands1 = ta.bbands(df['Close'], length=20, std=1)
    df['BB_upper1'] = bbands1['BBU_20_1.0']
    df['BB_lower1'] = bbands1['BBL_20_1.0']
    
    # ATR (Average True Range)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    # Calculate Keltner Channels manually
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    atr = df['ATR']
    ema20 = df['Close'].ewm(span=20, adjust=False).mean()
    
    df['KC_middle'] = ema20
    df['KC_upper'] = ema20 + (2 * atr)
    df['KC_lower'] = ema20 - (2 * atr)
    
    return df

def add_trend_indicators(df):
    """Add trend indicators to dataframe"""
    # ADX (Average Directional Index)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    df['ADX'] = adx['ADX_14']
    df['DMP'] = adx['DMP_14']
    df['DMN'] = adx['DMN_14']
    
    # Parabolic SAR
    df['SAR'] = ta.psar(df['High'], df['Low'])['PSARl_0.02_0.2']
    
    # Calculate Ichimoku Cloud components manually
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['ICHIMOKU_9'] = (high_9 + low_9) / 2
    
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['ICHIMOKU_26'] = (high_26 + low_26) / 2
    
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['ICHIMOKU_52'] = (high_52 + low_52) / 2
    
    # Calculate spans
    df['ICHIMOKU_spanA'] = ((df['ICHIMOKU_9'] + df['ICHIMOKU_26']) / 2).shift(26)
    df['ICHIMOKU_spanB'] = ((high_52 + low_52) / 2).shift(26)
    
    # Supertrend
    supertrend = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    df['SUPERTREND'] = supertrend['SUPERT_10_3.0']
    
    return df

def add_volume_indicators(df):
    """Add volume-based indicators"""
    # On Balance Volume
    df['OBV'] = ta.obv(df['Close'], df['Volume'])
    
    # Chaikin Money Flow
    df['CMF'] = ta.cmf(df['High'], df['Low'], df['Close'], df['Volume'], length=20)
    
    # Calculate MFI manually
    try:
        # Convert all inputs to float64 explicitly
        typical_price = ((df['High'].astype('float64') + df['Low'].astype('float64') + df['Close'].astype('float64')) / 3)
        volume = df['Volume'].astype('float64')
        
        # Calculate raw money flow
        raw_money_flow = (typical_price * volume).astype('float64')
        
        # Calculate positive and negative money flow
        price_change = typical_price.diff()
        
        pos_flow = raw_money_flow.where(price_change > 0, 0.0)
        neg_flow = raw_money_flow.where(price_change < 0, 0.0)
        
        # Calculate 14-period sums with explicit float64 type
        period = 14
        pos_flow_sum = pos_flow.rolling(window=period, min_periods=1).sum()
        neg_flow_sum = neg_flow.rolling(window=period, min_periods=1).sum()
        
        # Handle division by zero and calculate MFI
        money_ratio = pos_flow_sum / neg_flow_sum.replace(0, 1e-10)
        mfi = 100.0 - (100.0 / (1.0 + money_ratio))
        
        # Clean up any remaining NaN/inf values
        df['MFI'] = mfi.fillna(50.0).replace([np.inf, -np.inf], 50.0).clip(0, 100)
        
    except Exception as e:
        print(f"Error calculating MFI: {str(e)}")
        df['MFI'] = 50.0  # Neutral value as fallback
    
    try:
        # Volume-weighted MACD implementation with explicit float64 casting
        close = df['Close'].astype('float64')
        volume = df['Volume'].astype('float64')
        
        # Calculate VWAP for different periods
        vwap12 = ((close * volume).ewm(span=12, adjust=False).mean() / 
                  volume.ewm(span=12, adjust=False).mean()).astype('float64')
        vwap26 = ((close * volume).ewm(span=26, adjust=False).mean() / 
                  volume.ewm(span=26, adjust=False).mean()).astype('float64')
        
        # Calculate VMACD components
        df['VMACD'] = (vwap12 - vwap26).fillna(0.0)
        df['VMACD_signal'] = df['VMACD'].ewm(span=9, adjust=False).mean().fillna(0.0)
        df['VMACD_hist'] = (df['VMACD'] - df['VMACD_signal']).fillna(0.0)
        
    except Exception as e:
        print(f"Error calculating VMACD: {str(e)}")
        df['VMACD'] = 0.0
        df['VMACD_signal'] = 0.0
        df['VMACD_hist'] = 0.0
    
    return df

def add_pattern_indicators(df):
    """Add pattern recognition indicators using manual calculations"""
    # Initialize pattern columns with zeros
    df['CDL_DOJI'] = 0
    df['CDL_HAMMER'] = 0
    df['CDL_ENGULFING'] = 0
    df['CDL_MORNING_STAR'] = 0
    df['CDL_EVENING_STAR'] = 0
    
    for i in range(1, len(df)):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        # Doji pattern (body is very small)
        body = abs(curr['Close'] - curr['Open'])
        total_range = curr['High'] - curr['Low']
        if total_range > 0 and body <= 0.1 * total_range:
            df.at[df.index[i], 'CDL_DOJI'] = 1
        
        # Hammer pattern (long lower shadow, small upper shadow)
        if total_range > 0:
            body = abs(curr['Close'] - curr['Open'])
            upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
            lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
            
            if (lower_shadow > 2 * body) and (upper_shadow < 0.1 * lower_shadow):
                df.at[df.index[i], 'CDL_HAMMER'] = 1
        
        # Engulfing patterns
        curr_bullish = curr['Close'] > curr['Open']
        prev_bullish = prev['Close'] > prev['Open']
        
        if curr_bullish and not prev_bullish:  # Potential bullish engulfing
            if curr['Open'] < prev['Close'] and curr['Close'] > prev['Open']:
                df.at[df.index[i], 'CDL_ENGULFING'] = 1
        elif not curr_bullish and prev_bullish:  # Potential bearish engulfing
            if curr['Open'] > prev['Close'] and curr['Close'] < prev['Open']:
                df.at[df.index[i], 'CDL_ENGULFING'] = -1
    
    # Morning/Evening star patterns require 3 candles
    for i in range(2, len(df)):
        first = df.iloc[i-2]
        middle = df.iloc[i-1]
        last = df.iloc[i]
        
        # Morning Star
        if (first['Close'] < first['Open'] and  # First day: bearish
            abs(middle['Close'] - middle['Open']) < 0.1 * (middle['High'] - middle['Low']) and  # Second day: doji
            last['Close'] > last['Open'] and  # Third day: bullish
            last['Close'] > (first['Close'] + first['Open']) / 2):  # Close above midpoint of first day
            df.at[df.index[i], 'CDL_MORNING_STAR'] = 1
        
        # Evening Star
        if (first['Close'] > first['Open'] and  # First day: bullish
            abs(middle['Close'] - middle['Open']) < 0.1 * (middle['High'] - middle['Low']) and  # Second day: doji
            last['Close'] < last['Open'] and  # Third day: bearish
            last['Close'] < (first['Close'] + first['Open']) / 2):  # Close below midpoint of first day
            df.at[df.index[i], 'CDL_EVENING_STAR'] = 1
    
    return df