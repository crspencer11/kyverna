import pandas as pd
import numpy as np
import re

from pathlib import Path
from rapidfuzz import process

def load_data(file_path: str, sheet_name: str | None = None) -> pd.DataFrame:
    file = Path(file_path).expanduser().resolve()  # expands ~ and gives absolute path

    try:
        # Load Excel file into DataFrame
        df = pd.read_excel(file, sheet_name=sheet_name)

        print("DataFrame successfully created:")
        print(df.head())
        return df

    except FileNotFoundError:
        print(f"Error: The file '{file}' was not found on your computer. perhaps the wrong filepath?")
    except Exception as e:
        print(f"An error occurred: {e}")

def clean_dataframe(
    df: pd.DataFrame,
    fill_missing: str = "constant",   # default constant, but can be "mean", "median", "constant", "drop"
    constant_fill: str | int | float = "unknown"
) -> pd.DataFrame:
    """
    Cleans a DataFrame for analysis:
    - Strips whitespace and normalizes casing
    - Handles nulls with configurable strategy
    - Fixes spacing and unwanted characters
    - Standardizes numeric/date types
    - Drops duplicates

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    fill_missing : str, default="constant"
        Strategy for filling missing values:
        "mode", "mean", "median", "constant", or "drop"
    constant_fill : str/int/float, default="unknown"
        Value used if fill_missing="constant"

    Returns
    -------
    pd.DataFrame
    """

    df = df.copy()

    # String cleaning
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    for col in df.select_dtypes(include="object").columns:
        # normalize casing
        df[col] = df[col].str.lower()
        # collapse multiple spaces
        df[col] = df[col].str.replace(r"\s+", " ", regex=True)
        # remove non-printable characters
        df[col] = df[col].str.replace(r"[^\x20-\x7E]", "", regex=True)

    # Handle missing values
    for col in df.columns:
        if df[col].isnull().any():
            if fill_missing == "mode":
                df[col].fillna(df[col].mode(dropna=True)[0] if not df[col].mode().empty else constant_fill, inplace=True)
            elif fill_missing == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
            elif fill_missing == "median" and pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
            elif fill_missing == "constant":
                df[col].fillna(constant_fill, inplace=True)
            elif fill_missing == "drop":
                df = df.dropna(subset=[col])

    # Standardize data types
    for col in df.columns:
        # try numeric
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")
        # try datetime
        if df[col].dtype == "object":
            df[col] = pd.to_datetime(df[col], errors="ignore")

    # Reset index for cleanliness
    df.reset_index(drop=True, inplace=True)

    return df
    valid_values = ["apple", "banana", "orange"]

    df["fruit_cleaned"] = df["fruit"].apply(
        lambda x: process.extractOne(x, valid_values)[0] if isinstance(x, str) else x
    )
    # Strip whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalize string casing (example: everything lower-case)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.lower()

    # Replace multiple spaces with single space
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.replace(r"\s+", " ", regex=True)

    # Standardize types(example: try converting dates and numerics)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="ignore")
            df[col] = pd.to_datetime(df[col], errors="ignore")
        except Exception:
            pass

    return df

def main():
    return

if __name__ == "__main__":
    main()
