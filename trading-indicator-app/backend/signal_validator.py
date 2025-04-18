import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class SignalValidator:
    def __init__(self, history_file='signal_history.json'):
        self.history_file = history_file
        self.signal_history = self._load_history()
        
    def _load_history(self):
        """Load signal history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return {
                'signals': [],
                'metrics': {
                    'total_signals': 0,
                    'accurate_signals': 0,
                    'regime_accuracy': {},
                    'market_type_accuracy': {},
                    'timeframe_accuracy': {}
                }
            }
        except Exception as e:
            print(f"Error loading signal history: {e}")
            return {'signals': [], 'metrics': {}}
    
    def _save_history(self):
        """Save signal history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.signal_history, f, indent=2)
        except Exception as e:
            print(f"Error saving signal history: {e}")
    
    def validate_signal(self, signal, market_data, regime_metrics):
        """
        Validate signal against market conditions and historical accuracy
        Returns adjusted confidence score and validation metrics
        """
        # Initialize validation metrics
        validation = {
            'original_confidence': signal['confidence'],
            'adjusted_confidence': signal['confidence'],
            'regime_compatibility': 0.0,
            'historical_accuracy': 0.0,
            'volume_profile_score': 0.0,
            'market_context_score': 0.0,
            'warning_flags': []
        }
        
        # Check regime compatibility
        validation['regime_compatibility'] = self._check_regime_compatibility(
            signal['signal'], regime_metrics
        )
        
        # Calculate historical accuracy
        validation['historical_accuracy'] = self._calculate_historical_accuracy(
            signal['signal'], 
            regime_metrics['type'],
            market_data
        )
        
        # Analyze volume profile
        validation['volume_profile_score'] = self._analyze_volume_profile(
            market_data, signal
        )
        
        # Check market context
        validation['market_context_score'] = self._check_market_context(
            market_data, signal, regime_metrics
        )
        
        # Adjust confidence based on validation metrics
        confidence_adjustments = [
            validation['regime_compatibility'],
            validation['historical_accuracy'],
            validation['volume_profile_score'],
            validation['market_context_score']
        ]
        
        # Calculate weighted average of adjustments
        weights = [0.3, 0.3, 0.2, 0.2]  # Regime and historical accuracy weighted more heavily
        adjustment_factor = sum(adj * w for adj, w in zip(confidence_adjustments, weights))
        
        # Apply adjustment to confidence
        validation['adjusted_confidence'] = min(1.0, max(0.0, 
            signal['confidence'] * (1.0 + adjustment_factor)
        ))
        
        # Add warning flags for potential issues
        self._add_warning_flags(validation, signal, market_data, regime_metrics)
        
        return validation
    
    def _check_regime_compatibility(self, signal_type, regime_metrics):
        """Check if signal is compatible with current market regime"""
        regime_type = regime_metrics['type']
        trend_strength = regime_metrics['trend_strength']
        volatility = regime_metrics['volatility']
        
        compatibility_score = 0.0
        
        # Strong trend regime
        if regime_type == 'trending':
            if signal_type in ['STRONG_BUY', 'STRONG_SELL']:
                compatibility_score = 0.2
            elif signal_type in ['BUY', 'SELL']:
                compatibility_score = 0.1
            else:
                compatibility_score = -0.1
                
            # Adjust based on trend strength
            compatibility_score *= (1.0 + trend_strength)
        
        # Ranging market
        elif regime_type == 'ranging':
            if signal_type in ['WEAK_BUY', 'WEAK_SELL']:
                compatibility_score = 0.15
            elif signal_type == 'NEUTRAL':
                compatibility_score = 0.1
            else:
                compatibility_score = -0.15
        
        # Volatile market
        elif regime_type == 'volatile':
            if signal_type in ['STRONG_BUY', 'STRONG_SELL']:
                compatibility_score = -0.2  # Reduce confidence in strong signals
            elif signal_type == 'NEUTRAL':
                compatibility_score = 0.1
        
        # Adjust based on volatility
        if volatility == 'high':
            compatibility_score *= 0.8  # Reduce all signals in high volatility
        
        return compatibility_score
    
    def _calculate_historical_accuracy(self, signal_type, regime_type, market_data):
        """Calculate historical accuracy for similar market conditions"""
        similar_signals = [s for s in self.signal_history['signals']
                         if s['signal_type'] == signal_type 
                         and s['regime_type'] == regime_type
                         and s['validated']]
        
        if not similar_signals:
            return 0.0
        
        accurate_signals = len([s for s in similar_signals if s['was_accurate']])
        accuracy = accurate_signals / len(similar_signals)
        
        # Adjust score based on sample size
        confidence_factor = min(1.0, len(similar_signals) / 20)  # Max confidence at 20 samples
        return (accuracy - 0.5) * confidence_factor  # Center around 0
    
    def _analyze_volume_profile(self, market_data, signal):
        """Analyze volume profile for signal validation"""
        recent_data = market_data.tail(20)
        
        # Calculate volume metrics
        avg_volume = recent_data['Volume'].mean()
        current_volume = recent_data['Volume'].iloc[-1]
        volume_trend = np.polyfit(range(len(recent_data)), recent_data['Volume'], 1)[0]
        
        score = 0.0
        
        # Volume confirmation
        if current_volume > avg_volume * 1.5:
            score += 0.1
        elif current_volume < avg_volume * 0.5:
            score -= 0.1
        
        # Volume trend alignment
        if volume_trend > 0 and signal['signal'] in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
            score += 0.1
        elif volume_trend < 0 and signal['signal'] in ['STRONG_SELL', 'SELL', 'WEAK_SELL']:
            score += 0.1
        
        return score
    
    def _check_market_context(self, market_data, signal, regime_metrics):
        """Check broader market context for signal validation"""
        lookback = min(100, len(market_data))
        recent_data = market_data.tail(lookback)
        
        score = 0.0
        
        # Trend consistency
        price_trend = np.polyfit(range(len(recent_data)), recent_data['Close'], 1)[0]
        if (price_trend > 0 and signal['signal'] in ['STRONG_BUY', 'BUY', 'WEAK_BUY']) or \
           (price_trend < 0 and signal['signal'] in ['STRONG_SELL', 'SELL', 'WEAK_SELL']):
            score += 0.1
        
        # Volatility context
        current_volatility = recent_data['ATR'].iloc[-1]
        avg_volatility = recent_data['ATR'].mean()
        
        if current_volatility > avg_volatility * 1.5:
            score -= 0.1  # Higher risk in high volatility
        elif current_volatility < avg_volatility * 0.5:
            score += 0.05  # More predictable in low volatility
        
        return score
    
    def _add_warning_flags(self, validation, signal, market_data, regime_metrics):
        """Add warning flags for potential issues"""
        # Initialize warning flags
        warnings = []
        
        # Check for low historical accuracy
        if validation['historical_accuracy'] < -0.1:
            warnings.append("Low historical accuracy for similar conditions")
        
        # Check for regime mismatch
        if validation['regime_compatibility'] < -0.1:
            warnings.append("Signal may not suit current market regime")
        
        # Check for volume concerns
        if validation['volume_profile_score'] < -0.1:
            warnings.append("Insufficient volume confirmation")
        
        # Check for volatility
        if regime_metrics['volatility'] == 'high':
            warnings.append("High market volatility - consider reducing position size")
        
        # Check for extreme RSI
        latest = market_data.iloc[-1]
        if latest['RSI14'] > 80 or latest['RSI14'] < 20:
            warnings.append("Extreme RSI levels - potential reversal risk")
        
        validation['warning_flags'] = warnings
    
    def record_signal(self, signal, validation, regime_metrics):
        """Record signal for historical tracking"""
        signal_record = {
            'timestamp': datetime.now().isoformat(),
            'signal_type': signal['signal'],
            'confidence': signal['confidence'],
            'adjusted_confidence': validation['adjusted_confidence'],
            'regime_type': regime_metrics['type'],
            'validation_metrics': validation,
            'validated': False,
            'was_accurate': None,
            'price_at_signal': signal['entry_price']
        }
        
        self.signal_history['signals'].append(signal_record)
        self._save_history()
    
    def validate_historical_signal(self, signal_id, was_accurate, exit_price):
        """Update historical signal with accuracy information"""
        if signal_id < len(self.signal_history['signals']):
            signal = self.signal_history['signals'][signal_id]
            signal['validated'] = True
            signal['was_accurate'] = was_accurate
            signal['exit_price'] = exit_price
            
            # Update accuracy metrics
            metrics = self.signal_history['metrics']
            metrics['total_signals'] += 1
            if was_accurate:
                metrics['accurate_signals'] += 1
            
            # Update regime-specific accuracy
            regime = signal['regime_type']
            if regime not in metrics['regime_accuracy']:
                metrics['regime_accuracy'][regime] = {'total': 0, 'accurate': 0}
            metrics['regime_accuracy'][regime]['total'] += 1
            if was_accurate:
                metrics['regime_accuracy'][regime]['accurate'] += 1
            
            self._save_history()
    
    def get_accuracy_metrics(self):
        """Get current accuracy metrics"""
        metrics = self.signal_history['metrics']
        
        if metrics['total_signals'] == 0:
            return {
                'overall_accuracy': 0.0,
                'regime_accuracy': {},
                'sample_size': 0
            }
        
        overall_accuracy = metrics['accurate_signals'] / metrics['total_signals']
        
        regime_accuracy = {}
        for regime, stats in metrics['regime_accuracy'].items():
            if stats['total'] > 0:
                regime_accuracy[regime] = stats['accurate'] / stats['total']
        
        return {
            'overall_accuracy': overall_accuracy,
            'regime_accuracy': regime_accuracy,
            'sample_size': metrics['total_signals']
        }