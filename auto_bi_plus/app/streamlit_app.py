import os
import sys
import traceback
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=RuntimeWarning)

import streamlit as st
import pandas as pd
import chardet
import matplotlib.pyplot as plt

from src.modeling.forecast import forecast_with_prophet
from src.modeling.anomaly import detect_anomalies
from src.modeling.cluster import run_kmeans_clustering
from src.modeling.regression import run_regression_forecast
from src.narration.llm_narrator import generate_forecast_narrative
from src.narration.insight_engine import (
    summarize_forecast,
    summarize_anomalies,
    summarize_clusters,
    summarize_clusters_with_llm,
)

st.set_page_config(page_title="AutoBI+ Insights", layout="wide")
st.title("🤖 AutoBI+ – Smart Insight Engine")

def detect_datetime_columns(df):
    datetime_cols = []
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().sum() / len(df) > 0.6:
                datetime_cols.append(col)
        except Exception:
            continue
    return datetime_cols

uploaded_file = st.file_uploader("📁 Upload your data file", type=["csv"])

if uploaded_file:
    try:
        raw_bytes = uploaded_file.read()
        detected_encoding = chardet.detect(raw_bytes)["encoding"]
        encoding = "latin1" if detected_encoding is None or detected_encoding.lower() in ["johab", "ascii"] else detected_encoding
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding=encoding)
        st.success(f"✅ File loaded with encoding: `{encoding}`")
    except Exception as e:
        st.error(f"❌ File load failed: {e}")
        st.stop()

    st.write("### 🔍 Data Preview")
    st.dataframe(df.head())

    # Auto-detect fields
    date_cols = detect_datetime_columns(df)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    has_date = len(date_cols) > 0
    has_target = len(numeric_cols) >= 2

    task_type = (
        "Time Series Forecasting" if has_date else
        "Regression Forecasting" if has_target else
        "Clustering / Summarization"
    )
    st.markdown(f"### 🤔 Suggested Insight Path: **{task_type}**")

    analysis_type = st.radio("What would you like to do?", [
        "📈 Forecast values",
        "🚨 Detect anomalies",
        "🧠 Cluster and summarize",
    ])

    date_col = st.selectbox("📅 Date column (if any)", date_cols) if has_date else None
    value_col = st.selectbox("🎯 Value to forecast", numeric_cols) if numeric_cols else None

    if analysis_type == "📈 Forecast values":
        if value_col is None:
            st.warning("⚠️ Please select a numeric column for forecasting.")
        elif has_date and date_col:
            try:
                forecast_df = forecast_with_prophet(df.copy(), date_col, value_col)
                if 'ds' in forecast_df.columns and 'yhat' in forecast_df.columns:
                    st.line_chart(forecast_df.set_index("ds")[["yhat"]])
                st.success(generate_forecast_narrative(value_col, forecast_df))
                st.info(summarize_forecast(value_col, forecast_df))
            except Exception as e:
                st.error(f"❌ Time series forecast failed: {e}")
                st.code(traceback.format_exc())
        else:
            try:
                df = df.dropna(subset=[value_col])
                result_df = run_regression_forecast(df, value_col)
                st.dataframe(result_df.head())
                st.success("✅ Forecast generated using regression (XGBoost).")
                st.info("📌 Based on available numeric features.")
            except Exception as e:
                st.error(f"❌ Regression forecast failed: {e}")
                st.code(traceback.format_exc())

    elif analysis_type == "🚨 Detect anomalies":
        if not has_date or date_col is None:
            st.warning("⚠️ Anomaly detection requires a valid datetime column.")
        elif value_col is None:
            st.warning("⚠️ Please select a value column to check for anomalies.")
        else:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                df.set_index(date_col, inplace=True)
                result_df = detect_anomalies(df, value_col)
                st.dataframe(result_df[result_df["is_anomaly"] == 1])
                st.info(summarize_anomalies(result_df, value_col))
            except Exception as e:
                st.error(f"❌ Anomaly detection failed: {e}")
                st.code(traceback.format_exc())

    elif analysis_type == "🧠 Cluster and summarize":
        features = st.multiselect("📊 Select features to cluster", numeric_cols, default=numeric_cols[:2])
        n_clusters = st.slider("📌 Number of clusters", 2, 10, 3)

        if len(features) < 2:
            st.warning("⚠️ Please select at least 2 features for clustering.")
        else:
            try:
                clustered_df, model = run_kmeans_clustering(df, features, n_clusters)
                st.dataframe(clustered_df[features + ["cluster"]].head())
                cluster_summary_df = clustered_df.groupby("cluster")[features].mean().round(2)
                st.dataframe(cluster_summary_df)
                st.info(summarize_clusters(clustered_df))
                llm_summary = summarize_clusters_with_llm(cluster_summary_df)
                st.markdown("### 🤖 LLM Insight Summary")
                st.success(llm_summary)
            except Exception as e:
                st.error(f"❌ Clustering failed: {e}")
                st.code(traceback.format_exc())
