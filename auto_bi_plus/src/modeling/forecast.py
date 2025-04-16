# auto_bi_plus/src/modeling/forecast.py

import pandas as pd
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# auto_bi_plus/src/modeling/forecast.py

def forecast_with_prophet(df: pd.DataFrame, date_col: str, value_col: str, periods: int = 30):
    df = df[[date_col, value_col]].copy()
    df = df.rename(columns={date_col: "ds", value_col: "y"})

    # Clean data
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.dropna(subset=["ds", "y"])
    df = df.sort_values("ds").drop_duplicates("ds")
    
    if len(df) < 2:
        raise ValueError("Not enough data points for forecasting.")
    
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def forecast_with_xgboost(df: pd.DataFrame, date_col: str, value_col: str):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    # Feature engineering: extract time-based features
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['day'] = df[date_col].dt.day
    df['month'] = df[date_col].dt.month
    df['year'] = df[date_col].dt.year

    X = df[['dayofweek', 'day', 'month', 'year']]
    y = df[value_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    model = XGBRegressor()
    model.fit(X_train, y_train)
