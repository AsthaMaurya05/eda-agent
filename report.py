import os
import json
import pandas as pd
from fpdf import FPDF
from tools import (
    get_dataframe_overview,
    get_basic_statistics,
    detect_outliers
)

OUTPUTS_DIR = "outputs"


class EDAReport(FPDF):
    """Custom PDF class with header and footer."""

    def header(self):
        # Using helvetica - a standard built-in font
        self.set_font("helvetica", "B", 14)
        self.set_text_color(124, 106, 247)
        self.cell(0, 10, "EDA Agent - Analysis Report", align="C")
        self.ln(4)
        self.set_draw_color(124, 106, 247)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _clean_text(text: str) -> str:
    """
    Replace common Unicode characters that cause font issues.
    This is a safety net for better compatibility.
    """
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2018": "'",   # left single quote '
        "\u2019": "'",   # right single quote '
        "\u201c": '"',   # left double quote "
        "\u201d": '"',   # right double quote "
        "\u2022": "*",   # bullet •
        "\u2026": "...", # ellipsis …
        "\u00a0": " ",   # non-breaking space
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def generate_report(df: pd.DataFrame, agent_summary: str, charts: list) -> str:
    """
    Generates a PDF report and saves it to outputs/report.pdf
    Returns the file path.
    """
    pdf = EDAReport()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Use built-in fonts ──────────────────────────────────────────────────
    # Use Helvetica which is built into FPDF and handles most text well

    pdf.add_page()

    # ── Section 1: Dataset Overview ──────────────────────────────────────────
    _section_title(pdf, "1. Dataset Overview")

    overview = json.loads(get_dataframe_overview(df))

    _key_value(pdf, "Total Rows",    str(overview["rows"]))
    _key_value(pdf, "Total Columns", str(overview["columns"]))
    _key_value(pdf, "Column Names",  ", ".join(overview["column_names"]))

    pdf.ln(4)

    _small_heading(pdf, "Null Value Summary")
    _table_header(pdf, ["Column", "Data Type", "Null Count", "Null %"])

    for col in overview["column_names"]:
        _table_row(pdf, [
            col,
            overview["data_types"][col],
            str(overview["null_counts"][col]),
            f"{overview['null_percentage'][col]}%"
        ])

    pdf.ln(8)

    # ── Section 2: Basic Statistics ───────────────────────────────────────────
    _section_title(pdf, "2. Basic Statistics")

    stats = json.loads(get_basic_statistics(df))

    if "error" in stats:
        _body_text(pdf, stats["error"])
    else:
        numeric_cols = list(stats["mean"].keys())
        _table_header(pdf, ["Column", "Mean", "Median", "Std Dev", "Min", "Max"])

        for col in numeric_cols:
            _table_row(pdf, [
                col,
                str(stats["mean"][col]),
                str(stats["median"][col]),
                str(stats["std"][col]),
                str(stats["min"][col]),
                str(stats["max"][col])
            ])

    pdf.ln(8)

    # ── Section 3: Outlier Detection ─────────────────────────────────────────
    _section_title(pdf, "3. Outlier Detection (IQR Method)")

    outliers = json.loads(detect_outliers(df))

    if "error" in outliers:
        _body_text(pdf, outliers["error"])
    else:
        _table_header(pdf, ["Column", "Outlier Count", "Lower Bound", "Upper Bound"])

        for col, info in outliers.items():
            _table_row(pdf, [
                col,
                str(info["outlier_count"]),
                str(info["lower_bound"]),
                str(info["upper_bound"])
            ])

    pdf.ln(8)

    # ── Section 4: AI Agent Summary ───────────────────────────────────────────
    _section_title(pdf, "4. AI Agent Summary")
    _body_text(pdf, _clean_text(agent_summary))
    pdf.ln(8)

    # ── Section 5: Charts ─────────────────────────────────────────────────────
    if charts:
        _section_title(pdf, "5. Charts")

        for chart_path in charts:
            chart_path = chart_path.replace("\\", "/")

            if os.path.exists(chart_path):
                chart_name = (
                    os.path.basename(chart_path)
                    .replace(".png", "")
                    .replace("_", " ")
                    .title()
                )
                _small_heading(pdf, chart_name)

                if pdf.get_y() > 180:
                    pdf.add_page()

                pdf.image(chart_path, x=15, w=175)
                pdf.ln(6)

    # ── Save ──────────────────────────────────────────────────────────────────
    output_path = os.path.join(OUTPUTS_DIR, "report.pdf")
    pdf.output(output_path)
    return output_path


# ── Helper functions ──────────────────────────────────────────────────────────

def _section_title(pdf, text):
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(124, 106, 247)
    pdf.cell(0, 8, _clean_text(text))
    pdf.ln(6)
    pdf.set_text_color(30, 30, 30)


def _small_heading(pdf, text):
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, _clean_text(text))
    pdf.ln(5)


def _key_value(pdf, key, value):
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(50, 7, _clean_text(key + ":"))
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, _clean_text(value))
    pdf.ln(5)


def _body_text(pdf, text):
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 7, _clean_text(text))


def _table_header(pdf, columns):
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(124, 106, 247)
    pdf.set_text_color(255, 255, 255)
    col_width = 180 // len(columns)
    for col in columns:
        pdf.cell(col_width, 8, _clean_text(col), border=1, fill=True)
    pdf.ln()


def _table_row(pdf, values):
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.set_fill_color(245, 245, 255)
    col_width = 180 // len(values)
    for i, val in enumerate(values):
        fill = i % 2 == 0
        pdf.cell(col_width, 7, _clean_text(str(val)[:30]), border=1, fill=fill)
    pdf.ln()