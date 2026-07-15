"""
Subscription detector regression tests.

Baseline established during manual testing on the real 365-row dataset:
7 subscriptions detected (Broadband, CultFit, Hotstar, Local Gym,
MindWell App, Netflix, Spotify), 4 flagged as "forgotten" (Hotstar,
MindWell App, Netflix, Spotify), Rent correctly excluded (Housing category),
Amazon Prime correctly NOT detected (single charge in a 6-month window --
documented structural limitation, not a bug).
"""

EXPECTED_SUBSCRIPTION_MERCHANTS = {
    "Broadband", "CultFit", "Hotstar", "Local Gym",
    "MindWell App", "Netflix", "Spotify",
}

EXPECTED_FORGOTTEN_MERCHANTS = {
    "Hotstar", "MindWell App", "Netflix", "Spotify",
}


def test_detects_exactly_the_known_subscriptions(subscriptions: list[dict]):
    detected = {s["merchant"] for s in subscriptions}
    assert detected == EXPECTED_SUBSCRIPTION_MERCHANTS, (
        f"Detected set changed. Missing: {EXPECTED_SUBSCRIPTION_MERCHANTS - detected}, "
        f"Unexpected: {detected - EXPECTED_SUBSCRIPTION_MERCHANTS}"
    )


def test_rent_excluded_despite_recurring_pattern(subscriptions: list[dict]):
    """
    Rent is charged monthly with a fixed amount -- structurally identical
    to a subscription -- but must be excluded via the Housing category
    filter, since it isn't 'cancel-worthy' in the product sense.
    """
    merchants = {s["merchant"] for s in subscriptions}
    assert "Rent" not in merchants


def test_amazon_prime_not_detected_single_charge_limitation(subscriptions: list[dict]):
    """
    Documents (rather than hides) a known limitation: Amazon Prime is
    charged once in generate_dataset.py's 6-month window (annual_month=2),
    so there's no second charge to measure an interval against. This test
    will correctly FAIL if the dataset generator ever changes to include
    a second annual charge -- at which point this limitation would no
    longer apply and the test should be removed/updated, not just re-passed.
    """
    merchants = {s["merchant"] for s in subscriptions}
    assert "Amazon Prime" not in merchants


def test_forgotten_flags_match_known_baseline(subscriptions: list[dict]):
    forgotten = {s["merchant"] for s in subscriptions if s["is_forgotten"]}
    assert forgotten == EXPECTED_FORGOTTEN_MERCHANTS


def test_hotstar_detected_as_quarterly(subscriptions: list[dict]):
    """
    Regression test for the quarterly-billing edge case explicitly named
    in generate_dataset.py (only_months: [1, 4]).
    """
    hotstar = next((s for s in subscriptions if s["merchant"] == "Hotstar"), None)
    assert hotstar is not None
    assert hotstar["billing_cycle"] == "quarterly"


def test_no_false_positives_beyond_expected_set(subscriptions: list[dict]):
    """
    Every merchant flagged as a subscription must be one we've deliberately
    verified. A merchant appearing here that isn't in the expected set means
    either a new false positive, or the dataset changed and baselines need
    a conscious update -- not a silent pass.
    """
    detected = {s["merchant"] for s in subscriptions}
    unexpected = detected - EXPECTED_SUBSCRIPTION_MERCHANTS
    assert unexpected == set(), f"Unexpected subscriptions detected: {unexpected}"