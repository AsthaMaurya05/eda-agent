# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load API key: try st.secrets first (Streamlit Cloud), fall back to .env (local)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API key exists
if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found. Please add it to Streamlit Cloud Secrets.")
    st.stop()

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="EDA Agent",
    page_icon="📊",
    layout="wide",               # full width
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Softer background */
    .stApp { background-color: #f8f9fb; }

    /* Section cards */
    .section-card {
        background: white;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e8eaed;
        margin-bottom: 1.2rem;
    }

    /* Metric boxes */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .metric-box {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        flex: 1;
        text-align: center;
        border: 1px solid #d0d9ff;
    }
    .metric-box .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2c3e8c;
    }
    .metric-box .label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 2px;
    }

    /* Section headers */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.3rem;
    }
    .section-desc {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.8rem;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/data-configuration.png",
             width=64)
    st.title("EDA Agent")
    st.caption("AI-Powered Exploratory Data Analysis")

    st.divider()

    st.markdown("### How it works")
    st.markdown("""
    1. 📂 **Upload** any CSV file
    2. 📊 **Auto charts** are generated
    3. 🤖 **AI Agent** decides what to analyze
    4. 🔍 **Outliers** are flagged automatically
    5. 📄 **Download** a full PDF report
    """)

    st.divider()

    st.markdown("### Tech Stack")
    st.markdown("""
    - `Streamlit` — UI
    - `Pandas` — Data processing
    - `Matplotlib` — Charts
    - `Groq API` — AI Agent
    - `fpdf2` — PDF reports
    """)

    st.divider()
    st.caption("Built by **Your Name**")
    st.caption("[GitHub](#) · [LinkedIn](#)")


# ── MAIN AREA ─────────────────────────────────────────────────
st.markdown("## 📊 EDA Agent")
st.markdown("Upload any CSV file — the AI agent will automatically analyze it, "
            "generate charts, detect outliers, and produce a downloadable report.")

st.divider()

# ── FILE UPLOAD ───────────────────────────────────────────────
up_file = st.file_uploader(
    "Drop your CSV file here",
    type="csv",
    help="Supports any CSV file. The agent adapts to your data automatically."
)

# ── EMPTY STATE ───────────────────────────────────────────────
if up_file is None:
    st.markdown("""
    <div style='text-align:center; padding: 3rem; color: #999;'>
        <div style='font-size:3rem'>📂</div>
        <div style='font-size:1.1rem; margin-top:0.5rem'>
            No file uploaded yet
        </div>
        <div style='font-size:0.85rem; margin-top:0.3rem'>
            Upload a CSV above to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── LOAD DATA ─────────────────────────────────────────────────
df = pd.read_csv(up_file)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(
    include=["object", "string"]).columns.tolist()

# ── PHASE 1: OVERVIEW ─────────────────────────────────────────
st.markdown("### 🗂 Dataset Overview")

# Metric boxes
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rows", df.shape[0])
with col2:
    st.metric("Columns", df.shape[1])
with col3:
    st.metric("Numeric cols", len(numeric_cols))
with col4:
    missing_total = df.isnull().sum().sum()
    st.metric("Missing values", int(missing_total))

# Two columns layout — types + stats side by side
left, right = st.columns(2)

with left:
    st.markdown("**Column Types**")
    st.caption("Shows what kind of data each column holds — "
               "numbers (int/float) or text (str).")
    dtype_df = df.dtypes.astype(str).rename("dtype").reset_index()
    dtype_df.columns = ["column", "dtype"]
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

with right:
    st.markdown("**Basic Statistics**")
    st.caption("Count, mean, min, max and percentiles "
               "for every numeric column.")
    st.dataframe(df.describe().astype(str), use_container_width=True)

# Missing values
st.markdown("**Missing Values**")
st.caption("Columns with missing data need attention before modeling. "
           "Green means your dataset is complete.")
missing = df.isnull().sum().rename("missing_count")
missing_df = missing[missing > 0].reset_index()
missing_df.columns = ["column", "missing_count"]

if missing_df.empty:
    st.success("No missing values found. Dataset is complete.")
else:
    st.warning(f"{len(missing_df)} column(s) have missing values.")
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

st.divider()

# ── PHASE 2: AUTO CHARTS ──────────────────────────────────────
st.markdown("### 📈 Auto Charts")
st.caption("Charts are generated automatically based on your data types. "
           "No configuration needed.")

if not numeric_cols:
    st.warning("No numeric columns found. Charts need at least one numeric column.")
else:
    # Histograms
    st.markdown("#### Distributions")
    st.caption("Histograms show how values are spread across a column. "
               "A tall bar means many rows have that value.")

    # Responsive grid — 2 charts per row
    for i in range(0, len(numeric_cols), 2):
        cols = st.columns(2)
        for j, col_name in enumerate(numeric_cols[i:i+2]):
            with cols[j]:
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.hist(df[col_name].dropna(), bins=20,
                        color="#4f72c4", edgecolor="white")
                ax.set_title(f"{col_name}", fontweight="bold")
                ax.set_xlabel(col_name)
                ax.set_ylabel("Frequency")
                ax.spines[["top", "right"]].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

    # Smart bar chart
    if categorical_cols:
        st.markdown("#### Category Comparison")
        st.caption("Average of a numeric column grouped by a category. "
                   "Useful for comparing performance across groups.")

        best_cat = None
        for col in categorical_cols:
            if 2 <= df[col].nunique() <= 20:
                best_cat = col
                break

        best_num = numeric_cols[0]
        for col in numeric_cols:
            if df[col].nunique() > 10:
                best_num = col
                break

        if best_cat:
            grouped = df.groupby(best_cat)[best_num].mean().sort_values(
                ascending=False)
            fig, ax = plt.subplots(figsize=(10, 4))
            bars = ax.bar(grouped.index, grouped.values,
                          color="#e8735a", edgecolor="white")
            ax.set_title(f"Average {best_num} by {best_cat}",
                         fontweight="bold")
            ax.set_xlabel(best_cat)
            ax.set_ylabel(f"Avg {best_num}")
            ax.spines[["top", "right"]].set_visible(False)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    # Correlation heatmap
    if len(numeric_cols) >= 2:
        st.markdown("#### Correlation Heatmap")
        st.caption("Shows how strongly columns are related to each other. "
                   "Red = strong positive, Blue = strong negative, "
                   "White = no relationship.")
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
        ax.set_yticklabels(numeric_cols)
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}",
                        ha="center", va="center",
                        fontsize=9, color="black")
        ax.set_title("Correlation Matrix", fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

st.divider()

# ── PHASE 3: AI AGENT ─────────────────────────────────────────
st.markdown("### 🤖 AI Agent Analysis")
st.caption("The AI agent reads your column names and sample data, then "
           "decides which analyses are most useful — without you telling it what to do. "
           "This is called 'tool use' or 'agentic AI'.")

from groq import Groq
import json
from tools import (plot_histogram, plot_bar_chart, show_summary,
                   detect_outliers_iqr, detect_outliers_zscore)

if st.button("▶ Run AI Agent", type="primary"):

    sample = df.head(3).to_string()
    user_message = f"""
    I have a dataset with {df.shape[0]} rows and {df.shape[1]} columns.
    Numeric columns: {numeric_cols}
    Categorical columns: {categorical_cols}
    Sample data:
    {sample}

    Analyze this dataset. Call the available tools to generate
    the most useful charts and summaries. Be specific about
    which columns to use.
    """

    tools_groq = [
        {
            "type": "function",
            "function": {
                "name": "plot_histogram",
                "description": "Plot distribution of a numeric column",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {"type": "string",
                                   "description": "Numeric column to plot"}
                    },
                    "required": ["column"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plot_bar_chart",
                "description": "Plot average of numeric column by category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cat_column": {"type": "string",
                                       "description": "Categorical column"},
                        "num_column": {"type": "string",
                                       "description": "Numeric column"}
                    },
                    "required": ["cat_column", "num_column"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "show_summary",
                "description": "Show statistical summary of a column",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {"type": "string",
                                   "description": "Column to summarize"}
                    },
                    "required": ["column"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_outliers_iqr",
                "description": "Detect outliers using IQR method",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {"type": "string",
                                   "description": "Numeric column to check"}
                    },
                    "required": ["column"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_outliers_zscore",
                "description": "Detect outliers using Z-score method",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "column": {"type": "string",
                                   "description": "Numeric column to check"}
                    },
                    "required": ["column"]
                }
            }
        }
    ]

    client = Groq(api_key=GROQ_API_KEY)

    with st.spinner("Agent is thinking..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": user_message}],
                tools=tools_groq,
                tool_choice="auto"
            )
        except Exception as e:
            if "401" in str(e):
                st.error("Invalid API key. Check your .env file.")
            elif "429" in str(e):
                st.error("Rate limit hit. Wait a moment and try again.")
            else:
                st.error(f"API error: {e}")
            st.stop()

    message = response.choices[0].message

    if message.content:
        st.info(message.content)

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            with st.expander(
                f"🔧 Agent called `{tool_name}` "
                f"with `{tool_input}`", expanded=True
            ):
                if tool_name == "plot_histogram":
                    plot_histogram(df, tool_input["column"])
                elif tool_name == "plot_bar_chart":
                    plot_bar_chart(df, tool_input["cat_column"],
                                   tool_input["num_column"])
                elif tool_name == "show_summary":
                    show_summary(df, tool_input["column"])
                elif tool_name == "detect_outliers_iqr":
                    detect_outliers_iqr(df, tool_input["column"])
                elif tool_name == "detect_outliers_zscore":
                    detect_outliers_zscore(df, tool_input["column"])
    else:
        st.info("Agent returned text only — no tool calls made.")

st.divider()

# ── PHASE 5: REPORT ───────────────────────────────────────────
st.markdown("### 📄 Download Report")
st.caption("Generates a complete PDF report with all stats, "
           "outlier findings and charts — ready to share.")

from report import generate_report

if st.button("📥 Generate PDF Report", type="secondary"):
    with st.spinner("Building your report..."):
        try:
            pdf_bytes = generate_report(df)
            st.success("Report ready!")
            st.download_button(
                label="⬇ Download PDF",
                data=pdf_bytes,
                file_name="eda_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Report generation failed: {e}")
            
# Sample CSV for users who don't have data ready
with st.expander("Don't have a CSV? Download a sample"):
    sample_data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "Diana", "Eve",
                 "Frank", "Grace", "Henry", "Isla", "Jack"],
        "Age": [28, 34, 22, 45, 31, 29, 38, 26, 33, 41],
        "Department": ["Engineering", "Sales", "HR", "Engineering",
                       "Marketing", "Sales", "HR", "Engineering",
                       "Marketing", "Sales"],
        "Salary": [75000, 62000, 48000, 95000, 54000,
                   67000, 51000, 88000, 57000, 71000],
        "Performance_Score": [4.2, 3.8, 3.5, 4.7, 3.9,
                              4.1, 3.6, 4.5, 3.8, 4.0],
        "Years_Experience": [5, 8, 1, 15, 6, 7, 3, 12, 5, 9]
    })

    st.dataframe(sample_data, use_container_width=True)

    csv = sample_data.to_csv(index=False)
    st.download_button(
        label="Download sample CSV",
        data=csv,
        file_name="sample_employees.csv",
        mime="text/csv"
    )            