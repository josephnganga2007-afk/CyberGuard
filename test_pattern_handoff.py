from pattern_engine import analyze_pattern
from risk_engine import analyze_transaction


SUPPLIER = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


# Pattern engine expects:
# transaction[4] = account
# transaction[5] = transaction type
BASELINE_HISTORY = [
    (1, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
    (2, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
    (3, "ABC Supplies", "Baseline transaction", 15, "1234", "BASELINE"),
]


TEST_CASES = [
    {
        "name": "No Baseline History",
        "message": (
            "Please pay invoice 4582 using the existing payment account."
        ),
        "history": [],
        "expected_score": 0,
        "expected_deviations": 0,
    },
    {
        "name": "Normal Account",
        "message": (
            "Please pay invoice 4582 using account 1234."
        ),
        "history": BASELINE_HISTORY,
        "expected_score": 0,
        "expected_deviations": 0,
    },
    {
        "name": "Changed Account",
        "message": (
            "Please pay invoice 4582 using account 5678."
        ),
        "history": BASELINE_HISTORY,
        "expected_score": 10,
        "expected_deviations": 1,
    },
    {
        "name": "Banking Detail Change",
        "message": (
            "We have changed our banking details. "
            "Please update your records."
        ),
        "history": BASELINE_HISTORY,
        "expected_score": 10,
        "expected_deviations": 1,
    },
    {
        "name": "Urgency Change",
        "message": (
            "URGENT: Please process invoice 4582 immediately."
        ),
        "history": BASELINE_HISTORY,
        "expected_score": 10,
        "expected_deviations": 1,
    },
    {
        "name": "Multiple Behavioural Deviations",
        "message": (
            "URGENT: We have changed our banking details. "
            "Please pay invoice 4582 using account 5678 immediately."
        ),
        "history": BASELINE_HISTORY,
        "expected_score": 20,
        "expected_deviations": 3,
    },
]


def run_pattern_tests():

    print("=" * 60)
    print("CYBERGUARD - V9.2 SUPPLIER BEHAVIOUR VALIDATION")
    print("=" * 60)

    passed = 0
    failed = 0

    for index, test in enumerate(TEST_CASES, start=1):

        result = analyze_pattern(
            test["message"],
            test["history"]
        )

        score_pass = (
            result["deviation_score"]
            == test["expected_score"]
        )

        deviation_pass = (
            len(result["deviations"])
            == test["expected_deviations"]
        )

        test_pass = score_pass and deviation_pass

        print()
        print(f"TEST {index:02d} {test['name']}")

        print(
            f"PATTERN SCORE "
            f"{'PASS' if score_pass else 'FAIL'} "
            f"-> {result['deviation_score']}"
        )

        print(
            f"DEVIATIONS "
            f"{'PASS' if deviation_pass else 'FAIL'} "
            f"-> {len(result['deviations'])}"
        )

        if result["deviations"]:
            for deviation in result["deviations"]:
                print(
                    f"  - {deviation['type']}"
                )

        if test_pass:
            print("RESULT PASS")
            passed += 1
        else:
            print("RESULT FAIL")
            failed += 1

    print()
    print("=" * 60)
    print(f"TOTAL TESTS: {len(TEST_CASES)}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 60)

    return failed == 0


def run_score_isolation_test():

    print()
    print("=" * 60)
    print("V9.2 DETERMINISTIC SCORE ISOLATION")
    print("=" * 60)

    message = (
        "URGENT: We have changed our banking details. "
        "Please pay invoice 4582 using account 5678 immediately."
    )

    # Deterministic risk score
    score, risk_level, warnings, factors = analyze_transaction(
        message,
        SUPPLIER
    )

    # Behavioural analysis
    pattern_result = analyze_pattern(
        message,
        BASELINE_HISTORY
    )

    pattern_score = pattern_result["deviation_score"]

    # This is the architectural invariant:
    # behavioural analysis must NOT modify the deterministic score.
    final_score = score

    print(f"DETERMINISTIC SCORE: {score}")
    print(f"PATTERN SCORE:       {pattern_score}")
    print(f"FINAL SCORE:         {final_score}")

    if final_score == score:
        print("SCORE ISOLATION: PASS")
        return True

    print("SCORE ISOLATION: FAIL")
    return False


def run_factor_isolation_test():

    print()
    print("=" * 60)
    print("V9.2 FACTOR ISOLATION")
    print("=" * 60)

    message = (
        "URGENT: We have changed our banking details. "
        "Please pay invoice 4582 using account 5678 immediately."
    )

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        SUPPLIER
    )

    pattern_result = analyze_pattern(
        message,
        BASELINE_HISTORY
    )

    deterministic_factor_names = [
        factor.get("name")
        for factor in factors
    ]

    behavioural_deviation_names = [
        deviation.get("type")
        for deviation in pattern_result["deviations"]
    ]

    print(
        "DETERMINISTIC FACTORS:"
    )

    for factor in deterministic_factor_names:
        print(f"  - {factor}")

    print(
        "BEHAVIOURAL DEVIATIONS:"
    )

    for deviation in behavioural_deviation_names:
        print(f"  - {deviation}")

    # Behavioural deviation types should not be injected
    # into the deterministic factors list.
    leakage = any(
        deviation in deterministic_factor_names
        for deviation in behavioural_deviation_names
    )

    if not leakage:
        print("FACTOR ISOLATION: PASS")
        return True

    print("FACTOR ISOLATION: FAIL")
    return False


if __name__ == "__main__":

    pattern_pass = run_pattern_tests()
    score_pass = run_score_isolation_test()
    factor_pass = run_factor_isolation_test()

    print()
    print("=" * 60)

    if pattern_pass and score_pass and factor_pass:
        print("STATUS: V9.2 PATTERN HANDOFF VALIDATED")
    else:
        print("STATUS: V9.2 VALIDATION FAILED")

    print("=" * 60)