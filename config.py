"""
Configuration settings for the Market Data Analysis Tool
"""

# API Keys (get free keys from these services)
API_KEYS = {
    'alpha_vantage': 'YOUR_API_KEY_HERE',  # Get from https://www.alphavantage.co/
    'finnhub': 'YOUR_API_KEY_HERE',         # Get from https://finnhub.io/
}

# Data settings
DATA_SETTINGS = {
    'cache_dir': './data_cache',
    'output_dir': './analysis_output',
}

# Technical analysis defaults
TECHNICAL_ANALYSIS = {
    'sma_periods': [20, 50, 200],           # Simple Moving Averages
    'bollinger_period': 20,
    'bollinger_std_dev': 2,
    'rsi_period': 14,
}

# Visualization settings
CHART_SETTINGS = {
    'figure_size': (14, 8),
    'style': 'seaborn-v0_8-darkgrid',
    'dpi': 100,
}