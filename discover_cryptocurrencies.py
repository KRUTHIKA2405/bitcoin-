#!/usr/bin/env python3
"""
Script to discover all available cryptocurrencies on Yahoo Finance.
This creates and updates a dynamic list of all tradeable cryptocurrencies.
"""

import yfinance as yf
import json
import os
from datetime import datetime

# Common cryptocurrency suffixes on Yahoo Finance
CRYPTO_SUFFIXES = ['-USD', '-USDT', '-USDC', '-EUR', '-GBP']

# Base list of known cryptocurrencies (this will be expanded)
KNOWN_CRYPTOS = [
    'BTC', 'ETH', 'BNB', 'ADA', 'XRP', 'SOL', 'DOT', 'DOGE', 'AVAX', 'LTC',
    'TRX', 'ETC', 'BCH', 'LINK', 'XLM', 'ICP', 'HBAR', 'NEAR', 'FLOW', 'MANA',
    'SAND', 'AXS', 'CHZ', 'ENJ', 'BAT', 'OMG', 'ZRX', 'LRC', 'STORJ', 'WAVES',
    'LSK', 'ARK', 'XEM', 'QTUM', 'BTG', 'ZEC', 'DASH', 'XMR', 'ETN', 'PIVX',
    'ATOM', 'VET', 'FTT', 'SHIB', 'MATIC', 'LUNA', 'ALGO', 'CRO', 'GALA', 'GMT',
    'IMX', 'STX', 'LOKA', 'ANKR', 'CELO', 'ONE', 'EGLD', 'ZIL', 'THETA', 'TFUEL',
    'HOT', 'BTC', 'GRT', 'RUNE', 'BAND', 'UNI', 'AAVE', 'SUSHI', 'CURVE', 'YFI',
    'COMP', 'MKR', 'SNX', 'UMA', 'BNT', 'KNC', '1INCH', 'ALPHA', 'SRM', 'FTX',
    'OKB', 'LEO', 'OKEX', 'HT', 'BGB', 'GT', '0X', 'ZEN', 'ATOM', 'IOT',
    'AIO', 'XTZ', 'IOTA', 'AMP', 'LPT', 'GGM', 'AKITA', 'FLOKI', 'KISHU', 'SAITAMA',
    'BONE', 'LEASH', 'BabyDoge', 'Safemoon', 'ElonSperm', 'Cumrocket', 'SafeGalaxy',
    'Dogelon', 'Shinjirushi', 'Metashib', 'Shibnobi', 'Shiba2', 'Shibarmy',
    'OP', 'ARB', 'LDO', 'MNT', 'HYPE', 'MODE', 'SONIC', 'SUI', 'APT', 'INJ',
    'TIA', 'DYDX', 'SEI', 'PYTH', 'WLD', 'ENA', 'BLUR', 'ONDO', 'PEPE', 'BRETT'
]

def test_crypto(symbol, suffix='-USD'):
    """Test if a cryptocurrency ticker exists on Yahoo Finance."""
    ticker = f"{symbol}{suffix}"
    try:
        data = yf.download(ticker, period='1d', interval='1d', progress=False)
        if not data.empty:
            return True, ticker
    except:
        pass
    return False, None

def discover_cryptocurrencies():
    """
    Discover all available cryptocurrencies on Yahoo Finance.
    Returns a dictionary of symbol: ticker mappings.
    """
    print("🔍 Discovering cryptocurrencies on Yahoo Finance...")
    print("=" * 60)
    
    discovered = {}
    not_found = []
    
    for i, symbol in enumerate(KNOWN_CRYPTOS, 1):
        print(f"[{i}/{len(KNOWN_CRYPTOS)}] Testing {symbol}...", end=" ")
        
        # Try USD first
        found, ticker = test_crypto(symbol, '-USD')
        if found:
            print(f"✅ Found: {ticker}")
            discovered[symbol] = ticker
        else:
            # Try other suffixes
            found_alt = False
            for suffix in CRYPTO_SUFFIXES[1:]:  # Skip -USD as we already tried it
                found, ticker = test_crypto(symbol, suffix)
                if found:
                    print(f"✅ Found: {ticker}")
                    discovered[symbol] = ticker
                    found_alt = True
                    break
            
            if not found_alt:
                print(f"❌ Not found")
                not_found.append(symbol)
    
    print("=" * 60)
    print(f"✅ Discovered {len(discovered)} cryptocurrencies")
    print(f"❌ Could not find {len(not_found)} symbols")
    
    return discovered, not_found

def save_cryptocurrency_list(cryptocurrencies):
    """Save discovered cryptocurrencies to a JSON file."""
    config = {
        "last_updated": datetime.now().isoformat(),
        "total_cryptos": len(cryptocurrencies),
        "cryptocurrencies": cryptocurrencies,
        "auto_discovery_enabled": True,
        "description": "This list is automatically updated with new cryptocurrencies"
    }
    
    with open('cryptocurrencies.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Saved cryptocurrency list to cryptocurrencies.json")
    print(f"   Total cryptocurrencies: {len(cryptocurrencies)}")
    print(f"   Last updated: {config['last_updated']}")

def load_cryptocurrency_list():
    """Load cryptocurrency list from JSON file."""
    if os.path.exists('cryptocurrencies.json'):
        try:
            with open('cryptocurrencies.json', 'r') as f:
                config = json.load(f)
                return config.get('cryptocurrencies', {})
        except:
            pass
    return {}

def add_new_cryptocurrencies(new_symbols):
    """Add new cryptocurrency symbols to the discovery list."""
    # Load existing list
    existing_symbols = load_cryptocurrency_list()
    
    print(f"\n➕ Adding {len(new_symbols)} new cryptocurrency symbols...")
    added = 0
    
    for symbol in new_symbols:
        if symbol not in existing_symbols:
            found, ticker = test_crypto(symbol, '-USD')
            if found:
                existing_symbols[symbol] = ticker
                print(f"✅ Added: {symbol} ({ticker})")
                added += 1
            else:
                print(f"❌ Failed to add: {symbol}")
    
    if added > 0:
        save_cryptocurrency_list(existing_symbols)
        print(f"\n✅ Successfully added {added} new cryptocurrencies")
    
    return existing_symbols

def main():
    """Main discovery function."""
    print("\n" + "=" * 60)
    print("🔎 CRYPTOCURRENCY DISCOVERY ENGINE")
    print("=" * 60)
    
    # Discover cryptocurrencies
    discovered, not_found = discover_cryptocurrencies()
    
    # Save to file
    save_cryptocurrency_list(discovered)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully discovered: {len(discovered)} cryptocurrencies")
    print(f"📝 Not found: {len(not_found)} symbols")
    
    if not_found:
        print(f"\nSymbols not found: {', '.join(not_found[:10])}")
        if len(not_found) > 10:
            print(f"... and {len(not_found) - 10} more")
    
    print("\n✨ Discovery complete! Run download_all_crypto_data.py to process all coins")

if __name__ == "__main__":
    main()
