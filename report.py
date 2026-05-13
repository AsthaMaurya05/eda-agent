# report.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for saving files
from fpdf import FPDF
import io


def generate_report(df):
    """
    Generate a PDF report from the dataframe.
    Returns the PDF as bytes so Streamlit can offer it as download.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── HEADER ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "EDA Agent - Automated Report", fill=True,
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    # ── DATASET OVERVIEW ─────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "1. Dataset Overview", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Rows: {df.shape[0]}    Columns: {df.shape[1]}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Column types table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(80, 8, "Column", border=1, fill=True)
    pdf.cell(60, 8, "Data Type", border=1, fill=True,
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    for col, dtype in df.dtypes.items():
        pdf.cell(80, 7, str(col), border=1)
        pdf.cell(60, 7, str(dtype), border=1,
                 new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ── BASIC STATISTICS ─────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "2. Basic Statistics", new_x="LMARGIN", new_y="NEXT")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        desc = df[numeric_cols].describe().round(2)

        # Header row
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        col_w = 25
        stat_w = 170 // len(numeric_cols)

        pdf.cell(col_w, 7, "Stat", border=1, fill=True)
        for col in numeric_cols:
            # Truncate long column names
            label = col[:10] + ".." if len(col) > 10 else col
            pdf.cell(stat_w, 7, label, border=1, fill=True)
        pdf.ln()

        # Data rows
        pdf.set_font("Helvetica", "", 9)
        for stat in desc.index:
            pdf.cell(col_w, 6, str(stat), border=1)
            for col in numeric_cols:
                pdf.cell(stat_w, 6, str(desc.loc[stat, col]), border=1)
            pdf.ln()
        pdf.ln(6)
    else:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, "No numeric columns found.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # ── MISSING VALUES ───────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "3. Missing Values", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 7, "No missing values found. Dataset is complete.",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(30, 30, 30)
    else:
        pdf.set_text_color(200, 0, 0)
        for col, count in missing.items():
            pdf.cell(0, 7, f"{col}: {count} missing values",
                     new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(30, 30, 30)
    pdf.ln(4)

    # ── OUTLIER SUMMARY ──────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "4. Outlier Detection Summary",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    if numeric_cols:
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df[(df[col] < lower) | (df[col] > upper)]

            if outliers.empty:
                pdf.set_text_color(0, 150, 0)
                pdf.cell(0, 7, f"{col}: No outliers (range {lower:.1f} to {upper:.1f})",
                         new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.set_text_color(200, 0, 0)
                pdf.cell(0, 7, f"{col}: {len(outliers)} outlier(s) found!",
                         new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(30, 30, 30)
    else:
        pdf.cell(0, 7, "No numeric columns to check.",
                 new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── CHARTS ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "5. Charts", new_x="LMARGIN", new_y="NEXT")

    # Save charts to temp files and embed in PDF
    

    # Helper — converts a matplotlib figure to bytes without temp files
    def fig_to_bytes(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        buf.seek(0)
        return buf

    # Histograms for every numeric column
    for col in numeric_cols:
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.hist(df[col].dropna(), bins=20,
                color="steelblue", edgecolor="white")
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        plt.tight_layout()

        img_buf = fig_to_bytes(fig)
        plt.close(fig)

        # FPDF2 can read directly from BytesIO
        pdf.image(img_buf, w=170)
        pdf.ln(4)

    # Bar chart — smart column selection
    categorical_cols = df.select_dtypes(
        include=["object", "string"]).columns.tolist()

    best_cat = None
    for col in categorical_cols:
        if 2 <= df[col].nunique() <= 20:
            best_cat = col
            break

    if best_cat and numeric_cols:
        best_num = numeric_cols[0]
        for col in numeric_cols:
            if df[col].nunique() > 10:
                best_num = col
                break
        
        grouped = df.groupby(best_cat)[best_num].mean().sort_values(
            ascending=False)

        fig, ax = plt.subplots(figsize=(7, 3))
        ax.bar(grouped.index, grouped.values,
               color="coral", edgecolor="white")
        ax.set_title(f"Average {best_num} by {best_cat}")
        ax.set_xlabel(best_cat)
        ax.set_ylabel(f"Avg {best_num}")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        img_buf = fig_to_bytes(fig)
        plt.close(fig)

        pdf.image(img_buf, w=170)
        pdf.ln(4)

    # ── OUTPUT — also in memory, no temp files ───────────────────
    pdf_buf = io.BytesIO()
    pdf.output(pdf_buf)
    pdf_bytes = pdf_buf.getvalue()

    return pdf_bytes