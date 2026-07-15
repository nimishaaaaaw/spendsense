"""
Pydantic request/response schemas for the API layer.

Field names here intentionally mirror the dict keys already returned by
app/core/*.py (categorize_df, detect_subscriptions, insights.*) so the API
layer is a thin, honest pass-through -- no relabeling that could hide a
mismatch between what the engine computes and what the frontend receives.
"""

from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

class Transaction(BaseModel):
    Date: date
    Description: str
    Amount: float
    Type: Literal["DEBIT", "CREDIT"]
    Balance: Optional[float] = None
    Merchant: str
    Category: str
    IsSubscription: bool
    MatchMethod: Literal["rule", "fuzzy", "p2p_heuristic", "user_override", "none"]
    Confidence: float
    CounterpartyName: Optional[str] = None


class UploadResponse(BaseModel):
    session_id: str
    transaction_count: int
    date_range_start: date
    date_range_end: date
    unmatched_count: int  # rows still Category == "Uncategorized" after full pipeline
    transactions: list[Transaction]


class RecategorizeRequest(BaseModel):
    session_id: str
    description: str          # RAW description of the row being corrected
    merchant: str
    category: str
    is_subscription: bool = False


class RecategorizeResponse(BaseModel):
    updated_count: int         # how many rows matched this cleaned description and got updated
    transactions: list[Transaction]


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------

class Subscription(BaseModel):
    merchant: str
    billing_cycle: Literal["monthly", "quarterly", "annual"]
    amount: float
    monthly_cost: float
    annualized_cost: float
    occurrences: int
    first_charge: date
    last_charge: date
    is_forgotten: bool
    confidence: float


class SubscriptionBleed(BaseModel):
    total_monthly: float
    total_annual: float
    count: int
    forgotten_count: int


class SubscriptionsResponse(BaseModel):
    subscriptions: list[Subscription]
    bleed: SubscriptionBleed


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

class WeekdayVsWeekend(BaseModel):
    weekday_total: float
    weekend_total: float
    weekday_count: int
    weekend_count: int
    weekend_to_weekday_ratio: Optional[float] = None


class CategoryTrend(BaseModel):
    category: str
    month: str  # "2026-01" format (period string)
    total: float
    prev_month_total: Optional[float] = None
    pct_change: Optional[float] = None


class SpendingLeak(BaseModel):
    category: str
    total: float
    avg_transaction: float
    count: int


class SpendingVelocity(BaseModel):
    average_pct_spent_within_7_days: Optional[float] = None
    velocity_label: Literal["slow", "moderate", "fast", "unknown"]
    salary_events_analyzed: int


class InsightsResponse(BaseModel):
    weekday_vs_weekend: WeekdayVsWeekend
    category_trends: list[CategoryTrend]
    top_leaks: list[SpendingLeak]
    velocity: SpendingVelocity
    subscription_bleed: SubscriptionBleed


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    detail: str