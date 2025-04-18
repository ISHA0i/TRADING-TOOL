import React from 'react';

const RiskRewardCard = ({ data, symbolType }) => {
  const { ticker, last_price, signals } = data;
  const { 
    signal, 
    entry_price, 
    stop_loss, 
    take_profit, 
    support_levels, 
    resistance_levels,
    market_regime,
    validation
  } = signals;
  
  // Determine signal strength and market conditions
  const isBuySignal = signal.includes('BUY');
  const isStrongSignal = signal.includes('STRONG');
  const isVolatile = market_regime?.volatility === 'high';
  const mainColor = isBuySignal ? 'green' : signal.includes('SELL') ? 'red' : 'gray';
  
  // Calculate risk/reward metrics with market context
  const calculateMetrics = () => {
    if (!stop_loss || !take_profit || !entry_price) {
      const missingValues = [];
      if (!entry_price) missingValues.push('entry price');
      if (!stop_loss) missingValues.push('stop loss');
      if (!take_profit) missingValues.push('take profit');
      
      return {
        rr_ratio: null,
        stopLossPercent: null,
        takeProfitPercent: null,
        pipRisk: null,
        pipReward: null,
        pipValue: null,
        missingValues
      };
    }
    
    const risk = Math.abs(entry_price - stop_loss);
    const reward = Math.abs(entry_price - take_profit);
    let rr_ratio = risk === 0 ? 0 : reward / risk;
    
    // Adjust R:R ratio based on market conditions
    if (isVolatile) {
      rr_ratio *= 0.8; // Reduce expected reward in high volatility
    }
    if (isStrongSignal && validation?.regime_compatibility > 0) {
      rr_ratio *= 1.2; // Increase expected reward for strong signals in compatible regime
    }
    
    // Calculate potential profit/loss percentages
    const stopLossPercent = ((stop_loss - entry_price) / entry_price) * 100;
    const takeProfitPercent = ((take_profit - entry_price) / entry_price) * 100;
    
    // Calculate pip values for forex
    let pipValue = 0;
    let pipRisk = 0;
    let pipReward = 0;
    
    if (symbolType === 'forex') {
      const isJPYPair = ticker.includes('JPY');
      const pipMultiplier = isJPYPair ? 100 : 10000;
      
      pipValue = Math.pow(10, -4);
      if (isJPYPair) pipValue = 0.01;
      
      pipRisk = Math.abs(entry_price - stop_loss) * pipMultiplier;
      pipReward = Math.abs(entry_price - take_profit) * pipMultiplier;
    }
    
    return {
      rr_ratio,
      stopLossPercent,
      takeProfitPercent,
      pipRisk,
      pipReward,
      pipValue
    };
  };

  const metrics = calculateMetrics();
  
  // Update formatPrice function to handle price precision
  const formatPrice = (price) => {
    if (!price) return 'N/A';
    
    if (symbolType === 'crypto') {
      return price < 1 ? price.toFixed(6) : price.toFixed(2);
    } else if (symbolType === 'forex') {
      const isJPYPair = ticker.includes('JPY');
      return isJPYPair ? price.toFixed(3) : price.toFixed(5);
    }
    return price.toFixed(2);
  };
  
  // Format percentage with dynamic coloring
  const formatPercent = (value) => {
    if (!value) return 'N/A';
    
    const color = value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-dark-text';
    return (
      <span className={color}>
        {value > 0 ? '+' : ''}{value.toFixed(2)}%
        {isVolatile && '⚠️'}
      </span>
    );
  };
  
  // Get dynamic warning messages based on analysis
  const getWarnings = () => {
    const warnings = [];
    
    // Add missing values warning first
    if (metrics.missingValues?.length > 0) {
      warnings.push(`Missing required values: ${metrics.missingValues.join(', ')}`);
    }
    
    if (isVolatile) {
      warnings.push('High volatility - consider reducing position size');
    }
    if (metrics.rr_ratio && metrics.rr_ratio < 1.5) {
      warnings.push('Risk-reward ratio below recommended 1.5:1');
    }
    if (validation?.warning_flags) {
      warnings.push(...validation.warning_flags);
    }
    
    return warnings;
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-dark-text">Risk / Reward Analysis</h2>
      
      <div className="space-y-6">
        {/* Entry, Stop Loss, Target */}
        <div className="bg-dark-surface-2 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Entry Price</span>
              <span className="font-semibold text-dark-text">{formatPrice(entry_price)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Current Price</span>
              <div className="text-right">
                <span className="font-semibold text-dark-text">{formatPrice(last_price)}</span>
                {last_price !== entry_price && (
                  <div className="text-sm">
                    {formatPercent(((last_price - entry_price) / entry_price) * 100)}
                  </div>
                )}
              </div>
            </div>
            
            {stop_loss && (
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Stop Loss</span>
                <div className="text-right">
                  <div className="font-semibold text-red-500">
                    {formatPrice(stop_loss)}
                  </div>
                  <div className="text-sm text-red-400">
                    {formatPercent(metrics.stopLossPercent)}
                    {symbolType === 'forex' && ` (${metrics.pipRisk.toFixed(1)} pips)`}
                  </div>
                </div>
              </div>
            )}
            
            {take_profit && (
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Take Profit</span>
                <div className="text-right">
                  <div className="font-semibold text-green-500">
                    {formatPrice(take_profit)}
                  </div>
                  <div className="text-sm text-green-400">
                    {formatPercent(metrics.takeProfitPercent)}
                    {symbolType === 'forex' && ` (${metrics.pipReward.toFixed(1)} pips)`}
                  </div>
                </div>
              </div>
            )}
            
            <div className="border-t border-dark-border pt-2 mt-2">
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">Risk/Reward Ratio</span>
                <div className="text-right">
                  <span className={`font-bold ${metrics.rr_ratio >= 1.5 ? 'text-green-400' : metrics.rr_ratio ? 'text-yellow-400' : 'text-dark-text-secondary'}`}>
                    {metrics.rr_ratio ? `${metrics.rr_ratio.toFixed(2)}:1` : 'N/A'}
                  </span>
                  {metrics.missingValues?.length > 0 && (
                    <div className="text-xs text-dark-text-secondary">
                      Missing: {metrics.missingValues.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Warning Messages */}
        {getWarnings().length > 0 && (
          <div className="bg-yellow-400/10 border border-yellow-400/20 rounded-lg p-3">
            <h4 className="text-sm font-medium text-yellow-400 mb-2">Risk Warnings</h4>
            <ul className="list-disc pl-5 space-y-1">
              {getWarnings().map((warning, index) => (
                <li key={index} className="text-yellow-400/90 text-sm">{warning}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Support & Resistance Levels */}
        <div>
          <h3 className="text-md font-semibold mb-2 text-dark-text">Key Price Levels</h3>
          <div className="space-y-3">
            {/* Resistance Levels */}
            <div>
              <h4 className="text-sm text-dark-text-secondary mb-1">Resistance</h4>
              <div className="flex flex-wrap gap-2">
                {resistance_levels && resistance_levels.length > 0 ? (
                  resistance_levels.map((level, index) => {
                    const priceDiff = ((level - last_price) / last_price) * 100;
                    const isNearby = Math.abs(priceDiff) < 1;
                    return (
                      <div 
                        key={index}
                        className={`bg-dark-surface-2 border ${isNearby ? 'border-red-500' : 'border-red-500/20'} rounded p-2`}
                      >
                        <div className="text-red-400 font-medium">
                          {formatPrice(level)}
                        </div>
                        <div className="text-xs text-red-500">
                          {formatPercent(priceDiff)}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <span className="text-dark-text-secondary text-sm">No levels detected</span>
                )}
              </div>
            </div>

            {/* Support Levels */}
            <div>
              <h4 className="text-sm text-dark-text-secondary mb-1">Support</h4>
              <div className="flex flex-wrap gap-2">
                {support_levels && support_levels.length > 0 ? (
                  support_levels.map((level, index) => {
                    const priceDiff = ((level - last_price) / last_price) * 100;
                    const isNearby = Math.abs(priceDiff) < 1;
                    return (
                      <div 
                        key={index}
                        className={`bg-dark-surface-2 border ${isNearby ? 'border-green-500' : 'border-green-500/20'} rounded p-2`}
                      >
                        <div className="text-green-400 font-medium">
                          {formatPrice(level)}
                        </div>
                        <div className="text-xs text-green-500">
                          {formatPercent(priceDiff)}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <span className="text-dark-text-secondary text-sm">No levels detected</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskRewardCard;