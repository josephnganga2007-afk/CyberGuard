from email_pipeline import process_email


SUPPLIER = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


TEST_CASES = [

    # ========================================================
    # 1. IRRELEVANT EMAIL
    # ========================================================

    {
        "name": "Meeting Confirmation",

        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Meeting confirmation",
            "body": (
                "Hi Joseph,\n\n"
                "Just confirming our meeting tomorrow at 10:00.\n\n"
                "Regards,\n"
                "ABC Supplies"
            )
        },

        "expected_category": "IRRELEVANT",
        "expected_action": "STOP",
        "expected_stage": "TRIAGE",
        "risk_should_exist": False,
    },


    # ========================================================
    # 2. UNCERTAIN EMAIL
    # ========================================================

    {
        "name": "Ambiguous Account Update",

        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Account update",
            "body": (
                "Hi Joseph,\n\n"
                "Please update the account information "
                "in your records.\n\n"
                "Regards,\n"
                "ABC Supplies"
            )
        },

        "expected_category": "UNCERTAIN",
        "expected_action": "HOLD_FOR_REVIEW",
        "expected_stage": "TRIAGE",
        "risk_should_exist": False,
    },


    # ========================================================
    # 3. LEGITIMATE PAYMENT
    # ========================================================

    {
        "name": "Legitimate Invoice",

        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice 4582",
            "body": (
                "Hi Joseph,\n\n"
                "Please find invoice 4582 attached "
                "for the goods supplied this month.\n\n"
                "The invoice is due according to our "
                "normal payment terms.\n\n"
                "Regards,\n"
                "ABC Supplies"
            )
        },

        "expected_category": "PAYMENT_RELATED",
        "expected_action": "ANALYZE",
        "expected_stage": "RISK_ANALYSIS",
        "risk_should_exist": True,
    },


    # ========================================================
    # 4. PAYMENT DIVERSION ATTACK
    # ========================================================

    {
        "name": "Urgent Banking Change",

        "email": {
            "sender": "attacker@example.com",
            "subject": "URGENT - Banking details changed",
            "body": (
                "Hi Joseph,\n\n"
                "URGENT: We have changed our banking details.\n\n"
                "Please update the account immediately and "
                "pay invoice 4582 using the new account "
                "details below.\n\n"
                "Regards,\n"
                "ABC Supplies"
            )
        },

        "expected_category": "PAYMENT_RELATED",
        "expected_action": "ANALYZE",
        "expected_stage": "RISK_ANALYSIS",
        "risk_should_exist": True,
        "destination_should_exist": True,
    },


    # ========================================================
    # 5. EXISTING ACCOUNT — SHOULD NOT TRIGGER DESTINATION
    # ========================================================

    {
        "name": "Existing Payment Account",

        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice payment",
            "body": (
                "Hi Joseph,\n\n"
                "Please use the existing payment account "
                "for today's invoice.\n\n"
                "No changes are required.\n\n"
                "Regards,\n"
                "ABC Supplies"
            )
        },

        "expected_category": "PAYMENT_RELATED",
        "expected_action": "ANALYZE",
        "expected_stage": "RISK_ANALYSIS",
        "risk_should_exist": True,
        "destination_should_exist": False,
    },
]


print("=" * 75)
print("CYBERGUARD - V9 END-TO-END PIPELINE VALIDATION")
print("=" * 75)


passed = 0
failed = 0


for index, test in enumerate(TEST_CASES, start=1):

    print()
    print("=" * 75)
    print(f"TEST {index:02d} - {test['name']}")
    print("=" * 75)

    result = process_email(
        test["email"],
        SUPPLIER
    )

    actual_category = result.get("category")
    actual_action = result.get("action")
    actual_stage = result.get("stage")

    risk_exists = result.get("risk") is not None

    test_passed = True

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if actual_category != test["expected_category"]:
        print(
            f"FAIL: CATEGORY "
            f"(expected {test['expected_category']}, "
            f"got {actual_category})"
        )
        test_passed = False
    else:
        print(f"CATEGORY: PASS -> {actual_category}")

    # --------------------------------------------------------
    # ACTION
    # --------------------------------------------------------

    if actual_action != test["expected_action"]:
        print(
            f"FAIL: ACTION "
            f"(expected {test['expected_action']}, "
            f"got {actual_action})"
        )
        test_passed = False
    else:
        print(f"ACTION: PASS -> {actual_action}")

    # --------------------------------------------------------
    # STAGE
    # --------------------------------------------------------

    if actual_stage != test["expected_stage"]:
        print(
            f"FAIL: STAGE "
            f"(expected {test['expected_stage']}, "
            f"got {actual_stage})"
        )
        test_passed = False
    else:
        print(f"STAGE: PASS -> {actual_stage}")

    # --------------------------------------------------------
    # RISK EXISTENCE
    # --------------------------------------------------------

    if risk_exists != test["risk_should_exist"]:
        print(
            f"FAIL: RISK OBJECT "
            f"(expected {test['risk_should_exist']}, "
            f"got {risk_exists})"
        )
        test_passed = False
    else:
        print(f"RISK OBJECT: PASS -> {risk_exists}")

    # --------------------------------------------------------
    # DESTINATION DETECTION
    # --------------------------------------------------------

    if "destination_should_exist" in test:

        if risk_exists:

            factors = result["risk"].get("factors", [])

            destination_detected = any(
                factor.get("name") in (
                    "Beneficiary change",
                    "Payment destination change"
                )
                for factor in factors
            )

            expected_destination = test["destination_should_exist"]

            if destination_detected != expected_destination:

                print(
                    f"FAIL: DESTINATION "
                    f"(expected {expected_destination}, "
                    f"got {destination_detected})"
                )

                test_passed = False

            else:
                print(
                    f"DESTINATION: PASS -> "
                    f"{destination_detected}"
                )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if test_passed:
        print("RESULT: PASS")
        passed += 1
    else:
        print("RESULT: FAIL")
        failed += 1


print()
print("=" * 75)
print("V9 END-TO-END SUMMARY")
print("=" * 75)

print(f"TOTAL TESTS: {len(TEST_CASES)}")
print(f"PASSED:      {passed}")
print(f"FAILED:      {failed}")

print("=" * 75)

if failed == 0:
    print("STATUS: V9 PIPELINE VALIDATED")
else:
    print("STATUS: V9 PIPELINE FAILURE")