import pandas as pd
import numpy as np

# Function to calculate Simple Moving Average (SMA)
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

# Function to calculate Bollinger Bands

def calculate_bollinger_bands(data, window):
    sma = calculate_sma(data, window)
    std = data['Close'].rolling(window=window).std()
    data['Upper Band'] = sma + (std * 2)
    data['Lower Band'] = sma - (std * 2)
    return data

# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(data, window):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Function to calculate Volatility

def calculate_volatility(data, window):
    return data['Close'].pct_change().rolling(window=window).std() * np.sqrt(window)

# Function to calculate Daily Returns

def calculate_returns(data):
    data['Returns'] = data['Close'].pct_change()
    return data

# Function to find Support and Resistance levels

def calculate_support_resistance(data, n):
    pivots = data['Close'].rolling(window=n).mean()  # Simple pivot point
    support = pivots - (data['Close'].rolling(window=n).std())
    resistance = pivots + (data['Close'].rolling(window=n).std())
    data['Support'] = support
    data['Resistance'] = resistance
    return data

# Example usage
if __name__ == '__main__':
    # Load data
    # You can load your data using pandas if needed
    pass

