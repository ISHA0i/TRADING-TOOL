import React from 'react';

const SignalCard = ({ data }) => {
  const { ticker, last_price, signals } = data;
  const { 
    signal, 
    confidence, 
    reasons, 
    signal_metrics, 
    market_regime,
    validation,
    divergences,
    patterns 
  } = signals;
  
  // Determine signal color based on signal type and validation
  const getSignalColor = () => {
    const adjustedConfidence = validation?.adjusted_confidence || confidence;
    const isValidated = validation?.regime_compatibility > 0;
    
    switch(signal) {
      case 'STRONG_BUY':
        return isValidated ? 'bg-green-600' : 'bg-green-600/70';
      case 'BUY':
        return isValidated ? 'bg-green-500' : 'bg-green-500/70';
      case 'WEAK_BUY':
        return isValidated ? 'bg-green-400' : 'bg-green-400/70';
      case 'STRONG_SELL':
        return isValidated ? 'bg-red-600' : 'bg-red-600/70';
      case 'SELL':
        return isValidated ? 'bg-red-500' : 'bg-red-500/70';
      case 'WEAK_SELL':
        return isValidated ? 'bg-red-400' : 'bg-red-400/70';
      default:
        return 'bg-gray-400';
    }
  };
  
  // Calculate confidence percentage with validation adjustment
  const confidencePercent = Math.round((validation?.adjusted_confidence || confidence) * 100);
  
  // Format score as percentage with color and trend indicator
  const formatScore = (score) => {
    const percent = Math.round((score + 1) * 50);
    const getScoreColor = (value) => {
      if (value > 60) return 'text-green-400';
      if (value < 40) return 'text-red-400';
      return 'text-yellow-400';
    };
    
    // Add trend indicator
    const getTrendIcon = (value) => {
      if (value > 60) return '↑';
      if (value < 40) return '↓';
      return '→';
    };
    
    return (
      <div className="flex items-center">
        <span className={getScoreColor(percent)}>{percent}%</span>
        <span className={`ml-1 ${getScoreColor(percent)}`}>{getTrendIcon(percent)}</span>
      </div>
    );
  };

  // Format regime metrics
  const getRegimeIndicator = () => {
    if (!market_regime) return null;
    
    const getRegimeColor = () => {
      switch(market_regime.type) {
        case 'trending':
          return 'text-blue-400';
        case 'ranging':
          return 'text-yellow-400';
        case 'volatile':
          return 'text-red-400';
        default:
          return 'text-gray-400';
      }
    };
    
    return (
      <div className="mb-4 p-3 bg-dark-surface-2 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-dark-text-secondary">Market Regime</span>
          <span className={`font-semibold ${getRegimeColor()}`}>
            {market_regime.type.charAt(0).toUpperCase() + market_regime.type.slice(1)}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-dark-text-secondary">Trend Strength</span>
            <span className="text-dark-text">{(market_regime.trend_strength * 100).toFixed(0)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-text-secondary">Volatility</span>
            <span className={`${market_regime.volatility === 'high' ? 'text-red-400' : 'text-dark-text'}`}>
              {market_regime.volatility.charAt(0).toUpperCase() + market_regime.volatility.slice(1)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-dark-text">{ticker}</h2>
        <div className="text-right">
          <span className="text-dark-text-secondary text-sm">Last Price</span>
          <p className="text-lg font-semibold text-dark-text">${last_price.toFixed(2)}</p>
        </div>
      </div>
      
      {getRegimeIndicator()}
      
      <div className="bg-dark-surface-2 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-dark-text">Signal</span>
            {validation?.warning_flags?.length > 0 && (
              <span className="ml-2 text-yellow-400 text-sm">⚠️</span>
            )}
          </div>
          <span className={`px-3 py-1 rounded-full text-dark-text font-semibold ${getSignalColor()}`}>
            {signal.replace(/_/g, ' ')}
          </span>
        </div>
        
        <div className="mt-4">
          <div className="flex justify-between mb-1">
            <span className="text-dark-text">Overall Confidence</span>
            <div className="flex items-center">
              {validation?.original_confidence && (
                <span className="text-dark-text-secondary text-sm mr-2">
                  ({Math.round(validation.original_confidence * 100)}% → )
                </span>
              )}
              <span className="text-dark-text font-semibold">{confidencePercent}%</span>
            </div>
          </div>
          <div className="w-full bg-dark-surface rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${getSignalColor()}`} 
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
        </div>
        
        {signal_metrics && (
          <div className="mt-4 pt-4 border-t border-dark-border">
            <h3 className="text-sm font-medium text-dark-text mb-2">Signal Components</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Trend Analysis</span>
                {formatScore(signal_metrics.trend_score)}
              </div>
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Momentum</span>
                {formatScore(signal_metrics.momentum_score)}
              </div>
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Volume Analysis</span>
                {formatScore(signal_metrics.volume_score)}
              </div>
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Volatility</span>
                {formatScore(signal_metrics.volatility_score)}
              </div>
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Chart Patterns</span>
                {formatScore(signal_metrics.pattern_score)}
              </div>
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Support/Resistance</span>
                {formatScore(signal_metrics.support_resistance_score)}
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2 text-dark-text">Signal Analysis</h3>
        <div className="space-y-4">
          {/* Warning Flags */}
          {validation?.warning_flags?.length > 0 && (
            <div className="bg-yellow-400/10 border border-yellow-400/20 rounded-lg p-3">
              <h4 className="text-sm font-medium text-yellow-400 mb-2">Warnings</h4>
              <ul className="list-disc pl-5 space-y-1">
                {validation.warning_flags.map((warning, index) => (
                  <li key={index} className="text-yellow-400/90 text-sm">{warning}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Pattern Recognition */}
          {patterns?.length > 0 && (
            <div className="bg-dark-surface-2 rounded-lg p-3">
              <h4 className="text-sm font-medium text-dark-text mb-2">Detected Patterns</h4>
              <div className="flex flex-wrap gap-2">
                {patterns.map((pattern, index) => (
                  <span key={index} className="px-2 py-1 bg-dark-surface rounded text-sm text-dark-text-secondary">
                    {pattern}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Divergences */}
          {divergences?.length > 0 && (
            <div className="bg-dark-surface-2 rounded-lg p-3">
              <h4 className="text-sm font-medium text-dark-text mb-2">Divergences</h4>
              <div className="flex flex-wrap gap-2">
                {divergences.map((divergence, index) => (
                  <span key={index} className="px-2 py-1 bg-dark-surface rounded text-sm text-dark-text-secondary">
                    {divergence}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Signal Reasons */}
          <div className="bg-dark-surface-2 rounded-lg p-3">
            <h4 className="text-sm font-medium text-dark-text mb-2">Analysis Details</h4>
            <ul className="list-disc pl-5 space-y-1 max-h-48 overflow-y-auto">
              {reasons.map((reason, index) => (
                <li key={index} className="text-dark-text-secondary text-sm">{reason}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignalCard;