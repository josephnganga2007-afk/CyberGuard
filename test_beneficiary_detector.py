from risk_engine import has_beneficiary_change


tests = [
    {
        "name": "Account Manager Changed",
        "message": """
Our account manager has changed.
Please update your contact list.
""",
        "expected": False
    },

    {
        "name": "Account Details Unchanged",
        "message": """
The account details are unchanged.
No amendments are required.
""",
        "expected": False
    },

    {
        "name": "Changed Supplier Contact",
        "message": """
The supplier has changed their account manager.
Please direct future correspondence to the new contact.
""",
        "expected": False
    },

    {
        "name": "Existing Payment Account",
        "message": """
Please use the existing payment account for today's invoice.
""",
        "expected": False
    },

    {
        "name": "Account Number in Report",
        "message": """
The account number in the reconciliation report has changed.
Please review the updated report.
""",
        "expected": False
    },

    {
        "name": "New Account Manager",
        "message": """
Please review the new account manager assignment.
""",
        "expected": False
    },

    {
        "name": "Real Beneficiary Change",
        "message": """
Please use the new beneficiary details for the next payment.
""",
        "expected": True
    },

    {
        "name": "Real Receiving Account Change",
        "message": """
Our receiving account has changed.
Please update your records before the next transfer.
""",
        "expected": True
    },

    {
        "name": "Real Payment Destination Change",
        "message": """
The payment destination has changed.
Please use the new details for future payments.
""",
        "expected": True
    },

    {
        "name": "Real Redirection",
        "message": """
Please send the outstanding invoice to the new account instead.
""",
        "expected": True
    },

    {
        "name": "Real Revised Instructions",
        "message": """
Our payment instructions have been revised.
Please process the next transfer using the new details.
""",
        "expected": True
    },

    {
        "name": "Existing Destination",
        "message": """
Please continue using the existing payment destination.
No changes have been made.
""",
        "expected": False
    }
]


print("=" * 75)
print("CYBERGUARD - BENEFICIARY DETECTOR TRACE")
print("=" * 75)

passed = 0
failed = 0


for i, test in enumerate(tests, start=1):

    detected = has_beneficiary_change(test["message"])
    expected = test["expected"]

    if detected == expected:
        result = "PASS"
        passed += 1
    else:
        result = "FAIL"
        failed += 1

    print()
    print("=" * 75)
    print(f"TEST {i:02d} - {test['name']}")
    print("-" * 75)

    print(test["message"].strip())
    print()

    print(f"EXPECTED: {expected}")
    print(f"DETECTED: {detected}")
    print(f"RESULT:   {result}")


print()
print("=" * 75)
print("DETECTOR TRACE COMPLETE")
print("=" * 75)
print(f"TOTAL:  {len(tests)}")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print("=" * 75)


if failed == 0:
    print("STATUS: ALL TESTS PASSED")
else:
    print("STATUS: REGRESSION DETECTED")