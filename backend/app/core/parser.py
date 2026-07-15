"""
CSV upload parsing and validation.

Normalizes an uploaded bank/UPI statement CSV into the internal schema our
core engine expects: Date, Description, Amount, Type, Balance.

This targets the shape produced by generate_dataset.py (Date, Description,
Amount, Type, Balance) since that's the only real export format we've been
given to validate against. Real bank exports vary wildly in column naming --
handling arbitrary bank formats robustly is explicitly a stretch goal per
SpendSense.docx ("pdfplumber (stretch)"), not something this parser claims
to solve generally. It does light column-name normalization (case/whitespace
insensitive matching against expected names) so minor variations don't break,
but it will raise a clear error rather than silently guess on genuinely
different schemas.
"""

import io
import pandas as pd

REQUIRED_COLUMNS = {"date", "description", "amount", "type"}
OPTIONAL_COLUMNS = {"balance"}


class CSVValidationError(Exception):
    """Raised when an uploaded CSV doesn't match the expected schema."""
    pass


def _normalize_column_name(col: str) -> str:
    return col.strip().lower()


def parse_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Parses raw CSV bytes into a validated, normalized DataFrame with columns
    Date, Description, Amount, Type, Balance (Balance is optional -> NaN if
    absent). Raises CSVValidationError with a specific message on failure --
    never silently drops or fabricates rows.
    """
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise CSVValidationError(f"Could not read file as CSV: {e}")

    if df.empty:
        raise CSVValidationError("CSV file is empty.")

    # Normalize column names for matching (but keep original case in a map)
    normalized_map = {_normalize_column_name(c): c for c in df.columns}
    present_normalized = set(normalized_map.keys())

    missing = REQUIRED_COLUMNS - present_normalized
    if missing:
        raise CSVValidationError(
            f"CSV is missing required column(s): {', '.join(sorted(missing))}. "
            f"Expected columns: Date, Description, Amount, Type (Balance optional)."
        )

    # Rebuild with canonical column names
    rename_map = {}
    for canonical in REQUIRED_COLUMNS | OPTIONAL_COLUMNS:
        if canonical in present_normalized:
            rename_map[normalized_map[canonical]] = canonical.capitalize()
    df = df.rename(columns=rename_map)

    if "Balance" not in df.columns:
        df["Balance"] = None

    # Type validation -- fail loudly rather than coerce silently
    try:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    except Exception:
        raise CSVValidationError("Date column contains values that could not be parsed as dates.")

    try:
        df["Amount"] = pd.to_numeric(df["Amount"])
    except Exception:
        raise CSVValidationError("Amount column contains non-numeric values.")

    if (df["Amount"] < 0).any():
        raise CSVValidationError(
            "Amount column contains negative values. Amounts should be positive; "
            "use the Type column (DEBIT/CREDIT) to indicate direction."
        )

    df["Type"] = df["Type"].astype(str).str.strip().str.upper()
    invalid_types = set(df["Type"].unique()) - {"DEBIT", "CREDIT"}
    if invalid_types:
        raise CSVValidationError(
            f"Type column contains unrecognized value(s): {', '.join(invalid_types)}. "
            f"Expected only DEBIT or CREDIT."
        )

    df["Description"] = df["Description"].astype(str)
    if (df["Description"].str.strip() == "").any():
        raise CSVValidationError("Some rows have an empty Description -- cannot categorize.")

    return df[["Date", "Description", "Amount", "Type", "Balance"]].reset_index(drop=True)