import pandas as pd

from pathlib import Path
from rapidfuzz import process


def load_data(file_path: str, sheet_name: str | None = None) -> pd.DataFrame:
    file = Path(file_path).expanduser().resolve()
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        print("DataFrame successfully created:")
        print(df.head())
        return df
    except FileNotFoundError:
        print(f"Error: The file '{file}' was not found. Perhaps the wrong filepath?")
    except Exception as e:
        print(f"An error occurred: {e}")


def clean_dataframe(
    df: pd.DataFrame,
    fill_missing: str = "constant",
    constant_fill: str | int | float = "unknown",
    fuzzy_clean: bool = False,
    fuzzy_column: str | None = None,
    valid_values: list[str] | None = None
) -> pd.DataFrame:
    """
    Cleans a DataFrame for analysis:
    - Strips whitespace and normalizes casing
    - Handles nulls with configurable strategy
    - Fixes spacing and unwanted characters
    - Standardizes numeric/date types
    - Drops duplicates
    - (Optional) Fuzzy matches values in a specific column

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    fill_missing : str
        Strategy for filling missing values
    constant_fill : str/int/float
        Value used if fill_missing="constant"
    fuzzy_clean : bool
        Whether to apply fuzzy string matching cleanup
    fuzzy_column : str
        Column to apply fuzzy matching on (required if fuzzy_clean=True)
    valid_values : list[str]
        Allowed values for fuzzy cleaning

    Returns
    -------
    pd.DataFrame
    """

    df = df.copy()

    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.lower()
        df[col] = df[col].str.replace(r"\s+", " ", regex=True)
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

    # Optional fuzzy cleaning
    if fuzzy_clean and fuzzy_column and valid_values:
        df[f"{fuzzy_column}_cleaned"] = df[fuzzy_column].apply(
            lambda x: process.extractOne(x, valid_values)[0] if isinstance(x, str) else x
        )

    # Standardize data types
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")
        if df[col].dtype == "object":
            df[col] = pd.to_datetime(df[col], errors="ignore")

    df.reset_index(drop=True, inplace=True)

    return df


def main():
    # Example usage
    df = load_data("~/Desktop/mydata.xlsx")
    if df is not None:
        cleaned = clean_dataframe(df, fill_missing="median", fuzzy_clean=True, fuzzy_column="fruit",
                                  valid_values=["apple", "banana", "orange"])
        print(cleaned.head())


if __name__ == "__main__":
    main()
