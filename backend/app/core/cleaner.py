"""
Text cleaning for raw bank/UPI transaction descriptions.

Strips noise that varies per-transaction (ref numbers, UPI handles, POS
terminal codes) while preserving the merchant-identifying tokens that
merchant_dict.py keywords match against.

Design note: we clean to UPPERCASE with noise removed, but we deliberately
do NOT strip merchant name/legal-suffix words (LTD, PVT, LIMITED etc.) --
some merchant keywords (e.g. "BUNDL TECHNOLOGIES PVT LTD" -> we match on
"BUNDL TECHNOLOGIES", so the suffix is harmless either way) rely on partial
substring matches, so aggressive suffix-stripping isn't necessary and risks
deleting real signal. We only strip things that are PURELY noise: numbers,
ref codes, UPI handles, prefixes.
"""

import re

# Transaction rail prefixes seen in generate_dataset.py variants
_RAIL_PREFIXES = re.compile(r"\b(UPI|POS|NEFT|IMPS|BBPS)\b", re.IGNORECASE)

# UPI handle pattern: something@bank, e.g. "swiggy@axisbank", "priyasharma22@ybl"
_UPI_HANDLE = re.compile(r"\b[\w.]+@[\w]+\b")

# Long digit runs: transaction ref numbers (6-digit random refs from generator),
# POS terminal codes (4-digit), account-like numbers.
_DIGIT_RUN = re.compile(r"\b\d{4,}\b")

# Trailing/standalone tag words the generator appends: -PAYMENT, -RECURRING,
# -AUTOPAY, -REFUND, -RETRY etc. Keep REFUND as a word (categorizer needs it
# via the "SWIGGY REFUND" keyword) -- only strip pure connector noise.
_TAG_WORDS = re.compile(
    r"\b(PAYMENT|RECURRING|AUTOPAY|TRIP)\b", re.IGNORECASE
)

# Collapse repeated separators/whitespace left behind after stripping
_MULTI_SEP = re.compile(r"[-_]{2,}")
_MULTI_SPACE = re.compile(r"\s{2,}")


def clean(description: str) -> str:
    """
    Normalize a raw transaction description for keyword/fuzzy matching.

    Steps:
    1. Uppercase (keyword table and fuzzy matching both assume uppercase).
    2. Remove UPI handles (user@bank style) -- these are per-transaction noise.
    3. Remove rail prefixes (UPI-, POS, NEFT-, IMPS-, BBPS).
    4. Remove long digit runs (ref numbers, POS terminal codes).
    5. Remove generic tag words that add no merchant signal.
    6. Collapse leftover separators/whitespace, strip edges.
    """
    if not isinstance(description, str) or not description.strip():
        return ""

    text = description.upper()
    text = _UPI_HANDLE.sub(" ", text)
    text = _RAIL_PREFIXES.sub(" ", text)
    text = _DIGIT_RUN.sub(" ", text)
    text = _TAG_WORDS.sub(" ", text)

    # Replace remaining separators with spaces for consistent tokenization
    text = text.replace("-", " ").replace("_", " ")
    text = _MULTI_SEP.sub(" ", text)
    text = _MULTI_SPACE.sub(" ", text)

    return text.strip()