
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

    print("=" * 75)
    print(name)
    print("-" * 75)
    print(message.strip())
    print()

    print("SCORE:", score)
    print("RISK LEVEL:", risk_level)

    print()
    print("FACTORS:")

    if factors:
        for factor in factors:
            print(
                f"- {factor['name']}: "
                f"+{factor['points']}"
            )
    else:
        print("- None")

    print()


# ============================================================
# BENEFICIARY ATTACKS
# ============================================================

run_test(
    "TEST 1 — New Beneficiary Only",
    """
    From: accounts@abcsupplies.co.za

    Please update the beneficiary details.
    """
)


run_test(
    "TEST 2 — Beneficiary + Payment",
    """
    From: accounts@abcsupplies.co.za

    Please use the new beneficiary details for the payment.
    """
)


run_test(
    "TEST 3 — Beneficiary + Outstanding Amount",
    """
    From: accounts@abcsupplies.co.za

    Please use the new beneficiary details for the
    outstanding amount.
    """
)


run_test(
    "TEST 4 — Beneficiary + Urgency",
    """
    From: accounts@abcsupplies.co.za

    Please urgently update the beneficiary details.
    """
)


run_test(
    "TEST 5 — Beneficiary + Wrong Account",
    """
    From: accounts@abcsupplies.co.za

    Please use the new beneficiary details and account
    987654321 for future payments.
    """
)


# ============================================================
# BANKING CHANGE COMBINATIONS
# ============================================================

run_test(
    "TEST 6 — Banking Change + Payment",
    """
    From: accounts@abcsupplies.co.za

    Our banking details have changed.
    Please make payment to the new account.
    """
)


run_test(
    "TEST 7 — Banking Change + Urgency + Payment",
    """
    From: accounts@abcsupplies.co.za

    URGENT: Our banking details have changed.
    Please immediately make payment to the new account.
    """
)


# ============================================================
# ACCOUNT MISMATCH COMBINATIONS
# ============================================================

run_test(
    "TEST 8 — Wrong Account + Payment",
    """
    From: accounts@abcsupplies.co.za

    Please make payment to account 987654321.
    """
)


run_test(
    "TEST 9 — Wrong Account + Urgency + Payment",
    """
    From: accounts@abcsupplies.co.za

    Please urgently make payment to account 987654321.
    """
)


# ============================================================
# SENDER MISMATCH COMBINATIONS
# ============================================================

run_test(
    "TEST 10 — Sender Mismatch + Beneficiary",
    """
    From: attacker@example.com

    Please update the beneficiary details.
    """
)


run_test(
    "TEST 11 — Sender Mismatch + Beneficiary + Payment",
    """
    From: attacker@example.com

    Please use the new beneficiary details for the payment.
    """
)


run_test(
    "TEST 12 — Sender Mismatch + Beneficiary + Urgency",
    """
    From: attacker@example.com

    URGENT: Please update the new beneficiary details
    immediately.
    """
)


run_test(
    "TEST 13 — Sender Mismatch + Beneficiary + Payment + Urgency",
    """
    From: attacker@example.com

    URGENT: Please use the new beneficiary details
    immediately for the payment.
    """
)


# ============================================================
# LEGITIMATE CONTROL CASE
# ============================================================

run_test(
    "TEST 14 — Legitimate Existing Beneficiary",
    """
    From: accounts@abcsupplies.co.za

    Please make payment using the existing beneficiary
    information on file.
    """
)

