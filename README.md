# 🪙 Cryptocurrency Price Prediction System

An AI-powered multi-cryptocurrency price prediction system with automatic cryptocurrency discovery and support for all coins available on Yahoo Finance. Features advanced machine learning models, technical indicators, and an interactive Streamlit web interface.

## ✨ Features

### Multi-Cryptocurrency Support
- **All Yahoo Finance Cryptocurrencies**: Supports 100+ cryptocurrencies (BTC, ETH, ADA, DOGE, etc.)
- **Auto-Discovery**: Automatically finds new cryptocurrencies added to Yahoo Finance
- **Dynamic Management**: Add or remove cryptocurrencies from the system
- **Smart Fallback**: Works with 30+ major cryptocurrencies even if discovery fails

### Advanced Machine Learning
- **5 Prediction Models**:
  - Linear Regression
  - ARIMA (Statistical Time Series)
  - GARCH (Volatility Modeling)
  - LSTM (Deep Learning - Sequential)
  - CNN + LSTM (Hybrid Deep Learning)
- **Real-time Training**: Models train on user selection with 10-epoch optimization
- **Accurate Predictions**: MAE, RMSE, and Accuracy (MAPE-derived) metrics

### Technical Analysis
- Multiple indicators: SMA10, SMA30, EMA12, EMA26, RSI14, MACD
- Normalized features with MinMaxScaler
- 5-year historical data from Yahoo Finance

### User Interface
- Interactive Streamlit web app
- Real-time cryptocurrency selection (dropdown + custom input)
- Model comparison and performance visualization
- Lazy-loading with "Run Analysis" button for performance
- Responsive design with session-based caching

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initial Setup (Recommended)
Run the complete setup to discover cryptocurrencies and download data:
```bash
python setup.py
```

This will:
1. Discover all cryptocurrencies on Yahoo Finance
2. Save them to `cryptocurrencies.json`
3. Download price data for all coins
4. Launch the Streamlit app

### 3. Manual Setup (Alternative)
```bash
# Discover cryptocurrencies
python discover_cryptocurrencies.py

# Download data for all coins
python download_all_crypto_data.py

# Start the app
streamlit run app.py
```

### 4. Manage Cryptocurrencies
For an interactive menu to add/remove/update cryptocurrencies:
```bash
python manage_cryptocurrencies.py
```

## 📊 Project Structure

```
bitcoin/
├── app.py                              # Main Streamlit application
├── setup.py                            # Initial setup script
├── discover_cryptocurrencies.py        # Auto-discovery engine
├── download_all_crypto_data.py         # Bulk data downloader
├── manage_cryptocurrencies.py          # Cryptocurrency manager UI
├── requirements.txt                    # Python dependencies
├── cryptocurrencies.json               # Available cryptocurrencies (auto-generated)
├── README.md                           # This file
├── src/
│   ├── __init__.py
│   ├── data_pipeline.py               # Data loading and preprocessing
│   ├── models.py                      # Model implementations
│   ├── evaluation.py                  # Performance metrics
│   └── visualization.py               # Chart generation
├── data/                              # Downloaded cryptocurrency data
│   ├── processed_btc.csv
│   ├── processed_eth.csv
│   └── ...
└── outputs/                           # Generated model comparisons
    └── model_comparison.png
```

## 🛠️ Configuration

### cryptocurrencies.json
Auto-generated file containing all available cryptocurrencies:
```json
{
  "BTC": "BTC-USD",
  "ETH": "ETH-USD",
  "ADA": "ADA-USD",
  ...
}
```

### Adding Custom Cryptocurrencies

**Method 1: Interactive Manager**
```bash
python manage_cryptocurrencies.py
# Select option 3 to add custom coins
```

**Method 2: Manual JSON Edit**
Edit `cryptocurrencies.json` and add:
```json
{
  "NEWCOIN": "NEWCOIN-USD"
}
```

### Discovering New Coins
Automatically discover newly added Yahoo Finance cryptocurrencies:
```bash
python manage_cryptocurrencies.py
# Select option 5 to check for new coins
# Or option 2 to fully refresh discovery
```

## 💾 Data Files

### Input Data
- Downloaded from Yahoo Finance via `yfinance`
- 5-year historical price history
- OHLCV data (Open, High, Low, Close, Volume)

### Processed Data
Located in `data/` directory:
- `processed_[SYMBOL].csv` for each cryptocurrency
- Processed at 90,000 training / 10,000 test samples
- Features include technical indicators

## 🤖 Models Explained

| Model | Type | Best For | Training Time |
|-------|------|----------|----------------|
| Linear Regression | Regression | Baseline trends | < 1 second |
| ARIMA | Statistical | Mean reversion | 2-5 seconds |
| GARCH | Volatility | Risk assessment | 1-3 seconds |
| LSTM | Deep Learning | Sequential patterns | 10-20 seconds |
| CNN+LSTM | Hybrid DL | Complex patterns | 15-30 seconds |

## 📈 Usage Examples

### Example 1: Compare BTC Models
1. Open app: `streamlit run app.py`
2. Select "BTC" from dropdown
3. Click "🚀 Run Analysis"
4. Select models: Linear Regression, ARIMA, GARCH, LSTM, CNN+LSTM
5. View comparison chart

### Example 2: Predict Ethereum Price
1. Select "ETH" from dropdown
2. Choose LSTM model (best for trending)
3. Click "Run Analysis"
4. View predictions and accuracy metrics

### Example 3: Add New Cryptocurrency
1. Run: `python manage_cryptocurrencies.py`
2. Select "3. Add custom cryptocurrencies"
3. Enter symbol (e.g., "SHIB")
4. Return to app and select from dropdown

## 🔍 Advanced Usage

### Programmatic Access
```python
from src.data_pipeline import download_crypto_data, prepare_crypto_dataset
from src.models import train_lstm, train_linear_regression

# Download data
df = download_crypto_data("LUNA")

# Prepare dataset
X_train, X_test, y_train, y_test, scaler = prepare_crypto_dataset("LUNA")

# Train models
lstm_model = train_lstm(X_train, y_train)
lr_model = train_linear_regression(X_train, y_train)

# Evaluate
from src.evaluation import evaluate_model
metrics = evaluate_model(lstm_model, X_test, y_test, scaler)
print(metrics)
```

### Batch Download All Cryptos
```bash
python download_all_crypto_data.py
```

### Check Specific Coin Availability
```python
from discover_cryptocurrencies import test_crypto

available = test_crypto("PEPE", "-USD")
print(f"PEPE available: {available}")
```

## ⚙️ Performance Optimization

- **Lazy Loading**: "Run Analysis" button prevents unnecessary model training
- **Session Caching**: Streamlit caches datasets per cryptocurrency
- **Optimized Epochs**: LSTM/CNN trained with 10 epochs (reduced from 20)
- **Vectorized Processing**: NumPy for fast data operations
- **Lazy Crypto Loading**: Discover cryptocurrencies once, cache to JSON

## 🐛 Troubleshooting

### Issue: `cryptocurrencies.json` not found
**Solution**: Run `python discover_cryptocurrencies.py` to auto-generate

### Issue: Modified data not in dropdown
**Solution**: Restart Streamlit with `streamlit run app.py`

### Issue: Specific cryptocurrency not working
**Solution**: 
1. Run `python manage_cryptocurrencies.py`
2. Check option 5 to verify coin availability on Yahoo Finance
3. Use custom ticker input field in app

### Issue: Slow download of data
**Solution**: Downloader processes sequentially; consider scheduling for off-peak hours

## 📋 Requirements

See `requirements.txt` for dependencies:
- pandas
- numpy
- scikit-learn
- tensorflow >= 2.8
- statsmodels
- arch
- yfinance
- streamlit
- plotly

## 🔐 Environment Variables (Optional)

Environment-specific settings are configured in the code. No API keys required for Yahoo Finance.

## 📝 Output Files

- `cryptocurrencies.json` — Discovered/managed cryptocurrency list
- `data/processed_*.csv` — Training data for each cryptocurrency  
- `outputs/model_comparison.png` — Visualization of model predictions

## 🎯 Future Enhancements

- [ ] Real-time model retraining
- [ ] Multi-coin portfolio prediction
- [ ] Custom technical indicator selection
- [ ] Model parameter tuning UI
- [ ] Data export to CSV/JSON
- [ ] Mobile-responsive interface

## 📄 License

Open source

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional prediction models
- More technical indicators
- Improved UI/UX
- Performance optimization
- Additional data sources

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review `manage_cryptocurrencies.py` options
3. Check data files in `data/` directory
4. Verify Yahoo Finance API connectivity
