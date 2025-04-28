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
    signals.signal && 
    signals.confidence;
  
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
    if (value === undefined || value === null || typeof value !== 'number') return 'text-dark-text';
    if (value >= 0.7) return 'text-green-500';
    if (value >= 0.4) return 'text-green-400';
    if (value >= 0) return 'text-dark-text-secondary';
    if (value >= -0.4) return 'text-dark-text-secondary';
    if (value >= -0.7) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  // Get signal type color
  const getSignalTypeColor = (signalType) => {
    if (!signalType) return 'text-dark-text-secondary';
    
    if (signalType.includes('BUY') || signalType === 'STRONG_BUY') {
      return signalType.includes('STRONG') ? 'text-green-500' : 'text-green-400';
    } else if (signalType.includes('SELL') || signalType === 'STRONG_SELL') {
      return signalType.includes('STRONG') ? 'text-red-500' : 'text-red-400';
    }
    return 'text-dark-text-secondary';
  };
  
  // Format signal type for display
  const formatSignalType = (signalType) => {
    if (!signalType) return 'NEUTRAL';
    return signalType.replace('_', ' ');
  };
  
  // Get signal metrics for display
  const getSignalMetrics = () => {
    if (!signals.signal_metrics) return [];
    
    return Object.entries(signals.signal_metrics)
      .filter(([key, value]) => typeof value === 'number')
      .map(([key, value]) => ({
        name: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
        value: value,
        key: key
      }));
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
              <p className={`text-3xl font-bold ${getSignalTypeColor(signals.signal)}`}>
                {formatSignalType(signals.signal)}
              </p>
              <p className="text-xs text-dark-text-secondary mt-1">
                Confidence: {typeof signals.confidence === 'number' ? `${(signals.confidence * 100).toFixed(0)}%` : 'N/A'}
              </p>
            </div>
          </div>
          
          {signals.reasons && signals.reasons.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-medium text-dark-text-secondary mb-2">Reasons</h4>
              <ul className="text-sm text-dark-text space-y-2 list-disc pl-5">
                {signals.reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
          
          <div>
            <h4 className="text-sm font-medium text-dark-text-secondary mb-2">Signal Components</h4>
            
            <div className="space-y-3">
              {getSignalMetrics().map((metric) => (
                <div key={metric.key} className="flex justify-between items-center">
                  <span className="text-sm text-dark-text">
                    {metric.name}
                  </span>
                  <div className="flex items-center">
                    <div className="w-16 h-2 bg-dark-surface-2 rounded-full mr-2 overflow-hidden">
                      <div
                        className={`h-full ${metric.value > 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{
                          width: `${Math.min(Math.abs(metric.value), 1) * 100}%`,
                          marginLeft: metric.value > 0 ? '50%' : `${(1 - Math.min(Math.abs(metric.value), 1)) * 50}%`
                        }}
                      ></div>
                    </div>
                    <span className={`text-sm font-medium ${getSignalColor(metric.value)}`}>
                      {metric.value.toFixed(2)}
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