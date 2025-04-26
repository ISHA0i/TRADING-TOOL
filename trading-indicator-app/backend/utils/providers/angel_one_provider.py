from typing import Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
from SmartApi import SmartConnect
import pyotp
import logging

logger = logging.getLogger(__name__)

class AngelOneProvider:
    def __init__(self, api_key: str, client_id: str, secret_key: str, totp_key: str):
        self.api_key = api_key
        self.client_id = client_id
        self.secret_key = secret_key
        self.totp_key = totp_key
        self.smart_api = None
        self.session_token = None
        
    def connect(self) -> bool:
        """Establish connection with Angel One"""
        try:
            totp = pyotp.TOTP(self.totp_key)
            self.smart_api = SmartConnect(api_key=self.api_key)
            data = self.smart_api.generateSession(self.client_id, self.secret_key, totp.now())
            self.session_token = data['data']['jwtToken']
            return True
        except Exception as e:
            logger.error(f"Error connecting to Angel One: {str(e)}")
            return False
            
    def get_historical_data(self, symbol: str, timeframe: str = "ONE_DAY", 
                          from_date: datetime = None, to_date: datetime = None) -> pd.DataFrame:
        """
        Fetch historical data from Angel One
        
        Args:
            symbol: Trading symbol (e.g., 'RELIANCE-EQ')
            timeframe: Candle timeframe ('ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'THIRTY_MINUTE', 'ONE_HOUR', 'ONE_DAY')
            from_date: Start date for historical data
            to_date: End date for historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not self.smart_api:
                if not self.connect():
                    return pd.DataFrame()
                    
            # Default to last year if dates not provided
            if not to_date:
                to_date = datetime.now()
            if not from_date:
                from_date = to_date - timedelta(days=365)
                
            # Get historical data
            hist_data = self.smart_api.getCandleData({
                "exchange": "NSE",
                "symboltoken": symbol,
                "interval": timeframe,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            })
            
            if not hist_data or 'data' not in hist_data:
                logger.error(f"No data returned for {symbol}")
                return pd.DataFrame()
                
            # Convert to DataFrame
            df = pd.DataFrame(hist_data['data'], 
                            columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
            
    def format_symbol(self, symbol: str) -> str:
        """Format symbol for Angel One API"""
        # Add -EQ suffix if not present for equity symbols
        if not symbol.endswith('-EQ') and not symbol.endswith('-FUT'):
            symbol = f"{symbol}-EQ"
        return symbol