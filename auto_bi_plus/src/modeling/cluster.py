import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def generate_features(df: pd.DataFrame, numeric_cols: list):
    """
    Generate extra clustering features like rolling mean to enrich dimensionality.
    """
    df = df.copy()

    for col in numeric_cols:
        if df[col].nunique() > 5:
            df[f"{col}_rolling_mean"] = df[col].rolling(window=5).mean().bfill()

    return df

def run_kmeans_clustering(df: pd.DataFrame, feature_cols: list, n_clusters: int = 3):
    """
    Cluster rows in a dataframe based on selected numeric features.

    Args:
        df: Original DataFrame
        feature_cols: List of numeric columns to use for clustering
        n_clusters: Number of clusters to form

    Returns:
        clustered_df: DataFrame with assigned cluster labels
        model: Trained KMeans model
    """
    # Remove binary or constant features
    usable_cols = [
        col for col in feature_cols
        if df[col].nunique() > 2 and pd.api.types.is_numeric_dtype(df[col])
    ]

    if len(usable_cols) < 2:
        # Auto-generate additional features if needed
        df = generate_features(df, feature_cols)
        extra_cols = [c for c in df.columns if "_rolling_mean" in c]
        usable_cols.extend(extra_cols)

    data = df[usable_cols].dropna()

    if len(data) < n_clusters:
        raise ValueError("Not enough data points for the number of clusters requested.")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    model = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = model.fit_predict(X_scaled)

    clustered_df = df.copy()
    clustered_df = clustered_df.loc[data.index].copy()
    clustered_df["cluster"] = cluster_labels

    return clustered_df, model
