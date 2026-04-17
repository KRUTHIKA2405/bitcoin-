import streamlit as st
import pandas as pd
import numpy as np
from src.data_pipeline import compute_technical_indicators, download_btc_data, prepare_btc_dataset
from src.models import (
    FEATURE_COLUMNS,
    prepare_features,
    split_train_test,
    train_linear_regression,
    train_random_forest,
    train_xgboost,
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
    "Random Forest",
    "XGBoost",
    "ARIMA",
    "GARCH",
    "LSTM",
    "CNN+LSTM",
]


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv("data/processed_btc.csv", parse_dates=[0], index_col=0)
    except FileNotFoundError:
        df = prepare_btc_dataset()
    return df


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

    if "Random Forest" in selected_models:
        rf_model = train_random_forest(X_train, y_train)
        preds = pd.Series(rf_model.predict(X_test), index=X_test.index)
        predictions["Random Forest"] = preds
        results["Random Forest"] = calculate_metrics(y_test, preds)
        next_day_predictions["Random Forest"] = predict_next_day_ml(rf_model, X.iloc[-1])

    if "XGBoost" in selected_models:
        xgb_model = train_xgboost(X_train, y_train)
        preds = pd.Series(xgb_model.predict(X_test), index=X_test.index)
        predictions["XGBoost"] = preds
        results["XGBoost"] = calculate_metrics(y_test, preds)
        next_day_predictions["XGBoost"] = predict_next_day_ml(xgb_model, X.iloc[-1])

    if "ARIMA" in selected_models:
        arima_preds = arima_rolling_forecast(df["Close"], train_size=0.8)
        predictions["ARIMA"] = arima_preds
        results["ARIMA"] = calculate_metrics(df["Close"].iloc[int(len(df) * 0.8) :], arima_preds)
        next_day_predictions["ARIMA"] = arima_next_day(df["Close"])

    if "GARCH" in selected_models:
        vol_preds, actual_vol = garch_volatility_forecast(df["Close"], train_size=0.8)
        volatility_series = vol_preds
        results["GARCH"] = calculate_metrics(actual_vol, vol_preds)
        next_day_predictions["GARCH"] = float(np.nan)

    if "LSTM" in selected_models:
        lstm_model, scaler_X, scaler_y, metadata = train_lstm(X_train, y_train)
        lstm_preds = predict_sequence_model(lstm_model, scaler_X, scaler_y, X_test, y_test, window_size=metadata["window_size"])
        common_index = lstm_preds.index
        results["LSTM"] = calculate_metrics(y_test.loc[common_index], lstm_preds)
        predictions["LSTM"] = lstm_preds
        next_day_predictions["LSTM"] = predict_sequence_next_day(lstm_model, scaler_X, scaler_y, X, window_size=metadata["window_size"])

    if "CNN+LSTM" in selected_models:
        cnn_model, scaler_X, scaler_y, metadata = train_cnn_lstm(X_train, y_train)
        cnn_preds = predict_sequence_model(cnn_model, scaler_X, scaler_y, X_test, y_test, window_size=metadata["window_size"])
        common_index = cnn_preds.index
        results["CNN+LSTM"] = calculate_metrics(y_test.loc[common_index], cnn_preds)
        predictions["CNN+LSTM"] = cnn_preds
        next_day_predictions["CNN+LSTM"] = predict_sequence_next_day(cnn_model, scaler_X, scaler_y, X, window_size=metadata["window_size"])

    comparison = build_comparison_table(results)
    return predictions, results, comparison, volatility_series, X_test.index, y_test, next_day_predictions, latest_close


def main() -> None:
    st.set_page_config(page_title="Bitcoin Price Prediction", layout="wide")
    st.title("AI-powered Bitcoin Price Prediction")
    st.write(
        "Explore machine learning, time series, and deep learning predictions for BTC-USD with interactive charts and model comparisons."
    )

    df = load_data()
    if "df" not in st.session_state:
        st.session_state.df = df
    df = st.session_state.df

    st.sidebar.header("Data Input")
    with st.sidebar.expander("Upload BTC data CSV"):
        upload = st.file_uploader("Select CSV file", type=["csv"])
        if upload is not None and st.sidebar.button("Append uploaded data"):
            try:
                uploaded_df = pd.read_csv(upload, parse_dates=["Date"], index_col="Date")
                df = append_user_data(df, uploaded_df)
                st.session_state.df = df
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
                st.session_state.df = df
                st.success("New data row added to the dataset.")
            except Exception as exc:
                st.error(f"Could not add row: {exc}")

    if st.sidebar.button("Reset dataset"):
        st.session_state.df = load_data()
        st.experimental_rerun()

    if st.sidebar.button("Save dataset to CSV"):
        df.to_csv("data/processed_btc.csv")
        st.sidebar.success("Dataset saved to data/processed_btc.csv")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Dataset details")
    st.sidebar.write(f"Rows: {len(df)}")
    st.sidebar.write(f"Date range: {df.index.min().date()} to {df.index.max().date()}")
    st.sidebar.write("Features: Open, High, Low, Close, Volume, SMA, EMA, RSI, MACD")

    st.subheader("Dataset Overview")
    row1, row2, row3, row4 = st.columns(4)
    row1.metric("Rows", len(df))
    row2.metric("Date range", f"{df.index.min().date()} → {df.index.max().date()}")
    row3.metric("Latest Close", f"${df['Close'].iloc[-1]:,.2f}")
    row4.metric("Average Volume", f"{df['Volume'].mean():,.0f}")

    with st.expander("Show dataset preview"):
        st.dataframe(df.tail(20))

    with st.expander("Dataset statistics"):
        st.write(df.describe().T)

    st.sidebar.markdown("---")
    st.sidebar.header("Model Controls")
    selected_models = st.sidebar.multiselect("Select models to compare", MODEL_OPTIONS, default=["Linear Regression", "ARIMA", "LSTM"])
    if st.sidebar.button("Refresh data"):
        df = prepare_btc_dataset()
        st.session_state.df = df
        st.experimental_rerun()

    if not selected_models:
        st.warning("Please choose at least one model to display predictions.")
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
        st.dataframe(metric_df.style.format("{:.2f}"))

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
        "The alert logic compares each model's latest predicted BTC close against the current market close. "
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
    st.dataframe(comparison.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "Accuracy (%)": "{:.2f}"}))

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
