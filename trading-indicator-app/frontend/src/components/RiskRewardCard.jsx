import React from 'react';

const RiskRewardCard = ({ data }) => {
  const { ticker, last_price, signals } = data;
  const { signal, entry_price, stop_loss, take_profit, support_levels, resistance_levels } = signals;
  
  // Determine color theme based on signal direction
  const isBuySignal = signal.includes('BUY');
  const mainColor = isBuySignal ? 'green' : signal.includes('SELL') ? 'red' : 'gray';
  
  // Calculate risk/reward ratio
  const calculateRR = () => {
    if (!stop_loss || !take_profit) return 'N/A';
    
    const risk = Math.abs(entry_price - stop_loss);
    const reward = Math.abs(entry_price - take_profit);
    
    if (risk === 0) return 'N/A';
    return (reward / risk).toFixed(2) + ':1';
  };
  
  // Format price with 2 decimal places
  const formatPrice = (price) => {
    return price ? '$' + price.toFixed(2) : 'N/A';
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Risk / Reward</h2>
      
      <div className="space-y-6">
        {/* Entry, Stop Loss, Target */}
        <div className="bg-gray-100 rounded-lg p-4">
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-700">Entry</span>
              <span className="font-semibold">{formatPrice(entry_price)}</span>
            </div>
            
            {stop_loss && (
              <div className="flex justify-between">
                <span className="text-gray-700">Stop Loss</span>
                <span className={`font-semibold text-${mainColor}-600`}>
                  {formatPrice(stop_loss)}
                </span>
              </div>
            )}
            
            {take_profit && (
              <div className="flex justify-between">
                <span className="text-gray-700">Take Profit</span>
                <span className={`font-semibold text-${mainColor}-600`}>
                  {formatPrice(take_profit)}
                </span>
              </div>
            )}
            
            <div className="border-t pt-2 mt-2">
              <div className="flex justify-between">
                <span className="text-gray-700">Risk/Reward</span>
                <span className={`font-bold text-${mainColor}-600`}>
                  {calculateRR()}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Support & Resistance Levels */}
        <div>
          <h3 className="text-md font-semibold mb-2">Support Levels</h3>
          <div className="flex flex-wrap gap-2">
            {support_levels && support_levels.length > 0 ? (
              support_levels.map((level, index) => (
                <span 
                  key={index}
                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                >
                  ${level}
                </span>
              ))
            ) : (
              <span className="text-gray-500 text-sm">No levels detected</span>
            )}
          </div>
          
          <h3 className="text-md font-semibold mt-3 mb-2">Resistance Levels</h3>
          <div className="flex flex-wrap gap-2">
            {resistance_levels && resistance_levels.length > 0 ? (
              resistance_levels.map((level, index) => (
                <span 
                  key={index}
                  className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded"
                >
                  ${level}
                </span>
              ))
            ) : (
              <span className="text-gray-500 text-sm">No levels detected</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskRewardCard;