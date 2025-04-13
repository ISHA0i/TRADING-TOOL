import pandas as pd
import numpy as np
import pandas_ta as ta

def calculate_all(data):
    """Calculate all technical indicators and return enhanced dataframe"""
    df = data.copy()
    
    # Add basic indicators
    df = add_moving_averages(df)
    df = add_oscillators(df)
    df = add_volatility_indicators(df)
    df = add_trend_indicators(df)
    
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
    
    # MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['MACD_hist'] = macd['MACDh_12_26_9']
    
    return df

def add_oscillators(df):
    """Add oscillator indicators to dataframe"""
    # RSI
    df['RSI14'] = ta.rsi(df['Close'], length=14)
    
    # Stochastic
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    df['STOCH_K'] = stoch['STOCHk_14_3_3']
    df['STOCH_D'] = stoch['STOCHd_14_3_3']
    
    # CCI (Commodity Channel Index)
    df['CCI'] = ta.cci(df['High'], df['Low'], df['Close'], length=14)
    
    return df

def add_volatility_indicators(df):
    """Add volatility indicators to dataframe"""
    # Bollinger Bands
    bbands = ta.bbands(df['Close'], length=20, std=2)
    df['BB_upper'] = bbands['BBU_20_2.0']
    df['BB_middle'] = bbands['BBM_20_2.0']
    df['BB_lower'] = bbands['BBL_20_2.0']
    
    # ATR (Average True Range)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    
    return df

def add_trend_indicators(df):
    """Add trend indicators to dataframe"""
    # ADX (Average Directional Index)
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    df['ADX'] = adx['ADX_14']
    
    # Parabolic SAR
    df['SAR'] = ta.psar(df['High'], df['Low'])['PSARl_0.02_0.2']
    
    # Ichimoku Cloud (simplified)
    df['TENKAN_SEN'] = ta.sma(df['Close'], length=9)
    df['KIJUN_SEN'] = ta.sma(df['Close'], length=26)
    
    return df 