# Trading Indicator App

A full-stack application for technical analysis, generating trading signals, and calculating position sizing based on risk management principles.

## Features

- **Technical Analysis**: Calculate various technical indicators like Moving Averages, RSI, MACD, Bollinger Bands, etc.
- **Trading Signals**: Generate buy/sell signals with confidence scores
- **Position Sizing**: Calculate position size based on risk management
- **Support & Resistance**: Identify key price levels

## Architecture

This project consists of:

1. **Python Backend** (FastAPI)
   - Technical indicator calculations
   - Signal generation
   - Risk management / position sizing
   - Data fetching from financial APIs

2. **React Frontend**
   - User-friendly interface for analysis
   - Visualize signals and position sizing
   - Input controls for tickers and parameters

## Project Structure

```
trading-indicator-app/
├── backend/              # Python FastAPI backend
│   ├── main.py           # Entry point for API
│   ├── indicators.py     # Technical indicators
│   ├── strategy.py       # Signal logic
│   ├── capital_manager.py # Risk management
│   ├── requirements.txt  # Python dependencies
│   └── utils/
│       └── fetch_data.py # Data fetching logic
│
├── frontend/             # React frontend
│   ├── public/           # Static assets
│   ├── src/              # React source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── App.jsx       # Main application
│   │   └── api.js        # API service
│   └── package.json      # JavaScript dependencies
│
└── README.md             # Project documentation
```

## Setup & Installation

### Backend

1. Navigate to the backend directory:
   ```
   cd trading-indicator-app/backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   **Note**: This project uses `pandas-ta` instead of `TA-Lib` for technical indicators to avoid installation complexities. If you prefer to use TA-Lib, follow the installation instructions at [https://github.com/mrjbq7/ta-lib](https://github.com/mrjbq7/ta-lib) and uncomment the TA-Lib line in requirements.txt.

4. Run the backend:
   ```
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to the frontend directory:
   ```
   cd trading-indicator-app/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the frontend:
   ```
   npm start
   ```

## Usage

1. Launch both the backend and frontend servers
2. Enter a ticker symbol (e.g., AAPL, MSFT, TSLA)
3. Select timeframe and historical data period
4. Enter your available capital
5. Click "Analyze" to get trading signals and position sizing

## License

MIT License 