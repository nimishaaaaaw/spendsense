"""
SpendSense - Synthetic Transaction Dataset Generator
-------------------------------------------------------
Generates a realistic, intentionally messy 6-month bank/UPI transaction
history for a fictional young professional in India. The messiness
(merchant name variants, edge cases, irregular subscriptions) is
deliberate -- it's what makes the categorization + subscription
detection engine a real engineering problem instead of a lookup table.

Run: python3 generate_dataset.py
Output: data/transactions_raw.csv  (the "as exported from bank" version)
        data/transactions_truth.csv (same rows + a hidden ground-truth
                                     category/subscription label, used
                                     ONLY for evaluating your categorizer
                                     accuracy later -- not for building it)
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible runs

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 6, 30)
TOTAL_DAYS = (END_DATE - START_DATE).days

# ---------------------------------------------------------------------------
# 1. MERCHANT DEFINITIONS
# Each merchant has several real-world-style "raw text variants" because
# the same merchant appears differently depending on payment rail
# (UPI handle vs POS terminal vs NEFT vs subscription auto-debit).
# ---------------------------------------------------------------------------

MERCHANTS = {
    "Swiggy": {
        "category": "Food Delivery",
        "variants": [
            "UPI-SWIGGY-swiggy.{n}@ybl-{ref}-PAYMENT",
            "UPI-Swiggy Limited-swiggy@axisbank-{ref}",
            "BUNDL TECHNOLOGIES PVT LTD-{ref}",  # Swiggy's actual parent co. name
            "POS 4521 SWIGGY BANGALORE",
        ],
        "amount_range": (120, 600),
        "freq_per_month": (5, 11),
        "weekend_bias": 1.4,
    },
    "Zomato": {
        "category": "Food Delivery",
        "variants": [
            "UPI-ZOMATO-zomato.{n}@icici-{ref}",
            "UPI-Zomato Limited-{ref}-PAYMENT",
            "POS 7782 ZOMATO ONLINE",
        ],
        "amount_range": (150, 600),
        "freq_per_month": (3, 7),
        "weekend_bias": 1.3,
    },
    "Amazon": {
        "category": "Shopping",
        "variants": [
            "UPI-AMAZON PAY-amazonpay@apl-{ref}",
            "AMAZN PAY IND-{ref}",
            "POS 1190 AMAZON PAY INDIA",
            "AMAZON SELLER SERVICES-{ref}",
        ],
        "amount_range": (199, 2200),
        "freq_per_month": (1, 4),
        "weekend_bias": 1.1,
    },
    "Flipkart": {
        "category": "Shopping",
        "variants": [
            "UPI-FLIPKART-flipkart.{n}@hdfcbank-{ref}",
            "FLIPKART INTERNET PVT LTD-{ref}",
        ],
        "amount_range": (299, 1800),
        "freq_per_month": (0, 2),
        "weekend_bias": 1.1,
    },
    "Uber": {
        "category": "Transport",
        "variants": [
            "UPI-UBER INDIA-uber.payments@hdfcbank-{ref}",
            "UBER INDIA SYSTEMS-{ref}",
            "POS 3321 UBER TRIP",
        ],
        "amount_range": (80, 450),
        "freq_per_month": (8, 20),
        "weekend_bias": 1.2,
    },
    "Ola": {
        "category": "Transport",
        "variants": [
            "UPI-OLA CABS-olamoney@icici-{ref}",
            "ANI TECHNOLOGIES PVT LTD-{ref}",  # Ola's actual parent co. name
        ],
        "amount_range": (70, 400),
        "freq_per_month": (3, 9),
        "weekend_bias": 1.0,
    },
    "Netflix": {
        "category": "Subscription-Entertainment",
        "variants": ["NETFLIX.COM-{ref}-RECURRING", "UPI-NETFLIX-netflix@icici-{ref}"],
        "amount_range": (199, 199),
        "subscription": True,
        "monthly_day": 3,
    },
    "Spotify": {
        "category": "Subscription-Entertainment",
        "variants": ["SPOTIFY INDIA-{ref}-AUTOPAY", "UPI-SPOTIFY-spotify@axisbank-{ref}"],
        "amount_range": (119, 119),
        "subscription": True,
        "monthly_day": 11,
    },
    "Hotstar": {
        "category": "Subscription-Entertainment",
        "variants": ["NOVI DIGITAL ENTERTAINMENT-{ref}"],  # Hotstar's parent co.
        "amount_range": (299, 299),
        "subscription": True,
        "monthly_day": 17,
        "only_months": [1, 4],  # quarterly, not monthly -- edge case on purpose
    },
    "CultFit": {
        "category": "Subscription-Fitness",
        "variants": ["CURE FIT HEALTHCARE-{ref}-AUTOPAY", "UPI-CULTFIT-cultfit@ybl-{ref}"],
        "amount_range": (1499, 1499),
        "subscription": True,
        "monthly_day": 5,
    },
    "MindWell App": {
        # The "forgotten subscription" -- a meditation app free-trial-turned-
        # paid that the user stopped using around month 3 but never cancelled.
        "category": "Subscription-Wellness",
        "variants": ["MINDWELL TECHNOLOGIES-{ref}-AUTOPAY"],
        "amount_range": (149, 149),
        "subscription": True,
        "monthly_day": 21,
        "forgotten_after_month": 3,  # keeps charging, user stopped opening app
    },
    "Amazon Prime": {
        "category": "Subscription-Entertainment",
        "variants": ["AMAZON PRIME MEMBERSHIP-{ref}"],
        "amount_range": (1499, 1499),
        "subscription": True,
        "annual": True,
        "annual_month": 2,
    },
    "Local Gym": {
        "category": "Subscription-Fitness",
        "variants": ["UPI-FITZONE GYM-fitzone@ybl-{ref}", "FITZONE FITNESS CENTER-{ref}"],
        "amount_range": (1200, 1200),
        "subscription": True,
        "monthly_day": 1,
    },
    "Electricity Board": {
        "category": "Utilities",
        "variants": ["BSES RAJDHANI POWER LTD-{ref}", "UPI-ELECTRICITY BILL-bbps@upi-{ref}"],
        "amount_range": (800, 2400),
        "freq_per_month": (1, 1),
    },
    "Broadband": {
        "category": "Utilities",
        "variants": ["UPI-AIRTEL BROADBAND-airtel@paytm-{ref}", "BHARTI AIRTEL LTD-{ref}"],
        "amount_range": (799, 799),
        "subscription": True,
        "monthly_day": 4,
    },
    "Mobile Recharge": {
        "category": "Utilities",
        "variants": ["UPI-JIO RECHARGE-jio@icici-{ref}"],
        "amount_range": (299, 479),
        "freq_per_month": (1, 1),
    },
    "Rent": {
        "category": "Housing",
        "variants": ["NEFT-LANDLORD TRANSFER-{ref}", "IMPS-RENT PAYMENT-{ref}"],
        "amount_range": (14000, 14000),
        "freq_per_month": (1, 1),
    },
    "Salary": {
        "category": "Income",
        "variants": ["NEFT-TECHCORP SOLUTIONS PVT LTD-SAL-{ref}"],
        "amount_range": (42000, 42000),
        "monthly_day": 1,
        "is_credit": True,
    },
    "Big Bazaar/Grocery": {
        "category": "Groceries",
        "variants": [
            "UPI-BIGBASKET-bigbasket@ybl-{ref}",
            "POS 9012 DMART RETAIL",
            "UPI-ZEPTO-zepto@icici-{ref}",
            "BLINKIT INSTAMART-{ref}",
        ],
        "amount_range": (150, 1400),
        "freq_per_month": (4, 9),
        "weekend_bias": 1.2,
    },
    "Friend Transfer": {
        # P2P transfer that LOOKS like it could be miscategorized as a
        # business transaction -- deliberate ambiguous edge case.
        "category": "Personal Transfer",
        "variants": [
            "UPI-{friend}-{friend_handle}@ybl-{ref}-PAYMENT",
            "UPI-{friend}-{friend_handle}@paytm-{ref}",
        ],
        "amount_range": (100, 1800),
        "freq_per_month": (2, 5),
        "weekend_bias": 1.3,
        "is_p2p": True,
    },
    "Movie/PVR": {
        "category": "Entertainment",
        "variants": ["UPI-PVR CINEMAS-pvr@hdfcbank-{ref}", "PVR LIMITED-{ref}"],
        "amount_range": (300, 900),
        "freq_per_month": (0, 3),
        "weekend_bias": 2.0,
    },
    "Myntra": {
        "category": "Shopping",
        "variants": ["UPI-MYNTRA-myntra@icici-{ref}", "MYNTRA DESIGNS PVT LTD-{ref}"],
        "amount_range": (399, 1800),
        "freq_per_month": (0, 2),
        "weekend_bias": 1.0,
    },
    "Pharmacy": {
        "category": "Health",
        "variants": ["UPI-PHARMEASY-pharmeasy@ybl-{ref}", "POS 2210 APOLLO PHARMACY"],
        "amount_range": (100, 900),
        "freq_per_month": (0, 3),
        "weekend_bias": 0.8,
    },
    "Refund-Swiggy": {
        # Edge case: a refund that should net against an earlier debit
        "category": "Refund",
        "variants": ["UPI-SWIGGY REFUND-swiggy.{n}@ybl-{ref}-REFUND"],
        "amount_range": (120, 650),
        "freq_per_month": (0, 1),
        "is_credit": True,
        "rare": True,
    },
}

FRIEND_NAMES = [
    ("Priya Sharma", "priyasharma22"),
    ("Rohan Mehta", "rohan.mehta"),
    ("Ananya Iyer", "ananya.iyer"),
    ("Karan Verma", "karanv90"),
]

# ---------------------------------------------------------------------------
# 2. HELPERS
# ---------------------------------------------------------------------------

def daterange(start, end):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)

def random_ref(n=6):
    return "".join(random.choice("0123456789") for _ in range(n))

def is_weekend(d):
    return d.weekday() >= 5

def month_index(d):
    return (d.year - START_DATE.year) * 12 + (d.month - START_DATE.month) + 1  # 1-based

def pick_variant(template, ref, friend=None, friend_handle=None):
    n = random.randint(1, 99)
    text = template.format(n=n, ref=ref, friend=(friend or ""), friend_handle=(friend_handle or ""))
    return text

# ---------------------------------------------------------------------------
# 3. GENERATE TRANSACTIONS
# ---------------------------------------------------------------------------

rows = []  # each: dict with Date, Description, Amount, Type (Debit/Credit)
truth = []  # parallel ground-truth: Date, Description, TrueMerchant, TrueCategory, IsSubscription

STARTING_BALANCE = 35000.0

def add_txn(d, merchant_name, info, amount, is_credit=False, friend=None, friend_handle=None):
    # NOTE: balance is intentionally NOT computed here. Transactions are
    # generated out of chronological order (fixed-monthly pass, then
    # variable-frequency pass), and only sorted by date afterward. Computing
    # a running balance during generation would scramble it. We compute the
    # real running balance in a single final pass after sorting (see below).
    template = random.choice(info["variants"])
    desc = pick_variant(template, random_ref(), friend, friend_handle)
    txn_type = "CREDIT" if (is_credit or info.get("is_credit")) else "DEBIT"
    rows.append({
        "Date": d.isoformat(),
        "Description": desc,
        "Amount": round(amount, 2),
        "Type": txn_type,
    })
    truth.append({
        "Date": d.isoformat(),
        "Description": desc,
        "TrueMerchant": merchant_name,
        "TrueCategory": info["category"],
        "IsSubscription": bool(info.get("subscription", False)),
    })

# Defensive check: a merchant must be handled by exactly ONE of the two
# generation passes below (fixed-monthly OR variable-frequency), never both.
# This guards against the exact bug we hit during testing, where Rent and
# utilities had both "monthly_day" and "freq_per_month" set and got charged
# 2-3x per month instead of once.
for _name, _info in MERCHANTS.items():
    if "monthly_day" in _info and "freq_per_month" in _info:
        raise ValueError(
            f"{_name} has both 'monthly_day' and 'freq_per_month' set -- "
            "it will be double-counted. Pick one generation strategy."
        )

# --- 3a. Fixed monthly items: salary, rent, EMIs, subscriptions, utilities ---
current = START_DATE
while current <= END_DATE:
    mi = month_index(current)
    for name, info in MERCHANTS.items():
        if info.get("rare"):
            continue
        if info.get("annual"):
            if current.month == info["annual_month"] and current.day == 1:
                add_txn(current, name, info, info["amount_range"][0])
            continue
        if "monthly_day" in info:
            if info.get("only_months") and current.month not in info["only_months"]:
                continue
            # NOTE: "forgotten_after_month" is intentionally NOT used to stop
            # the charge -- that's the whole point of MindWell App as a
            # "forgotten subscription" edge case. The user stopped USING it
            # but it keeps auto-charging every month regardless. The field
            # exists so a future "usage log" feature could reference it.
            if current.day == info["monthly_day"]:
                amt = info["amount_range"][0]
                add_txn(current, name, info, amt)
    current += timedelta(days=1)

# --- 3b. Variable-frequency spending (food, transport, shopping, groceries) ---
for name, info in MERCHANTS.items():
    if "freq_per_month" not in info or info.get("rare"):
        continue
    lo, hi = info["freq_per_month"]
    for month_offset in range(6):
        month_start = date(2026, month_offset + 1, 1)
        if month_start > END_DATE:
            break
        month_end = date(2026, month_offset + 1, 28)
        n_txns = random.randint(lo, hi)
        for _ in range(n_txns):
            # bias toward weekends if weekend_bias > 1
            for _attempt in range(5):
                day_offset = random.randint(0, 27)
                d = month_start + timedelta(days=day_offset)
                if d > END_DATE:
                    continue
                bias = info.get("weekend_bias", 1.0)
                if is_weekend(d) and random.random() < (bias - 1.0) * 0.4:
                    break
                if not is_weekend(d):
                    break
            amt = round(random.uniform(*info["amount_range"]), 2)
            if name == "Friend Transfer":
                friend, handle = random.choice(FRIEND_NAMES)
                add_txn(d, name, info, amt, friend=friend, friend_handle=handle)
            else:
                add_txn(d, name, info, amt)

# --- 3c. A couple of rare edge-case refunds ---
refund_info = MERCHANTS["Refund-Swiggy"]
for _ in range(2):
    d = START_DATE + timedelta(days=random.randint(20, TOTAL_DAYS - 20))
    add_txn(d, "Refund-Swiggy", refund_info, round(random.uniform(150, 400), 2), is_credit=True)

# --- 3d. One duplicate/failed-then-retried transaction edge case ---
dup_day = date(2026, 3, 14)
dup_info = MERCHANTS["Amazon"]
add_txn(dup_day, "Amazon", dup_info, 1999.00)
add_txn(dup_day, "Amazon", dup_info, 1999.00)  # looks like a duplicate charge

# --- 3e. Sort everything chronologically (bank exports always are) ---
# Sort by date only; for same-day transactions, shuffle order slightly so it
# doesn't look machine-generated (real statements don't list same-day
# transactions in a suspiciously clean order), but keep it deterministic.
combined = list(zip(rows, truth))
combined.sort(key=lambda pair: (pair[0]["Date"], random.random()))
rows = [r for r, t in combined]
truth = [t for r, t in combined]

# --- 3f. Compute the running balance in one correct, chronological pass ---
# This MUST happen after sorting, and only once, or the balance column
# becomes inconsistent (this bit me during testing -- computing balance
# while generating, before the final sort, scrambled it completely).
running_balance = STARTING_BALANCE
for r in rows:
    signed_amount = r["Amount"] if r["Type"] == "CREDIT" else -r["Amount"]
    running_balance += signed_amount
    r["Balance"] = round(running_balance, 2)

# ---------------------------------------------------------------------------
# 4. WRITE CSVs
# ---------------------------------------------------------------------------

with open("data/transactions_raw.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Date", "Description", "Amount", "Type", "Balance"])
    writer.writeheader()
    writer.writerows(rows)

with open("data/transactions_truth.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Date", "Description", "TrueMerchant", "TrueCategory", "IsSubscription"])
    writer.writeheader()
    writer.writerows(truth)

print(f"Generated {len(rows)} transactions from {START_DATE} to {END_DATE}")
print(f"Files written: data/transactions_raw.csv, data/transactions_truth.csv")
