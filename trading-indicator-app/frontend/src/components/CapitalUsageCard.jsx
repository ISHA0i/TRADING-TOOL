import React from 'react';

const CapitalUsageCard = ({ data, symbolType }) => {
  // Check if we have valid capital efficiency data
  const hasCapitalEfficiency = data && 
    data.capital_efficiency && 
    typeof data.capital_efficiency === 'object' && 
    !data.capital_efficiency.error;
  
  // Get position data safely
  const position = data?.position || {};
  // Get capital efficiency data safely
  const capEfficiency = hasCapitalEfficiency ? data.capital_efficiency : null;
  
  // Get basic data from response
  const { ticker, last_price } = data || {};
  
  // Format monetary values with K/M/B suffixes
  const formatMoney = (value) => {
    if (!value && value !== 0) return 'N/A';
    
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
    if (value === undefined || value === null) return 'N/A';
    
    const color = value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-dark-text';
    return (
      <span className={color}>
        {value.toFixed(2)}%
      </span>
    );
  };

  // Format units based on market type with improved precision
  const formatUnits = (units) => {
    if (!units && units !== 0) return 'N/A';
    
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

  // Get market-specific metrics
  const getMarketSpecificMetrics = () => {
    if (!position.position_size_units) return null;
    
    if (symbolType === 'forex') {
      const isJPYPair = ticker?.includes('JPY');
      const standardLotSize = 100000;
      const lotValue = position.position_size_units / standardLotSize;
      const pipValue = isJPYPair ? 0.01 : 0.0001;
      const pipMoneyValue = (lotValue * standardLotSize * pipValue);
      
      return {
        lotSize: lotValue.toFixed(2),
        pipValue: formatMoney(pipMoneyValue)
      };
    } else if (symbolType === 'crypto') {
      const btcValue = position.position_size_dollars / last_price;
      return {
        btcValue: btcValue.toFixed(8),
        dollarsPerCoin: last_price ? last_price.toFixed(2) : 'N/A'
      };
    }
    return null;
  };

  const marketMetrics = getMarketSpecificMetrics();
  
  // Calculate percentage of total capital used in position
  const totalCapital = position.total_capital || 0;
  const positionSizeDollars = position.position_size_dollars || 0;
  const capitalUsedPercent = totalCapital > 0 ? (positionSizeDollars / totalCapital) * 100 : 0;
  
  // Get position size percent
  const positionSizePercent = position.risk_percent || 
    (totalCapital > 0 ? positionSizeDollars / totalCapital : 0);

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
                {(positionSizePercent * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-dark-text-secondary">
                ${positionSizeDollars.toFixed(2)}
              </p>
            </div>
            
            <div>
              <p className="text-sm text-dark-text-secondary mb-1">Units</p>
              <p className="text-2xl font-bold text-dark-text">
                {formatUnits(position.position_size_units)}
              </p>
              <p className="text-xs text-dark-text-secondary">
                {symbolType === 'forex' ? 'Currency Units' : symbolType === 'crypto' ? 'Coins' : 'Shares'}
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
                  <span className="text-xs text-dark-text-secondary">Current: {(positionSizePercent * 100).toFixed(1)}%</span>
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