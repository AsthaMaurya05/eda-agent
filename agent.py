import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from tools import (
    get_dataframe_overview,
    get_basic_statistics,
    detect_outliers,
    plot_distributions,
    plot_correlation_matrix
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def run_eda_agent(df: pd.DataFrame) -> dict:
    """
    Run EDA analysis on the dataframe.
    Runs all analysis tools directly, then uses Groq for summary generation.
    """
    print("\n[Agent] Starting EDA analysis...")
    
    charts_generated = []
    
    try:
        # Run overview first
        print("[Agent] Getting dataframe overview...")
        overview = json.loads(get_dataframe_overview(df))
        
        # Get statistics for numeric columns
        print("[Agent] Calculating basic statistics...")
        stats = json.loads(get_basic_statistics(df))
        
        # Detect outliers
        print("[Agent] Detecting outliers...")
        outliers = json.loads(detect_outliers(df))
        
        # Generate distribution charts
        print("[Agent] Generating distribution charts...")
        dist_result = json.loads(plot_distributions(df))
        if "chart_saved" in dist_result:
            charts_generated.append(dist_result["chart_saved"])
        
        # Generate correlation matrix
        print("[Agent] Generating correlation matrix...")
        corr_result = json.loads(plot_correlation_matrix(df))
        if "chart_saved" in corr_result:
            charts_generated.append(corr_result["chart_saved"])
        
        # Use Groq to generate a summary
        print("[Agent] Generating AI summary...")
        
        summary_prompt = f"""Based on this dataset analysis:
- Shape: {overview.get('rows')} rows × {overview.get('columns')} columns
- Columns: {', '.join(overview.get('column_names', []))}
- Null values detected: {any(v > 0 for v in overview.get('null_counts', {}).values())}

Key Statistics:
{json.dumps(stats, indent=2)[:800]}

Outliers Found:
{json.dumps(outliers, indent=2)[:800]}

Please provide a professional EDA summary with key insights and recommendations."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert data analyst. Provide clear, actionable insights from EDA analysis."
            },
            {
                "role": "user",
                "content": summary_prompt
            }
        ]
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )
            summary = response.choices[0].message.content
        except Exception as e:
            print(f"[Agent] Groq API error: {e}. Using fallback summary.")
            summary = f"""Analysis Complete

Dataset: {overview.get('rows')} rows × {overview.get('columns')} columns
Columns Analyzed: {', '.join(overview.get('column_names', [])[:5])}...

Data Quality: {'Missing values detected' if any(v > 0 for v in overview.get('null_counts', {}).values()) else 'No missing values'}
Charts Generated: {len(charts_generated)}

See detailed statistics and charts above for complete analysis."""
        
        return {
            "summary": summary,
            "charts": charts_generated,
            "messages": 1,
            "overview": overview,
            "statistics": stats,
            "outliers": outliers
        }
    
    except Exception as e:
        print(f"[Agent] Error: {str(e)}")
        return {
            "summary": f"Error during analysis: {str(e)}",
            "charts": charts_generated,
            "messages": 0,
            "overview": {},
            "statistics": {},
            "outliers": {}
        }