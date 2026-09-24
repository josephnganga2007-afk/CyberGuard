from risk_engine import analyze_transaction, has_beneficiary_change


supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


tests = [
    {
        "name": "Generic Account Changed",
        "message": """
The account has changed.
Please update your records.
""",
        "expected_destination": False
    },

    {
        "name": "Generic Account Update",
        "message": """
Please update the account information.
""",
        "expected_destination": False
    },

    {
        "name": "New Account",
        "message": """
Please use the new account.
""",
        "expected_destination": False
    },

    {
        "name": "Bank Account Changed",
        "message": """
Our bank account has changed.
Please update your records.
""",
        "expected_destination": True
    },

    {
        "name": "Update Bank Account",
        "message": """
Please update our bank account for future payments.
""",
        "expected_destination": True
    },

    {
        "name": "Payment to New Account",
        "message": """
Please send the payment to the new account.
""",
        "expected_destination": True
    },

    {
        "name": "Invoice to New Account",
        "message": """
Please send the outstanding invoice to the new account.
""",
        "expected_destination": True
    },

    {
        "name": "Existing Payment Account",
        "message": """
Please use the existing payment account for today's invoice.
""",
        "expected_destination": False
    },

    {
        "name": "Account Manager Changed",
        "message": """
Our account manager has changed.
""",
        "expected_destination": False
    },

    {
        "name": "Account Number Changed",
        "message": """
The account number in the reconciliation report has changed.
""",
        "expected_destination": False
    },

    {
        "name": "Receiving Account",
        "message": """
Our receiving account has changed.
""",
        "expected_destination": True
    },

    {
        "name": "Payment Destination",
        "message": """
The payment destination has changed.
""",
        "expected_destination": True
    }
]


print("=" * 75)
print("CYBERGUARD — ACCOUNT AMBIGUITY TEST")
print("=" * 75)

passed = 0
failed = 0

for i, test in enumerate(tests, start=1):

    message = (
        f"From: {supplier['email']}\n\n"
        f"{test['message'].strip()}"
    )

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        supplier
    )

    detected = has_beneficiary_change(message)

    expected = test["expected_destination"]

    result = "PASS" if detected == expected else "FAIL"

    if result == "PASS":
        passed += 1
    else:
        failed += 1

    print()
    print("=" * 75)
    print(f"TEST {i:02d} - {test['name']}")
    print("-" * 75)
    print(test["message"].strip())
    print()
    print(f"SCORE: {score}")
    print(f"RISK LEVEL: {risk_level}")
    print(f"EXPECTED DESTINATION: {expected}")
    print(f"DETECTED DESTINATION: {detected}")
    print(f"RESULT: {result}")

    print()
    print("FACTORS:")

    if factors:
        for factor in factors:
            print(f"- {factor}")
    else:
        print("- None")


print()
print("=" * 75)
print("ACCOUNT AMBIGUITY TEST COMPLETE")
print("=" * 75)
print(f"TOTAL:  {len(tests)}")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print("=" * 75)