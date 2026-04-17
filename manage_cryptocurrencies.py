#!/usr/bin/env python3
"""
Helper script to manage cryptocurrency updates and additions.
This allows you to:
1. Discover all cryptocurrencies on Yahoo Finance
2. Add new cryptocurrencies to the list
3. Remove coins from the list
4. Refresh the cryptocurrency list
"""

import json
import os
from discover_cryptocurrencies import discover_cryptocurrencies, load_cryptocurrency_list, save_cryptocurrency_list, add_new_cryptocurrencies
from src.data_pipeline import MAJOR_CRYPTOCURRENCIES, is_new_coin_available

def view_crypto_list():
    """View current cryptocurrency list."""
    cryptos = load_cryptocurrency_list()
    print("\n" + "=" * 70)
    print(f"📋 CURRENT CRYPTOCURRENCY LIST ({len(cryptos)} total)")
    print("=" * 70)
    
    for i, (symbol, ticker) in enumerate(sorted(cryptos.items()), 1):
        print(f"{i:3d}. {symbol:8s} → {ticker}")
    
    print("=" * 70)

def update_crypto_list():
    """Update the cryptocurrency list with newly discovered coins."""
    print("\n" + "=" * 70)
    print("🔄 UPDATING CRYPTOCURRENCY LIST")
    print("=" * 70)
    
    discovered, not_found = discover_cryptocurrencies()
    save_cryptocurrency_list(discovered)
    
    print(f"\n✅ Updated list contains {len(discovered)} cryptocurrencies")

def add_custom_coins():
    """Add custom cryptocurrency symbols to the list."""
    print("\n" + "=" * 70)
    print("➕ ADD CUSTOM CRYPTOCURRENCIES")
    print("=" * 70)
    print("Enter cryptocurrency symbols (comma-separated)")
    print("Example: SHIB, MATIC, PEPE, XEC")
    print()
    
    user_input = input("Enter symbols: ").strip().upper()
    
    if not user_input:
        print("❌ No symbols entered")
        return
    
    new_symbols = [s.strip() for s in user_input.split(',')]
    
    print(f"\n📝 Adding {len(new_symbols)} new cryptocurrency symbols...")
    add_new_cryptocurrencies(new_symbols)

def remove_coins():
    """Remove cryptocurrencies from the list."""
    print("\n" + "=" * 70)
    print("➖ REMOVE CRYPTOCURRENCIES")
    print("=" * 70)
    print("Enter cryptocurrency symbols to remove (comma-separated)")
    print()
    
    user_input = input("Enter symbols: ").strip().upper()
    
    if not user_input:
        print("❌ No symbols entered")
        return
    
    symbols_to_remove = [s.strip() for s in user_input.split(',')]
    cryptos = load_cryptocurrency_list()
    
    removed = 0
    for symbol in symbols_to_remove:
        if symbol in cryptos:
            del cryptos[symbol]
            print(f"✅ Removed: {symbol}")
            removed += 1
        else:
            print(f"❌ Not found: {symbol}")
    
    if removed > 0:
        save_cryptocurrency_list(cryptos)
        print(f"\n✅ Successfully removed {removed} cryptocurrencies")

def check_new_coins():
    """Check if new coins have been added to Yahoo Finance."""
    print("\n" + "=" * 70)
    print("✨ CHECK FOR NEWLY DISCOVERED COINS")
    print("=" * 70)
    
    # List of potential new cryptocurrencies to check
    potential_coins = [
        'SHIB', 'MATIC', 'PEPE', 'XEC', 'BCH', 'BSV', 'DYN', 'ARPA', 'LTO', 'KIN',
        'VTHO', 'THETA', 'TFUEL', 'FUN', '0X', 'GTC', 'POWR', 'CTXC', 'AION', 'LOOM',
        'MITH', 'POLY', 'GO', 'POA', 'DOCK', 'AST', 'BNT', 'MEW', 'DTA', 'ETHOS'
    ]
    
    current = load_cryptocurrency_list()
    new_coins = []
    
    print(f"🔍 Checking {len(potential_coins)} potential new coins...")
    
    for symbol in potential_coins:
        if symbol not in current:
            if is_new_coin_available(symbol):
                new_coins.append(symbol)
                print(f"✨ Found new coin: {symbol}")
    
    if new_coins:
        print(f"\n✅ Found {len(new_coins)} new coins!")
        print(f"Coins: {', '.join(new_coins)}")
        
        add_now = input("\nAdd these coins to the list? (y/n): ").strip().lower()
        if add_now == 'y':
            add_new_cryptocurrencies(new_coins)
    else:
        print("ℹ️  No new coins found at this time")

def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 70)
    print("🌍 CRYPTOCURRENCY MANAGER")
    print("=" * 70)
    print("1. View current cryptocurrency list")
    print("2. Fully refresh cryptocurrency discovery")
    print("3. Add custom cryptocurrencies")
    print("4. Remove cryptocurrencies")
    print("5. Check for newly discovered coins")
    print("6. Download data for all coins")
    print("0. Exit")
    print("=" * 70)

def main():
    """Main menu loop."""
    while True:
        show_menu()
        choice = input("Select an option (0-6): ").strip()
        
        if choice == '1':
            view_crypto_list()
        elif choice == '2':
            update_crypto_list()
        elif choice == '3':
            add_custom_coins()
        elif choice == '4':
            remove_coins()
        elif choice == '5':
            check_new_coins()
        elif choice == '6':
            print("\n🚀 Downloading data for all coins...")
            os.system('python download_all_crypto_data.py')
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
