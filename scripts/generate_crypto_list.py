#!/usr/bin/env python3
"""
Generate cryptocurrencies.json from existing data files.
This extracts all cryptocurrency symbols from the data directory
and creates a proper mapping for the application.
"""

import os
import json
import re

def generate_crypto_list():
    """Extract cryptocurrency symbols from data/*.csv files."""
    data_dir = "data"
    cryptos = {}
    
    print("🔍 Scanning data directory for cryptocurrency files...")
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return {}
    
    # Get all CSV files
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".csv"):
            # Extract symbol from filename: processed_BTC.csv -> BTC
            match = re.match(r'processed_([A-Za-z0-9]+)\.csv', filename)
            if match:
                symbol = match.group(1).upper()
                # Assume -USD ticker
                ticker = f"{symbol}-USD"
                cryptos[symbol] = ticker
                print(f"  ✅ {symbol:8} → {ticker}")
    
    print(f"\n📊 Found {len(cryptos)} cryptocurrencies")
    return cryptos

def save_cryptocurrencies_json(cryptos, filename="cryptocurrencies.json"):
    """Save cryptocurrency list to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(cryptos, f, indent=2, sort_keys=True)
        print(f"✅ Saved to {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("🔧 CRYPTOCURRENCY LIST GENERATOR")
    print("=" * 70 + "\n")
    
    cryptos = generate_crypto_list()
    
    if not cryptos:
        print("❌ No cryptocurrencies found!")
        return False
    
    # Save to file
    if save_cryptocurrencies_json(cryptos):
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"Generated {len(cryptos)} cryptocurrency entries")
        print("\nFirst 10 entries:")
        for i, (symbol, ticker) in enumerate(sorted(cryptos.items())[:10], 1):
            print(f"  {i:2}. {symbol:8} → {ticker}")
        if len(cryptos) > 10:
            print(f"  ... and {len(cryptos) - 10} more")
        return True
    else:
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
