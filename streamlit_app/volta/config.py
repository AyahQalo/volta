"""Central settings for the VOLTA app. Edit values here, not inside the pages."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "volta_clean_hourly.csv"
MODEL_DIR = ROOT / "models"

# --- Column names (exactly as they appear in volta_clean_hourly.csv) ---
TIME = "time"
PRICE = "price actual"
PRICE_DA = "price day ahead"
LOAD = "total load actual"
LOAD_FC = "total load forecast"
WIND_FC = "forecast wind onshore day ahead"
SOLAR_FC = "forecast solar day ahead"
RENEWABLE = "renewable_total"
FOSSIL = "fossil_total"
RESIDUAL = "residual_load"          # derived in volta/data.py

# --- Forecasting setup (must match demo.ipynb) ---
INPUT_WINDOW = 168   # past hours given to the model
HORIZON = 24         # hours predicted (one day, issued at 00:00 UTC)
EXCLUDED_YEAR = 2018  # kept out of the modeling experiments

CITIES = ["barcelona", "bilbao", "madrid", "seville", "valencia"]

# Generation sources grouped for the mix chart
GEN_GROUPS = {
    "Gas": ["generation fossil gas"],
    "Hard coal": ["generation fossil hard coal"],
    "Brown coal": ["generation fossil brown coal/lignite"],
    "Oil": ["generation fossil oil"],
    "Nuclear": ["generation nuclear"],
    "Hydro": ["generation hydro run-of-river and poundage",
              "generation hydro water reservoir"],
    "Wind": ["generation wind onshore"],
    "Solar": ["generation solar"],
    "Biomass & other": ["generation biomass", "generation waste",
                        "generation other", "generation other renewable"],
}

# Colour palette (used by CSS and by every chart)
C = {
    "navy": "#0F2A4A", "blue": "#2F6FED", "sky": "#6EA8FE", "yellow": "#F5B301",
    "teal": "#10A38C", "red": "#E5484D", "violet": "#7C5CFC", "slate": "#6B7A90",
    "grid": "#E5EAF2", "bg": "#F5F7FB", "text": "#14213D",
}
GEN_COLORS = {
    "Gas": "#E5484D", "Hard coal": "#4B5563", "Brown coal": "#92643A", "Oil": "#9CA3AF",
    "Nuclear": "#7C5CFC", "Hydro": "#2F6FED", "Wind": "#10A38C", "Solar": "#F5B301",
    "Biomass & other": "#84CC16",
}
