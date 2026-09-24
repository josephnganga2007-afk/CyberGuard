
from risk_engine import analyze_transaction


supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


def run_test(name, message):

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        supplier
    )

    print("=" * 70)
    print(name)
    print("-" * 70)
    print(message)
    print()

    print("SCORE:", score)
    print("RISK LEVEL:", risk_level)

    print()
    print("WARNINGS:")
    for warning in warnings:
        print("-", warning)

    print()
    print("FACTORS:")
    for factor in factors:
        print(
            f"- {factor['name']}: "
            f"+{factor['points']}"
        )

    print()


# ============================================================
# 1. LEGITIMATE PAYMENT
# ============================================================

run_test(
    "TEST 1 — Legitimate Payment",
    """
    From: accounts@abcsupplies.co.za

    Please make payment for invoice 4582 according to our
    existing payment arrangement.
    """
)


# ============================================================
# 2. LEGITIMATE INVOICE
# ============================================================

run_test(
    "TEST 2 — Legitimate Invoice",
    """
    From: accounts@abcsupplies.co.za

    Please find attached invoice 4582 for your records.
    """
)


# ============================================================
# 3. BANKING DETAILS CHANGE
# ============================================================

run_test(
    "TEST 3 — Banking Details Change",
    """
    From: accounts@abcsupplies.co.za

    Please note that our banking details have changed.
    """
)


# ============================================================
# 4. BANKING CHANGE + PAYMENT
# ============================================================

run_test(
    "TEST 4 — Banking Change + Payment",
    """
    From: accounts@abcsupplies.co.za

    We have changed our banking details.
    Please update the account and pay invoice 4582.
    """
)


# ============================================================
# 5. BANKING CHANGE + URGENCY
# ============================================================

run_test(
    "TEST 5 — Banking Change + Urgency",
    """
    From: accounts@abcsupplies.co.za

    Our banking details have changed.
    Please update them immediately.
    """
)


# ============================================================
# 6. BENEFICIARY + OUTSTANDING AMOUNT
# ============================================================

run_test(
    "TEST 6 — Beneficiary + Outstanding Amount",
    """
    From: accounts@abcsupplies.co.za

    Please use the new beneficiary details for the
    outstanding amount.
    """
)


# ============================================================
# 7. ACCOUNT NUMBER MISMATCH
# ============================================================

run_test(
    "TEST 7 — Account Number Mismatch",
    """
    From: accounts@abcsupplies.co.za

    Please pay the invoice to account 987654321.
    """
)


# ============================================================
# 8. SENDER MISMATCH
# ============================================================

run_test(
    "TEST 8 — Sender Mismatch",
    """
    From: attacker@example.com

    Please make payment for invoice 4582.
    """
)


# ============================================================
# 9. SENDER + ACCOUNT MISMATCH
# ============================================================

run_test(
    "TEST 9 — Sender + Account Mismatch",
    """
    From: attacker@example.com

    Please urgently pay invoice 4582 to account 987654321.
    """
)


# ============================================================
# 10. URGENT PAYMENT DIVERSION
# ============================================================

run_test(
    "TEST 10 — Urgent Payment Diversion",
    """
    From: attacker@example.com

    URGENT: Our banking details have changed.
    Please immediately transfer payment for invoice 4582
    to account 987654321.
    """
)


# ============================================================
# 11. COMPLETELY IRRELEVANT
# ============================================================

run_test(
    "TEST 11 — Irrelevant Email",
    """
    From: accounts@abcsupplies.co.za

    Just confirming our meeting tomorrow at 10:00.
    """
)


# ============================================================
# 12. FRAUD AWARENESS ARTICLE
# ============================================================

run_test(
    "TEST 12 — Fraud Awareness Article",
    """
    From: security@example.com

    Please read our article explaining common payment
    fraud techniques and banking scams.
    """
)


# ============================================================
# 13. LEGITIMATE ACCOUNT NUMBER
# ============================================================

run_test(
    "TEST 13 — Matching Account",
    """
    From: accounts@abcsupplies.co.za

    Please make payment to account 1234.
    """
)


# ============================================================
# 14. BANKING CHANGE + WRONG ACCOUNT
# ============================================================

run_test(
    "TEST 14 — Banking Change + Wrong Account",
    """
    From: accounts@abcsupplies.co.za

    Our banking details have changed.
    Please use account 987654321 for the payment.
    """
)


# ============================================================
# 15. URGENT WRONG ACCOUNT
# ============================================================

run_test(
    "TEST 15 — Urgent Wrong Account",
    """
    From: accounts@abcsupplies.co.za

    Please urgently make payment to account 987654321.
    """
)

