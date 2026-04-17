#!/usr/bin/env python3
"""
Script to download data for all cryptocurrencies.
This loads from cryptocurrencies.json and processes all available coins.
If new coins are added to the JSON, they will be automatically processed.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_pipeline import MAJOR_CRYPTOCURRENCIES, prepare_crypto_dataset

def main():
    """Download data for all cryptocurrencies in the list."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    total_cryptos = len(MAJOR_CRYPTOCURRENCIES)
    print("=" * 70)
    print("📊 CRYPTOCURRENCY DATA DOWNLOADER")
    print("=" * 70)
    print(f"📈 Total cryptocurrencies to download: {total_cryptos}")
    print("=" * 70)

    successful = 0
    failed = 0
    failed_cryptos = []

    for i, (symbol, ticker) in enumerate(MAJOR_CRYPTOCURRENCIES.items(), 1):
        try:
            print(f"[{i}/{total_cryptos}] Downloading {symbol} ({ticker})...", end=" ")
            prepare_crypto_dataset(symbol)
            print(f"✅ Success")
            successful += 1
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
            failed += 1
            failed_cryptos.append(symbol)

    print("=" * 70)
    print(f"✅ Successfully downloaded: {successful} cryptocurrencies")
    print(f"❌ Failed: {failed} cryptocurrencies")
    
    if failed_cryptos:
        print(f"\nFailed cryptos: {', '.join(failed_cryptos[:10])}")
        if len(failed_cryptos) > 10:
            print(f"... and {len(failed_cryptos) - 10} more")
    
    print("=" * 70)
    print("💾 Data files saved in the 'data/' directory")
    print("🚀 Ready to use with the Streamlit app!")

if __name__ == "__main__":
    main()