"""
Subscription detector.

Groups transactions by Merchant (post-categorization) and detects recurring
billing patterns algorithmically -- NOT via lookup against known subscription
merchants. This deliberately ignores IsSubscription from ground truth; a real
user's statement won't have that column, so the algorithm has to earn it.

Detects three billing rhythms:
  - Monthly   (~25-35 day gaps between charges)
  - Quarterly (~80-100 day gaps)          e.g. Hotstar
  - Annual    (~350-380 day gaps)         e.g. Amazon Prime -- needs 2+ charges
                                            to detect interval; a single annual
                                            charge in a 6-month window can't be
                                            distinguished from a one-off purchase,
                                            so it's left undetected (documented
                                            limitation, not guessed at).

"Forgotten" subscriptions: charged for FORGOTTEN_MONTHS_ACTIVE+ months, amount
under FORGOTTEN_MAX_AMOUNT (small-ticket charges people don't notice).

Excludes structurally-recurring-but-not-cancel-able categories (Housing,
Income) -- Rent and Salary repeat monthly with consistent amounts just like
a subscription would, but they aren't "subscription bleed" in the product
sense, so they're filtered out before pattern detection runs.
"""

import pandas as pd

from app.config import (
    SUBSCRIPTION_AMOUNT_VARIANCE,
    SUBSCRIPTION_MIN_INTERVAL_DAYS,
    SUBSCRIPTION_MAX_INTERVAL_DAYS,
    SUBSCRIPTION_QUARTERLY_MIN_DAYS,
    SUBSCRIPTION_QUARTERLY_MAX_DAYS,
    SUBSCRIPTION_ANNUAL_MIN_DAYS,
    SUBSCRIPTION_ANNUAL_MAX_DAYS,
    SUBSCRIPTION_MIN_OCCURRENCES,
    FORGOTTEN_MONTHS_ACTIVE,
    FORGOTTEN_MAX_AMOUNT,
)

# Categories that are structurally recurring but are NOT "subscriptions" in
# the cancel-worthy sense (rent, EMIs, mandatory utilities, income credits).
# Excluded so Rent etc. don't get flagged as subscription bleed alongside
# Netflix/Spotify.
_EXCLUDED_CATEGORIES = {"Housing", "Income"}


def _amounts_consistent(amounts: list[float]) -> bool:
    """All amounts within SUBSCRIPTION_AMOUNT_VARIANCE of the median."""
    if len(amounts) < 2:
        return True
    median = sorted(amounts)[len(amounts) // 2]
    if median == 0:
        return False
    return all(
        abs(a - median) / median <= SUBSCRIPTION_AMOUNT_VARIANCE for a in amounts
    )


def _classify_interval(avg_gap_days: float) -> str | None:
    if SUBSCRIPTION_MIN_INTERVAL_DAYS <= avg_gap_days <= SUBSCRIPTION_MAX_INTERVAL_DAYS:
        return "monthly"
    if SUBSCRIPTION_QUARTERLY_MIN_DAYS <= avg_gap_days <= SUBSCRIPTION_QUARTERLY_MAX_DAYS:
        return "quarterly"
    if SUBSCRIPTION_ANNUAL_MIN_DAYS <= avg_gap_days <= SUBSCRIPTION_ANNUAL_MAX_DAYS:
        return "annual"
    return None


def detect_subscriptions(
    df: pd.DataFrame,
    merchant_col: str = "Merchant",
    category_col: str = "Category",
    date_col: str = "Date",
    amount_col: str = "Amount",
    type_col: str = "Type",
    as_of_date: pd.Timestamp | None = None,
) -> list[dict]:
    """
    Returns a list of detected subscriptions, one dict per merchant flagged
    as recurring:
        {
            merchant, billing_cycle ("monthly"/"quarterly"/"annual"),
            amount, monthly_cost, annualized_cost, occurrences,
            first_charge, last_charge, is_forgotten, confidence
        }
    """
    if as_of_date is None:
        as_of_date = pd.to_datetime(df[date_col]).max()

    work = df[df[type_col].str.upper() == "DEBIT"].copy()
    work[date_col] = pd.to_datetime(work[date_col])

    # Merchant -> category lookup, built once, used to skip excluded
    # categories (Rent under Housing, Salary under Income, etc.)
    merchant_category = work.groupby(merchant_col)[category_col].first().to_dict()

    results = []

    for merchant, group in work.groupby(merchant_col):
        if merchant_category.get(merchant) in _EXCLUDED_CATEGORIES:
            continue

        group = group.sort_values(date_col)
        n = len(group)

        amounts = group[amount_col].tolist()
        dates = group[date_col].tolist()

        if n >= SUBSCRIPTION_MIN_OCCURRENCES:
            gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            avg_gap = sum(gaps) / len(gaps)
            cycle = _classify_interval(avg_gap)
            consistent_amount = _amounts_consistent(amounts)

            if cycle and consistent_amount:
                median_amount = sorted(amounts)[len(amounts) // 2]
                monthly_cost = {
                    "monthly": median_amount,
                    "quarterly": median_amount / 3,
                    "annual": median_amount / 12,
                }[cycle]

                months_active = (as_of_date - dates[0]).days / 30
                is_forgotten = (
                    months_active >= FORGOTTEN_MONTHS_ACTIVE
                    and median_amount <= FORGOTTEN_MAX_AMOUNT
                )

                results.append({
                    "merchant": merchant,
                    "billing_cycle": cycle,
                    "amount": round(median_amount, 2),
                    "monthly_cost": round(monthly_cost, 2),
                    "annualized_cost": round(monthly_cost * 12, 2),
                    "occurrences": n,
                    "first_charge": dates[0].date().isoformat(),
                    "last_charge": dates[-1].date().isoformat(),
                    "is_forgotten": is_forgotten,
                    "confidence": 95 if cycle == "monthly" else 85,
                })
                continue

        # Single-charge / non-recurring edge case (e.g. Amazon Prime bought
        # once inside this window): interval can't be measured, so we do NOT
        # guess. A genuinely annual subscription needs >=2 charges (i.e.
        # >=12-13 months of data) for this detector to confirm it. Documented
        # limitation, left undetected here rather than heuristically guessed.

    return results