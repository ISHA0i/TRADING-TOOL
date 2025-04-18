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
    portfolio_risk
  } = capital_plan;
  
  // Format monetary values
  const formatMoney = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  // Format percentage
  const formatPercent = (value) => {
    return value.toFixed(2) + '%';
  };

  // Format units based on market type
  const formatUnits = (units) => {
    if (symbolType === 'forex') {
      return units.toFixed(2) + ' lots';
    } else if (symbolType === 'crypto') {
      return units.toFixed(8) + ' coins'; // Use 8 decimals for crypto
    }
    return units.toFixed(4) + ' units';
  };
  
  // Calculate percentage of total capital used in position
  const capitalUsedPercent = (position_size_usd / total_capital) * 100;

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
      // Add crypto-specific metrics
      const btcValue = ticker.startsWith('BTC-') ? position_size_units : 
                      (position_size_usd / (signals.bitcoin_price || 0));
      return {
        btcValue: btcValue.toFixed(8),
        dollarsPerCoin: (position_size_usd / position_size_units).toFixed(2)
      };
    }
    return null;
  };

  const marketMetrics = getMarketSpecificMetrics();
  
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
            
            {/* Capital Usage Bar */}
            <div className="pt-2">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-dark-text-secondary">Capital Allocation</span>
                <span className="text-xs text-dark-text-secondary font-semibold">
                  {formatPercent(capitalUsedPercent)}
                </span>
              </div>
              <div className="w-full bg-dark-surface rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${capitalUsedPercent > max_position_size_percent ? 'bg-dark-error' : 'bg-dark-primary'}`}
                  style={{ width: `${Math.min(100, capitalUsedPercent)}%` }}
                ></div>
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
              <span className={`font-semibold ${portfolio_risk > 2 ? 'text-red-500' : 'text-dark-text'}`}>
                {formatPercent(portfolio_risk)}
              </span>
            </div>
            
            <div className="pt-2 border-t border-dark-border">
              <h4 className="text-sm font-medium text-dark-text mb-2">Advanced Metrics</h4>
              
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-dark-text-secondary">Kelly Criterion</span>
                  <span className="font-medium text-dark-text">
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
                  <span className="font-medium text-dark-text">
                    {risk_reward_ratio.toFixed(2)}:1
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CapitalUsageCard;