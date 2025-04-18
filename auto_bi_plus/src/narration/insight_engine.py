from typing import Optional
import numpy as np
from transformers import pipeline

# Initialize lightweight open-source summarizer
summarizer = pipeline("text2text-generation", model="google/flan-t5-base", max_length=512)


def summarize_forecast(kpi: str, df) -> str:
    if "yhat" not in df.columns:
        return "Forecast summary unavailable."

    trend = df["yhat"].diff().mean()
    pct_change = 100 * (df["yhat"].iloc[-1] - df["yhat"].iloc[0]) / df["yhat"].iloc[0]
    direction = "increase 📈" if trend > 0 else "decrease 📉" if trend < 0 else "stay stable"

    return (
        f"🔮 The forecast for **{kpi}** is expected to {direction} over the next period.\n\n"
        f"- Projected change: **{pct_change:.2f}%** from start to end\n"
        f"- Trend appears to be {'upward' if trend > 0 else 'downward' if trend < 0 else 'flat'}"
    )


def summarize_anomalies(df, value_col: str) -> str:
    total = len(df)
    count = df["is_anomaly"].sum()
    anomaly_pct = 100 * count / total

    top_anomalies = df[df["is_anomaly"] == 1].nlargest(3, "shap_value")
    if top_anomalies.empty:
        return "No significant anomalies detected in the selected metric."

    lines = [
        f"🚨 Detected **{count} anomalies** out of {total} records (**{anomaly_pct:.1f}%**) in `{value_col}`.",
        "",
        "Top anomalies by SHAP score:"
    ]
    for i, row in top_anomalies.iterrows():
        lines.append(
            f"- On `{i}`: Value = {row[value_col]}, SHAP = {row['shap_value']:.3f}"
        )

    return "\n".join(lines)


def summarize_clusters(df, cluster_col: str = "cluster") -> str:
    if cluster_col not in df.columns:
        return "No cluster column found."

    cluster_counts = df[cluster_col].value_counts().sort_index()
    summary = [f"🧠 Detected **{len(cluster_counts)} clusters**:"]

    for c, count in cluster_counts.items():
        summary.append(f"- Cluster {c}: {count} rows")

    return "\n".join(summary)


def summarize_clusters_with_llm(cluster_summary_df):
    """
    Generate a domain-agnostic summary of clusters using an LLM.
    Accepts a DataFrame of aggregated cluster stats (e.g., mean feature values).
    """
    prompt = (
        "You are an AI data analyst.\n"
        "The following table shows average values for several clusters from an unknown dataset.\n\n"
        f"{cluster_summary_df.to_markdown(index=True)}\n\n"
        "Please describe how these clusters differ. Focus on patterns and trends in the numbers. "
        "Avoid domain-specific language or assumptions."
    )

    result = summarizer(prompt)[0]["generated_text"]
    return result
