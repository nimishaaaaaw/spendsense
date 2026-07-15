"""
Categorizer regression tests.

These assert against the REAL verified baseline established during manual
testing: 100% merchant accuracy on the full 365-row generated dataset
(confirmed 2026-07-15 via manual positional-alignment comparison against
transactions_truth.csv). If this ever drops below 100%, something in
cleaner.py, merchant_dict.py, or categorizer.py has regressed -- these
tests exist to catch that, not to set an aspirational target.
"""

import pandas as pd


def test_row_counts_match(raw_df: pd.DataFrame, truth_df: pd.DataFrame):
    """
    Sanity precondition for every other test in this file: raw and truth
    CSVs must be the same length and positionally aligned (per
    generate_dataset.py section 3e, rows and truth are shuffled together
    as pairs -- NOT joined by Date, which is not unique).
    """
    assert len(raw_df) == len(truth_df)


def test_merchant_accuracy_is_100_percent(categorized_df: pd.DataFrame, truth_df: pd.DataFrame):
    truth = truth_df.reset_index(drop=True)
    correct = (categorized_df["Merchant"] == truth["TrueMerchant"]).sum()
    total = len(categorized_df)
    accuracy = correct / total

    mismatches = pd.DataFrame({
        "Description": categorized_df["Description"],
        "Predicted": categorized_df["Merchant"],
        "TrueMerchant": truth["TrueMerchant"],
    })[categorized_df["Merchant"] != truth["TrueMerchant"]]

    assert accuracy == 1.0, (
        f"Merchant accuracy dropped to {accuracy:.1%} ({correct}/{total}). "
        f"Mismatches:\n{mismatches.to_string()}"
    )


def test_no_uncategorized_rows(categorized_df: pd.DataFrame):
    """
    Every one of the 365 rows should resolve to a known merchant via
    rule/fuzzy/p2p_heuristic. If this fails, a new uncategorized pattern
    has appeared -- either from a merchant_dict.py gap or a cleaner.py
    regression that's mangling descriptions before they reach matching.
    """
    uncategorized = categorized_df[categorized_df["Category"] == "Uncategorized"]
    assert len(uncategorized) == 0, (
        f"{len(uncategorized)} rows uncategorized:\n"
        f"{uncategorized[['Description']].to_string()}"
    )


def test_refund_not_swallowed_by_swiggy(categorized_df: pd.DataFrame):
    """
    Regression test for the specific ordering bug named in SpendSense.docx:
    'refund being swallowed by Swiggy keyword.' Confirms Refund-Swiggy rows
    are categorized as Refund, not as Food Delivery/Swiggy.
    """
    refund_rows = categorized_df[
        categorized_df["Description"].str.contains("SWIGGY REFUND", case=False, na=False)
    ]
    assert len(refund_rows) > 0, "Expected at least one Swiggy refund row in the dataset."
    assert (refund_rows["Merchant"] == "Refund-Swiggy").all()
    assert (refund_rows["Category"] == "Refund").all()


def test_p2p_transfers_use_friend_transfer_schema(categorized_df: pd.DataFrame, truth_df: pd.DataFrame):
    """
    Regression test for the merchant-label bug found during manual testing:
    P2P rows must report Merchant == 'Friend Transfer' (matching ground
    truth schema) with the real name kept separately in CounterpartyName --
    NOT the person's name as the Merchant value.
    """
    truth = truth_df.reset_index(drop=True)
    p2p_mask = truth["TrueMerchant"] == "Friend Transfer"
    assert p2p_mask.sum() > 0, "Expected Friend Transfer rows in ground truth."

    p2p_rows = categorized_df[p2p_mask]
    assert (p2p_rows["Merchant"] == "Friend Transfer").all()
    assert (p2p_rows["MatchMethod"] == "p2p_heuristic").all()
    assert p2p_rows["CounterpartyName"].notna().all()


def test_recategorize_override_applies_to_all_matching_rows(raw_df: pd.DataFrame):
    """
    Confirms the manually-verified override behavior: correcting one
    transaction retroactively fixes every row sharing the same cleaned
    description (the 'engine remembers going forward' feature).
    """
    from app.core.categorizer import categorize_df, clean

    target_description = "POS 3321 UBER TRIP"
    cleaned_key = clean(target_description)

    overrides = {cleaned_key: {"merchant": "Test Override Merchant", "category": "Transport", "is_subscription": False}}
    result = categorize_df(raw_df, overrides=overrides)

    matching_raw_rows = raw_df[raw_df["Description"] == target_description]
    assert len(matching_raw_rows) > 0, f"No rows found with description '{target_description}' -- test data may have changed."

    updated_rows = result.loc[matching_raw_rows.index]
    assert (updated_rows["Merchant"] == "Test Override Merchant").all()
    assert (updated_rows["MatchMethod"] == "user_override").all()