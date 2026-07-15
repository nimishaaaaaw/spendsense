"""
POST /transactions/recategorize -- lets the user correct a wrong
merchant/category for a transaction. The correction is stored as an
override keyed by CLEANED description text (see categorizer.categorize()),
then the entire session's categorized DataFrame is recomputed so every
transaction sharing that same cleaned description gets fixed too --
this is the "engine remembers that merchant going forward" behavior from
the brief, not a per-row patch.
"""

from fastapi import APIRouter, HTTPException
import pandas as pd

from app.core.cleaner import clean
from app.core.categorizer import categorize_df
from app.core.subscription_detector import detect_subscriptions
from app.session_store import get_session, update_session
from app.models.schemas import RecategorizeRequest, RecategorizeResponse
from app.api.routes.upload import _df_to_transactions

router = APIRouter()


@router.post("/transactions/recategorize", response_model=RecategorizeResponse)
def recategorize_transaction(payload: RecategorizeRequest):
    session_data = get_session(payload.session_id)
    if session_data is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your statement.",
        )

    raw_df: pd.DataFrame = session_data["raw_df"]
    overrides: dict = session_data["overrides"]

    cleaned_desc = clean(payload.description)
    if not cleaned_desc:
        raise HTTPException(
            status_code=422,
            detail="Could not derive a stable merchant key from this description.",
        )

    overrides[cleaned_desc] = {
        "merchant": payload.merchant,
        "category": payload.category,
        "is_subscription": payload.is_subscription,
    }

    # Recompute categorization for the WHOLE session with the new override
    # applied -- this is what makes the correction retroactive across every
    # transaction sharing this cleaned description, not just the one row
    # the user clicked on.
    recategorized_df = categorize_df(raw_df, overrides=overrides)
    updated_count = int((recategorized_df["Merchant"] == payload.merchant).sum())

    subscriptions = detect_subscriptions(recategorized_df)

    update_session(payload.session_id, {
        "raw_df": raw_df,
        "categorized_df": recategorized_df,
        "overrides": overrides,
        "subscriptions": subscriptions,
    })

    return RecategorizeResponse(
        updated_count=updated_count,
        transactions=_df_to_transactions(recategorized_df),
    )