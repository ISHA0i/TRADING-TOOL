import React from 'react';
import Home from './pages/Home';
import Header from './components/Header';

function App() {
  return (
    <div className="min-h-screen bg-dark-bg text-dark-text">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <Home />
      </div>
    </div>
  );
}

export default App;