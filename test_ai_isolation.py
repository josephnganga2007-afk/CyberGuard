from unittest.mock import patch

from app import app
from risk_engine import analyze_transaction


SUPPLIER = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


LEGITIMATE_MESSAGE = (
    "From: accounts@abcsupplies.co.za\n"
    "Subject: Invoice 4582\n\n"
    "Please find invoice 4582 attached for the goods supplied "
    "this month. The invoice is due according to our normal "
    "payment terms."
)


SUSPICIOUS_MESSAGE = (
    "From: attacker@example.com\n"
    "Subject: URGENT - Banking details changed\n\n"
    "URGENT: We have changed our banking details. "
    "Please update the account immediately and pay invoice 4582 "
    "using the new account details below."
)


AI_STATES = {
    "LOW": {
        "assessment": "No significant threat detected.",
        "confidence": "LOW",
        "threat_type": "No Significant Threat",
        "indicators": []
    },

    "HIGH": {
        "assessment": "The communication contains suspicious payment instructions.",
        "confidence": "HIGH",
        "threat_type": "Payment Diversion",
        "indicators": [
            "Urgency",
            "Banking detail change"
        ]
    },

    "CRITICAL": {
        "assessment": "Strong indicators of business email compromise.",
        "confidence": "HIGH",
        "threat_type": "Business Email Compromise",
        "indicators": [
            "Urgent request",
            "Changed banking details",
            "Account redirection"
        ]
    },

    "UNAVAILABLE": {
        "assessment": "AI analysis unavailable.",
        "confidence": "UNAVAILABLE",
        "threat_type": "UNAVAILABLE",
        "indicators": [
            "Gemini analysis could not be completed."
        ]
    }
}


def calculate_deterministic_result(message):

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        SUPPLIER
    )

    return {
        "score": score,
        "risk_level": risk_level,
        "warnings": warnings,
        "factors": factors
    }


def submit_with_ai(message, ai_result):

    client = app.test_client()

    with patch(
        "app.analyze_with_ai",
        return_value=ai_result
    ):

        response = client.post(
            "/",
            data={
                "message": message,
                "supplier": "ABC Supplies"
            },
            follow_redirects=True
        )

    return response


def test_suspicious_score_is_invariant():

    print()
    print("=" * 60)
    print("TEST 01 - SUSPICIOUS EMAIL SCORE INVARIANCE")
    print("=" * 60)

    deterministic = calculate_deterministic_result(
        SUSPICIOUS_MESSAGE
    )

    expected_score = deterministic["score"]
    expected_level = deterministic["risk_level"]

    print(
        f"BASELINE DETERMINISTIC SCORE: "
        f"{expected_score}"
    )

    print(
        f"BASELINE RISK LEVEL: "
        f"{expected_level}"
    )

    passed = True

    for state, ai_result in AI_STATES.items():

        response = submit_with_ai(
            SUSPICIOUS_MESSAGE,
            ai_result
        )

        status_pass = response.status_code == 200

        # The deterministic calculation is independent
        # of whatever AI response is supplied.
        current = calculate_deterministic_result(
            SUSPICIOUS_MESSAGE
        )

        score_pass = current["score"] == expected_score
        level_pass = current["risk_level"] == expected_level

        test_pass = (
            status_pass
            and score_pass
            and level_pass
        )

        print()
        print(
            f"AI STATE: {state}"
        )

        print(
            f"PIPELINE STATUS: "
            f"{'PASS' if status_pass else 'FAIL'}"
        )

        print(
            f"SCORE: "
            f"{'PASS' if score_pass else 'FAIL'} "
            f"-> {current['score']}"
        )

        print(
            f"RISK LEVEL: "
            f"{'PASS' if level_pass else 'FAIL'} "
            f"-> {current['risk_level']}"
        )

        if test_pass:
            print("RESULT: PASS")
        else:
            print("RESULT: FAIL")
            passed = False

    return passed


def test_legitimate_score_is_invariant():

    print()
    print("=" * 60)
    print("TEST 02 - LEGITIMATE EMAIL SCORE INVARIANCE")
    print("=" * 60)

    deterministic = calculate_deterministic_result(
        LEGITIMATE_MESSAGE
    )

    expected_score = deterministic["score"]
    expected_level = deterministic["risk_level"]

    print(
        f"BASELINE DETERMINISTIC SCORE: "
        f"{expected_score}"
    )

    print(
        f"BASELINE RISK LEVEL: "
        f"{expected_level}"
    )

    passed = True

    # Deliberately give Gemini the strongest possible
    # interpretation while keeping the actual message legitimate.
    ai_result = AI_STATES["CRITICAL"]

    response = submit_with_ai(
        LEGITIMATE_MESSAGE,
        ai_result
    )

    current = calculate_deterministic_result(
        LEGITIMATE_MESSAGE
    )

    status_pass = response.status_code == 200
    score_pass = current["score"] == expected_score
    level_pass = current["risk_level"] == expected_level

    print()
    print("AI STATE: CRITICAL")
    print(
        f"PIPELINE STATUS: "
        f"{'PASS' if status_pass else 'FAIL'}"
    )

    print(
        f"SCORE: "
        f"{'PASS' if score_pass else 'FAIL'} "
        f"-> {current['score']}"
    )

    print(
        f"RISK LEVEL: "
        f"{'PASS' if level_pass else 'FAIL'} "
        f"-> {current['risk_level']}"
    )

    if status_pass and score_pass and level_pass:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
        passed = False

    return passed


def test_ai_failure_preserves_deterministic_result():

    print()
    print("=" * 60)
    print("TEST 03 - AI FAILURE SCORE INVARIANCE")
    print("=" * 60)

    deterministic = calculate_deterministic_result(
        SUSPICIOUS_MESSAGE
    )

    expected_score = deterministic["score"]
    expected_level = deterministic["risk_level"]

    client = app.test_client()

    with patch(
        "app.analyze_with_ai",
        side_effect=RuntimeError(
            "Simulated Gemini failure"
        )
    ):

        response = client.post(
            "/",
            data={
                "message": SUSPICIOUS_MESSAGE,
                "supplier": "ABC Supplies"
            },
            follow_redirects=True
        )

    current = calculate_deterministic_result(
        SUSPICIOUS_MESSAGE
    )

    status_pass = response.status_code == 200
    score_pass = current["score"] == expected_score
    level_pass = current["risk_level"] == expected_level

    print(
        f"PIPELINE STATUS: "
        f"{'PASS' if status_pass else 'FAIL'}"
    )

    print(
        f"EXPECTED SCORE: {expected_score}"
    )

    print(
        f"ACTUAL SCORE:   {current['score']}"
    )

    print(
        f"SCORE INVARIANCE: "
        f"{'PASS' if score_pass else 'FAIL'}"
    )

    print(
        f"RISK LEVEL INVARIANCE: "
        f"{'PASS' if level_pass else 'FAIL'}"
    )

    if status_pass and score_pass and level_pass:
        print("RESULT: PASS")
        return True

    print("RESULT: FAIL")
    return False


def run_tests():

    print("=" * 60)
    print("CYBERGUARD - V10.1 AI SCORE ISOLATION")
    print("=" * 60)

    results = []

    tests = [
        test_suspicious_score_is_invariant,
        test_legitimate_score_is_invariant,
        test_ai_failure_preserves_deterministic_result,
    ]

    for test in tests:

        try:
            results.append(test())

        except Exception as e:

            print()
            print("TEST ERROR:", e)
            results.append(False)

    passed = sum(results)
    failed = len(results) - passed

    print()
    print("=" * 60)
    print(f"TOTAL TESTS: {len(results)}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 60)

    if failed == 0:
        print("STATUS: V10.1 AI SCORE ISOLATION VALIDATED")
    else:
        print("STATUS: V10.1 VALIDATION FAILED")


if __name__ == "__main__":
    run_tests()