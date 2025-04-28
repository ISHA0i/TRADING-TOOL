"""
Strategy Controller - Generates trading signals based on technical indicators
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class StrategyController:
    """
    Controller for generating trading signals based on technical indicators
    """
    
    def __init__(self):
        """Initialize strategy controller"""
        logger.info("Initializing StrategyController")
    
    def generate_signals(self, data):
        """
        Generate trading signals based on technical indicators
        
        Args:
            data (pd.DataFrame): Market data with technical indicators
            
        Returns:
            dict: Trading signals and analysis
        """
        try:
            if data is None or data.empty:
                logger.warning("Empty data provided to generate_signals")
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0.5,
                    "reasons": ["Insufficient data for analysis"]
                }
            
            # Use the most recent data for signal generation
            latest_data = data.iloc[-1]
            
            # Calculate different signal components
            trend_score = self._analyze_trend(data)
            momentum_score = self._analyze_momentum(data)
            volatility_score = self._analyze_volatility(data)
            volume_score = self._analyze_volume(data)
            pattern_score = self._analyze_patterns(data)
            sr_score = self._analyze_support_resistance(data)
            
            # Calculate overall signal based on component scores
            signal_metrics = {
                "trend_score": trend_score,
                "momentum_score": momentum_score,
                "volatility_score": volatility_score,
                "volume_score": volume_score,
                "pattern_score": pattern_score,
                "support_resistance_score": sr_score
            }
            
            # Calculate weighted average for overall signal
            weights = {
                "trend_score": 0.30,
                "momentum_score": 0.20,
                "volatility_score": 0.10,
                "volume_score": 0.15,
                "pattern_score": 0.10,
                "support_resistance_score": 0.15
            }
            
            overall_score = sum(score * weights[key] for key, score in signal_metrics.items())
            
            # Determine signal type and confidence based on overall score
            signal_type, confidence = self._determine_signal(overall_score)
            
            # Generate reasons for the signal
            reasons = self._generate_reasons(signal_metrics, data)
            
            # Detect chart patterns
            patterns = self._detect_patterns(data)
            
            # Detect divergences
            divergences = self._detect_divergences(data)
            
            # Identify support and resistance levels
            support_levels, resistance_levels = self._find_support_resistance_levels(data)
            
            # Calculate entry, stop loss, and take profit prices
            entry_price = latest_data['Close']
            stop_loss = self._calculate_stop_loss(data, signal_type)
            take_profit = self._calculate_take_profit(data, signal_type, entry_price, stop_loss)
            
            # Determine market regime
            market_regime = self._determine_market_regime(data)
            
            return {
                "signal": signal_type,
                "confidence": confidence,
                "reasons": reasons,
                "signal_metrics": signal_metrics,
                "patterns": patterns if patterns else None,
                "divergences": divergences if divergences else None,
                "market_regime": market_regime,
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return {
                "signal": "ERROR",
                "confidence": 0,
                "reasons": [f"Error in signal generation: {str(e)}"]
            }
    
    def _analyze_trend(self, data):
        """Analyze price trend based on moving averages"""
        try:
            latest = data.iloc[-1]
            
            # Check moving average relationships
            ma_score = 0
            
            # Check if price is above/below SMAs
            if latest['Close'] > latest['SMA_20']:
                ma_score += 0.2
            else:
                ma_score -= 0.2
                
            if latest['Close'] > latest['SMA_50']:
                ma_score += 0.3
            else:
                ma_score -= 0.3
                
            if latest['Close'] > latest['SMA_200']:
                ma_score += 0.5
            else:
                ma_score -= 0.5
            
            # Check MA crossovers
            if latest['SMA_20'] > latest['SMA_50'] and data.iloc[-2]['SMA_20'] <= data.iloc[-2]['SMA_50']:
                ma_score += 0.5  # Golden cross (short-term)
            
            if latest['SMA_50'] > latest['SMA_200'] and data.iloc[-2]['SMA_50'] <= data.iloc[-2]['SMA_200']:
                ma_score += 0.7  # Golden cross (long-term)
                
            if latest['SMA_20'] < latest['SMA_50'] and data.iloc[-2]['SMA_20'] >= data.iloc[-2]['SMA_50']:
                ma_score -= 0.5  # Death cross (short-term)
            
            if latest['SMA_50'] < latest['SMA_200'] and data.iloc[-2]['SMA_50'] >= data.iloc[-2]['SMA_200']:
                ma_score -= 0.7  # Death cross (long-term)
            
            # Normalize score to range [-1, 1]
            ma_score = max(min(ma_score, 1), -1)
            
            return ma_score
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return 0
    
    def _analyze_momentum(self, data):
        """Analyze momentum based on RSI and stochastic"""
        try:
            latest = data.iloc[-1]
            
            # RSI analysis
            rsi_score = 0
            
            if latest['RSI'] > 70:
                rsi_score = -0.8  # Overbought
            elif latest['RSI'] < 30:
                rsi_score = 0.8   # Oversold
            elif latest['RSI'] > 50:
                rsi_score = 0.4   # Bullish momentum
            elif latest['RSI'] < 50:
                rsi_score = -0.4  # Bearish momentum
            
            # Stochastic analysis
            stoch_score = 0
            
            if latest['%K'] > 80 and latest['%D'] > 80:
                stoch_score = -0.7  # Overbought
            elif latest['%K'] < 20 and latest['%D'] < 20:
                stoch_score = 0.7   # Oversold
            
            # Stochastic crossover
            if latest['%K'] > latest['%D'] and data.iloc[-2]['%K'] <= data.iloc[-2]['%D']:
                stoch_score += 0.3  # Bullish crossover
            elif latest['%K'] < latest['%D'] and data.iloc[-2]['%K'] >= data.iloc[-2]['%D']:
                stoch_score -= 0.3  # Bearish crossover
            
            # Combine scores (equal weight)
            momentum_score = (rsi_score + stoch_score) / 2
            
            return momentum_score
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {str(e)}")
            return 0
    
    def _analyze_volatility(self, data):
        """Analyze volatility based on Bollinger Bands and ATR"""
        try:
            latest = data.iloc[-1]
            
            # Bollinger Band analysis
            bb_score = 0
            
            # %B analysis (position within BB)
            if 'BB_%B' in latest and not np.isnan(latest['BB_%B']):
                if latest['BB_%B'] > 1:
                    bb_score = -0.7  # Price above upper band (overextended)
                elif latest['BB_%B'] < 0:
                    bb_score = 0.7   # Price below lower band (oversold)
                elif latest['BB_%B'] > 0.8:
                    bb_score = -0.3  # Price near upper band
                elif latest['BB_%B'] < 0.2:
                    bb_score = 0.3   # Price near lower band
            
            # Use the BB_Width column we've calculated in indicators_controller.py
            bb_width = 0
            if 'BB_Width' in latest and not np.isnan(latest['BB_Width']):
                bb_width = latest['BB_Width']
            elif ('BB_Middle' in latest and 'BB_Upper' in latest and 'BB_Lower' in latest and
                latest['BB_Middle'] != 0 and not np.isnan(latest['BB_Upper']) and 
                not np.isnan(latest['BB_Lower']) and not np.isnan(latest['BB_Middle'])):
                try:
                    bb_width = (latest['BB_Upper'] - latest['BB_Lower']) / latest['BB_Middle']
                except (ZeroDivisionError, FloatingPointError):
                    bb_width = 0
            
            # Calculate rolling average BB width safely
            bb_width_avg = 0
            try:
                if 'BB_Width' in data.columns:
                    # Directly use the pre-calculated BB_Width column
                    valid_bb_width = data['BB_Width'].dropna()
                    if not valid_bb_width.empty:
                        bb_width_avg = valid_bb_width.mean()
                else:
                    # Fallback to calculating it manually
                    valid_rows = (data['BB_Middle'] != 0) & ~np.isnan(data['BB_Upper']) & ~np.isnan(data['BB_Lower']) & ~np.isnan(data['BB_Middle'])
                    
                    if valid_rows.any():
                        temp_data = data[valid_rows].copy()
                        temp_data['BB_Width'] = (temp_data['BB_Upper'] - temp_data['BB_Lower']) / temp_data['BB_Middle']
                        bb_width_avg = temp_data['BB_Width'].mean()
                
                # Analyze current BB width vs average
                if np.isfinite(bb_width) and np.isfinite(bb_width_avg) and bb_width_avg > 0:
                    if bb_width > bb_width_avg * 1.5:
                        bb_score -= 0.3  # High volatility
                    elif bb_width < bb_width_avg * 0.5:
                        bb_score += 0.2  # Low volatility, potential for expansion
            except Exception as e:
                logger.warning(f"Error calculating BB width: {str(e)}")
            
            # ATR analysis for volatility
            atr_score = 0
            if 'ATR' in latest and 'Close' in latest and latest['Close'] > 0 and not np.isnan(latest['ATR']):
                atr_percent = latest['ATR'] / latest['Close']
                
                if atr_percent > 0.03:
                    atr_score = -0.3  # High volatility
                elif atr_percent < 0.01:
                    atr_score = 0.3   # Low volatility
            
            # Combine scores
            volatility_score = (bb_score + atr_score) / 2
            
            return volatility_score
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {str(e)}")
            return 0
    
    def _analyze_volume(self, data):
        """Analyze volume indicators"""
        try:
            latest = data.iloc[-1]
            prev = data.iloc[-2]
            
            volume_score = 0
            
            # Volume relative to average
            if latest['Volume'] > latest['Volume_SMA'] * 1.5:
                # High volume
                if latest['Close'] > prev['Close']:
                    volume_score += 0.6  # High volume on up move
                else:
                    volume_score -= 0.6  # High volume on down move
            
            # OBV trend
            obv_slope = (latest['OBV'] - data.iloc[-5]['OBV']) / 5
            
            if obv_slope > 0:
                volume_score += 0.4  # Rising OBV
            else:
                volume_score -= 0.4  # Falling OBV
            
            # Normalize score
            volume_score = max(min(volume_score, 1), -1)
            
            return volume_score
            
        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return 0
    
    def _analyze_patterns(self, data):
        """Analyze chart patterns"""
        # This is a simplified placeholder that would be expanded
        # with actual pattern recognition in a real implementation
        return 0
    
    def _analyze_support_resistance(self, data):
        """Analyze price in relation to support/resistance levels"""
        try:
            # This is a simplified implementation
            support_levels, resistance_levels = self._find_support_resistance_levels(data)
            
            latest_close = data.iloc[-1]['Close']
            
            sr_score = 0
            
            # Check if price is near support
            if support_levels and latest_close > 0:
                # Safely calculate distances and avoid division by zero
                distances = [abs(latest_close - level) / latest_close if latest_close != 0 else float('inf') for level in support_levels]
                # Filter out any NaN or inf values before using min()
                valid_distances = [d for d in distances if np.isfinite(d)]
                if valid_distances and min(valid_distances) < 0.02:
                    sr_score += 0.7  # Price near support
            
            # Check if price is near resistance
            if resistance_levels and latest_close > 0:
                # Safely calculate distances and avoid division by zero
                distances = [abs(latest_close - level) / latest_close if latest_close != 0 else float('inf') for level in resistance_levels]
                # Filter out any NaN or inf values before using min()
                valid_distances = [d for d in distances if np.isfinite(d)]
                if valid_distances and min(valid_distances) < 0.02:
                    sr_score -= 0.7  # Price near resistance
            
            return sr_score
            
        except Exception as e:
            logger.error(f"Error analyzing support/resistance: {str(e)}")
            return 0
    
    def _determine_signal(self, overall_score):
        """Determine signal type and confidence based on overall score"""
        if overall_score > 0.6:
            return "STRONG_BUY", min(0.9, 0.5 + overall_score * 0.5)
        elif overall_score > 0.3:
            return "BUY", min(0.8, 0.5 + overall_score * 0.4)
        elif overall_score > 0.1:
            return "WEAK_BUY", min(0.7, 0.5 + overall_score * 0.3)
        elif overall_score > -0.1:
            return "NEUTRAL", 0.5
        elif overall_score > -0.3:
            return "WEAK_SELL", min(0.7, 0.5 - overall_score * 0.3)
        elif overall_score > -0.6:
            return "SELL", min(0.8, 0.5 - overall_score * 0.4)
        else:
            return "STRONG_SELL", min(0.9, 0.5 - overall_score * 0.5)
    
    def _generate_reasons(self, signal_metrics, data):
        """Generate human-readable reasons for the signal"""
        reasons = []
        latest = data.iloc[-1]
        
        # Trend reasons
        if signal_metrics["trend_score"] > 0.5:
            reasons.append("Strong uptrend identified with price above key moving averages")
        elif signal_metrics["trend_score"] > 0.2:
            reasons.append("Moderate uptrend with price above short-term moving averages")
        elif signal_metrics["trend_score"] < -0.5:
            reasons.append("Strong downtrend identified with price below key moving averages")
        elif signal_metrics["trend_score"] < -0.2:
            reasons.append("Moderate downtrend with price below short-term moving averages")
        
        # Momentum reasons
        if signal_metrics["momentum_score"] > 0.5:
            reasons.append("Strong bullish momentum indicated by oscillators")
        elif signal_metrics["momentum_score"] > 0.2:
            reasons.append("Improving momentum with oscillators in bullish territory")
        elif signal_metrics["momentum_score"] < -0.5:
            reasons.append("Strong bearish momentum indicated by oscillators")
        elif signal_metrics["momentum_score"] < -0.2:
            reasons.append("Deteriorating momentum with oscillators in bearish territory")
        
        # Volatility reasons
        if abs(signal_metrics["volatility_score"]) > 0.5:
            if signal_metrics["volatility_score"] > 0:
                reasons.append("Price is near lower Bollinger Band, suggesting potential oversold condition")
            else:
                reasons.append("Price is near upper Bollinger Band, suggesting potential overbought condition")
        
        # Volume reasons
        if signal_metrics["volume_score"] > 0.5:
            reasons.append("Strong volume supporting price action")
        elif signal_metrics["volume_score"] < -0.5:
            reasons.append("Volume indicators suggesting potential weakness")
        
        # Support/resistance reasons
        if signal_metrics["support_resistance_score"] > 0.5:
            reasons.append("Price is near key support level")
        elif signal_metrics["support_resistance_score"] < -0.5:
            reasons.append("Price is testing key resistance level")
        
        # Add pattern-specific reasons
        patterns = self._detect_patterns(data)
        if patterns:
            for pattern in patterns:
                reasons.append(f"Detected {pattern} pattern")
        
        # Make sure we have at least one reason
        if not reasons:
            if sum(signal_metrics.values()) > 0:
                reasons.append("Multiple technical indicators showing bullish signals")
            else:
                reasons.append("Multiple technical indicators showing bearish signals")
        
        return reasons
    
    def _detect_patterns(self, data):
        """Detect chart patterns in the data"""
        # Placeholder for pattern detection
        # In a real implementation, this would be a more sophisticated algorithm
        return []
    
    def _detect_divergences(self, data):
        """Detect divergences between price and indicators"""
        # Placeholder for divergence detection
        # In a real implementation, this would check for divergences between price and oscillators
        return []
    
    def _find_support_resistance_levels(self, data):
        """Find key support and resistance levels"""
        # This is a simplified implementation
        support_levels = []
        resistance_levels = []
        
        # Use recent lows as support
        for i in range(5, len(data)):
            if (data.iloc[i-2]['Low'] > data.iloc[i-1]['Low'] and 
                data.iloc[i]['Low'] > data.iloc[i-1]['Low']):
                support_levels.append(data.iloc[i-1]['Low'])
        
        # Use recent highs as resistance
        for i in range(5, len(data)):
            if (data.iloc[i-2]['High'] < data.iloc[i-1]['High'] and 
                data.iloc[i]['High'] < data.iloc[i-1]['High']):
                resistance_levels.append(data.iloc[i-1]['High'])
        
        # Filter to keep just a few levels
        if support_levels:
            support_levels = sorted(support_levels)[-3:]
        if resistance_levels:
            resistance_levels = sorted(resistance_levels)[:3]
        
        return support_levels, resistance_levels
    
    def _calculate_stop_loss(self, data, signal_type):
        """Calculate appropriate stop loss level"""
        latest = data.iloc[-1]
        
        if "BUY" in signal_type:
            # For buy signals, use recent lows or ATR-based stop
            recent_lows = data.iloc[-10:]['Low']
            atr_stop = latest['Close'] - 1.5 * latest.get('ATR', latest['Close'] * 0.02)
            return max(min(recent_lows), atr_stop)
        else:
            # For sell signals, use recent highs or ATR-based stop
            recent_highs = data.iloc[-10:]['High']
            atr_stop = latest['Close'] + 1.5 * latest.get('ATR', latest['Close'] * 0.02)
            return min(max(recent_highs), atr_stop)
    
    def _calculate_take_profit(self, data, signal_type, entry_price, stop_loss):
        """Calculate take profit target based on risk/reward ratio"""
        risk = abs(entry_price - stop_loss)
        
        if "BUY" in signal_type:
            return entry_price + risk * 2  # 2:1 reward-to-risk ratio
        else:
            return entry_price - risk * 2  # 2:1 reward-to-risk ratio
    
    def _determine_market_regime(self, data):
        """Determine current market regime (trending, ranging, volatile)"""
        try:
            # Calculate ADX for trend strength
            adx = self._calculate_adx(data)
            latest_adx = adx.iloc[-1] if not adx.empty else 0
            
            # Calculate volatility
            returns = data['Close'].pct_change()
            volatility = returns.rolling(20).std().iloc[-1] * (252 ** 0.5)  # Annualized
            
            # Determine regime
            trend_strength = latest_adx / 100  # Normalize to 0-1
            
            if latest_adx > 25:
                regime_type = "trending"
            elif volatility > returns.rolling(20).std().mean() * 1.5:
                regime_type = "volatile"
            else:
                regime_type = "ranging"
                
            # Determine volatility level
            volatility_level = "high" if volatility > 0.3 else "medium" if volatility > 0.15 else "low"
            
            return {
                "type": regime_type,
                "trend_strength": trend_strength,
                "volatility": volatility_level,
                "adx": latest_adx,
                "volatility_value": volatility
            }
            
        except Exception as e:
            logger.error(f"Error determining market regime: {str(e)}")
            return {
                "type": "unknown",
                "trend_strength": 0,
                "volatility": "unknown"
            }
    
    def _calculate_adx(self, data, period=14):
        """Calculate Average Directional Index"""
        try:
            df = data.copy()
            
            # Calculate +DM, -DM, and TR
            df['up_move'] = df['High'] - df['High'].shift(1)
            df['down_move'] = df['Low'].shift(1) - df['Low']
            
            df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
            df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
            
            # Use previously calculated TR or calculate
            if 'TR' not in df.columns:
                df['tr1'] = abs(df['High'] - df['Low'])
                df['tr2'] = abs(df['High'] - df['Close'].shift(1))
                df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
                df['TR'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Calculate smoothed +DM, -DM, and TR
            df['plus_di'] = 100 * (df['plus_dm'].rolling(period).mean() / df['TR'].rolling(period).mean())
            df['minus_di'] = 100 * (df['minus_dm'].rolling(period).mean() / df['TR'].rolling(period).mean())
            
            # Calculate DX and ADX
            df['dx'] = 100 * abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
            df['ADX'] = df['dx'].rolling(period).mean()
            
            return df['ADX']
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {str(e)}")
            return pd.Series(dtype=float) 