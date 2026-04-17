#!/usr/bin/env python3
"""
Initial setup script to discover and download all cryptocurrencies.
This is the first script to run after installation.

Steps:
1. Discover all cryptocurrencies on Yahoo Finance
2. Save to cryptocurrencies.json
3. Download data for all coins
4. Start the Streamlit app
"""

import subprocess
import sys
import os

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n📍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"⚠️  Command failed with return code {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_section("CRYPTOCURRENCY PREDICTION SYSTEM - SETUP")
    
    print("\n📋 This setup will:")
    print("   1. Discover all cryptocurrencies on Yahoo Finance")
    print("   2. Save discovered coins to cryptocurrencies.json")
    print("   3. Download price data for all coins")
    print("   4. Launch the Streamlit web interface")
    
    # Step 1: Discover cryptocurrencies
    if not run_command(
        "python discover_cryptocurrencies.py",
        "Step 1/3: Discovering cryptocurrencies on Yahoo Finance"
    ):
        print("❌ Discovery failed. Continuing anyway...")
    
    print_section("Step 2/3: Downloading Cryptocurrency Data")
    print("\n⏳ This may take several minutes depending on internet speed...")
    print("   (~100+ cryptocurrencies × API calls)")
    
    if not run_command(
        "python download_all_crypto_data.py",
        "Downloading data for all coins"
    ):
        print("⚠️  Some downloads may have failed, but Streamlit can handle missing data")
    
    # Step 3: Launch Streamlit
    print_section("Setup Complete!")
    print("\n✅ System is ready to use!")
    print("\n📍 Launching Streamlit application...")
    print("   Browser will open at: http://localhost:8503")
    
    run_command(
        "streamlit run app.py --logger.level=error",
        "Launching Streamlit app"
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
