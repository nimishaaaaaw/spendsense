"""
GET /subscriptions/{session_id} -- returns the current subscription list
and bleed totals for a session. Subscriptions are recomputed from the
session's CURRENT categorized_df (which reflects any recategorizations
applied), not cached from upload time, so this stays consistent after
corrections.
"""

from fastapi import APIRouter, HTTPException

from app.session_store import get_session
from app.core.insights import subscription_bleed
from app.models.schemas import SubscriptionsResponse

router = APIRouter()


@router.get("/subscriptions/{session_id}", response_model=SubscriptionsResponse)
def get_subscriptions(session_id: str):
    session_data = get_session(session_id)
    if session_data is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your statement.",
        )

    subscriptions = session_data["subscriptions"]
    bleed = subscription_bleed(subscriptions)

    return SubscriptionsResponse(subscriptions=subscriptions, bleed=bleed)