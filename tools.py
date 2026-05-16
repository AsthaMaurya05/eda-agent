import pandas as pd
import matplotlib
matplotlib.use('Agg')  # important — no display needed, saves to file
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

OUTPUTS_DIR = "outputs"

# ── Tool 1 ──────────────────────────────────────────────
def get_dataframe_overview(df: pd.DataFrame) -> str:
    """
    Returns shape, column names, data types, and null counts.
    This is always the FIRST thing an analyst checks.
    """
    info = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "null_percentage": (
            (df.isnull().sum() / len(df)) * 100
        ).round(2).to_dict()
    }
    return json.dumps(info, indent=2)


# ── Tool 2 ──────────────────────────────────────────────
def get_basic_statistics(df: pd.DataFrame) -> str:
    """
    Returns mean, median, std, min, max for all numeric columns.
    """
    numeric_df = df.select_dtypes(include='number')

    if numeric_df.empty:
        return json.dumps({"error": "No numeric columns found"})

    stats = {
        "mean":   numeric_df.mean().round(2).to_dict(),
        "median": numeric_df.median().round(2).to_dict(),
        "std":    numeric_df.std().round(2).to_dict(),
        "min":    numeric_df.min().round(2).to_dict(),
        "max":    numeric_df.max().round(2).to_dict(),
    }
    return json.dumps(stats, indent=2)


# ── Tool 3 ──────────────────────────────────────────────
def detect_outliers(df: pd.DataFrame) -> str:
    """
    Uses IQR method to detect outliers in numeric columns.
    IQR = Inter Quartile Range. Values outside 1.5x IQR are outliers.
    This is the standard statistical method — not magic, just math.
    """
    numeric_df = df.select_dtypes(include='number')

    if numeric_df.empty:
        return json.dumps({"error": "No numeric columns found"})

    outlier_report = {}

    for col in numeric_df.columns:
        Q1 = numeric_df[col].quantile(0.25)
        Q3 = numeric_df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = numeric_df[
            (numeric_df[col] < lower) | (numeric_df[col] > upper)
        ][col]

        outlier_report[col] = {
            "outlier_count": int(len(outliers)),
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(float(upper), 2),
            "outlier_values": outliers.head(5).tolist()
        }

    return json.dumps(outlier_report, indent=2)


# ── Tool 4 ──────────────────────────────────────────────
def plot_distributions(df: pd.DataFrame) -> str:
    """
    Plots histogram for every numeric column.
    Saves one image file. Returns the file path.
    """
    numeric_df = df.select_dtypes(include='number')

    if numeric_df.empty:
        return json.dumps({"error": "No numeric columns to plot"})

    cols = numeric_df.columns.tolist()
    n = len(cols)

    fig, axes = plt.subplots(
        nrows=(n + 1) // 2,
        ncols=2,
        figsize=(12, 4 * ((n + 1) // 2))
    )
    axes = axes.flatten()

    for i, col in enumerate(cols):
        axes[i].hist(
            numeric_df[col].dropna(),
            bins=30,
            color='steelblue',
            edgecolor='white'
        )
        axes[i].set_title(col)
        axes[i].set_xlabel("Value")
        axes[i].set_ylabel("Frequency")

    # hide unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, "distributions.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    return json.dumps({"chart_saved": path})


# ── Tool 5 ──────────────────────────────────────────────
def plot_correlation_matrix(df: pd.DataFrame) -> str:
    """
    Plots a heatmap showing correlations between numeric columns.
    Correlation of 1.0 = perfect positive, -1.0 = perfect negative.
    """
    numeric_df = df.select_dtypes(include='number')

    if numeric_df.shape[1] < 2:
        return json.dumps({"error": "Need at least 2 numeric columns"})

    corr = numeric_df.corr()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.5
    )
    plt.title("Correlation Matrix")
    plt.tight_layout()

    path = os.path.join(OUTPUTS_DIR, "correlation_matrix.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    return json.dumps({"chart_saved": path})