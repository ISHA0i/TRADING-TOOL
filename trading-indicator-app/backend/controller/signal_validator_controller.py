"""
Signal Validator Controller - Validates and refines trading signals
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SignalValidatorController:
    """
    Controller for validating trading signals against market conditions
    """
    
    def __init__(self):
        """Initialize signal validator controller"""
        logger.info("Initializing SignalValidatorController")
    
    def validate_signal(self, signals, data):
        """
        Validate trading signals against market conditions
        
        Args:
            signals (dict): Trading signals and analysis
            data (pd.DataFrame): Market data with indicators
            
        Returns:
            dict: Validated trading signals
        """
        try:
            if signals is None or not isinstance(signals, dict):
                logger.warning("Invalid signals provided to validate_signal")
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0.5,
                    "validation": {
                        "original_signal": "NONE",
                        "original_confidence": 0.0,
                        "warning_flags": ["Invalid signal data"]
                    }
                }
                
            # Make a copy of the original signals
            original_signal = signals.get('signal', 'NEUTRAL')
            original_confidence = signals.get('confidence', 0.5)
            
            # Store original values for reference
            signals['validation'] = {
                'original_signal': original_signal,
                'original_confidence': original_confidence,
                'warning_flags': []
            }
            
            # Apply validations
            self._validate_market_regime(signals, data)
            self._validate_signal_strength(signals, data)
            self._validate_context(signals, data)
            self._validate_conflicting_indicators(signals, data)
            
            return signals
            
        except Exception as e:
            logger.error(f"Error validating signals: {str(e)}")
            
            # Return original signals with error flag
            if signals and isinstance(signals, dict):
                signals['validation'] = {
                    'original_signal': signals.get('signal', 'NEUTRAL'),
                    'original_confidence': signals.get('confidence', 0.5),
                    'warning_flags': [f"Error in signal validation: {str(e)}"]
                }
                return signals
            else:
                return {
                    "signal": "NEUTRAL",
                    "confidence": 0.5,
                    "validation": {
                        "warning_flags": [f"Error in signal validation: {str(e)}"]
                    }
                }
    
    def _validate_market_regime(self, signals, data):
        """
        Validate signal against market regime
        - Reduce confidence in ranging markets
        - Flag signals against the trend
        """
        if 'market_regime' not in signals:
            signals['validation']['warning_flags'].append("Market regime data not available")
            return
            
        market_regime = signals['market_regime']
        regime_type = market_regime.get('type', 'unknown')
        trend_strength = market_regime.get('trend_strength', 0)
        signal_type = signals.get('signal', 'NEUTRAL')
        
        adjustment = 1.0
        
        # Adjust based on regime
        if regime_type == 'ranging':
            # Reduce confidence in ranging markets
            adjustment = 0.8
            signals['validation']['warning_flags'].append("Signal in ranging market - reduced confidence")
            
        elif regime_type == 'volatile':
            # Volatile markets need stronger signals
            adjustment = 0.7
            signals['validation']['warning_flags'].append("Signal in volatile market - reduced confidence")
            
        elif regime_type == 'trending' and trend_strength > 0.5:
            # Check if signal aligns with trend
            is_buy_signal = 'BUY' in signal_type
            is_uptrend = self._is_uptrend(data)
            
            if (is_buy_signal and not is_uptrend) or (not is_buy_signal and is_uptrend):
                adjustment = 0.6
                signals['validation']['warning_flags'].append("Signal against prevailing trend - reduced confidence")
            else:
                # Signal aligns with trend, can boost confidence
                adjustment = 1.1
        
        # Calculate regime compatibility (0-1)
        regime_compatibility = adjustment
        
        # Apply adjustment to confidence
        original_confidence = signals['validation']['original_confidence']
        signals['confidence'] = min(0.95, original_confidence * adjustment)
        
        # Add to validation data
        signals['validation']['adjusted_confidence'] = signals['confidence']
        signals['validation']['regime_compatibility'] = regime_compatibility
    
    def _validate_signal_strength(self, signals, data):
        """
        Validate signal strength based on context
        - Strong signals should have strong indicator readings
        """
        signal_type = signals.get('signal', 'NEUTRAL')
        signal_metrics = signals.get('signal_metrics', {})
        
        # Check for conflicting metrics
        if not signal_metrics:
            return
            
        # Check if strong signals have corresponding metrics
        if 'STRONG' in signal_type:
            # Define primary metrics based on signal type
            if 'BUY' in signal_type:
                primary_metrics = ['trend_score', 'momentum_score']
            else:
                primary_metrics = ['trend_score', 'momentum_score']
                
            # Check primary metrics
            weak_metrics = []
            for metric in primary_metrics:
                if metric in signal_metrics:
                    value = signal_metrics[metric]
                    if ('BUY' in signal_type and value < 0.3) or ('SELL' in signal_type and value > -0.3):
                        weak_metrics.append(metric)
            
            if weak_metrics:
                metrics_str = ', '.join(weak_metrics)
                signals['validation']['warning_flags'].append(f"Strong signal with weak {metrics_str}")
                
                # Adjust confidence
                signals['confidence'] = signals['confidence'] * 0.85
                signals['validation']['adjusted_confidence'] = signals['confidence']
    
    def _validate_context(self, signals, data):
        """
        Validate signal in broader market context
        - Check against key levels
        - Check against recent price action
        """
        # Check proximity to key levels
        support_levels = signals.get('support_levels', [])
        resistance_levels = signals.get('resistance_levels', [])
        
        if not data.empty:
            latest_close = data.iloc[-1]['Close']
            
            # Check if we're too close to resistance for a buy
            if 'BUY' in signals.get('signal', ''):
                for level in resistance_levels:
                    if abs(latest_close - level) / latest_close < 0.02:  # Within 2%
                        signals['validation']['warning_flags'].append("Buy signal near resistance level")
                        signals['confidence'] = signals['confidence'] * 0.9
                        break
                        
            # Check if we're too close to support for a sell
            if 'SELL' in signals.get('signal', ''):
                for level in support_levels:
                    if abs(latest_close - level) / latest_close < 0.02:  # Within 2%
                        signals['validation']['warning_flags'].append("Sell signal near support level")
                        signals['confidence'] = signals['confidence'] * 0.9
                        break
            
            # Update adjusted confidence
            signals['validation']['adjusted_confidence'] = signals['confidence']
    
    def _validate_conflicting_indicators(self, signals, data):
        """
        Validate signal for conflicting indicators
        - Check for disagreement between indicators
        """
        signal_metrics = signals.get('signal_metrics', {})
        
        if not signal_metrics:
            return
            
        # Define indicator groups
        trend_indicators = ['trend_score', 'support_resistance_score']
        momentum_indicators = ['momentum_score', 'pattern_score']
        
        # Check for internal conflicts in trend group
        trend_conflict = self._check_group_conflict(signal_metrics, trend_indicators)
        
        # Check for internal conflicts in momentum group
        momentum_conflict = self._check_group_conflict(signal_metrics, momentum_indicators)
        
        # Check for conflict between groups
        groups_conflict = False
        if 'trend_score' in signal_metrics and 'momentum_score' in signal_metrics:
            trend_sign = 1 if signal_metrics['trend_score'] > 0 else -1
            momentum_sign = 1 if signal_metrics['momentum_score'] > 0 else -1
            
            if trend_sign != momentum_sign and abs(signal_metrics['trend_score']) > 0.3 and abs(signal_metrics['momentum_score']) > 0.3:
                groups_conflict = True
        
        # Apply confidence adjustments for conflicts
        if trend_conflict:
            signals['validation']['warning_flags'].append("Conflicting trend indicators")
            signals['confidence'] = signals['confidence'] * 0.9
            
        if momentum_conflict:
            signals['validation']['warning_flags'].append("Conflicting momentum indicators")
            signals['confidence'] = signals['confidence'] * 0.9
            
        if groups_conflict:
            signals['validation']['warning_flags'].append("Trend and momentum indicators in conflict")
            signals['confidence'] = signals['confidence'] * 0.85
            
        # Update adjusted confidence
        signals['validation']['adjusted_confidence'] = signals['confidence']
    
    def _check_group_conflict(self, metrics, indicator_group):
        """Check for conflicts within an indicator group"""
        positive_count = 0
        negative_count = 0
        
        for indicator in indicator_group:
            if indicator in metrics:
                if metrics[indicator] > 0.2:
                    positive_count += 1
                elif metrics[indicator] < -0.2:
                    negative_count += 1
        
        # If we have both strong positive and negative indicators in the same group
        return positive_count > 0 and negative_count > 0
    
    def _is_uptrend(self, data):
        """Determine if the market is in an uptrend"""
        if data.empty or len(data) < 20:
            return False
            
        # Check moving averages if available
        if 'SMA_20' in data.columns and 'SMA_50' in data.columns:
            latest = data.iloc[-1]
            return latest['Close'] > latest['SMA_20'] and latest['SMA_20'] > latest['SMA_50']
        
        # Fallback to simple price comparison
        return data.iloc[-1]['Close'] > data.iloc[-20]['Close']
            
    def analyze_historical_accuracy(self, signals, historical_signals):
        """
        Analyze accuracy of signals based on historical performance
        
        Args:
            signals (dict): Current trading signals
            historical_signals (list): Historical signals and outcomes
            
        Returns:
            dict: Signal accuracy analysis
        """
        try:
            if not historical_signals:
                return None
                
            current_signal = signals.get('signal', 'NEUTRAL')
            
            # Filter for similar signals
            similar_signals = [s for s in historical_signals if s.get('signal') == current_signal]
            
            if not similar_signals:
                return None
                
            # Calculate accuracy metrics
            total_signals = len(similar_signals)
            successful_signals = sum(1 for s in similar_signals if s.get('outcome') == 'success')
            
            accuracy = successful_signals / total_signals if total_signals > 0 else 0
            
            # Calculate average profit factor
            wins = [s.get('profit', 0) for s in similar_signals if s.get('outcome') == 'success']
            losses = [abs(s.get('loss', 0)) for s in similar_signals if s.get('outcome') == 'failure']
            
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
            
            return {
                "signal_type": current_signal,
                "historical_accuracy": accuracy,
                "sample_size": total_signals,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "profit_factor": profit_factor
            }
            
        except Exception as e:
            logger.error(f"Error analyzing historical accuracy: {str(e)}")
            return None 