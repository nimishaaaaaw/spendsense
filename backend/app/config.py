"""
Central configuration for SpendSense backend.

"""

# CORS: allows the Vite dev server. Adds prod frontend origin when deployed.
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Categorization thresholds
FUZZY_MATCH_THRESHOLD = 72  # rapidfuzz token_set_ratio cutoff (per brief)

# Subscription detection thresholds
SUBSCRIPTION_AMOUNT_VARIANCE = 0.10        # ±10% amount tolerance
SUBSCRIPTION_MIN_INTERVAL_DAYS = 25        # loosened from 28 to absorb jitter
SUBSCRIPTION_MAX_INTERVAL_DAYS = 35        # loosened from 32 to absorb jitter
SUBSCRIPTION_QUARTERLY_MIN_DAYS = 80
SUBSCRIPTION_QUARTERLY_MAX_DAYS = 100
SUBSCRIPTION_ANNUAL_MIN_DAYS = 350
SUBSCRIPTION_ANNUAL_MAX_DAYS = 380
SUBSCRIPTION_MIN_OCCURRENCES = 2           # need at least 2 charges to detect a pattern

# "Forgotten subscription" heuristic
FORGOTTEN_MONTHS_ACTIVE = 4   # charged for at least this many months
FORGOTTEN_MAX_AMOUNT = 500    # small-ticket charges are more likely to be forgotten (INR)

# Session store (in-memory, no persistence)
SESSION_TTL_MINUTES = 60