import pandas as pd

from app.core.categorizer import categorize_df
from app.core.subscription_detector import detect_subscriptions

raw = pd.read_csv("data/transactions_raw.csv")
categorized = categorize_df(raw)
subs = detect_subscriptions(categorized)

print("Detected subscriptions:\n")

for s in subs:
    print(
        f"{s['merchant']} | "
        f"{s['billing_cycle']} | "
        f"{s['amount']} | "
        f"forgotten: {s['is_forgotten']}"
    )

truth = pd.read_csv("data/transactions_truth.csv")

true_subs = truth[truth["IsSubscription"]]["TrueMerchant"].unique()
detected = {s["merchant"] for s in subs}

print("\n----------------------------------------")
print("True subscription merchants:")
print(sorted(true_subs))

print("\nDetected merchants:")
print(sorted(detected))

print("\nMissed:")
print(sorted(set(true_subs) - detected))