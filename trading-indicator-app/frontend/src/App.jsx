import React from 'react';
import Home from './pages/Home';

function App() {
  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-dark-primary">Trading Indicator App</h1>
        </div>
        
        <Home />
      </div>
    </div>
  );
}

export default App;