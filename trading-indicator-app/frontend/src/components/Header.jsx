import React, { useState, useEffect } from 'react';
import { checkApiStatus } from '../api';

const Header = () => {
  const [apiName, setApiName] = useState('Trading Indicator API');
  const [apiConnected, setApiConnected] = useState(false);
  
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const status = await checkApiStatus();
        if (status && status.message) {
          setApiName(status.message.replace(' is running', ''));
        }
        setApiConnected(true);
      } catch (error) {
        setApiConnected(false);
      }
    };
    
    checkAPI();
  }, []);
  
  return (
    <header className="bg-dark-surface text-dark-text p-4 border-b border-dark-border flex justify-between items-center">
      <div className="font-bold text-xl">💹 {apiName}</div>
      <div className="text-sm">
        <span className={`inline-block w-2 h-2 rounded-full mr-2 ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
        {apiConnected ? 'API Connected' : 'API Disconnected'}
      </div>
    </header>
  );
};

export default Header;
  