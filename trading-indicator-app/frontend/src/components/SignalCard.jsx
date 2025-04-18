import React from 'react';

const SignalCard = ({ data }) => {
  const { ticker, last_price, signals } = data;
  const { signal, confidence, reasons } = signals;
  
  // Determine signal color based on signal type
  const getSignalColor = () => {
    switch(signal) {
      case 'STRONG_BUY':
        return 'bg-green-600';
      case 'BUY':
        return 'bg-green-400';
      case 'STRONG_SELL':
        return 'bg-red-600';
      case 'SELL':
        return 'bg-red-400';
      default:
        return 'bg-gray-400';
    }
  };
  
  // Calculate confidence percentage (0-100%)
  const confidencePercent = Math.round(confidence * 100);
  
  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-dark-text">{ticker}</h2>
        <div className="text-right">
          <span className="text-dark-text-secondary text-sm">Last Price</span>
          <p className="text-lg font-semibold text-dark-text">${last_price.toFixed(2)}</p>
        </div>
      </div>
      
      <div className="bg-dark-surface-2 rounded-lg p-4 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-dark-text">Signal</span>
          <span className={`px-3 py-1 rounded-full text-dark-text font-semibold ${getSignalColor()}`}>
            {signal.replace('_', ' ')}
          </span>
        </div>
        
        <div className="mt-4">
          <div className="flex justify-between mb-1">
            <span className="text-dark-text">Confidence</span>
            <span className="text-dark-text font-semibold">{confidencePercent}%</span>
          </div>
          <div className="w-full bg-dark-surface rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${getSignalColor()}`} 
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-2 text-dark-text">Signal Reasons</h3>
        <ul className="list-disc pl-5 space-y-1">
          {reasons.map((reason, index) => (
            <li key={index} className="text-dark-text-secondary text-sm">{reason}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SignalCard;