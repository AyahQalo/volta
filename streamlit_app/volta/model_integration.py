"""
Model integration layer (NO Streamlit code in this file).

The Streamlit pages only call two functions:

    bundle = load_model()                 # find / load the model, or fall back to demo mode
    result = predict(history, bundle)     # 24-hour price forecast

HOW TO CONNECT YOUR REAL MODEL LATER
1. In demo.ipynb save the final model and the price scaler, for example:
       model.save("models/model.keras")
       joblib.dump(scaler, "models/scaler.joblib")
2. Put both files in the `models/` folder of this project.
3. Restart the app. `load_model()` will find them. Then check `_predict_real()`
   below and adapt it to match your notebook (input shape, extra features, ...).

Nothing here claims that a trained model exists. Until the files above are
present, the app runs in DEMO mode and says so on screen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from volta import config as cfg

MODEL_FILE = cfg.MODEL_DIR / "model.keras"
SCALER_FILE = cfg.MODEL_DIR / "scaler.joblib"


@dataclass
class ModelBundle:
    mode: str                      # "demo" or "real"
    name: str                      # text shown in the UI
    description: str               # one honest sentence about what produces the forecast
    model: Any = None
    scaler: Any = None
    input_window: int = cfg.INPUT_WINDOW
    horizon: int = cfg.HORIZON
    feature_names: list[str] = field(default_factory=lambda: [cfg.PRICE])
    warning: str | None = None


def load_model() -> ModelBundle:
    """Load the real model if its files exist, otherwise return the demo bundle."""
    if MODEL_FILE.exists() and SCALER_FILE.exists():
        try:
            import joblib
            from tensorflow import keras  # imported only when a model file exists

            return ModelBundle(
                mode="real",
                name="Trained model",
                description="Forecast produced by the saved model in the models/ folder.",
                model=keras.models.load_model(MODEL_FILE),
                scaler=joblib.load(SCALER_FILE),
            )
        except Exception as exc:  # keep the app alive, but be transparent
            return _demo(warning=f"Model files were found but could not be loaded: {exc}")
    return _demo()


def _demo(warning: str | None = None) -> ModelBundle:
    return ModelBundle(
        mode="demo",
        name="Demo mode (no trained model connected)",
        description=("Seasonal-naive baseline: each hour is forecast with the price of the "
                     "same hour on the previous day. This is NOT a machine learning model."),
        warning=warning,
    )


def validate_input(history: pd.DataFrame, bundle: ModelBundle) -> None:
    """Raise a clear error if the input is not what the model expects."""
    missing = [c for c in bundle.feature_names if c not in history.columns]
    if missing:
        raise ValueError(f"Missing input columns: {missing}")
    if len(history) != bundle.input_window:
        raise ValueError(f"Expected {bundle.input_window} hourly rows, got {len(history)}.")
    if history[bundle.feature_names].isna().any().any():
        raise ValueError("Input contains missing values.")
    steps = history.index.to_series().diff().dropna()
    if not (steps == pd.Timedelta(hours=1)).all():
        raise ValueError("Input must be strictly hourly with no gaps.")


def predict(history: pd.DataFrame, bundle: ModelBundle) -> pd.DataFrame:
    """
    Forecast the next `bundle.horizon` hours.

    history : DataFrame indexed by hourly UTC timestamps, exactly `input_window` rows,
              ending at the hour before the forecast day starts, containing the
              columns in `bundle.feature_names` (only past information).
    returns : DataFrame indexed by the next 24 hourly timestamps with column "forecast"
              (EUR/MWh).
    """
    validate_input(history, bundle)
    future_index = pd.date_range(history.index[-1] + pd.Timedelta(hours=1),
                                 periods=bundle.horizon, freq="h")
    if bundle.mode == "real":
        values = _predict_real(history, bundle)
    else:
        values = history[cfg.PRICE].to_numpy(float)[-bundle.horizon:]  # same hour, previous day
    return pd.DataFrame({"forecast": values}, index=future_index)


def _predict_real(history: pd.DataFrame, bundle: ModelBundle) -> np.ndarray:
    """
    Starting point for a price-only model. ADAPT THIS to your final notebook:
    - same scaler, same window length, same input shape
    - if the final model has a second input (e.g. residual_load_forecast),
      build it here and pass [past, future] to model.predict
    """
    raw = history[cfg.PRICE].to_numpy(float).reshape(-1, 1)
    scaled = bundle.scaler.transform(raw).reshape(1, bundle.input_window, 1)
    pred_scaled = bundle.model.predict(scaled, verbose=0)
    return bundle.scaler.inverse_transform(pred_scaled.reshape(-1, 1)).ravel()
