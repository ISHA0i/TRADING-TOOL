import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/analyze/BTC-USD');
        setData(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-bg text-dark-text flex items-center justify-center">
        <div className="animate-pulse-slow text-2xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-dark-bg text-dark-text flex items-center justify-center">
        <div className="text-dark-error text-xl">Error: {error}</div>
      </div>
    );
  }

  const chartData = {
    labels: data?.historical_data?.map(d => new Date(d.date).toLocaleTimeString()),
    datasets: [
      {
        label: 'Price',
        data: data?.historical_data?.map(d => d.Close),
        borderColor: '#BB86FC',
        backgroundColor: 'rgba(187, 134, 252, 0.1)',
        tension: 0.4,
      },
      {
        label: 'SMA 20',
        data: data?.historical_data?.map(d => d.SMA_20),
        borderColor: '#03DAC6',
        backgroundColor: 'rgba(3, 218, 198, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#FFFFFF',
        },
      },
    },
    scales: {
      y: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#B0B0B0',
        },
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#B0B0B0',
        },
      },
    },
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-dark-bg text-dark-text' : 'bg-white text-gray-900'}`}>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-dark-primary">Trading Indicator App</h1>
          <button
            onClick={toggleDarkMode}
            className="px-4 py-2 rounded-lg bg-dark-surface text-dark-text hover:bg-opacity-80 transition-colors"
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Price Chart */}
          <div className="bg-dark-surface p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-dark-primary">Price Chart</h2>
            <div className="h-96">
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>

          {/* Trading Signals */}
          <div className="bg-dark-surface p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-dark-primary">Trading Signals</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 rounded-lg bg-opacity-20 bg-dark-primary">
                <span className="text-dark-text">Signal</span>
                <span className={`font-bold ${data.signal === 'BUY' ? 'text-green-500' : data.signal === 'SELL' ? 'text-red-500' : 'text-yellow-500'}`}>
                  {data.signal}
                </span>
              </div>
              <div className="flex justify-between items-center p-4 rounded-lg bg-opacity-20 bg-dark-secondary">
                <span className="text-dark-text">Confidence</span>
                <span className="font-bold text-dark-secondary">{data.confidence}%</span>
              </div>
              <div className="flex justify-between items-center p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text">Entry Price</span>
                <span className="font-bold text-dark-text">${data.entry_price}</span>
              </div>
              <div className="flex justify-between items-center p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text">Stop Loss</span>
                <span className="font-bold text-dark-text">${data.stop_loss}</span>
              </div>
              <div className="flex justify-between items-center p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text">Take Profit</span>
                <span className="font-bold text-dark-text">${data.take_profit}</span>
              </div>
            </div>
          </div>

          {/* Technical Indicators */}
          <div className="bg-dark-surface p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-dark-primary">Technical Indicators</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text-secondary">RSI</span>
                <div className="text-2xl font-bold text-dark-text">{data.indicators.RSI.toFixed(2)}</div>
              </div>
              <div className="p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text-secondary">MACD</span>
                <div className="text-2xl font-bold text-dark-text">{data.indicators.MACD.toFixed(2)}</div>
              </div>
              <div className="p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text-secondary">SMA 20</span>
                <div className="text-2xl font-bold text-dark-text">${data.indicators.SMA_20.toFixed(2)}</div>
              </div>
              <div className="p-4 rounded-lg bg-opacity-20 bg-dark-surface">
                <span className="text-dark-text-secondary">Volume</span>
                <div className="text-2xl font-bold text-dark-text">{data.indicators.Volume.toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Support & Resistance */}
          <div className="bg-dark-surface p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4 text-dark-primary">Support & Resistance</h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-dark-text-secondary mb-2">Support Levels</h3>
                <div className="flex flex-wrap gap-2">
                  {data.support_levels.map((level, index) => (
                    <span key={index} className="px-3 py-1 rounded-full bg-opacity-20 bg-green-500 text-green-500">
                      ${level}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-dark-text-secondary mb-2">Resistance Levels</h3>
                <div className="flex flex-wrap gap-2">
                  {data.resistance_levels.map((level, index) => (
                    <span key={index} className="px-3 py-1 rounded-full bg-opacity-20 bg-red-500 text-red-500">
                      ${level}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 