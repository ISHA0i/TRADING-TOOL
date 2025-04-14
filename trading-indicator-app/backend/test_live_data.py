import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
from indicators import calculate_indicators
from strategy import generate_signals

def fetch_live_data(symbol="BTC-USD", interval="1h", period="7d"):
    """
    Fetch live cryptocurrency data from Yahoo Finance
    """
    try:
        # Fetch data
        data = yf.download(symbol, period=period, interval=interval)
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Rename columns to match our expected format
        data = data.rename(columns={
            'Date': 'date',
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Volume': 'Volume'
        })
        
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def plot_indicators(data, signals):
    """
    Create interactive visualization of indicators and signals
    """
    # Create subplots
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=data['date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ))
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['SMA_20'],
        name='SMA 20',
        line=dict(color='blue', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['SMA_50'],
        name='SMA 50',
        line=dict(color='orange', width=1)
    ))
    
    # Add Bollinger Bands
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['BB_upper'],
        name='BB Upper',
        line=dict(color='gray', width=1, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['BB_lower'],
        name='BB Lower',
        line=dict(color='gray', width=1, dash='dash')
    ))
    
    # Add RSI
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['RSI'],
        name='RSI',
        line=dict(color='purple', width=1),
        yaxis='y2'
    ))
    
    # Add MACD
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['MACD'],
        name='MACD',
        line=dict(color='green', width=1),
        yaxis='y3'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['MACD_signal'],
        name='MACD Signal',
        line=dict(color='red', width=1),
        yaxis='y3'
    ))
    
    # Add volume
    fig.add_trace(go.Bar(
        x=data['date'],
        y=data['Volume'],
        name='Volume',
        marker_color='rgba(0,0,255,0.3)',
        yaxis='y4'
    ))
    
    # Update layout
    fig.update_layout(
        title='BTC-USD Technical Analysis',
        yaxis=dict(title='Price'),
        yaxis2=dict(title='RSI', overlaying='y', side='right'),
        yaxis3=dict(title='MACD', overlaying='y', side='right'),
        yaxis4=dict(title='Volume', overlaying='y', side='right'),
        xaxis=dict(rangeslider=dict(visible=False))
    )
    
    # Save the plot
    fig.write_html('technical_analysis.html')
    print("\nTechnical analysis plot saved as 'technical_analysis.html'")

def print_detailed_indicators(data):
    """
    Print detailed information about all indicators
    """
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    
    print("\n=== Detailed Indicator Analysis ===")
    
    # Moving Averages
    print("\nMoving Averages:")
    print(f"SMA 20: {latest['SMA_20']:.2f} ({'↑' if latest['SMA_20'] > prev['SMA_20'] else '↓'})")
    print(f"SMA 50: {latest['SMA_50']:.2f} ({'↑' if latest['SMA_50'] > prev['SMA_50'] else '↓'})")
    print(f"EMA 20: {latest['EMA_20']:.2f} ({'↑' if latest['EMA_20'] > prev['EMA_20'] else '↓'})")
    
    # Bollinger Bands
    print("\nBollinger Bands:")
    print(f"Upper Band: {latest['BB_upper']:.2f}")
    print(f"Middle Band: {latest['BB_middle']:.2f}")
    print(f"Lower Band: {latest['BB_lower']:.2f}")
    print(f"Band Width: {(latest['BB_upper'] - latest['BB_lower']) / latest['BB_middle']:.2%}")
    
    # RSI
    print("\nRSI Analysis:")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"RSI Trend: {'↑' if latest['RSI'] > prev['RSI'] else '↓'}")
    print(f"RSI Position: {'Overbought' if latest['RSI'] > 70 else 'Oversold' if latest['RSI'] < 30 else 'Neutral'}")
    
    # MACD
    print("\nMACD Analysis:")
    print(f"MACD: {latest['MACD']:.2f}")
    print(f"Signal Line: {latest['MACD_signal']:.2f}")
    print(f"Histogram: {latest['MACD_hist']:.2f}")
    print(f"MACD Trend: {'↑' if latest['MACD'] > prev['MACD'] else '↓'}")
    
    # Volume Analysis
    print("\nVolume Analysis:")
    print(f"Current Volume: {latest['Volume']:,.0f}")
    print(f"Volume Change: {(latest['Volume'] - prev['Volume']) / prev['Volume']:.2%}")
    print(f"Volume SMA 20: {latest['Volume_SMA_20']:,.0f}")
    print(f"OBV: {latest['OBV']:,.0f}")
    print(f"CMF: {latest['CMF']:.2f}")

def test_live_signals():
    """
    Test our trading indicators with live BTC-USD data
    """
    # Fetch live data
    print("Fetching live BTC-USD data...")
    data = fetch_live_data()
    
    if data is None:
        print("Failed to fetch data. Exiting...")
        return
    
    print(f"Successfully fetched {len(data)} data points")
    
    # Calculate indicators
    print("Calculating technical indicators...")
    data_with_indicators = calculate_indicators(data)
    
    # Generate signals
    print("Generating trading signals...")
    signals = generate_signals(data_with_indicators)
    
    # Print detailed indicator analysis
    print_detailed_indicators(data_with_indicators)
    
    # Print results
    print("\n=== Trading Signals ===")
    print(f"Signal: {signals['signal']}")
    print(f"Confidence: {signals['confidence']:.2%}")
    print(f"Entry Price: {signals['entry_price']:.2f}")
    print(f"Stop Loss: {signals['stop_loss']:.2f}")
    print(f"Take Profit: {signals['take_profit']:.2f}")
    
    print("\n=== Signal Reasons ===")
    for reason in signals['reasons']:
        print(f"- {reason}")
    
    print("\n=== Support & Resistance ===")
    print(f"Support Levels: {signals['support_levels']}")
    print(f"Resistance Levels: {signals['resistance_levels']}")
    
    print("\n=== Patterns ===")
    for pattern in signals['patterns']:
        print(f"- {pattern}")
    
    print("\n=== Divergences ===")
    for divergence in signals['divergences']:
        print(f"- {divergence}")
    
    # Create visualization
    print("\nCreating visualization...")
    plot_indicators(data_with_indicators, signals)

if __name__ == "__main__":
    test_live_signals() 