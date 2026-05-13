# tools.py
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

def plot_histogram(df, column):
    """Plot distribution of a numeric column"""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found.")
        return
    
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(df[column].dropna(), bins=20, color="steelblue", edgecolor="white")
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def plot_bar_chart(df, cat_column, num_column):
    """Plot average of numeric column grouped by categorical column"""
    if cat_column not in df.columns or num_column not in df.columns:
        st.warning(f"Column not found.")
        return
    
    grouped = df.groupby(cat_column)[num_column].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(grouped.index, grouped.values, color="coral", edgecolor="white")
    ax.set_title(f"Average {num_column} by {cat_column}")
    ax.set_xlabel(cat_column)
    ax.set_ylabel(f"Avg {num_column}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def show_summary(df, column):
    """Show statistical summary of a column"""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found.")
        return
    
    stats = df[column].describe()
    st.markdown(f"**Summary of `{column}`**")
    st.dataframe(stats.to_frame().astype(str))
    
def detect_outliers_iqr(df, column):
    """Detect outliers using IQR method and show them"""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found.")
        return

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df[column] < lower) | (df[column] > upper)]

    st.markdown(f"**Outlier Detection (IQR) — `{column}`**")
    st.write(f"Normal range: `{lower:.2f}` to `{upper:.2f}`")

    if outliers.empty:
        st.success(f"No outliers found in `{column}`")
    else:
        st.error(f"{len(outliers)} outlier(s) found in `{column}`")
        st.dataframe(outliers)

    # Plot with outliers highlighted
  

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(df[column].dropna(), bins=20,
            color="steelblue", edgecolor="white", label="Normal")

    # Highlight outlier zones in red
    ax.axvline(lower, color="red", linestyle="--", linewidth=1.5,
               label=f"Lower fence: {lower:.0f}")
    ax.axvline(upper, color="red", linestyle="--", linewidth=1.5,
               label=f"Upper fence: {upper:.0f}")

    ax.set_title(f"Outlier Detection — {column} (IQR Method)")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def detect_outliers_zscore(df, column):
    """Detect outliers using Z-score method"""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found.")
        return


    mean = df[column].mean()
    std = df[column].std()

    # Calculate z-score for every row
    df_temp = df.copy()
    df_temp["z_score"] = (df_temp[column] - mean) / std

    outliers = df_temp[df_temp["z_score"].abs() > 3]

    st.markdown(f"**Outlier Detection (Z-Score) — `{column}`**")
    st.write(f"Mean: `{mean:.2f}` | Std: `{std:.2f}`")
    st.write(f"Outlier threshold: Z > 3 or Z < -3")

    if outliers.empty:
        st.success(f"No outliers found in `{column}` using Z-Score")
    else:
        st.error(f"{len(outliers)} outlier(s) found in `{column}`")
        st.dataframe(outliers)
        

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(range(len(df_temp)), df_temp["z_score"],
           color=["red" if abs(z) > 3 else "steelblue"
                  for z in df_temp["z_score"]])
    ax.axhline(3,  color="red", linestyle="--",
               linewidth=1.5, label="Z = +3")
    ax.axhline(-3, color="red", linestyle="--",
               linewidth=1.5, label="Z = -3")
    ax.set_title(f"Z-Scores — {column}")
    ax.set_xlabel("Row index")
    ax.set_ylabel("Z-Score")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)    
    
    