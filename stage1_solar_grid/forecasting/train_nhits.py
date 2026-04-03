"""
Sprint 2: Irradiance Forecasting with NeuralForecast (NHITS)
=============================================================
Trains an NHITS model on historical GHI data from Fremont, CA.
Produces 24-hour ahead forecasts with confidence intervals.

Input:  stage1_solar_grid/data/raw/weather_fremont.csv
Output: stage1_solar_grid/data/processed/forecast_output.csv
        stage1_solar_grid/forecasting/nhits_model/  (saved model)
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from neuralforecast import NeuralForecast
from neuralforecast.models import NHITS
from neuralforecast.losses.pytorch import MAE

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_PATH       = Path(__file__).parent.parent / "data" / "raw" / "weather_fremont.csv"
PROCESSED_DIR  = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR      = Path(__file__).parent / "nhits_model"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
HORIZON     = 24    # forecast 24 hours ahead
INPUT_SIZE  = 72    # use last 72 hours as input (3 days of context)
TRAIN_RATIO = 0.85  # 85% train, 15% validation
VAL_SIZE    = 24 * 7  # 7 days used internally by NeuralForecast for early stopping

# ── Load and prepare data ─────────────────────────────────────────────────────
def prepare_data(path):
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)

    df_nf = pd.DataFrame({
        "unique_id" : "fremont_ghi",
        "ds"        : df.index,
        "y"         : df["ghi_wm2"],
        "temp_c"    : df["temp_c"],
        "cloud_pct" : df["cloud_pct"],
    }).reset_index(drop=True)

    daytime = df_nf[df_nf["y"] > 0]
    print(f"Total rows     : {len(df_nf)}")
    print(f"Daytime rows   : {len(daytime)}")
    print(f"Max GHI (W/m²) : {df_nf['y'].max():.1f}")
    print(f"Mean GHI (W/m²): {daytime['y'].mean():.1f}  (daytime only)")

    return df_nf


# ── Train/validation split ────────────────────────────────────────────────────
def split_data(df, ratio):
    n = len(df)
    split = int(n * ratio)
    train = df.iloc[:split]
    val   = df.iloc[split:]
    print(f"\nTrain: {len(train)} rows  ({train['ds'].iloc[0].date()} → {train['ds'].iloc[-1].date()})")
    print(f"Val  : {len(val)} rows  ({val['ds'].iloc[0].date()} → {val['ds'].iloc[-1].date()})")
    return train, val


# ── Build and train model ─────────────────────────────────────────────────────
def train_model(train_df):
    models = [
        NHITS(
            h                         = HORIZON,
            input_size                = INPUT_SIZE,
            loss                      = MAE(),
            max_steps                 = 500,
            val_check_steps           = 50,
            early_stop_patience_steps = 5,
        )
    ]

    nf = NeuralForecast(models=models, freq="h")

    print("\nTraining NHITS model...")
    # val_size tells NeuralForecast how many rows at the end of train_df
    # to hold out for internal early stopping validation
    nf.fit(df=train_df, val_size=VAL_SIZE)
    print("Training complete.")

    return nf


# ── Generate forecast ─────────────────────────────────────────────────────────
def generate_forecast(nf, df):
    forecast = nf.predict(df=df)
    print(f"\nForecast shape: {forecast.shape}")
    print(forecast.head())
    return forecast


# ── Plot results ──────────────────────────────────────────────────────────────
def plot_results(df, forecast, n_days=7):
    fig, ax = plt.subplots(figsize=(14, 5))

    last = df.tail(n_days * 24)
    ax.plot(last["ds"], last["y"], label="Actual GHI", color="#EF9F27", linewidth=1.5)
    ax.plot(forecast["ds"], forecast["NHITS"], label="Forecast",
            color="#185FA5", linewidth=1.5, linestyle="--")

    ax.set_title("Solar Irradiance Forecast — Fremont CA (NHITS)")
    ax.set_xlabel("Time")
    ax.set_ylabel("GHI (W/m²)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    plot_path = PROCESSED_DIR / "forecast_plot.png"
    plt.savefig(plot_path, dpi=150)
    print(f"\nPlot saved to: {plot_path}")
    plt.show()


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = prepare_data(RAW_PATH)
    train_df, val_df = split_data(df, TRAIN_RATIO)
    nf = train_model(train_df)

    forecast = generate_forecast(nf, train_df)

    out_path = PROCESSED_DIR / "forecast_output.csv"
    forecast.to_csv(out_path, index=False)
    print(f"Forecast saved to: {out_path}")

    plot_results(train_df, forecast)
