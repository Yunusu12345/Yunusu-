"""
Module for fetching market data from multiple free APIs
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
from config import API_KEYS, DATA_SETTINGS

class DataFetcher:
    """Fetch stock and cryptocurrency data from free APIs"""
    
    def __init__(self):
        self.cache_dir = Path(DATA_SETTINGS['cache_dir'])
        self.cache_dir.mkdir(exist_ok=True)
        
    def fetch_alpha_vantage(self, symbol, asset_type='stock'):
        """
        Fetch data from Alpha Vantage API
        asset_type: 'stock' or 'crypto'
        """
        api_key = API_KEYS['alpha_vantage']
        
        if asset_type == 'stock':
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full"
            response = requests.get(url)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                df = df.astype(float)
                return df
            else:
                raise Exception(f"Error fetching data: {data.get('Note', 'Unknown error')}")
                
        elif asset_type == 'crypto':
            url = f"https://www.alphavantage.co/query?function=CURRENCY_DAILY&from_symbol={symbol}&to_symbol=USD&apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df.columns = ['open', 'high', 'low', 'close']
                df = df.astype(float)
                return df
            else:
                raise Exception(f"Error fetching data: {data.get('Note', 'Unknown error')}")
    
    def fetch_coingecko(self, crypto_id, days=365):
        """
        Fetch cryptocurrency data from CoinGecko API (Free, no API key needed)
        crypto_id: e.g., 'bitcoin', 'ethereum', 'cardano'
        """
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.set_index('timestamp')
            df = df.astype(float)
            
            return df
        except Exception as e:
            raise Exception(f"Error fetching from CoinGecko: {str(e)}")
    
    def cache_data(self, df, symbol, asset_type):
        """Cache data to avoid repeated API calls"""
        cache_file = self.cache_dir / f"{symbol}_{asset_type}.csv"
        df.to_csv(cache_file)
    
    def load_cached_data(self, symbol, asset_type):
        """Load data from cache if available"""
        cache_file = self.cache_dir / f"{symbol}_{asset_type}.csv"
        if cache_file.exists():
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            return df
        return None
