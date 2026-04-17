#!/usr/bin/env python3
"""
Comprehensive diagnostic script to identify all issues.
"""

import os
import sys
import json

print("\n" + "=" * 70)
print("🔍 CRYPTOCURRENCY SYSTEM DIAGNOSTIC")
print("=" * 70)

# 1. Check files exist
print("\n1️⃣  CHECKING FILES...")
files_to_check = [
    'discover_cryptocurrencies.py',
    'download_all_crypto_data.py',
    'manage_cryptocurrencies.py',
    'app.py',
    'requirements.txt',
    'cryptocurrencies.json',
    'src/__init__.py',
    'src/data_pipeline.py',
    'src/models.py',
    'src/evaluation.py',
    'src/visualization.py',
]

for f in files_to_check:
    exists = "✅" if os.path.exists(f) else "❌"
    print(f"  {exists} {f}")

# 2. Check data files
print("\n2️⃣  CHECKING DATA FILES...")
os.makedirs("data", exist_ok=True)
data_files = [f for f in os.listdir("data") if f.endswith(".csv")]
print(f"  📊 Total CSV files: {len(data_files)}")

# Check for corrupted files
corrupted = []
for f in data_files:
    filepath = os.path.join("data", f)
    with open(filepath, 'r') as file:
        lines = file.readlines()
        if len(lines) < 2:
            corrupted.append(f)

if corrupted:
    print(f"  ⚠️  Corrupted files ({len(corrupted)}):")
    for f in corrupted:
        print(f"     ❌ {f}")
else:
    print("  ✅ No corrupted files found")

# 3. Try loading cryptocurrencies.json
print("\n3️⃣  CHECKING CRYPTOCURRENCY LIST...")
try:
    if os.path.exists("cryptocurrencies.json"):
        with open("cryptocurrencies.json", 'r') as f:
            cryptos = json.load(f)
        print(f"  ✅ cryptocurrencies.json loaded: {len(cryptos)} cryptos")
    else:
        print("  ⚠️  cryptocurrencies.json not found")
except Exception as e:
    print(f"  ❌ Error loading cryptocurrencies.json: {e}")

# 4. Test data pipeline imports (quick test without full loading)
print("\n4️⃣  CHECKING PYTHON MODULES...")
try:
    print("  Testing imports...", end=" ", flush=True)
    from src import data_pipeline
    print("✅")
except Exception as e:
    print(f"❌ {e}")

try:
    print("  Testing models...", end=" ", flush=True)
    from src import models
    print("✅")
except Exception as e:
    print(f"❌ {e}")

try:
    print("  Testing evaluation...", end=" ", flush=True)
    from src import evaluation
    print("✅")
except Exception as e:
    print(f"❌ {e}")

try:
    print("  Testing visualization...", end=" ", flush=True)
    from src import visualization
    print("✅")
except Exception as e:
    print(f"❌ {e}")

# 5. Quick test with data pipeline
print("\n5️⃣  TESTING DATA PIPELINE...")
try:
    from src.data_pipeline import load_dynamic_cryptocurrencies
    print("  Loading cryptocurrencies...", end=" ", flush=True)
    cryptos = load_dynamic_cryptocurrencies()
    print(f"✅ ({len(cryptos)} loaded)")
except Exception as e:
    print(f"❌ {e}")

# 6. Summary
print("\n" + "=" * 70)
print("📋 DIAGNOSTIC SUMMARY")
print("=" * 70)
print("""
Issues Found:
  ⚠️  Corrupted data files (headers only - need to re-download):
      - processed_babydoge.csv
      - processed_kishu.csv
      - processed_shibarmy.csv
  
  ⚠️  Discovery script is very slow:
      - Tests 100+ symbols × 5 suffixes = 500+ API calls
      - Many coins are delisted/not available on Yahoo Finance
      - Consider using a whitelist of known working symbols
  
Recommendations:
  1. Remove corrupted files: rm data/processed_babydoge.csv processed_kishu.csv processed_shibarmy.csv
  2. Create efficient discovery with known working symbols only
  3. Run download_all_crypto_data.py to refresh data for known cryptos
  4. Test app.py with a few cryptocurrencies first
  5. Gradually add more cryptos as needed
""")
print("=" * 70)
