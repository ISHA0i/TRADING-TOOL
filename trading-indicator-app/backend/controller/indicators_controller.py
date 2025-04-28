"""
Indicators Controller - Handles technical indicator calculations
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class IndicatorsController:
    """
    Controller for calculating technical indicators on market data
    """
    
    def __init__(self):
        """Initialize indicators controller"""
        logger.info("Initializing IndicatorsController")
    
    def calculate_all(self, data):
        """
        Calculate all technical indicators on the given market data
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            pd.DataFrame: Original data with added indicator columns
        """
        try:
            if data is None or data.empty:
                logger.warning("Empty data provided to calculate_all")
                return data
                
            # Make a copy to avoid modifying the original
            df = data.copy()
            
            # Calculate trend indicators
            df = self._calculate_moving_averages(df)
            df = self._calculate_macd(df)
            
            # Calculate momentum indicators
            df = self._calculate_rsi(df)
            df = self._calculate_stochastic(df)
            
            # Calculate volatility indicators
            df = self._calculate_bollinger_bands(df)
            df = self._calculate_atr(df)
            
            # Calculate volume indicators
            df = self._calculate_volume_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            # Return the original data if there's an error
            return data
    
    def _calculate_moving_averages(self, df):
        """Calculate various moving averages"""
        try:
            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating moving averages: {str(e)}")
            return df
    
    def _calculate_macd(self, df):
        """Calculate MACD indicator"""
        try:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            return df
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return df
    
    def _calculate_rsi(self, df, periods=14):
        """Calculate Relative Strength Index"""
        try:
            # Calculate price changes
            delta = df['Close'].diff()
            
            # Separate gains and losses
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # Calculate average gain and loss
            avg_gain = gain.rolling(window=periods).mean()
            avg_loss = loss.rolling(window=periods).mean()
            
            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            return df
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return df
    
    def _calculate_stochastic(self, df, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        try:
            # Calculate %K
            low_min = df['Low'].rolling(window=k_period).min()
            high_max = df['High'].rolling(window=k_period).max()
            df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
            
            # Calculate %D
            df['%D'] = df['%K'].rolling(window=d_period).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {str(e)}")
            return df
    
    def _calculate_bollinger_bands(self, df, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        try:
            # Check if there's enough data for calculation
            if len(df) < window:
                logger.warning(f"Not enough data for Bollinger Bands calculation (needed {window}, got {len(df)})")
                # Add empty columns and return
                df['BB_Middle'] = np.nan
                df['BB_Std'] = np.nan
                df['BB_Upper'] = np.nan
                df['BB_Lower'] = np.nan
                df['BB_%B'] = np.nan
                df['BB_Width'] = np.nan
                return df

            # Calculate middle band (SMA)
            df['BB_Middle'] = df['Close'].rolling(window=window).mean()
            
            # Calculate standard deviation with minimum value to prevent ultra-low volatility issues
            raw_std = df['Close'].rolling(window=window).std()
            df['BB_Std'] = np.where(
                raw_std < 1e-6,  # If std is too small (near zero)
                1e-6,           # Set a minimum value to prevent div/0
                raw_std
            )
            
            # Calculate upper and lower bands
            df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * num_std)
            df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * num_std)
            
            # Calculate %B with handling for division by zero and extreme values
            bb_diff = df['BB_Upper'] - df['BB_Lower']
            close_lower_diff = df['Close'] - df['BB_Lower']
            
            # Safely calculate %B
            df['BB_%B'] = np.where(
                (bb_diff > 1e-6) & ~np.isnan(bb_diff) & ~np.isnan(close_lower_diff),
                close_lower_diff / bb_diff,
                np.nan
            )
            
            # Create BB_Width column for easier analysis
            df['BB_Width'] = np.where(
                (df['BB_Middle'] > 1e-6) & ~np.isnan(df['BB_Middle']) & 
                ~np.isnan(df['BB_Upper']) & ~np.isnan(df['BB_Lower']),
                (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'],
                np.nan
            )
            
            # Fill potential NaN values in %B with sensible defaults
            # Values > 1 mean price is above upper band
            # Values < 0 mean price is below lower band
            df['BB_%B'] = np.where(
                (df['Close'] > df['BB_Upper']) & np.isnan(df['BB_%B']),
                1.1,  # Price above upper band
                df['BB_%B']
            )
            
            df['BB_%B'] = np.where(
                (df['Close'] < df['BB_Lower']) & np.isnan(df['BB_%B']),
                -0.1,  # Price below lower band
                df['BB_%B']
            )
            
            return df
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return df
    
    def _calculate_atr(self, df, window=14):
        """Calculate Average True Range"""
        try:
            # Calculate True Range
            df['TR'] = pd.DataFrame({
                'HL': df['High'] - df['Low'],
                'HC': abs(df['High'] - df['Close'].shift()),
                'LC': abs(df['Low'] - df['Close'].shift())
            }).max(axis=1)
            
            # Calculate ATR
            df['ATR'] = df['TR'].rolling(window=window).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return df
    
    def _calculate_volume_indicators(self, df):
        """Calculate volume-based indicators"""
        try:
            # Calculate On-Balance Volume (OBV)
            df['OBV_Signal'] = np.where(df['Close'] > df['Close'].shift(), 
                                df['Volume'], 
                                np.where(df['Close'] < df['Close'].shift(), 
                                        -df['Volume'], 0))
            df['OBV'] = df['OBV_Signal'].cumsum()
            
            # Volume Moving Average
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            
            return df
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            return df 