
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def run_regression_forecast(df: pd.DataFrame, target_col: str, test_size: float = 0.2):
    """
    Performs regression-based forecasting using XGBoost.
    Assumes target_col is the column to predict, all other numeric columns are features.
    """
    features = df.select_dtypes(include="number").drop(columns=[target_col], errors="ignore")
    if features.empty:
        raise ValueError("No numeric features available for regression.")

    X = features
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    result_df = X_test.copy()
    result_df["actual"] = y_test
    result_df["predicted"] = y_pred
    result_df["error"] = y_test - y_pred

    rmse = mean_squared_error(y_test, y_pred, squared=False)
    result_df.attrs["rmse"] = rmse

    return result_df.reset_index()
