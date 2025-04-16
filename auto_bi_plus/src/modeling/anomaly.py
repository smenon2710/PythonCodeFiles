import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import shap

def detect_anomalies(df: pd.DataFrame, value_col: str, contamination: float = 0.05):
    df = df.copy()
    df = df[[value_col]].dropna()
    df = df.sort_index()

    scaler = StandardScaler()
    df["value_scaled"] = scaler.fit_transform(df[[value_col]])

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(df[["value_scaled"]])

    df["anomaly_score"] = model.decision_function(df[["value_scaled"]])
    df["is_anomaly"] = model.predict(df[["value_scaled"]]).astype(int)
    df["is_anomaly"] = df["is_anomaly"].map({1: 0, -1: 1})

    # SHAP explanation (compatible version)
    explainer = shap.Explainer(model.predict, df[["value_scaled"]])
    shap_values = explainer(df[["value_scaled"]])
    df["shap_value"] = shap_values.values.flatten()

    return df
