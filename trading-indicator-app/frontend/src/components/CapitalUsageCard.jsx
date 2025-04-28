import React from 'react';

const CapitalUsageCard = ({ data, symbolType }) => {
  const hasCapitalEfficiency = data && 
    data.capital_efficiency && 
    typeof data.capital_efficiency === 'object' && 
    !data.capital_efficiency.error;
  
  const position = data?.position || {};
  const capEfficiency = hasCapitalEfficiency ? data.capital_efficiency : null;
  
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
      <h3 className="text-lg font-semibold mb-4 text-dark-primary border-b border-dark-border pb-2">
        Capital Management
      </h3>
      
      {data ? (
        <>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <p className="text-sm text-dark-text-secondary mb-1">Position Size</p>
              <p className="text-2xl font-bold text-dark-text">
                {position.position_size_percent ? `${(position.position_size_percent * 100).toFixed(1)}%` : 'N/A'}
              </p>
              <p className="text-xs text-dark-text-secondary">
                ${position.position_size_value?.toFixed(2) || 'N/A'}
              </p>
            </div>
            
            <div>
              <p className="text-sm text-dark-text-secondary mb-1">Units</p>
              <p className="text-2xl font-bold text-dark-text">
                {position.position_size_units?.toFixed(symbolType === 'forex' ? 0 : 2) || 'N/A'}
              </p>
              <p className="text-xs text-dark-text-secondary">
                {symbolType === 'forex' ? 'Currency Units' : 'Shares'}
              </p>
            </div>
          </div>
          
          {hasCapitalEfficiency ? (
            <>
              <hr className="border-dark-border my-4" />
              
              <div className="mb-4">
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-dark-text-secondary">Optimal Position</span>
                  <span className="text-sm font-medium">
                    {(capEfficiency.optimal_position_percent * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-dark-surface-2 rounded-full h-2">
                  <div 
                    className="bg-dark-primary h-2 rounded-full" 
                    style={{ width: `${Math.min(capEfficiency.position_vs_optimal * 100, 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-dark-text-secondary">Current: {(position.position_size_percent * 100).toFixed(1)}%</span>
                  <span className="text-xs text-dark-text-secondary">
                    {capEfficiency.position_vs_optimal > 1 ? 'Overallocated' : 'Underallocated'}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-sm text-dark-text-secondary mb-1">Win Rate (est.)</p>
                  <p className="text-lg font-semibold text-dark-text">
                    {(capEfficiency.estimated_win_rate * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-dark-text-secondary mb-1">Kelly Criterion</p>
                  <p className="text-lg font-semibold text-dark-text">
                    {(capEfficiency.kelly_criterion * 100).toFixed(1)}%
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-dark-text-secondary mb-1">Expected Value</p>
                  <p className="text-lg font-semibold text-dark-text">
                    {capEfficiency.expected_value > 0 ? '+' : ''}{capEfficiency.expected_value.toFixed(2)}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-dark-text-secondary mb-1">Capital Usage</p>
                  <p className="text-lg font-semibold text-dark-text">
                    {(capEfficiency.capital_usage_percent * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
            </>
          ) : (
            <>
              <hr className="border-dark-border my-4" />
              <div className="p-3 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text-secondary">
                <p className="font-medium">Capital efficiency data not available</p>
                <p className="text-sm mt-1">
                  This may be due to insufficient historical data or calculation constraints.
                </p>
              </div>
            </>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-dark-text-secondary">
          Loading capital data...
        </div>
      )}
    </div>
  );
};

export default CapitalUsageCard;