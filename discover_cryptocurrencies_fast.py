#!/usr/bin/env python3
"""
Optimized cryptocurrency discovery using whitelist.
Instead of brute-force testing 500+ symbols, tests only known working cryptos.
Much faster: completes in 2-3 minutes instead of 30+ minutes.
"""

import yfinance as yf
from datetime import datetime
import json
import os

# Curated list of known working cryptocurrencies on Yahoo Finance
KNOWN_WORKING_CRYPTOS = [
    # Top 20 by market cap
    'BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'DOGE', 'LINK', 'LTC', 'XRP', 'AVAX',
    'MATIC', 'ATOM', 'ALGO', 'DOT', 'LUNA', 'XLM', 'XMR', 'ZEC', 'ETC', 'VET',
    # Popular altcoins
    'ARB', 'OP', 'NEAR', 'FTM', 'CELO', 'FLOW', 'ICP', 'HBAR', 'THETA', 'TFUEL',
    'ENJ', 'MANA', 'SAND', 'AXS', 'GALA', 'CHZ', 'RUNE', 'SUSHI', 'UNI', 'AAVE',
    'MKR', 'YFI', 'CRV', 'BAT', 'ZRX', 'KNC', 'LRC', 'COMP', 'SNX', 'UMA',
    # DeFi & Bridge tokens
    'BNT', 'LOKA', 'LPT', 'SRM', 'FTT', 'GT', 'HT', 'OKB', 'LEO', 'CRO',
    'DASH', 'BTG', 'BCH', 'DYDX', 'TIA', 'PYTH', 'FLOKI', 'SHIB', 'LEASH',
    'ANKR', 'BAND', 'LDO', 'INJ', 'SEI', 'ONDO', 'ENA', 'WLD', 'BLUR', 'MODE',
    'ARK', 'ALPHA', 'AMP', 'AIO', 'AKITA', 'PIVX', 'EGLD', 'HOT', 'ETN', 'IOTA',
    'IOT', 'QTUM', 'ONE', 'LSK', 'STORJ', 'WAVES', 'LOKA', 'XTZ', 'ZIL', 'ZEN'
]

CRYPTO_SUFFIXES = ['-USD', '-USDT', '-USDC']  # Reduced from 5 to 3 most common

def test_crypto(symbol, suffix='-USD'):
    """Test if a cryptocurrency symbol works on Yahoo Finance."""
    ticker = f"{symbol}{suffix}"
    try:
        data = yf.download(ticker, period='1d', progress=False)
        if len(data) > 0:
            return ticker
    except Exception:
        pass
    return None

def discover_cryptocurrencies_fast():
    """
    Discover cryptocurrencies using whitelist approach.
    Much faster than brute force: completes in 2-3 minutes.
    """
    print("\n" + "=" * 70)
    print("🚀 FAST CRYPTOCURRENCY DISCOVERY (Whitelist-based)")
    print("=" * 70)
    print(f"\n🔍 Testing {len(KNOWN_WORKING_CRYPTOS)} known cryptos...")
    print(f"   {len(CRYPTO_SUFFIXES)} suffixes per crypto")
    print(f"   Total tests: ~{len(KNOWN_WORKING_CRYPTOS) * len(CRYPTO_SUFFIXES)}")
    
    discovered = {}
    failed = []
    
    for i, symbol in enumerate(KNOWN_WORKING_CRYPTOS, 1):
        found = False
        for suffix in CRYPTO_SUFFIXES:
            ticker = test_crypto(symbol, suffix)
            if ticker:
                discovered[symbol] = ticker
                print(f"[{i:3}/{len(KNOWN_WORKING_CRYPTOS)}] ✅ {symbol:8} → {ticker}")
                found = True
                break
        
        if not found:
            failed.append(symbol)
            # Only show failed on last few or every 10th
            if len(KNOWN_WORKING_CRYPTOS) - i <= 5 or i % 10 == 0:
                print(f"[{i:3}/{len(KNOWN_WORKING_CRYPTOS)}] ❌ {symbol}")
    
    return discovered, failed

def save_cryptocurrency_list(cryptos, filename="cryptocurrencies.json"):
    """Save discovered cryptocurrencies to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(cryptos, f, indent=2, sort_keys=True)
        return True
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return False

def main():
    """Main discovery process."""
    discovered, failed = discover_cryptocurrencies_fast()
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Discovered: {len(discovered)} cryptocurrencies")
    print(f"❌ Failed: {len(failed)} cryptocurrencies")
    
    if failed:
        print(f"\nFailed cryptos: {', '.join(failed)}")
    
    # Save results
    if save_cryptocurrency_list(discovered):
        print(f"\n✅ Saved {len(discovered)} cryptocurrencies to cryptocurrencies.json")
        
        # Show timestamp
        with open("cryptocurrencies.json", 'r') as f:
            data = json.load(f)
        
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        return True
    
    return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
