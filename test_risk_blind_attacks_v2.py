from risk_engine import analyze_transaction

supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}

tests = [
    {
        "name": "Route Payment Using Details",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please route the next payment using the details below.
"""
    },

    {
        "name": "Attachment Settlement Account",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Use the account shown in the attachment for future settlements.
"""
    },

    {
        "name": "Revised Bank Instructions",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
The bank instructions for upcoming payments have been revised.
"""
    },

    {
        "name": "New Payment Details",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please direct the invoice to our new details.
"""
    },

    {
        "name": "Different Account",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
The payment should now be made to a different account.
"""
    },

    {
        "name": "Outstanding Balance Redirection",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Kindly settle the outstanding balance using the information below.
"""
    },

    {
        "name": "Alternative Payment Route",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
For the next transfer, please use the alternative payment route
provided below.
"""
    },

    {
        "name": "Updated Account Instructions",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please follow the updated account instructions when processing
our next invoice.
"""
    },

    {
        "name": "Attacker Different Account",
        "sender": "attacker@example.com",
        "message": """
Please pay the outstanding invoice into a different account.
"""
    },

    {
        "name": "Attacker Revised Instructions",
        "sender": "attacker@example.com",
        "message": """
Immediate action required.

Our payment instructions have been revised.
Please process today's transfer using the new details.
"""
    },

    # NEGATIVE CONTROLS
    {
        "name": "Existing Account Confirmed",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Please confirm that the existing account is still on file.
"""
    },

    {
        "name": "Banking Instructions Unchanged",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
Our banking instructions remain unchanged.
Please continue using the existing details.
"""
    },

    {
        "name": "No Payment Detail Changes",
        "sender": "accounts@abcsupplies.co.za",
        "message": """
No changes have been made to our payment details.
"""
    }
]


print("=" * 70)
print("CYBERGUARD — BLIND ADVERSARIAL TEST SUITE V2")
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
print("BLIND ADVERSARIAL TESTING V2 COMPLETE")
print("=" * 70)