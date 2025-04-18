# auto_bi_plus/src/modeling/forecast.py

import pandas as pd
from prophet import Prophet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# auto_bi_plus/src/modeling/forecast.py




def forecast_with_prophet(df, date_col, value_col, periods=30):
    try:
        # Clean and parse the datetime column
        df[date_col] = df[date_col].astype(str)

        # If values contain ranges like "Aug 17, 2022 07:00 PM - Aug 17, 2022 08:00 PM"
        if df[date_col].str.contains(" - ").any():
            df[date_col] = df[date_col].str.extract(r'^(.*?)(?:\s*-\s*.*)?')[0]

        # Try to convert to datetime
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

        # Drop rows with unparseable datetimes or missing values
        df = df.dropna(subset=[date_col, value_col])

        # Rename columns for Prophet
        prophet_df = df[[date_col, value_col]].rename(columns={date_col: "ds", value_col: "y"})

        # Sort by datetime
        prophet_df = prophet_df.sort_values("ds")

        # Fit the model
        model = Prophet()
        model.fit(prophet_df)

        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        return forecast

    except Exception as e:
        raise RuntimeError(f"Prophet forecasting failed: {e}")



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
