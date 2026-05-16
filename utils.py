"""
Helper functions for file reading, data cleaning, and utilities
"""

import os
import pandas as pd
from pathlib import Path


def clean_data(df: pd.DataFrame, drop_missing: bool = False) -> pd.DataFrame:
    """
    Clean data by handling missing values and data types
    """
    df_clean = df.copy()
    
    # Convert date columns if detected
    for col in df_clean.columns:
        if 'date' in col.lower():
            try:
                df_clean[col] = pd.to_datetime(df_clean[col])
            except:
                pass
    
    # Handle missing values
    if drop_missing:
        df_clean = df_clean.dropna()
    
    return df_clean


def validate_csv(file_path: str) -> tuple[bool, str]:
    """
    Validate if file is a valid CSV
    Returns: (is_valid, message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not file_path.endswith('.csv'):
        return False, "File must be a CSV"
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return False, "CSV file is empty"
        return True, "Valid CSV file"
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def get_file_info(file_path: str) -> dict:
    """Get information about uploaded file"""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    return {
        "name": file_name,
        "size_bytes": file_size,
        "size_mb": round(file_size / (1024 * 1024), 2)
    }


def format_results(data: dict, format_type: str = "json") -> str:
    """
    Format analysis results for output
    """
    if format_type == "json":
        import json
        return json.dumps(data, indent=2, default=str)
    return str(data)


def cleanup_old_files(directory: str, days: int = 7):
    """
    Clean up files older than specified days
    Useful for uploads and outputs directories
    """
    import time
    current_time = time.time()
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if (current_time - file_time) > (days * 86400):
                os.remove(file_path)


if __name__ == "__main__":
    print("Utils module loaded successfully")
