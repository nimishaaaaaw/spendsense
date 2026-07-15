"""
Merchant rule table for the categorization engine.

Each entry:
- merchant: canonical name (matches TrueMerchant in transactions_truth.csv)
- category: matches TrueCategory in transactions_truth.csv
- is_subscription: matches IsSubscription in transactions_truth.csv
- keywords: substrings to match against the CLEANED (uppercased) description.
            Order matters within the overall MERCHANT_RULES list -- more specific
            entries (e.g. refunds, parent-company names) are placed before the
            generic merchant they could be confused with.

NOTE: Friend Transfer / P2P is intentionally NOT in this table. Real UPI handles
with real names aren't a fixed keyword set -- it's detected separately via a
P2P heuristic in categorizer.py (per SpendSense.docx section 2).
"""

MERCHANT_RULES = [
    # --- Refunds must come before Swiggy's generic rule (known ordering bug) ---
    {
        "merchant": "Refund-Swiggy",
        "category": "Refund",
        "is_subscription": False,
        "keywords": ["SWIGGY REFUND"],
    },

    # --- Amazon Prime must come before generic Amazon (subset-string collision) ---
    {
        "merchant": "Amazon Prime",
        "category": "Subscription-Entertainment",
        "is_subscription": True,
        "keywords": ["AMAZON PRIME MEMBERSHIP", "AMAZON PRIME"],
    },

    # --- Food delivery ---
    {
        "merchant": "Swiggy",
        "category": "Food Delivery",
        "is_subscription": False,
        "keywords": ["SWIGGY", "BUNDL TECHNOLOGIES"],
    },
    {
        "merchant": "Zomato",
        "category": "Food Delivery",
        "is_subscription": False,
        "keywords": ["ZOMATO"],
    },

    # --- Shopping ---
    {
        "merchant": "Amazon",
        "category": "Shopping",
        "is_subscription": False,
        "keywords": ["AMAZON PAY", "AMAZN PAY", "AMAZON SELLER SERVICES"],
    },
    {
        "merchant": "Flipkart",
        "category": "Shopping",
        "is_subscription": False,
        "keywords": ["FLIPKART"],
    },
    {
        "merchant": "Myntra",
        "category": "Shopping",
        "is_subscription": False,
        "keywords": ["MYNTRA"],
    },

    # --- Transport ---
    {
        "merchant": "Uber",
        "category": "Transport",
        "is_subscription": False,
        "keywords": ["UBER"],
    },
    {
        "merchant": "Ola",
        "category": "Transport",
        "is_subscription": False,
        "keywords": ["OLA CABS", "ANI TECHNOLOGIES"],
    },

    # --- Subscriptions: Entertainment ---
    {
        "merchant": "Netflix",
        "category": "Subscription-Entertainment",
        "is_subscription": True,
        "keywords": ["NETFLIX"],
    },
    {
        "merchant": "Spotify",
        "category": "Subscription-Entertainment",
        "is_subscription": True,
        "keywords": ["SPOTIFY"],
    },
    {
        "merchant": "Hotstar",
        "category": "Subscription-Entertainment",
        "is_subscription": True,
        "keywords": ["NOVI DIGITAL ENTERTAINMENT", "HOTSTAR"],
    },

    # --- Subscriptions: Fitness / Wellness ---
    {
        "merchant": "CultFit",
        "category": "Subscription-Fitness",
        "is_subscription": True,
        "keywords": ["CURE FIT HEALTHCARE", "CULTFIT"],
    },
    {
        "merchant": "Local Gym",
        "category": "Subscription-Fitness",
        "is_subscription": True,
        "keywords": ["FITZONE"],
    },
    {
        "merchant": "MindWell App",
        "category": "Subscription-Wellness",
        "is_subscription": True,
        "keywords": ["MINDWELL"],
    },

    # --- Utilities ---
    {
        "merchant": "Electricity Board",
        "category": "Utilities",
        "is_subscription": False,
        "keywords": ["BSES RAJDHANI POWER", "ELECTRICITY BILL"],
    },
    {
        "merchant": "Broadband",
        "category": "Utilities",
        "is_subscription": True,
        "keywords": ["AIRTEL BROADBAND", "BHARTI AIRTEL"],
    },
    {
        "merchant": "Mobile Recharge",
        "category": "Utilities",
        "is_subscription": False,
        "keywords": ["JIO RECHARGE"],
    },

    # --- Housing / Income ---
    {
        "merchant": "Rent",
        "category": "Housing",
        "is_subscription": False,
        "keywords": ["LANDLORD TRANSFER", "RENT PAYMENT"],
    },
    {
        "merchant": "Salary",
        "category": "Income",
        "is_subscription": False,
        "keywords": ["TECHCORP SOLUTIONS"],
    },

    # --- Groceries ---
    {
        "merchant": "Big Bazaar/Grocery",
        "category": "Groceries",
        "is_subscription": False,
        "keywords": ["BIGBASKET", "DMART RETAIL", "ZEPTO", "BLINKIT INSTAMART"],
    },

    # --- Entertainment (non-subscription) ---
    {
        "merchant": "Movie/PVR",
        "category": "Entertainment",
        "is_subscription": False,
        "keywords": ["PVR CINEMAS", "PVR LIMITED"],
    },

    # --- Health ---
    {
        "merchant": "Pharmacy",
        "category": "Health",
        "is_subscription": False,
        "keywords": ["PHARMEASY", "APOLLO PHARMACY"],
    },
]

# Flat set of merchant names considered "subscriptions" -- convenience export
# for subscription_detector.py so it doesn't have to re-derive this from rules.
SUBSCRIPTION_MERCHANTS = {
    rule["merchant"] for rule in MERCHANT_RULES if rule["is_subscription"]
}