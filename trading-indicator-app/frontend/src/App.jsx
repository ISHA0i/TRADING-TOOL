import React from 'react';
import Home from './pages/Home';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Trading Indicator App</h1>
          <p className="text-blue-200">
            Technical Analysis & Position Sizing Calculator
          </p>
        </div>
      </header>
      
      <Home />
      
      <footer className="bg-gray-100 mt-12 py-6 border-t border-gray-200">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>Trading Indicator App &copy; {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
}

export default App; 