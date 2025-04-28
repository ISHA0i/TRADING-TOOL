# Trading Indicator API - Backend

The backend component of the Trading Indicator Application provides market data analysis, technical indicators, trading signals, and capital management calculations via a RESTful API. It's built with FastAPI and provides endpoints for stock, forex, crypto, and index market analysis.

## Features

- Technical indicator calculations for market data
- Trading signal generation with confidence levels and explanations
- Position sizing and capital management recommendations
- Market regime detection and volatility analysis
- Support for multiple timeframes and historical periods
- Data providers for various markets (stocks, forex, crypto, indices)

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **Pandas/Numpy**: Data manipulation and analysis
- **yfinance**: Yahoo Finance market data provider
- **pandas-ta/ta**: Technical analysis libraries for indicators
- **Uvicorn**: ASGI server for serving the FastAPI application

## File Structure

```
backend/
├── controller/              # Business logic (processing data, generating signals)
│   ├── indicators_controller.py
│   ├── strategy_controller.py
│   ├── capital_manager_controller.py
│   └── signal_validator_controller.py
│
├── models/                  # Pydantic models (request/response schemas)
│   ├── analyze_request.py
│   ├── analyze_response.py
│   └── common.py
│
├── routes/                  # API routes
│   ├── analyze_routes.py
│   ├── forex_routes.py
│   ├── stocks_routes.py
│   └── index_routes.py
│
├── utils/                   # Utility functions
│   ├── data_provider/
│   │   ├── yahoo_provider.py
│   │   └── __init__.py
│   └── market_regime.py
│
├── tests/                   # Unit and integration tests
│   ├── test_indicators.py
│   ├── test_strategy.py
│   └── test_api.py
│
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
└── uvicorn_patch.py         # Uvicorn compatibility patch (optional)
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/trading-indicator-app.git
   cd trading-indicator-app/backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Start the backend server:

```
python main.py
```

The API will be available at `http://localhost:8000`.

For development with auto-reload:

```
uvicorn main:app --reload
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

- `GET /api` - API status check
- `GET /api/analyze/{ticker}` - Analyze a ticker with default parameters
- `POST /api/analyze/{ticker}` - Analyze a ticker with custom parameters
- `GET /api/forex/pairs` - Get list of available forex pairs
- `GET /api/indices` - Get list of available market indices
- `GET /api/indian-stocks` - Get list of available Indian stocks
- `GET /api/us-stocks` - Get list of available US stocks

## Request Parameters

When analyzing a ticker, you can specify the following parameters:

- `ticker`: Stock/forex/crypto symbol to analyze
- `timeframe`: Time frame for analysis (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
- `period`: Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
- `capital`: Available capital for trading calculations

## Core Modules

- **indicators.py**: Calculates technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **strategy.py**: Generates trading signals based on indicator values
- **capital_manager.py**: Manages position sizing and risk calculations
- **signal_validator.py**: Validates signals against market regime and other factors

## Data Providers

The application supports multiple data sources:

- Yahoo Finance (default)
- (Other providers can be configured in app/utils/data_provider/)

## Development

### Adding New Indicators

To add new technical indicators, modify the `indicators.py` file and implement your calculation function.

### Creating New Strategies

To create new trading strategies, extend the strategy module in `strategy.py`.

### Adding Data Providers

To add support for new data sources, create a new provider in the `app/utils/data_provider/providers/` directory.

## Testing

Run the tests with:

```
pytest
```

## License

[Include your license information here] 