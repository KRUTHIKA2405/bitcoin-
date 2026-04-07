# Bitcoin Price Prediction System

This repository contains an AI-powered Bitcoin price prediction system with a modular backend and an interactive Streamlit web interface.

## Features

- Data pipeline using Yahoo Finance (`BTC-USD`)
- Technical feature engineering: SMA, EMA, RSI, MACD
- Model implementations:
  - Linear Regression
  - Random Forest
  - XGBoost
  - ARIMA
  - GARCH
  - LSTM
  - CNN + LSTM
- Evaluation metrics: MAE, RMSE, Accuracy (%) derived from MAPE
- Combined visualization of actual price, predictions, and volatility
- Streamlit frontend for model selection and performance analysis

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Generate the processed dataset and start the app:

```bash
python -c "from src.data_pipeline import prepare_btc_dataset; prepare_btc_dataset()"
streamlit run app.py
```

Then open the Streamlit app in your browser and use the sidebar to select models and compare predictions.

## Output

- `data/processed_btc.csv` — preprocessed Bitcoin dataset
- `outputs/model_comparison.png` — combined model comparison chart

## Notes

The app trains selected models on historical BTC-USD data and displays predictions, performance metrics, and comparison charts.
