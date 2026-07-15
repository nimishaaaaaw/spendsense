from app.core.cleaner import clean

tests = [
    "UPI-SWIGGY-swiggy.42@ybl-193847-PAYMENT",
    "BUNDL TECHNOLOGIES PVT LTD-582910",
    "UPI-SWIGGY REFUND-swiggy.12@ybl-403981-REFUND",
    "POS 4521 SWIGGY BANGALORE",
    "NEFT-TECHCORP SOLUTIONS PVT LTD-SAL-119284",
    "UPI-Priya Sharma-priyasharma22@ybl-882910-PAYMENT",
]

for t in tests:
    print(f"{t!r:60} -> {clean(t)!r}")