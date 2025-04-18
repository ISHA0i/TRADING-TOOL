import React from 'react';

const RiskRewardCard = ({ data, symbolType }) => {
  const { ticker, last_price, signals } = data;
  const { signal, entry_price, stop_loss, take_profit, support_levels, resistance_levels } = signals;
  
  // Determine color theme based on signal direction
  const isBuySignal = signal.includes('BUY');
  const mainColor = isBuySignal ? 'green' : signal.includes('SELL') ? 'red' : 'gray';
  
  // Calculate risk/reward metrics
  const calculateMetrics = () => {
    if (!stop_loss || !take_profit || !entry_price) return {};
    
    const risk = Math.abs(entry_price - stop_loss);
    const reward = Math.abs(entry_price - take_profit);
    const rr_ratio = risk === 0 ? 0 : reward / risk;
    
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
      
      pipValue = Math.pow(10, -4); // Standard pip value (0.0001)
      if (isJPYPair) pipValue = 0.01; // JPY pairs have different pip value
      
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
  
  // Update formatPrice function to handle crypto
  const formatPrice = (price) => {
    if (!price) return 'N/A';
    
    if (symbolType === 'crypto') {
      // Format crypto prices with more decimals for low-value coins
      return price < 1 ? price.toFixed(6) : price.toFixed(2);
    } else if (symbolType === 'forex') {
      const isJPYPair = ticker.includes('JPY');
      return isJPYPair ? price.toFixed(3) : price.toFixed(5);
    }
    return price.toFixed(2);
  };
  
  // Format percentage
  const formatPercent = (value) => {
    if (!value) return 'N/A';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
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
              <span className="font-semibold text-dark-text">{formatPrice(last_price)}</span>
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
                <span className="font-bold text-dark-primary">
                  {metrics.rr_ratio ? `${metrics.rr_ratio.toFixed(2)}:1` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
        
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
                    return (
                      <div 
                        key={index}
                        className="bg-dark-surface-2 border border-red-500/20 rounded p-2"
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
                    return (
                      <div 
                        key={index}
                        className="bg-dark-surface-2 border border-green-500/20 rounded p-2"
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