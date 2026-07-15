"""
Categorization engine.

Pipeline (per SpendSense.docx section 2):
  clean() -> rule_match() -> fuzzy_match() -> P2P heuristic -> uncategorized

categorize_df() runs this over a full DataFrame and overlays the P2P heuristic,
matching the brief's "DataFrame-level with P2P heuristic overlay" description.
"""

import re
import pandas as pd
from rapidfuzz import fuzz

from app.core.cleaner import clean
from app.core.merchant_dict import MERCHANT_RULES
from app.config import FUZZY_MATCH_THRESHOLD

# Heuristic signal for P2P transfers: personal UPI handles in the generator
# look like "firstname.lastname@bank" or "firstnameNN@bank" with a real-looking
# name preceding it in the raw description (e.g. "UPI-Priya Sharma-..."), and
# critically they do NOT match any known merchant rule. We detect P2P by:
#   1. Description (raw, before cleaning) contains a personal-name pattern
#      immediately after the UPI- prefix (Title Case two-word name), AND
#   2. No merchant rule matched.
_PERSON_NAME_PATTERN = re.compile(r"UPI-([A-Z][a-z]+ [A-Z][a-z]+)-", re.IGNORECASE)


def rule_match(cleaned_text: str) -> dict | None:
    """
    Keyword lookup against MERCHANT_RULES, preserving table order so that
    more-specific entries (e.g. Refund-Swiggy, Amazon Prime) placed earlier
    in the table win over generic ones they could collide with.
    """
    if not cleaned_text:
        return None
    for rule in MERCHANT_RULES:
        for kw in rule["keywords"]:
            if kw in cleaned_text:
                return {
                    "merchant": rule["merchant"],
                    "category": rule["category"],
                    "is_subscription": rule["is_subscription"],
                    "match_method": "rule",
                    "confidence": 100,
                }
    return None


def fuzzy_match(cleaned_text: str, threshold: int = FUZZY_MATCH_THRESHOLD) -> dict | None:
    """
    Fallback fuzzy match using rapidfuzz token_set_ratio against each rule's
    merchant name and keyword phrases. Catches abbreviations / typos / minor
    variants that don't contain an exact keyword substring.
    """
    if not cleaned_text:
        return None

    best_score = 0
    best_rule = None
    for rule in MERCHANT_RULES:
        candidates = [rule["merchant"]] + rule["keywords"]
        for candidate in candidates:
            score = fuzz.token_set_ratio(cleaned_text, candidate.upper())
            if score > best_score:
                best_score = score
                best_rule = rule

    if best_rule and best_score >= threshold:
        return {
            "merchant": best_rule["merchant"],
            "category": best_rule["category"],
            "is_subscription": best_rule["is_subscription"],
            "match_method": "fuzzy",
            "confidence": round(best_score, 1),
        }
    return None


def categorize(raw_description: str, overrides: dict[str, dict] | None = None) -> dict:
    """
    Single-row categorization pipeline.

    overrides: optional dict of {cleaned_description: {merchant, category,
    is_subscription}} representing user corrections from a previous session
    (feature 5 -- "engine remembers that merchant going forward").
    """
    cleaned = clean(raw_description)

    if overrides and cleaned in overrides:
        override = overrides[cleaned]
        return {
            "merchant": override["merchant"],
            "category": override["category"],
            "is_subscription": override.get("is_subscription", False),
            "match_method": "user_override",
            "confidence": 100,
            "cleaned_text": cleaned,
        }

    result = rule_match(cleaned)
    if result is None:
        result = fuzzy_match(cleaned)
    if result is None:
        # P2P check happens at categorize_df level (needs raw, pre-clean text);
        # single-row path flags uncategorized here and categorize_df overlays P2P.
        result = {
            "merchant": "Uncategorized",
            "category": "Uncategorized",
            "is_subscription": False,
            "match_method": "none",
            "confidence": 0,
        }

    result["cleaned_text"] = cleaned
    return result


def _is_p2p(raw_description: str) -> str | None:
    """
    Returns the extracted person name if the raw description matches the
    P2P transfer pattern, else None.
    """
    match = _PERSON_NAME_PATTERN.search(raw_description)
    return match.group(1) if match else None


def categorize_df(
    df: pd.DataFrame,
    description_col: str = "Description",
    overrides: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """
    Runs categorize() over every row, then overlays the P2P heuristic on
    rows that came back Uncategorized -- this fixes the known bug noted in
    the brief ("P2P detection not firing in single-row path") by running
    the name-pattern check against the RAW description at the DataFrame
    level, where we have full row context.

    Returns a copy of df with new columns: Merchant, Category, IsSubscription,
    MatchMethod, Confidence.
    """
    results = df[description_col].apply(lambda d: categorize(d, overrides))
    results_df = pd.DataFrame(list(results))

    out = df.copy()
    out["Merchant"] = results_df["merchant"]
    out["Category"] = results_df["category"]
    out["IsSubscription"] = results_df["is_subscription"]
    out["MatchMethod"] = results_df["match_method"]
    out["Confidence"] = results_df["confidence"]

    # P2P overlay: only touch rows still Uncategorized after rule+fuzzy
    # P2P overlay: only touch rows still Uncategorized after rule+fuzzy
    uncategorized_mask = out["Category"] == "Uncategorized"
    for idx in out[uncategorized_mask].index:
        raw_desc = out.at[idx, description_col]
        person_name = _is_p2p(raw_desc)
        if person_name:
            out.at[idx, "Merchant"] = "Friend Transfer"       # matches TrueMerchant schema
            out.at[idx, "Category"] = "Personal Transfer"
            out.at[idx, "IsSubscription"] = False
            out.at[idx, "MatchMethod"] = "p2p_heuristic"
            out.at[idx, "Confidence"] = 90
            out.at[idx, "CounterpartyName"] = person_name     # new: real name kept separately

    return out