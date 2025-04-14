import pandas as pd
import numpy as np
# Set numpy NaN value explicitly
np.nan  # Use this instead of NaN
import pandas_ta as ta
from ta.trend import SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator

def calculate_indicators(df):
    """
    Calculate technical indicators for the given dataframe
    """
    # Ensure we have the required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Add basic indicators
    df = add_moving_averages(df)
    df = add_oscillators(df)
    df = add_volatility_indicators(df)
    df = add_trend_indicators(df)
    df = add_volume_indicators(df)
    df = add_pattern_indicators(df)
    
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
    
    # Volume Weighted Average Price
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    # MACD with histogram
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['MACD_hist'] = macd['MACDh_12_26_9']
    
    return df

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
    
    # Money Flow Index
    df['MFI'] = ta.mfi(df['High'], df['Low'], df['Close'], df['Volume'], length=14)
    
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
    
    # Keltner Channels
    keltner = ta.kc(df['High'], df['Low'], df['Close'], length=20)
    df['KC_upper'] = keltner['KCU_20_2']
    df['KC_middle'] = keltner['KCM_20_2']
    df['KC_lower'] = keltner['KCL_20_2']
    
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
    
    # Complete Ichimoku Cloud
    ichimoku = ta.ichimoku(df['High'], df['Low'], df['Close'])
    df['ICHIMOKU_9'] = ichimoku['ICHIMOKU_9']
    df['ICHIMOKU_26'] = ichimoku['ICHIMOKU_26']
    df['ICHIMOKU_52'] = ichimoku['ICHIMOKU_52']
    df['ICHIMOKU_spanA'] = ichimoku['ICHIMOKU_spanA']
    df['ICHIMOKU_spanB'] = ichimoku['ICHIMOKU_spanB']
    
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
    
    # Volume Weighted MACD
    vmacd = ta.vwmacd(df['Close'], df['Volume'])
    df['VMACD'] = vmacd['VMACD_12_26_9']
    df['VMACD_signal'] = vmacd['VMACDs_12_26_9']
    df['VMACD_hist'] = vmacd['VMACDh_12_26_9']
    
    return df

def add_pattern_indicators(df):
    """Add pattern recognition indicators"""
    # Candlestick patterns
    df['CDL_DOJI'] = ta.cdl_doji(df['Open'], df['High'], df['Low'], df['Close'])
    df['CDL_HAMMER'] = ta.cdl_hammer(df['Open'], df['High'], df['Low'], df['Close'])
    df['CDL_ENGULFING'] = ta.cdl_engulfing(df['Open'], df['High'], df['Low'], df['Close'])
    df['CDL_MORNING_STAR'] = ta.cdl_morningstar(df['Open'], df['High'], df['Low'], df['Close'])
    df['CDL_EVENING_STAR'] = ta.cdl_eveningstar(df['Open'], df['High'], df['Low'], df['Close'])
    
    # Fibonacci Retracement Levels (simplified)
    recent_high = df['High'].rolling(window=20).max()
    recent_low = df['Low'].rolling(window=20).min()
    range_size = recent_high - recent_low
    
    df['FIB_0'] = recent_low
    df['FIB_0.236'] = recent_low + 0.236 * range_size
    df['FIB_0.382'] = recent_low + 0.382 * range_size
    df['FIB_0.5'] = recent_low + 0.5 * range_size
    df['FIB_0.618'] = recent_low + 0.618 * range_size
    df['FIB_0.786'] = recent_low + 0.786 * range_size
    df['FIB_1'] = recent_high
    
    return df 