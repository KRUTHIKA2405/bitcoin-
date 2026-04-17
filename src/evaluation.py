import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> dict:
    actual, predicted = actual.align(predicted, join="inner")
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = np.mean(np.abs((actual - predicted) / np.clip(np.abs(actual), 1e-8, None))) * 100
    accuracy = max(0.0, 100.0 - mape)
    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "MAPE": float(mape),
        "Accuracy": float(accuracy),
    }


def build_comparison_table(results: dict) -> pd.DataFrame:
    rows = []
    for model_name, metrics in results.items():
        row = {
            "Model": model_name,
            "MAE": metrics.get("MAE", None),
            "RMSE": metrics.get("RMSE", None),
            "Accuracy (%)": metrics.get("Accuracy", None),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    # Sort by RMSE, but put models with None accuracy at the bottom
    df["sort_key"] = df["RMSE"].fillna(float('inf'))
    df = df.sort_values(by="sort_key").drop(columns="sort_key")
    return df
