VOLTA — Project Decisions

Project Scope

* Target: price actual (EUR/MWh).
* Forecast horizon: Next 24 hours, with one prediction per hour.
* Forecast frequency: One 24-hour forecast issued daily at 00:00 UTC.
* Input window: Previous 168 hours (7 days).
* Geographic scope: Spain.

Dataset

* Source: Kaggle — Energy consumption, generation, prices and weather in Spain.
* Time period: 2015–2018.
* Frequency: Hourly.

Data Splitting

* Training: 2015–2016.
* Validation: 2017.
* Testing: 2018.
* Chronological splitting only, without random shuffling.
* Scalers are fitted using training data only.

Models and Evaluation

* Models: LSTM and GRU.
* Baselines: Last Value, Lag-24, and Lag-168.
* Primary metric: MAE (EUR/MWh).
* Secondary metric: RMSE (EUR/MWh).
* Compare models on identical validation timestamps.

Feature Engineering

* Start with historical price actual.
* Add is_weekend using Spain’s local calendar.
* Future calendar information is allowed because it is known in advance.
* Do not use future actual measurements as inputs.
* Exclude price day ahead from the input features based on instructor guidance about data leakage.

Model Improvement

* Compare the original models with the weekend-enhanced models.
* Tune selected hyperparameters one at a time.
* Select the best model using validation results.
* Evaluate the selected final model on the untouched 2018 test set.

Final Deliverables

* Reproducible modeling notebook.
* Saved trained model and preprocessing artifacts.
* Prediction notebook that loads the saved model without retraining.
* Interactive visualization of hourly forecasts.
* Final presentation with model comparisons, results, and limitations.
