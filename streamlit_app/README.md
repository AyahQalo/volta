# VOLTA – Streamlit App

An interactive, English-language app for the VOLTA energy forecasting project.
It lets you explore the dataset and shows how a 24-hour price forecast will be presented.

**Important:** no trained model is connected yet. The Forecast page runs in clearly labelled
**demo mode** (a simple "same hour yesterday" baseline). Final results belong in `demo.ipynb`.

## 1. Folder structure

```
volta_app/
├─ app.py                      Landing page (start here)
├─ requirements.txt            Libraries to install
├─ README.md                   This file
├─ .streamlit/config.toml      Colours and theme
├─ data/
│  └─ volta_clean_hourly.csv   <-- YOU copy your dataset here
├─ models/                     <-- the real model + scaler go here later
├─ pages/
│  ├─ 1_Dashboard.py           Charts and KPIs
│  ├─ 2_Data_Explorer.py       Table, column catalog, data quality
│  ├─ 3_Forecast_Demo.py       24-hour forecast page (demo mode for now)
│  └─ 4_About.py               Goal, status, glossary
└─ volta/
   ├─ config.py                Column names, colours, window sizes (safe to edit)
   ├─ data.py                  Loads the CSV, quality checks, sidebar filters
   ├─ charts.py                All Plotly charts
   ├─ theme.py                 CSS, KPI cards, helpers
   └─ model_integration.py     load_model() and predict() - the ONLY place for model code
```

## 2. Setup on Windows (VS Code)

1. Install Python 3.10 or newer from python.org (tick **Add Python to PATH**).
2. Open the `volta_app` folder in VS Code (**File > Open Folder**).
3. Open the terminal (**Terminal > New Terminal**) and run:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell blocks activation, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

4. Copy `volta_clean_hourly.csv` into the `data` folder.

## 3. Run the app

```
streamlit run app.py
```

The browser opens at http://localhost:8501. Stop the app with `Ctrl + C` in the terminal.

## 4. Which files can I edit?

| File | Edit? |
|---|---|
| `volta/config.py` | Yes. Column names, colours, window sizes |
| `volta/model_integration.py` | Yes. This is where the real model is connected |
| `pages/*.py`, `volta/charts.py`, `volta/theme.py` | Only if you want to change the design |
| Your notebooks and `volta_clean_hourly.csv` | Keep unchanged |

## 5. Connect the real model later

1. In `demo.ipynb`, save the final model and the scaler:
   ```python
   model.save("models/model.keras")
   import joblib; joblib.dump(scaler, "models/scaler.joblib")
   ```
2. Install what the model needs: `pip install tensorflow scikit-learn joblib`.
3. Open `volta/model_integration.py` and check `_predict_real()`. Make it match the notebook
   (same scaler, window length, input shape and any extra inputs such as residual load).
4. Restart the app. The Forecast page switches from demo mode to the model automatically.

If you use another format (for example `.h5` or a PyTorch file), only `load_model()` and
`_predict_real()` need to change. The pages stay the same.

## 6. Troubleshooting

- **"Dataset not found"**: the CSV must be at `data/volta_clean_hourly.csv`.
- **`streamlit` is not recognised**: activate the virtual environment first (`.venv\Scripts\activate`).
- **Dark sidebar colours missing**: update Streamlit with `pip install -U streamlit`.
