import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


sns.set_style("darkgrid")


def plot_predictions(actual: pd.Series, predictions: dict, volatility: pd.Series | None = None, output_path: str = "outputs/model_comparison.png") -> None:
    plt.figure(figsize=(14, 8))
    plt.plot(actual.index, actual, label="Actual Close", color="#1f77b4", linewidth=2)
    for name, series in predictions.items():
        plt.plot(series.index, series, label=name, alpha=0.8)

    if volatility is not None and not volatility.empty:
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax2.plot(volatility.index, volatility, label="GARCH Volatility", color="#ff7f0e", linestyle="--", alpha=0.9)
        ax2.set_ylabel("Volatility", color="#ff7f0e")
        ax2.tick_params(axis="y", labelcolor="#ff7f0e")

    plt.xlabel("Date")
    plt.ylabel("BTC-USD Close Price")
    plt.title("Bitcoin Price Predictions vs Actual")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def build_model_comparison_chart(results: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    results_sorted = results.sort_values(by="RMSE")
    sns.barplot(x="RMSE", y="Model", data=results_sorted, palette="viridis", ax=ax)
    ax.set_title("Model Comparison by RMSE")
    ax.set_xlabel("RMSE")
    ax.set_ylabel("Model")
    plt.tight_layout()
    return fig
