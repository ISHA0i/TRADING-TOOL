import React from 'react';

const SignalCard = ({ data, symbolType = 'stock' }) => {
  if (!data || !data.signals) {
    return (
      <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-dark-primary border-b border-dark-border pb-2">
          Signal Analysis
        </h3>
        <div className="text-center py-8 text-dark-text-secondary">
          No signal data available
        </div>
      </div>
    );
  }

  const { ticker, timeframe, period, last_price, last_updated, signals } = data;
  
  // Check if signals object is valid
  const hasSignals = signals && 
    typeof signals === 'object' && 
    !signals.error && 
    Object.keys(signals).length > 0;
  
  // Format date string
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };
  
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
  
  // Get color based on signal strength
  const getSignalColor = (value) => {
    if (typeof value !== 'number') return 'text-dark-text';
    if (value >= 0.7) return 'text-green-500';
    if (value >= 0.4) return 'text-yellow-500';
    if (value >= 0) return 'text-dark-text-secondary';
    if (value >= -0.4) return 'text-dark-text-secondary';
    if (value >= -0.7) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  // Get final signal text
  const getSignalText = (signal) => {
    if (typeof signal !== 'number') return 'NEUTRAL';
    if (signal > 0.7) return 'STRONG BUY';
    if (signal > 0.3) return 'BUY';
    if (signal > -0.3) return 'NEUTRAL';
    if (signal > -0.7) return 'SELL';
    return 'STRONG SELL';
  };
  
  // Get color for final signal
  const getFinalSignalColor = (signal) => {
    if (typeof signal !== 'number') return 'text-dark-text-secondary';
    if (signal > 0.7) return 'text-green-500';
    if (signal > 0.3) return 'text-green-400';
    if (signal > -0.3) return 'text-dark-text-secondary';
    if (signal > -0.7) return 'text-red-400';
    return 'text-red-500';
  };
  
  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4 text-dark-primary border-b border-dark-border pb-2">
        Signal Analysis
      </h3>
      
      <div className="mb-4">
        <div className="flex justify-between items-baseline">
          <div>
            <h4 className="text-xl font-bold text-dark-text">{ticker}</h4>
            <p className="text-sm text-dark-text-secondary">
              {timeframe} {period}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold text-dark-text">${formatPrice(last_price)}</p>
            <p className="text-xs text-dark-text-secondary">Last updated: {formatDate(last_updated)}</p>
          </div>
        </div>
      </div>
      
      {hasSignals ? (
        <>
          <div className="mb-6 flex items-center justify-center bg-dark-surface-2 rounded-lg p-4">
            <div className="text-center">
              <p className="text-sm text-dark-text-secondary mb-1">Signal</p>
              <p className={`text-3xl font-bold ${getFinalSignalColor(signals.final_signal)}`}>
                {getSignalText(signals.final_signal)}
              </p>
              <p className="text-xs text-dark-text-secondary mt-1">
                Confidence: {typeof signals.signal_strength === 'number' ? `${(signals.signal_strength * 100).toFixed(0)}%` : 'N/A'}
              </p>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-dark-text-secondary mb-2">Signal Components</h4>
            
            <div className="space-y-3">
              {Object.entries(signals)
                .filter(([key]) => !['final_signal', 'signal_strength'].includes(key))
                .map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-sm text-dark-text">
                      {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                    </span>
                    <div className="flex items-center">
                      <div className="w-16 h-2 bg-dark-surface-2 rounded-full mr-2 overflow-hidden">
                        <div
                          className={`h-full ${value > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                          style={{
                            width: `${Math.abs(value) * 100}%`,
                            marginLeft: value > 0 ? '50%' : `${(1 - Math.abs(value)) * 50}%`
                          }}
                        ></div>
                      </div>
                      <span className={`text-sm font-medium ${getSignalColor(value)}`}>
                        {typeof value === 'number' ? value.toFixed(2) : 'N/A'}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </>
      ) : (
        <div className="p-3 bg-dark-surface-2 border border-dark-border rounded-md text-dark-text-secondary">
          <p className="font-medium">Signal data not available</p>
          <p className="text-sm mt-1">
            This may be due to insufficient market data or calculation issues.
          </p>
        </div>
      )}
    </div>
  );
};

export default SignalCard;