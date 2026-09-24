from pattern_engine import analyze_pattern


BASELINE_HISTORY = [
    (1, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
    (2, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
    (3, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
]


TEST_CASES = [

    # =========================================================
    # LEGITIMATE / STABILITY CASES
    # =========================================================

    {
        "name": "Today's Invoice",
        "message": (
            "Please process today's invoice using the existing "
            "payment account."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Payment Due Today",
        "message": (
            "Payment is due today according to our normal payment terms."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Existing Account Today",
        "message": (
            "Please use the existing payment account for today's invoice."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Existing Banking Details",
        "message": (
            "Our existing banking details remain unchanged. "
            "Please continue using the details on file."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "No Banking Change",
        "message": (
            "There are no changes to our banking details. "
            "Please process the invoice normally."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Bank Details Unchanged",
        "message": (
            "Our bank details are unchanged."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Existing Payment Account",
        "message": (
            "Please continue using the existing payment account."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "No Amendments",
        "message": (
            "No amendments are required to the current banking details."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Routine Invoice Deadline",
        "message": (
            "The invoice is due today under our normal payment terms."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Continue Existing Instructions",
        "message": (
            "Please continue to use the existing banking instructions."
        ),
        "expected_deviations": 0,
    },


    # =========================================================
    # GENUINE BEHAVIOURAL CHANGES
    # =========================================================

    {
        "name": "Explicit Urgency",
        "message": (
            "URGENT: Please process invoice 4582 immediately."
        ),
        "expected_deviations": 1,
        "expected_type": "Urgency change",
    },

    {
        "name": "Immediate Action",
        "message": (
            "Please process the payment immediately."
        ),
        "expected_deviations": 1,
        "expected_type": "Urgency change",
    },

    {
        "name": "ASAP Request",
        "message": (
            "Please settle the outstanding invoice as soon as possible."
        ),
        "expected_deviations": 1,
        "expected_type": "Urgency change",
    },

    {
        "name": "Changed Banking Details",
        "message": (
            "We have changed our banking details. "
            "Please update your records."
        ),
        "expected_deviations": 1,
        "expected_type": "Banking detail change",
    },

    {
        "name": "Updated Bank Details",
        "message": (
            "Our bank details have been updated. "
            "Please use the new information."
        ),
        "expected_deviations": 1,
        "expected_type": "Banking detail change",
    },

    {
        "name": "Changed Account",
        "message": (
            "Please pay invoice 4582 using account 5678."
        ),
        "expected_deviations": 1,
        "expected_type": "Account change",
    },

    {
        "name": "New Account",
        "message": (
            "Our new account is 5678. Please use it for the invoice."
        ),
        "expected_deviations": 1,
        "expected_type": "Account change",
    },

    {
        "name": "Urgent Banking Change",
        "message": (
            "URGENT: Our banking details have changed. "
            "Please update them immediately."
        ),
        "expected_deviations": 2,
    },

    {
        "name": "Changed Account With Urgency",
        "message": (
            "URGENT: Please pay invoice 4582 using account 5678 "
            "immediately."
        ),
        "expected_deviations": 2,
    },

    {
        "name": "Full Behavioural Shift",
        "message": (
            "URGENT: We have changed our banking details. "
            "Please pay invoice 4582 using account 5678 "
            "immediately."
        ),
        "expected_deviations": 3,
    },


    # =========================================================
    # AMBIGUOUS CASES
    # =========================================================

    {
        "name": "Process Payment Today",
        "message": (
            "Please process the payment today."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Settle Today",
        "message": (
            "Please settle the outstanding invoice today."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Banking Details Mentioned",
        "message": (
            "Please confirm that the banking details on file "
            "are correct."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Account Information",
        "message": (
            "Please confirm the account information we have "
            "on file."
        ),
        "expected_deviations": 0,
    },

    {
        "name": "Tomorrow Payment",
        "message": (
            "Please process the payment tomorrow."
        ),
        "expected_deviations": 0,
    },
]


def run_tests():

    print("=" * 60)
    print("CYBERGUARD - V11.1 BEHAVIOURAL CORPUS")
    print("=" * 60)

    passed = 0
    failed = 0

    for index, test in enumerate(TEST_CASES, start=1):

        result = analyze_pattern(
            test["message"],
            BASELINE_HISTORY
        )

        actual_count = len(result["deviations"])

        count_pass = (
            actual_count == test["expected_deviations"]
        )

        type_pass = True

        if "expected_type" in test:

            type_pass = any(
                deviation["type"] == test["expected_type"]
                for deviation in result["deviations"]
            )

        test_pass = count_pass and type_pass

        print()
        print(
            f"TEST {index:02d} {test['name']}"
        )

        print(
            f"EXPECTED DEVIATIONS: "
            f"{test['expected_deviations']}"
        )

        print(
            f"ACTUAL DEVIATIONS:   "
            f"{actual_count}"
        )

        print(
            f"COUNT: "
            f"{'PASS' if count_pass else 'FAIL'}"
        )

        if "expected_type" in test:

            print(
                f"EXPECTED TYPE: "
                f"{'PASS' if type_pass else 'FAIL'} "
                f"-> {test['expected_type']}"
            )

        if result["deviations"]:

            for deviation in result["deviations"]:
                print(
                    f"  - {deviation['type']}"
                )

        if test_pass:

            print("RESULT: PASS")
            passed += 1

        else:

            print("RESULT: FAIL")
            failed += 1

    print()
    print("=" * 60)
    print(f"TOTAL TESTS: {len(TEST_CASES)}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 60)

    if failed == 0:
        print("STATUS: V11.1 CORPUS PASSED")
    else:
        print("STATUS: V11.1 HARDENING REQUIRED")


if __name__ == "__main__":
    run_tests()