"""
GET /insights/{session_id} -- returns the full insights bundle for a
session: weekday/weekend comparison, category trends, top spending leaks,
spending velocity, and subscription bleed.

Computed fresh from the session's CURRENT categorized_df on every call
(unlike subscriptions.py, which reads a cached list) -- these are cheap
pandas groupby operations on at most a few hundred/thousand rows, so
recomputing live is simpler than cache-invalidation logic and guarantees
insights always reflect the latest recategorizations.
"""

from fastapi import APIRouter, HTTPException

from app.session_store import get_session
from app.core.insights import (
    weekday_vs_weekend,
    monthly_category_trends,
    top_spending_leaks,
    spending_velocity,
    subscription_bleed,
)
from app.models.schemas import InsightsResponse

router = APIRouter()


@router.get("/insights/{session_id}", response_model=InsightsResponse)
def get_insights(session_id: str):
    session_data = get_session(session_id)
    if session_data is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your statement.",
        )

    categorized_df = session_data["categorized_df"]
    subscriptions = session_data["subscriptions"]

    return InsightsResponse(
        weekday_vs_weekend=weekday_vs_weekend(categorized_df),
        category_trends=monthly_category_trends(categorized_df),
        top_leaks=top_spending_leaks(categorized_df),
        velocity=spending_velocity(categorized_df),
        subscription_bleed=subscription_bleed(subscriptions),
    )