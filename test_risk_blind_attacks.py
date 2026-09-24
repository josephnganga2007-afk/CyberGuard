from risk_engine import analyze_transaction


# ============================================================
# CYBERGUARD — BLIND ADVERSARIAL TEST SUITE
# ============================================================

supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


tests = [
    {
        "name": "Updated Beneficiary",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please use the updated beneficiary information
for the next settlement.
"""
    },

    {
        "name": "Changed Settlement Destination",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
We have changed where future invoices should be settled.
Please amend your records.
"""
    },

    {
        "name": "Alternative Account",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Kindly send the outstanding amount to the account
listed below instead.
"""
    },

    {
        "name": "Latest Banking Instructions",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please use our latest banking instructions when
processing the next transfer.
"""
    },

    {
        "name": "Different Receiving Account",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
The account receiving our supplier payments is different now.
Kindly update your records.
"""
    },

    {
        "name": "Attacker + Revised Account",
        "sender": "attacker@example.com",
        "message": """
Please send the outstanding invoice to the revised
account provided below.
"""
    },

    {
        "name": "Attacker + Urgency + Destination Change",
        "sender": "attacker@example.com",
        "message": """
Immediate action required.

The destination for today's supplier payment has been altered.
Please process using the new instructions.
"""
    },

    {
        "name": "Legitimate / No Change",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please review the existing banking instructions before
processing the invoice.

No amendments have been made.
"""
    }
]


# ============================================================
# RUN TESTS
# ============================================================

print("=" * 70)
print("CYBERGUARD — BLIND ADVERSARIAL TEST SUITE")
print("=" * 70)


for i, test in enumerate(tests, start=1):

    message = (
        f"From: {test['sender']}\n\n"
        f"{test['message'].strip()}"
    )

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        supplier
    )

    print()
    print("=" * 70)
    print(f"TEST {i:02d} - {test['name']}")
    print("-" * 70)

    print(f"From: {test['sender']}")
    print()
    print(test["message"].strip())
    print()

    print(f"SCORE: {score}")
    print(f"RISK LEVEL: {risk_level}")

    print()
    print("FACTORS:")

    if factors:
        for factor in factors:
            print(f"- {factor}")
    else:
        print("- None")

    print()
    print("WARNINGS:")

    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("- None")


print()
print("=" * 70)
print("BLIND ADVERSARIAL TESTING COMPLETE")
print("=" * 70)

