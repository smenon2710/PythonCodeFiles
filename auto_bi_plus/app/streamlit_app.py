import os
import sys
import traceback
import warnings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Suppress tokenizer & PyTorch noise
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=RuntimeWarning)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import chardet
from src.modeling.forecast import forecast_with_prophet
from src.modeling.anomaly import detect_anomalies
from src.modeling.cluster import run_kmeans_clustering
from src.narration.llm_narrator import generate_forecast_narrative

st.set_page_config(page_title="AutoBI+ Insights", layout="wide")
st.title("📊 AutoBI+ – ML-powered Dashboard Analysis")

uploaded_file = st.file_uploader("Upload your dashboard CSV", type=["csv"])

if uploaded_file:
    try:
        # Smart encoding detection with fallback
        raw_bytes = uploaded_file.read()
        detected_encoding = chardet.detect(raw_bytes)["encoding"]

        # Handle bad guesses like johab or None
        if detected_encoding is None or detected_encoding.lower() in ["johab", "ascii"]:
            encoding = "latin1"
        else:
            encoding = detected_encoding

        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding=encoding)
        st.success(f"✅ File loaded with encoding: `{encoding}`")

    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()

    st.write("### 📄 Data preview:")
    st.dataframe(df.head())

    # Column suggestions
    date_cols = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not date_cols:
        st.warning("⚠️ No obvious date/time column found.")
        date_col = st.selectbox("📅 Select date column", df.columns)
    else:
        date_col = st.selectbox("📅 Select date column", df.columns, index=df.columns.get_loc(date_cols[0]))

    if not numeric_cols:
        st.error("❌ No numeric columns found.")
        st.stop()
    else:
        value_col = st.selectbox("📈 Select value column", numeric_cols)

    analysis_type = st.radio("Choose analysis type", ["Forecasting", "Anomaly Detection", "Clustering"])

    if analysis_type == "Clustering":
        cluster_features = st.multiselect(
            "🔢 Select features for clustering",
            numeric_cols,
            default=numeric_cols[:2],
            help="Select at least 2 numeric features. Binary or constant features will be ignored."
        )
        n_clusters = st.slider("🎯 Number of clusters", 2, 10, 3)

    if st.button("🚀 Run Analysis"):
        with st.spinner("Crunching the numbers..."):
            try:
                df[date_col] = pd.to_datetime(df[date_col])
            except Exception as e:
                st.error(f"❌ Failed to parse date column: {e}")
                st.stop()

            df = df.dropna(subset=[date_col, value_col])
            df = df.sort_values(date_col)

            if not pd.api.types.is_numeric_dtype(df[value_col]):
                st.error(f"❌ '{value_col}' is not numeric.")
                st.stop()

            # Forecasting
            if analysis_type == "Forecasting":
                try:
                    forecast_df = forecast_with_prophet(df, date_col, value_col)
                    st.subheader("📈 Forecast Output")
                    st.line_chart(forecast_df.set_index("ds")[["yhat"]])

                    narrative = generate_forecast_narrative(value_col, forecast_df)
                    st.markdown("### 🧠 AI-generated Insight")
                    st.success(narrative)

                    csv = forecast_df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download forecast as CSV", csv, f"forecast_{value_col}.csv", "text/csv")
                except Exception as e:
                    st.error(f"❌ Forecasting failed:\n{e}")
                    st.code(traceback.format_exc())

            # Anomaly Detection
            elif analysis_type == "Anomaly Detection":
                try:
                    df.set_index(date_col, inplace=True)
                    result_df = detect_anomalies(df, value_col)

                    st.subheader("🚨 Anomaly Detection Result")
                    st.dataframe(result_df[result_df["is_anomaly"] == 1])

                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.plot(result_df.index, result_df[value_col], label="Value", linewidth=2)
                    ax.scatter(
                        result_df[result_df["is_anomaly"] == 1].index,
                        result_df[result_df["is_anomaly"] == 1][value_col],
                        color="red", label="Anomaly", zorder=5
                    )
                    ax.set_title("Anomaly Detection")
                    ax.set_xlabel("Date")
                    ax.set_ylabel(value_col)
                    ax.legend()
                    st.pyplot(fig)

                    st.markdown("### 🔍 SHAP Impact")
                    top_anomalies = result_df[result_df["is_anomaly"] == 1].nlargest(5, "shap_value")
                    fig2, ax2 = plt.subplots()
                    ax2.bar(top_anomalies.index.astype(str), top_anomalies["shap_value"])
                    ax2.set_ylabel("SHAP Value")
                    ax2.set_title("Top Anomalies by SHAP")
                    st.pyplot(fig2)

                    csv = result_df.reset_index().to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download anomaly report", csv, f"anomaly_{value_col}.csv", "text/csv")

                except Exception as e:
                    st.error(f"❌ Anomaly Detection failed:\n{e}")
                    st.code(traceback.format_exc())

            # Clustering
            elif analysis_type == "Clustering":
                if len(cluster_features) < 2:
                    st.warning("Please select at least 2 features for clustering.")
                    st.stop()

                if len(df) < n_clusters:
                    st.warning("Not enough rows for selected number of clusters.")
                    st.stop()

                try:
                    clustered_df, model = run_kmeans_clustering(df, cluster_features, n_clusters)

                    st.subheader("🧠 Clustering Result")
                    st.dataframe(clustered_df[cluster_features + ["cluster"]].head())

                    st.markdown("### 📋 Cluster Summary")
                    st.dataframe(clustered_df.groupby("cluster")[cluster_features].mean().round(2))

                    csv = clustered_df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download clustered data", csv, "clusters.csv", "text/csv")

                except Exception as e:
                    st.error(f"❌ Clustering failed:\n{e}")
                    st.code(traceback.format_exc())
