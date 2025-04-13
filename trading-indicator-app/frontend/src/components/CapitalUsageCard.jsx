import React from 'react';

const CapitalUsageCard = ({ data }) => {
  const { ticker, last_price, capital_plan } = data;
  const { 
    total_capital, 
    risk_percent,
    max_position_size_percent, 
    position_size_usd,
    position_size_units,
    stop_loss_usd,
    potential_profit_usd,
    risk_reward_ratio
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
  
  // Calculate percentage of total capital used in position
  const capitalUsedPercent = (position_size_usd / total_capital) * 100;
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Capital Management</h2>
      
      <div className="space-y-6">
        {/* Position Size */}
        <div className="bg-gray-100 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-700">Total Capital</span>
              <span className="font-semibold">{formatMoney(total_capital)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-700">Position Size</span>
              <span className="font-semibold">{formatMoney(position_size_usd)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-700">Units to Trade</span>
              <span className="font-semibold">{position_size_units.toFixed(4)}</span>
            </div>
            
            {/* Capital Usage Bar */}
            <div className="pt-2">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-gray-600">Capital Used</span>
                <span className="text-xs text-gray-600 font-semibold">
                  {formatPercent(capitalUsedPercent)}
                </span>
              </div>
              <div className="w-full bg-gray-300 rounded-full h-2">
                <div 
                  className="h-2 rounded-full bg-blue-500" 
                  style={{ width: `${Math.min(100, capitalUsedPercent)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Risk Parameters */}
        <div>
          <h3 className="text-md font-semibold mb-3">Risk Analysis</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-700">Risk Amount</span>
              <span className="font-semibold text-red-600">{formatMoney(stop_loss_usd)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-700">Risk Percent</span>
              <span className="font-semibold text-red-600">{formatPercent(risk_percent)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-700">Potential Profit</span>
              <span className="font-semibold text-green-600">{formatMoney(potential_profit_usd)}</span>
            </div>
            
            <div className="flex justify-between border-t pt-2">
              <span className="text-gray-700">Risk/Reward Ratio</span>
              <span className="font-bold">
                {risk_reward_ratio > 0 ? risk_reward_ratio.toFixed(2) + ':1' : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CapitalUsageCard; 