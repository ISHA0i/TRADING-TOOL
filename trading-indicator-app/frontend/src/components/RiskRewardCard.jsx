import React from 'react';

const RiskRewardCard = ({ data, symbolType }) => {
  if (!data || !data.position || !data.signals) {
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-dark-primary border-b border-dark-border pb-2">
          Risk/Reward Analysis
        </h3>
        <div className="text-center py-8 text-dark-text-secondary">
          No risk/reward data available
        </div>
      </div>
    );
  }

  const { ticker, last_price } = data;
  const { position_size_value = 0, risk_amount = 0, reward_amount = 0 } = data.position;
  
  // Calculate risk-reward ratio
  const riskRewardRatio = risk_amount && reward_amount 
    ? (reward_amount / risk_amount).toFixed(2) 
    : 'N/A';
  
  // Get color based on risk-reward ratio
  const getRatioColor = (ratio) => {
    if (ratio === 'N/A') return 'text-dark-text-secondary';
    const numRatio = parseFloat(ratio);
    if (numRatio >= 3) return 'text-green-500';
    if (numRatio >= 2) return 'text-green-400';
    if (numRatio >= 1) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  // Calculate percentage of investment
  const riskPercent = position_size_value ? (risk_amount / position_size_value) * 100 : 0;
  const rewardPercent = position_size_value ? (reward_amount / position_size_value) * 100 : 0;
  
  // Format price according to symbol type (yfinance convention)
  const formatPrice = (price) => {
    if (price === undefined || price === null) return 'N/A';
    
    if (symbolType === 'crypto') {
      // For cryptocurrencies, format with more decimal places for small values
      if (price < 1) return price.toFixed(6);
      if (price < 10) return price.toFixed(4);
      return price.toFixed(2);
    } else if (symbolType === 'forex') {
      // For forex, typically 4 decimal places (or 2 for JPY pairs)
      const isJPYPair = ticker && (ticker.includes('JPY') || ticker.includes('USDJPY'));
      return isJPYPair ? price.toFixed(2) : price.toFixed(4);
    }
    
    // Default format for stocks and indices
    return price.toFixed(2);
  };
  
  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-dark-primary border-b border-dark-border pb-2">
        Risk/Reward Analysis
      </h3>
      
      <div className="mb-6 text-center">
        <p className="text-sm text-dark-text-secondary mb-1">Risk/Reward Ratio</p>
        <p className={`text-3xl font-bold ${getRatioColor(riskRewardRatio)}`}>
          {riskRewardRatio}:1
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-5 mb-5">
        <div>
          <p className="text-sm text-dark-text-secondary mb-1">Potential Loss</p>
          <p className="text-xl font-bold text-red-500">
            ${formatPrice(risk_amount)}
          </p>
          <p className="text-xs text-dark-text-secondary">
            {riskPercent.toFixed(1)}% of position
          </p>
        </div>
        
        <div>
          <p className="text-sm text-dark-text-secondary mb-1">Potential Gain</p>
          <p className="text-xl font-bold text-green-500">
            ${formatPrice(reward_amount)}
          </p>
          <p className="text-xs text-dark-text-secondary">
            {rewardPercent.toFixed(1)}% of position
          </p>
        </div>
      </div>
      
      <div className="relative pt-1">
        <div className="flex justify-between mb-1 text-xs text-dark-text-secondary">
          <span>Risk</span>
          <span>Current</span>
          <span>Target</span>
        </div>
        <div className="h-2 bg-dark-surface-2 rounded-full">
          <div className="absolute top-0 h-6 w-0.5 bg-dark-border" style={{ left: '50%', marginTop: '18px' }}></div>
          {data.position.stop_price && (
            <div 
              className="absolute top-0 h-6 w-0.5 bg-red-500" 
              style={{ 
                left: `${25}%`, 
                marginTop: '18px'
              }}
            ></div>
          )}
          {data.position.target_price && (
            <div 
              className="absolute top-0 h-6 w-0.5 bg-green-500" 
              style={{ 
                left: `${75}%`, 
                marginTop: '18px'
              }}
            ></div>
          )}
        </div>
        <div className="flex justify-between mt-1 text-xs">
          <span className="text-red-500">
            ${formatPrice(data.position.stop_price)}
          </span>
          <span className="text-dark-text">
            ${formatPrice(last_price)}
          </span>
          <span className="text-green-500">
            ${formatPrice(data.position.target_price)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RiskRewardCard;