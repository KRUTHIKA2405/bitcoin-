import streamlit as st
import pandas as pd
import numpy as np
import os
from src.data_pipeline import compute_technical_indicators, download_btc_data, download_eth_data, prepare_btc_dataset, prepare_eth_dataset, load_dynamic_cryptocurrencies, download_crypto_data, prepare_crypto_dataset
from src.models import (
    FEATURE_COLUMNS,
    prepare_features,
    split_train_test,
    train_linear_regression,
    arima_rolling_forecast,
    arima_next_day,
    garch_volatility_forecast,
    predict_next_day_ml,
    predict_sequence_next_day,
    train_lstm,
    train_cnn_lstm,
    predict_sequence_model,
)
from src.evaluation import calculate_metrics, build_comparison_table
from src.visualization import plot_predictions, build_model_comparison_chart


def append_user_data(df: pd.DataFrame, new_rows: pd.DataFrame) -> pd.DataFrame:
    raw_cols = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in new_rows.columns for col in raw_cols):
        raise ValueError("Uploaded data must include Open, High, Low, Close, and Volume columns.")
    combined = pd.concat([df[raw_cols], new_rows[raw_cols]], axis=0)
    combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    return compute_technical_indicators(combined)


def get_trade_signal(actual_price: float, predicted_price: float, threshold: float = 0.005) -> tuple[str, str]:
    delta = (predicted_price - actual_price) / actual_price
    percent_change = delta * 100
    if percent_change >= threshold * 100:
        return (
            "Buy",
            f"Predicted price is {percent_change:.2f}% above the latest close, suggesting an upward trend.",
        )
    if percent_change <= -threshold * 100:
        return (
            "Sell",
            f"Predicted price is {abs(percent_change):.2f}% below the latest close, suggesting downward pressure.",
        )
    return (
        "Hold",
        f"Predicted price is within {threshold*100:.1f}% of the latest close, suggesting a neutral range.",
    )


MODEL_OPTIONS = [
    "Linear Regression",
    "ARIMA",
    "GARCH",
    "LSTM",
    "CNN+LSTM",
]


@st.cache_data(show_spinner=False)
def load_data(crypto: str = "BTC") -> pd.DataFrame:
    """Load cryptocurrency data from CSV file or download if not available."""
    # Try to load from existing CSV file (lowercase filename)
    csv_path = f"data/processed_{crypto.lower()}.csv"
    
    try:
        with st.spinner(f"Loading {crypto} data..."):
            df = pd.read_csv(csv_path, parse_dates=[0], index_col=0)
            return df
    except FileNotFoundError:
        pass  # File doesn't exist, download it
    
    # File doesn't exist - try to download and prepare
    try:
        with st.spinner(f"Downloading {crypto} data from Yahoo Finance..."):
            # Get ticker from cryptocurrency list or assume X-USD format
            cryptos = load_dynamic_cryptocurrencies()
            if crypto in cryptos:
                ticker = cryptos[crypto]
            else:
                ticker = f"{crypto}-USD"
            
            # Download and prepare data
            df = download_crypto_data(ticker)
            # Apply technical indicators
            df = compute_technical_indicators(df)
            # Save to CSV for future use
            df.to_csv(csv_path)
            return df
    except Exception as e:
        st.error(f"Could not load data for {crypto}. Error: {e}")
        return None


@st.cache_data(show_spinner=False)
def get_predictions(df: pd.DataFrame, selected_models: list[str]) -> tuple[dict, dict, pd.DataFrame, dict, float]:
    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)
    results = {}
    predictions = {}
    volatility_series = None
    next_day_predictions = {}
    latest_close = float(df["Close"].iloc[-1])

    if "Linear Regression" in selected_models:
        lr_model = train_linear_regression(X_train, y_train)
        preds = pd.Series(lr_model.predict(X_test), index=X_test.index)
        predictions["Linear Regression"] = preds
        results["Linear Regression"] = calculate_metrics(y_test, preds)
        next_day_predictions["Linear Regression"] = predict_next_day_ml(lr_model, X.iloc[-1])

    if "ARIMA" in selected_models:
        arima_preds = arima_rolling_forecast(df["Close"], train_size=0.8)
        predictions["ARIMA"] = arima_preds
        results["ARIMA"] = calculate_metrics(df["Close"].iloc[int(len(df) * 0.8) :], arima_preds)
        next_day_predictions["ARIMA"] = arima_next_day(df["Close"])

    if "GARCH" in selected_models:
        vol_preds, actual_vol = garch_volatility_forecast(df["Close"], train_size=0.8)
        volatility_series = vol_preds
        # GARCH predicts volatility, not price, so use different evaluation
        garch_metrics = calculate_metrics(actual_vol, vol_preds)
        # For volatility models, we'll show MAE and RMSE but not "accuracy"
        results["GARCH"] = {
            "MAE": garch_metrics["MAE"],
            "RMSE": garch_metrics["RMSE"],
            "MAPE": garch_metrics["MAPE"],
            "Accuracy": None  # Volatility models don't have traditional "accuracy"
        }
        next_day_predictions["GARCH"] = float(np.nan)

    if "LSTM" in selected_models:
        lstm_model, scaler_X, scaler_y, metadata = train_lstm(X_train, y_train)
        lstm_preds = predict_sequence_model(lstm_model, scaler_X, scaler_y, X_train, X_test, y_test, window_size=metadata["window_size"])
        # Only evaluate predictions that correspond to test period
        test_predictions = lstm_preds[lstm_preds.index.isin(y_test.index)]
        results["LSTM"] = calculate_metrics(y_test.loc[test_predictions.index], test_predictions)
        predictions["LSTM"] = test_predictions
        next_day_predictions["LSTM"] = predict_sequence_next_day(lstm_model, scaler_X, scaler_y, X, window_size=metadata["window_size"])

    if "CNN+LSTM" in selected_models:
        cnn_model, scaler_X, scaler_y, metadata = train_cnn_lstm(X_train, y_train)
        cnn_preds = predict_sequence_model(cnn_model, scaler_X, scaler_y, X_train, X_test, y_test, window_size=metadata["window_size"])
        # Only evaluate predictions that correspond to test period
        test_predictions = cnn_preds[cnn_preds.index.isin(y_test.index)]
        results["CNN+LSTM"] = calculate_metrics(y_test.loc[test_predictions.index], test_predictions)
        predictions["CNN+LSTM"] = test_predictions
        next_day_predictions["CNN+LSTM"] = predict_sequence_next_day(cnn_model, scaler_X, scaler_y, X, window_size=metadata["window_size"])

    comparison = build_comparison_table(results)
    return predictions, results, comparison, volatility_series, X_test.index, y_test, next_day_predictions, latest_close


def main() -> None:
    st.set_page_config(page_title="Cryptocurrency Price Prediction", layout="wide")

    # Load available cryptocurrencies
    available_cryptos = load_dynamic_cryptocurrencies()
    if not available_cryptos:
        st.error("Could not load cryptocurrency list. Please check cryptocurrencies.json")
        return
    
    crypto_list = sorted(available_cryptos.keys())
    
    # Cryptocurrency selection
    st.sidebar.header("Cryptocurrency Selection")
    selected_crypto = st.sidebar.selectbox(
        f"Select Cryptocurrency ({len(crypto_list)} available)",
        crypto_list,
        index=0 if "BTC" in crypto_list else 0
    )
    
    # Get ticker and name
    crypto_ticker = available_cryptos.get(selected_crypto, f"{selected_crypto}-USD")
    crypto_name = f"{selected_crypto} ({crypto_ticker})"

    st.title(f"🪙 AI-powered {crypto_name} Price Prediction")
    st.write(
        f"Explore machine learning, time series, and deep learning predictions for {crypto_ticker} with interactive charts and model comparisons."
    )

    df = load_data(selected_crypto)
    if df is None or df.empty:
        st.error(f"Could not load data for {selected_crypto}. Please try another cryptocurrency.")
        return
    
    if f"df_{selected_crypto}" not in st.session_state:
        st.session_state[f"df_{selected_crypto}"] = df
    df = st.session_state[f"df_{selected_crypto}"]

    st.sidebar.header("Data Input")
    with st.sidebar.expander(f"Upload {selected_crypto} data CSV"):
        upload = st.file_uploader("Select CSV file", type=["csv"])
        if upload is not None and st.sidebar.button("Append uploaded data"):
            try:
                uploaded_df = pd.read_csv(upload, parse_dates=["Date"], index_col="Date")
                df = append_user_data(df, uploaded_df)
                st.session_state[f"df_{selected_crypto}"] = df
                st.sidebar.success("Uploaded data appended successfully.")
            except Exception as exc:
                st.sidebar.error(f"Upload error: {exc}")

    with st.sidebar.expander("Add a new data row"):
        with st.form("manual_data_form"):
            new_date = st.date_input("Date", value=df.index.max().date())
            open_price = st.number_input("Open", value=float(df["Open"].iloc[-1]))
            high_price = st.number_input("High", value=float(df["High"].iloc[-1]))
            low_price = st.number_input("Low", value=float(df["Low"].iloc[-1]))
            close_price = st.number_input("Close", value=float(df["Close"].iloc[-1]))
            volume = st.number_input("Volume", value=float(df["Volume"].iloc[-1]))
            add_row = st.form_submit_button("Add data row")
        if add_row:
            try:
                new_row = pd.DataFrame(
                    {
                        "Open": [open_price],
                        "High": [high_price],
                        "Low": [low_price],
                        "Close": [close_price],
                        "Volume": [volume],
                    },
                    index=[pd.to_datetime(new_date)],
                )
                df = append_user_data(df, new_row)
                st.session_state[f"df_{selected_crypto}"] = df
                st.success("New data row added to the dataset.")
            except Exception as exc:
                st.error(f"Could not add row: {exc}")

    if st.sidebar.button("Reset dataset"):
        st.session_state[f"df_{selected_crypto}"] = load_data(selected_crypto)
        st.rerun()

    if st.sidebar.button("Save dataset to CSV"):
        df.to_csv(f"data/processed_{selected_crypto.lower()}.csv")
        st.sidebar.success(f"Dataset saved to data/processed_{selected_crypto.lower()}.csv")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Dataset details")
    st.sidebar.write(f"Rows: {len(df)}")
    st.sidebar.write(f"Date range: {df.index.min().date()} to {df.index.max().date()}")
    st.sidebar.write("Features: Open, High, Low, Close, Volume, SMA, EMA, RSI, MACD")

    st.subheader("Dataset Overview")
    row1, row2, row3, row4 = st.columns(4)
    row1.metric("Rows", len(df))
    row2.metric("Date range", f"{df.index.min().date()} → {df.index.max().date()}")
    row3.metric("Latest Close", f"${df['Close'].iloc[-1]:,.2f} ({crypto_ticker})")
    row4.metric("Average Volume", f"{df['Volume'].mean():,.0f}")

    with st.expander("Show dataset preview"):
        st.dataframe(df.tail(20))

    with st.expander("Dataset statistics"):
        st.write(df.describe().T)

    st.sidebar.markdown("---")
    st.sidebar.header("Model Controls")
    selected_models = st.sidebar.multiselect("Select models to compare", MODEL_OPTIONS, default=["Linear Regression", "ARIMA"])
    if st.sidebar.button("Refresh data"):
        if selected_crypto == "BTC":
            df = prepare_btc_dataset()
        else:
            df = prepare_eth_dataset()
        st.session_state[f"df_{selected_crypto}"] = df
        st.experimental_rerun()

    # Add a button to trigger analysis
    run_analysis = st.sidebar.button("🚀 Run Analysis", type="primary")

    if not selected_models:
        st.info("👆 Select models above and click 'Run Analysis' to start.")
        return

    if not run_analysis:
        st.info("👆 Click 'Run Analysis' to train models and generate predictions.")
        return

    with st.spinner("Training models and generating predictions..."):
        predictions, metrics, comparison, volatility_series, test_index, y_test, next_day_predictions, latest_close = get_predictions(df, selected_models)

    st.subheader("Actual vs Predicted")
    chart_data = pd.DataFrame({"Actual Close": df["Close"].iloc[int(len(df) * 0.8) :]})
    for name, series in predictions.items():
        chart_data[name] = series
    st.line_chart(chart_data.dropna())

    st.subheader("Performance Metrics")
    if metrics:
        metric_df = pd.DataFrame(metrics).T[["MAE", "RMSE", "Accuracy"]]
        metric_df.columns = ["MAE", "RMSE", "Accuracy (%)"]
        # Handle None values in accuracy column
        def format_accuracy(val):
            return f"{val:.2f}" if val is not None else "N/A"
        st.dataframe(metric_df.style.format({
            "MAE": "{:.2f}",
            "RMSE": "{:.2f}",
            "Accuracy (%)": format_accuracy
        }))

    if next_day_predictions:
        st.subheader("Next-Day Predictions")
        next_day_rows = []
        for name, predicted_price in next_day_predictions.items():
            if np.isnan(predicted_price):
                next_day_rows.append(
                    {
                        "Model": name,
                        "Predicted Next Day": "N/A",
                        "Expected Change (%)": "N/A",
                    }
                )
                continue
            change_pct = (predicted_price - latest_close) / latest_close * 100
            next_day_rows.append(
                {
                    "Model": name,
                    "Predicted Next Day": f"${predicted_price:,.2f}",
                    "Expected Change (%)": f"{change_pct:.2f}%",
                }
            )
        st.dataframe(pd.DataFrame(next_day_rows))

    st.markdown("### Trading Signals")
    st.write(
        f"The alert logic compares each model's latest predicted {crypto_ticker} close against the current market close. "
        "A prediction more than 0.5% higher produces a Buy alert, more than 0.5% lower produces a Sell alert, "
        "and otherwise the model recommends Hold."
    )

    latest_close = df["Close"].iloc[-1]
    signals = []
    for name, series in predictions.items():
        if len(series) == 0:
            signals.append({
                "Model": name,
                "Latest Actual": latest_close,
                "Latest Predicted": None,
                "Change (%)": None,
                "Signal": "No prediction",
                "Explanation": "This model did not return a usable prediction for the latest date.",
            })
            continue
        predicted_price = float(series.iloc[-1])
        signal, explanation = get_trade_signal(latest_close, predicted_price)
        change_pct = (predicted_price - latest_close) / latest_close * 100
        signals.append(
            {
                "Model": name,
                "Latest Actual": latest_close,
                "Latest Predicted": predicted_price,
                "Change (%)": change_pct,
                "Signal": signal,
                "Explanation": explanation,
            }
        )
    signal_df = pd.DataFrame(signals)
    st.dataframe(signal_df.style.format({"Latest Actual": "${:,.2f}", "Latest Predicted": "${:,.2f}", "Change (%)": "{:.2f}"}), height=320)

    st.markdown("---")
    st.subheader("Model Comparison")
    def format_accuracy_comparison(val):
        return f"{val:.2f}" if pd.notna(val) else "N/A"
    st.dataframe(comparison.style.format({
        "MAE": "{:.2f}",
        "RMSE": "{:.2f}",
        "Accuracy (%)": format_accuracy_comparison
    }))

    if "GARCH" in selected_models and volatility_series is not None:
        st.markdown("### GARCH Volatility Forecast")
        fig = build_model_comparison_chart(comparison)
        st.pyplot(fig)
        st.line_chart(pd.DataFrame({"Forecasted Volatility": volatility_series, "Actual Volatility": np.abs(df["Close"].pct_change().dropna().iloc[int(len(df["Close"].pct_change().dropna()) * 0.8) :])}).dropna())

    st.markdown("---")
    st.markdown("### Combined Predictions & Volatility Analysis")
    plot_predictions(df["Close"].iloc[int(len(df) * 0.8) :], predictions, volatility_series)
    st.image("outputs/model_comparison.png", caption="Combined prediction comparison chart", use_column_width=True)

    st.markdown("---")
    st.write("Built with Yahoo Finance data, sklearn, xgboost, statsmodels, arch, and TensorFlow.")


if __name__ == "__main__":
    main()
