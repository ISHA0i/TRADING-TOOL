import React from 'react';

const CapitalUsageCard = ({ data, symbolType }) => {
  const { ticker, last_price, capital_plan, signals } = data;
  const { 
    total_capital, 
    risk_percent,
    max_position_size_percent, 
    position_size_usd,
    position_size_units,
    stop_loss_usd,
    potential_profit_usd,
    risk_reward_ratio,
    kelly_criterion,
    volatility_adjusted_size,
    portfolio_risk,
    market_conditions,
    regime_adjustments
  } = capital_plan;
  
  // Format monetary values with K/M/B suffixes
  const formatMoney = (value) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  // Format percentage with dynamic coloring
  const formatPercent = (value) => {
    const color = value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-dark-text';
    return (
      <span className={color}>
        {value.toFixed(2)}%
      </span>
    );
  };

  // Format units based on market type with improved precision
  const formatUnits = (units) => {
    if (symbolType === 'forex') {
      const lots = units / 100000; // Standard lot size
      if (lots >= 1) {
        return `${lots.toFixed(2)} lots`;
      } else {
        return `${(lots * 100).toFixed(1)} mini lots`;
      }
    } else if (symbolType === 'crypto') {
      if (units < 0.00000001) {
        return '< 0.00000001 coins';
      }
      return `${units.toFixed(8)} coins`;
    }
    return `${units.toFixed(4)} units`;
  };

  // Calculate market-specific metrics
  const getMarketSpecificMetrics = () => {
    if (symbolType === 'forex') {
      const isJPYPair = ticker.includes('JPY');
      const standardLotSize = 100000;
      const lotValue = position_size_units / standardLotSize;
      const pipValue = isJPYPair ? 0.01 : 0.0001;
      const pipMoneyValue = (lotValue * standardLotSize * pipValue);
      
      return {
        lotSize: lotValue.toFixed(2),
        pipValue: formatMoney(pipMoneyValue)
      };
    } else if (symbolType === 'crypto') {
      const btcValue = ticker.startsWith('BTC-') ? position_size_units : 
                      (position_size_usd / (signals.bitcoin_price || 0));
      return {
        btcValue: btcValue.toFixed(8),
        dollarsPerCoin: (position_size_usd / position_size_units || 0).toFixed(2)
      };
    }
    return null;
  };

  const marketMetrics = getMarketSpecificMetrics();
  
  // Calculate percentage of total capital used in position
  const capitalUsedPercent = (position_size_usd / total_capital) * 100;
  
  // Get risk level color
  const getRiskColor = (risk) => {
    if (risk > 3) return 'text-red-500';
    if (risk > 2) return 'text-yellow-400';
    return 'text-dark-text';
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold mb-4 text-dark-text">Capital Management</h2>
      
      <div className="space-y-6">
        {/* Position Size */}
        <div className="bg-dark-surface-2 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Total Capital</span>
              <span className="font-semibold text-dark-text">{formatMoney(total_capital)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Position Size</span>
              <div className="text-right">
                <div className="font-semibold text-dark-text">{formatMoney(position_size_usd)}</div>
                <div className="text-sm text-dark-text-secondary">{formatUnits(position_size_units)}</div>
              </div>
            </div>
            
            {marketMetrics && (
              <div className="flex justify-between">
                <span className="text-dark-text-secondary">
                  {symbolType === 'forex' ? 'Lot Size' : symbolType === 'crypto' ? 'BTC Value' : ''}
                </span>
                <div className="text-right">
                  <div className="font-semibold text-dark-text">
                    {symbolType === 'forex' ? (
                      `${marketMetrics.lotSize} lots`
                    ) : symbolType === 'crypto' ? (
                      `${marketMetrics.btcValue} BTC`
                    ) : null}
                  </div>
                  <div className="text-sm text-dark-text-secondary">
                    {symbolType === 'forex' ? (
                      `Per pip: ${marketMetrics.pipValue}`
                    ) : symbolType === 'crypto' ? (
                      `$${marketMetrics.dollarsPerCoin} per coin`
                    ) : null}
                  </div>
                </div>
              </div>
            )}
            
            {/* Capital Usage Bar with regime-based adjustments */}
            <div className="pt-2">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-dark-text-secondary">Capital Allocation</span>
                <span className="text-xs text-dark-text-secondary font-semibold">
                  {formatPercent(capitalUsedPercent)}
                  {regime_adjustments?.size_adjustment && (
                    <span className="ml-1 text-xs">
                      ({regime_adjustments.size_adjustment > 0 ? '+' : ''}
                      {regime_adjustments.size_adjustment}% regime adj.)
                    </span>
                  )}
                </span>
              </div>
              <div className="w-full bg-dark-surface rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${capitalUsedPercent > max_position_size_percent ? 'bg-dark-error' : 'bg-dark-primary'}`}
                  style={{ width: `${Math.min(100, capitalUsedPercent)}%` }}
                />
              </div>
              <div className="text-xs text-dark-text-secondary mt-1">
                Max allowed: {formatPercent(max_position_size_percent)}
              </div>
            </div>
          </div>
        </div>
        
        {/* Risk Parameters */}
        <div>
          <h3 className="text-md font-semibold mb-3 text-dark-text">Risk Analysis</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Risk Amount</span>
              <div className="text-right">
                <div className="font-semibold text-red-500">{formatMoney(stop_loss_usd)}</div>
                <div className="text-sm text-dark-text-secondary">{formatPercent(risk_percent)} of capital</div>
              </div>
            </div>
            
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Potential Profit</span>
              <div className="text-right">
                <div className="font-semibold text-green-500">{formatMoney(potential_profit_usd)}</div>
                <div className="text-sm text-dark-text-secondary">
                  {formatPercent((potential_profit_usd / total_capital) * 100)} of capital
                </div>
              </div>
            </div>
            
            <div className="flex justify-between">
              <span className="text-dark-text-secondary">Portfolio Risk</span>
              <span className={`font-semibold ${getRiskColor(portfolio_risk)}`}>
                {formatPercent(portfolio_risk)}
              </span>
            </div>
            
            <div className="pt-2 border-t border-dark-border">
              <h4 className="text-sm font-medium text-dark-text mb-2">Advanced Metrics</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-dark-text-secondary">Kelly Criterion</span>
                  <span className={`font-medium ${kelly_criterion > 0.5 ? 'text-green-400' : 'text-dark-text'}`}>
                    {(kelly_criterion * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-dark-text-secondary">Volatility Adjusted Size</span>
                  <span className="font-medium text-dark-text">
                    {formatPercent(volatility_adjusted_size)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-dark-text-secondary">Risk/Reward Ratio</span>
                  <span className={`font-medium ${risk_reward_ratio >= 1.5 ? 'text-green-400' : 'text-yellow-400'}`}>
                    {risk_reward_ratio.toFixed(2)}:1
                  </span>
                </div>
              </div>
            </div>

            {/* Market Condition Adjustments */}
            {market_conditions && Object.keys(market_conditions).length > 0 && (
              <div className="pt-2 border-t border-dark-border">
                <h4 className="text-sm font-medium text-dark-text mb-2">Market Conditions</h4>
                <div className="space-y-2 text-sm">
                  {Object.entries(market_conditions).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-dark-text-secondary">
                        {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </span>
                      <span className="font-medium text-dark-text">
                        {typeof value === 'number' ? formatPercent(value * 100) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CapitalUsageCard;