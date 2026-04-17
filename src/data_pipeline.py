import pandas as pd
import numpy as np
import yfinance as yf
import os
import json
from datetime import datetime


def load_dynamic_cryptocurrencies():
    """Load cryptocurrency list from JSON file. Falls back to defaults if not found."""
    config_path = 'cryptocurrencies.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('cryptocurrencies', {})
        except Exception as e:
            print(f"Warning: Could not load cryptocurrencies.json: {e}")
    
    # Fallback to default major cryptocurrencies
    return {
        'BTC': 'BTC-USD', 'ETH': 'ETH-USD', 'BNB': 'BNB-USD', 'ADA': 'ADA-USD',
        'XRP': 'XRP-USD', 'SOL': 'SOL-USD', 'DOT': 'DOT-USD', 'DOGE': 'DOGE-USD',
        'AVAX': 'AVAX-USD', 'LTC': 'LTC-USD', 'TRX': 'TRX-USD', 'ETC': 'ETC-USD',
        'BCH': 'BCH-USD', 'LINK': 'LINK-USD', 'XLM': 'XLM-USD', 'ICP': 'ICP-USD',
        'HBAR': 'HBAR-USD', 'NEAR': 'NEAR-USD', 'FLOW': 'FLOW-USD', 'MANA': 'MANA-USD',
        'SAND': 'SAND-USD', 'AXS': 'AXS-USD', 'CHZ': 'CHZ-USD', 'ENJ': 'ENJ-USD',
        'BAT': 'BAT-USD', 'OMG': 'OMG-USD', 'ZRX': 'ZRX-USD', 'LRC': 'LRC-USD',
        'STORJ': 'STORJ-USD', 'WAVES': 'WAVES-USD', 'LSK': 'LSK-USD', 'ARK': 'ARK-USD',
        'XEM': 'XEM-USD', 'QTUM': 'QTUM-USD', 'BTG': 'BTG-USD', 'ZEC': 'ZEC-USD',
        'DASH': 'DASH-USD', 'XMR': 'XMR-USD'
    }


# Dynamic cryptocurrency list - loads from cryptocurrencies.json
MAJOR_CRYPTOCURRENCIES = load_dynamic_cryptocurrencies()


def download_crypto_data(ticker: str = "BTC-USD", period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Download cryptocurrency data from Yahoo Finance for any ticker."""
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError(f"No data downloaded from Yahoo Finance for ticker: {ticker}. Check ticker validity or connectivity.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    if len(df.columns) == 5 and len(df.columns.unique()) == 1:
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df.index = pd.to_datetime(df.index)
    return df


def download_btc_data(ticker: str = "BTC-USD", period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Legacy function for backward compatibility."""
    return download_crypto_data(ticker, period, interval)


def download_eth_data(ticker: str = "ETH-USD", period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Legacy function for backward compatibility."""
    return download_crypto_data(ticker, period, interval)


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for cryptocurrency data."""
    df = df.copy()
    df["SMA10"] = df["Close"].rolling(window=10, min_periods=10).mean()
    df["SMA30"] = df["Close"].rolling(window=30, min_periods=30).mean()
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df["RSI14"] = 100 - (100 / (1 + rs))

    df = df.dropna()
    return df


def prepare_crypto_dataset(symbol: str, output_path: str = None) -> pd.DataFrame:
    """Prepare dataset for any cryptocurrency symbol."""
    if symbol in MAJOR_CRYPTOCURRENCIES:
        ticker = MAJOR_CRYPTOCURRENCIES[symbol]
    else:
        # Assume it's already a valid ticker (e.g., BTC-USD, ETH-USD)
        ticker = symbol if '-USD' in symbol else f"{symbol}-USD"
    
    if output_path is None:
        output_path = f"data/processed_{symbol.lower()}.csv"
    
    raw = download_crypto_data(ticker)
    processed = compute_technical_indicators(raw)
    processed.to_csv(output_path)
    return processed


def prepare_btc_dataset(output_path: str = "data/processed_btc.csv") -> pd.DataFrame:
    """Legacy function for backward compatibility."""
    return prepare_crypto_dataset("BTC", output_path)


def prepare_eth_dataset(output_path: str = "data/processed_eth.csv") -> pd.DataFrame:
    """Legacy function for backward compatibility."""
    return prepare_crypto_dataset("ETH", output_path)


def get_available_cryptocurrencies():
    """Get all available cryptocurrencies."""
    return MAJOR_CRYPTOCURRENCIES


def is_new_coin_available(symbol: str) -> bool:
    """Check if a new coin is available on Yahoo Finance."""
    ticker = symbol if '-USD' in symbol else f"{symbol}-USD"
    try:
        data = yf.download(ticker, period='1d', interval='1d', progress=False)
        return not data.empty
    except:
        return False


