import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Dense, Dropout, Flatten, LSTM
from tensorflow.keras.optimizers import Adam

FEATURE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "SMA10",
    "SMA30",
    "EMA12",
    "EMA26",
    "RSI14",
    "MACD",
]

def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    data = df.copy()
    data["Target"] = data["Close"].shift(-1)
    data = data.dropna()
    X = data[FEATURE_COLUMNS]
    y = data["Target"]
    return X, y

def split_train_test(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> tuple:
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    return X_train, X_test, y_train, y_test

def train_linear_regression(X_train: pd.DataFrame, y_train: pd.Series) -> LinearRegression:
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train: pd.DataFrame, y_train: pd.Series) -> XGBRegressor:
    model = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    model.fit(X_train, y_train)
    return model

def arima_rolling_forecast(series: pd.Series, train_size: float = 0.8, order: tuple = (5, 1, 0)) -> pd.Series:
    """
    Implements a rolling forecast for ARIMA to fix alignment issues.
    The model is updated with the latest actual observation at each step.
    """
    split_idx = int(len(series) * train_size)
    train = series.iloc[:split_idx].copy()
    test = series.iloc[split_idx:].copy()
    
    predictions = []
    # Using a list for history for better performance during iteration
    history = [x for x in train]

    for t in range(len(test)):
        model = ARIMA(history, order=order)
        model_fit = model.fit()
        
        # Forecast the next single step
        output = model_fit.forecast()
        yhat = output[0]
        predictions.append(yhat)
        
        # Add the true observation to history for the next step
        obs = test.iloc[t]
        history.append(obs)
        
    return pd.Series(predictions, index=test.index)

def arima_next_day(series: pd.Series, order: tuple = (5, 1, 0)) -> float:
    model = ARIMA(series, order=order)
    fitted = model.fit()
    forecast = fitted.forecast(steps=1)
    return float(forecast.iloc[0])

def predict_next_day_ml(model, last_row: pd.Series) -> float:
    return float(model.predict(last_row.to_frame().T)[0])

def predict_sequence_next_day(model, scaler_X: MinMaxScaler, scaler_y: MinMaxScaler, X_data: pd.DataFrame, window_size: int = 60) -> float:
    if len(X_data) < window_size:
        return float(np.nan)
    X_scaled = scaler_X.transform(X_data)
    seq = X_scaled[-window_size:].reshape(1, window_size, X_scaled.shape[1])
    predictions = model.predict(seq, verbose=0)
    return float(scaler_y.inverse_transform(predictions.reshape(-1, 1))[0, 0])

def garch_volatility_forecast(series: pd.Series, train_size: float = 0.8) -> tuple[pd.Series, pd.Series]:
    returns = 100 * series.pct_change().dropna()
    split_idx = int(len(returns) * train_size)
    train = returns.iloc[:split_idx].copy()
    test = returns.iloc[split_idx:].copy()
    history = train.copy()
    vol_forecasts = []
    for timestamp, actual in test.items():
        model = arch_model(history, vol="Garch", p=1, q=1, dist="normal")
        fitted = model.fit(disp="off")
        forecast = fitted.forecast(horizon=1).variance.iloc[-1, 0]
        vol_forecasts.append(np.sqrt(forecast))
        history = pd.concat([history, pd.Series({timestamp: actual})])
    predicted_volatility = pd.Series(vol_forecasts, index=test.index)
    actual_volatility = test.abs()
    return predicted_volatility, actual_volatility

def _build_sequence_data(
    X: np.ndarray,
    y: np.ndarray,
    window_size: int = 60,
) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for i in range(window_size, len(X)):
        xs.append(X[i - window_size : i])
        ys.append(y[i])
    return np.array(xs), np.array(ys)

def train_lstm(X_train: pd.DataFrame, y_train: pd.Series, window_size: int = 60) -> tuple[Sequential, MinMaxScaler, MinMaxScaler, dict]:
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X_train)
    y_scaled = scaler_y.fit_transform(y_train.to_frame())
    X_seq, y_seq = _build_sequence_data(X_scaled, y_scaled.ravel(), window_size)
    model = Sequential([
        LSTM(64, input_shape=(X_seq.shape[1], X_seq.shape[2]), return_sequences=False),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
    model.fit(X_seq, y_seq, epochs=10, batch_size=32, verbose=0)
    metadata = {"window_size": window_size}
    return model, scaler_X, scaler_y, metadata

def train_cnn_lstm(X_train: pd.DataFrame, y_train: pd.Series, window_size: int = 60) -> tuple[Sequential, MinMaxScaler, MinMaxScaler, dict]:
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(X_train)
    y_scaled = scaler_y.fit_transform(y_train.to_frame())
    X_seq, y_seq = _build_sequence_data(X_scaled, y_scaled.ravel(), window_size)
    model = Sequential([
        Conv1D(filters=32, kernel_size=3, activation="relu", input_shape=(X_seq.shape[1], X_seq.shape[2])),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dense(32, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
    model.fit(X_seq, y_seq, epochs=10, batch_size=32, verbose=0)
    metadata = {"window_size": window_size}
    return model, scaler_X, scaler_y, metadata

def predict_sequence_model(
    model: Sequential,
    scaler_X: MinMaxScaler,
    scaler_y: MinMaxScaler,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    window_size: int = 60,
) -> pd.Series:
    # Combine train and test data for scaling
    X_combined = pd.concat([X_train, X_test])
    X_scaled = scaler_X.transform(X_combined)

    # Build sequences starting from the beginning of test data
    # Use the last window_size points from training + test data
    X_seq = []
    start_idx = len(X_train) - window_size

    for i in range(window_size, len(X_scaled)):
        X_seq.append(X_scaled[i - window_size : i])

    X_seq = np.array(X_seq)
    predictions_scaled = model.predict(X_seq, verbose=0)
    predictions = scaler_y.inverse_transform(predictions_scaled).ravel()

    # Return predictions aligned with test set
    output_index = X_combined.index[window_size:]
    return pd.Series(predictions, index=output_index)