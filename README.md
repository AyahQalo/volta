# VOLTA — Electricity price forecasting for Spain

**Idea:** forecast short-term electricity values (price first; demand and generation next) and turn the forecasts into an hour-by-hour *energy-system pressure* signal (Balanced / Elevated / High Stress).

**Data:** Kaggle "Energy consumption, generation, prices and weather in Spain" — hourly, 2015–2018.
Download `energy_dataset.csv` and `weather_features.csv` and put them in `data/raw/` (they are not stored in Git).

## Structure
```
data/raw/          original files (not committed)
data/processed/    cleaned / feature files shared by the team
notebooks/         working notebooks (add your name when several people edit the same topic)
src/               shared helper code
results/           saved plots, metrics, predictions
DECISIONS.md       agreed decisions (read this first)
```

## Team rules
- One shared train / validation / test split (see DECISIONS.md). Never shuffle time order.
- One main metric for comparing models (MAE). Same dates and horizon for every model.
- Only use features that are known at forecast time.
- Keep Git simple: pull before you work, push often. Don't edit the same notebook at the same time.
- Experiment first, clean later. One clean `notebooks/demo.ipynb` at the end.
