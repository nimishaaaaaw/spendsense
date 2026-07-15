import pandas as pd

from app.core.categorizer import categorize_df
from app.core.subscription_detector import detect_subscriptions
from app.core.insights import (
    weekday_vs_weekend,
    top_spending_leaks,
    spending_velocity,
    subscription_bleed,
)

raw = pd.read_csv("data/transactions_raw.csv")
categorized = categorize_df(raw)
subs = detect_subscriptions(categorized)

print("Weekday vs Weekend:")
print(weekday_vs_weekend(categorized))

print("\nTop leaks:")
print(top_spending_leaks(categorized))

print("\nVelocity:")
print(spending_velocity(categorized))

print("\nSubscription bleed:")
print(subscription_bleed(subs))