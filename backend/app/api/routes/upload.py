"""
POST /upload -- accepts a CSV file, runs it through the full pipeline
(parse -> categorize -> detect subscriptions), stores the result in an
in-memory session, and returns the categorized transactions plus a session_id
the frontend must send on every subsequent request.

POST /upload/sample -- same pipeline, but loads the bundled synthetic
dataset instead of an uploaded file, so a user can explore the app without
needing their own CSV on hand.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import pathlib

from app.core.parser import parse_csv, CSVValidationError
from app.core.categorizer import categorize_df
from app.core.subscription_detector import detect_subscriptions
from app.session_store import create_session
from app.models.schemas import UploadResponse, Transaction

router = APIRouter()

_SAMPLE_DATA_PATH = pathlib.Path(__file__).parent.parent.parent.parent / "data" / "transactions_raw.csv"


@router.post("/upload", response_model=UploadResponse)
async def upload_statement(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported currently.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        raw_df = parse_csv(file_bytes)
    except CSVValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    categorized_df = categorize_df(raw_df)
    subscriptions = detect_subscriptions(categorized_df)

    session_id = create_session({
        "raw_df": raw_df,
        "categorized_df": categorized_df,
        "overrides": {},
        "subscriptions": subscriptions,
    })

    unmatched_count = int((categorized_df["Category"] == "Uncategorized").sum())

    transactions = _df_to_transactions(categorized_df)

    return UploadResponse(
        session_id=session_id,
        transaction_count=len(categorized_df),
        date_range_start=categorized_df["Date"].min(),
        date_range_end=categorized_df["Date"].max(),
        unmatched_count=unmatched_count,
        transactions=transactions,
    )


@router.post("/upload/sample", response_model=UploadResponse)
async def upload_sample_data():
    """
    Loads the bundled sample dataset (data/transactions_raw.csv) through the
    exact same pipeline as a real upload -- parse -> categorize -> detect
    subscriptions -> create session. This is NOT a separate demo/mock path;
    it's the real pipeline running on real (synthetic) data, so a user
    exploring with sample data sees a completely honest preview of what
    their own statement would produce.
    """
    if not _SAMPLE_DATA_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Sample dataset not found on server. Contact support.",
        )

    file_bytes = _SAMPLE_DATA_PATH.read_bytes()

    try:
        raw_df = parse_csv(file_bytes)
    except CSVValidationError as e:
        # If this ever fires, the bundled sample itself is malformed --
        # a server-side bug, not a user error, so we say so explicitly.
        raise HTTPException(status_code=500, detail=f"Bundled sample data is invalid: {e}")

    categorized_df = categorize_df(raw_df)
    subscriptions = detect_subscriptions(categorized_df)

    session_id = create_session({
        "raw_df": raw_df,
        "categorized_df": categorized_df,
        "overrides": {},
        "subscriptions": subscriptions,
    })

    unmatched_count = int((categorized_df["Category"] == "Uncategorized").sum())
    transactions = _df_to_transactions(categorized_df)

    return UploadResponse(
        session_id=session_id,
        transaction_count=len(categorized_df),
        date_range_start=categorized_df["Date"].min(),
        date_range_end=categorized_df["Date"].max(),
        unmatched_count=unmatched_count,
        transactions=transactions,
    )


def _df_to_transactions(df: pd.DataFrame) -> list[Transaction]:
    """
    Converts a categorized DataFrame into a list of Transaction schema
    objects. Shared helper -- also used by transactions.py after
    recategorization, so both endpoints serialize identically.
    """
    records = df.to_dict(orient="records")
    transactions = []
    for r in records:
        # NaN from pandas (e.g. missing Balance/CounterpartyName) must become
        # None for Pydantic -- pandas NaN is a float and fails Optional[str] etc.
        cleaned = {k: (None if pd.isna(v) else v) for k, v in r.items()}
        transactions.append(Transaction(**cleaned))
    return transactions