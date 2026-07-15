"""
Insights engine.

Computes the analytics shown on the dashboard/insights pages:
  - weekday vs weekend spending comparison
  - month-over-month category trends
  - top spending-leak categories (small + frequent transactions)
  - spending velocity after salary credit
  - total subscription bleed (delegates to subscription_detector output)

All functions take an already-categorized DataFrame (output of categorize_df)
plus, where needed, the subscription list (output of detect_subscriptions).
Nothing here touches ground truth -- these are descriptive stats over
predicted categories, exactly as a real deployment would compute them.
"""

import pandas as pd


def weekday_vs_weekend(df: pd.DataFrame, date_col: str = "Date", amount_col: str = "Amount", type_col: str = "Type") -> dict:
    """
    Compares total DEBIT spend on weekdays vs weekends.
    Returns totals and a ratio (weekend / weekday), guarding against
    div-by-zero if there's no weekday spend in the window.
    """
    work = df[df[type_col].str.upper() == "DEBIT"].copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work["is_weekend"] = work[date_col].dt.weekday >= 5

    weekday_total = work.loc[~work["is_weekend"], amount_col].sum()
    weekend_total = work.loc[work["is_weekend"], amount_col].sum()

    weekday_count = int((~work["is_weekend"]).sum())
    weekend_count = int(work["is_weekend"].sum())

    ratio = (weekend_total / weekday_total) if weekday_total > 0 else None

    return {
        "weekday_total": round(weekday_total, 2),
        "weekend_total": round(weekend_total, 2),
        "weekday_count": weekday_count,
        "weekend_count": weekend_count,
        "weekend_to_weekday_ratio": round(ratio, 2) if ratio is not None else None,
    }


def monthly_category_trends(df: pd.DataFrame, date_col: str = "Date", amount_col: str = "Amount", category_col: str = "Category", type_col: str = "Type") -> list[dict]:
    """
    Month-over-month totals per category. Returns a list of
    {category, month, total, prev_month_total, pct_change} sorted by month.
    pct_change is None for a category's first appearance (no prior month
    to compare against) or when the previous month's total was zero.
    """
    work = df[df[type_col].str.upper() == "DEBIT"].copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work["month"] = work[date_col].dt.to_period("M").astype(str)

    grouped = (
        work.groupby(["month", category_col])[amount_col]
        .sum()
        .reset_index()
        .sort_values([category_col, "month"])
    )
    grouped.columns = ["month", "category", "total"]

    results = []
    for category, cat_group in grouped.groupby("category"):
        cat_group = cat_group.sort_values("month").reset_index(drop=True)
        prev_total = None
        for _, row in cat_group.iterrows():
            pct_change = None
            if prev_total is not None and prev_total > 0:
                pct_change = round(((row["total"] - prev_total) / prev_total) * 100, 1)
            results.append({
                "category": category,
                "month": row["month"],
                "total": round(row["total"], 2),
                "prev_month_total": round(prev_total, 2) if prev_total is not None else None,
                "pct_change": pct_change,
            })
            prev_total = row["total"]

    return results


def top_spending_leaks(df: pd.DataFrame, amount_col: str = "Amount", category_col: str = "Category", type_col: str = "Type", min_transaction_count: int = 4, top_n: int = 5) -> list[dict]:
    """
    Identifies "leak" categories: many small, frequent transactions that add
    up. Ranked by total spend among categories with at least
    min_transaction_count transactions AND a below-median average transaction
    size (i.e. "small + frequent", not just "high total" -- a single ₹14,000
    rent payment has a high total but isn't a leak; ten ₹150 coffee/snack
    purchases are).
    """
    work = df[df[type_col].str.upper() == "DEBIT"].copy()

    agg = work.groupby(category_col)[amount_col].agg(["sum", "mean", "count"]).reset_index()
    agg.columns = ["category", "total", "avg_transaction", "count"]

    frequent = agg[agg["count"] >= min_transaction_count]
    if frequent.empty:
        return []

    median_avg_txn = frequent["avg_transaction"].median()
    leaks = frequent[frequent["avg_transaction"] <= median_avg_txn]
    leaks = leaks.sort_values("total", ascending=False).head(top_n)

    return [
        {
            "category": row["category"],
            "total": round(row["total"], 2),
            "avg_transaction": round(row["avg_transaction"], 2),
            "count": int(row["count"]),
        }
        for _, row in leaks.iterrows()
    ]


def spending_velocity(df: pd.DataFrame, date_col: str = "Date", amount_col: str = "Amount", type_col: str = "Type", category_col: str = "Category", salary_category: str = "Income") -> dict:
    """
    Measures how fast money is spent after each salary credit: for each
    salary credit date, sums DEBIT spend in the following 7 days and
    computes what % of the salary that represents. Returns the average
    across all salary credits found plus a qualitative label.

    Returns velocity_label of "slow" / "moderate" / "fast" based on average
    7-day-post-salary spend as a % of that salary credit. Thresholds are a
    simple, explainable split (not calibrated against any labeled data,
    since no ground truth exists for "velocity" in transactions_truth.csv --
    this is a heuristic, and is labeled as such in the response schema).
    """
    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work[type_col] = work[type_col].str.upper()

    salary_credits = work[
        (work[type_col] == "CREDIT") & (work[category_col] == salary_category)
    ].sort_values(date_col)

    if salary_credits.empty:
        return {
            "average_pct_spent_within_7_days": None,
            "velocity_label": "unknown",
            "salary_events_analyzed": 0,
        }

    debits = work[work[type_col] == "DEBIT"]

    pct_spent_list = []
    for _, credit_row in salary_credits.iterrows():
        salary_amt = credit_row[amount_col]
        if salary_amt <= 0:
            continue
        window_start = credit_row[date_col]
        window_end = window_start + pd.Timedelta(days=7)
        spent_in_window = debits[
            (debits[date_col] >= window_start) & (debits[date_col] < window_end)
        ][amount_col].sum()
        pct_spent_list.append((spent_in_window / salary_amt) * 100)

    if not pct_spent_list:
        return {
            "average_pct_spent_within_7_days": None,
            "velocity_label": "unknown",
            "salary_events_analyzed": 0,
        }

    avg_pct = sum(pct_spent_list) / len(pct_spent_list)

    if avg_pct < 20:
        label = "slow"
    elif avg_pct < 40:
        label = "moderate"
    else:
        label = "fast"

    return {
        "average_pct_spent_within_7_days": round(avg_pct, 1),
        "velocity_label": label,
        "salary_events_analyzed": len(pct_spent_list),
    }


def subscription_bleed(subscriptions: list[dict]) -> dict:
    """
    Aggregates subscription_detector output into a single bleed figure.
    Takes the already-computed subscription list rather than recomputing
    detection, so this stays a pure aggregation step.
    """
    if not subscriptions:
        return {"total_monthly": 0.0, "total_annual": 0.0, "count": 0, "forgotten_count": 0}

    total_monthly = sum(s["monthly_cost"] for s in subscriptions)
    total_annual = sum(s["annualized_cost"] for s in subscriptions)
    forgotten_count = sum(1 for s in subscriptions if s["is_forgotten"])

    return {
        "total_monthly": round(total_monthly, 2),
        "total_annual": round(total_annual, 2),
        "count": len(subscriptions),
        "forgotten_count": forgotten_count,
    }