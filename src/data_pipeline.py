import pandas as pd
import numpy as np
import yfinance as yf


def download_btc_data(ticker: str = "BTC-USD", period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError("No data downloaded from Yahoo Finance. Check ticker or connectivity.")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    if len(df.columns) == 5 and len(df.columns.unique()) == 1:
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
    df.index = pd.to_datetime(df.index)
    return df


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
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


def prepare_btc_dataset(output_path: str = "data/processed_btc.csv") -> pd.DataFrame:
    raw = download_btc_data()
    processed = compute_technical_indicators(raw)
    processed.to_csv(output_path)
    return processed
