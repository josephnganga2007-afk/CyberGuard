from risk_engine import analyze_transaction


SUPPLIER = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


TESTS = [
    (
        "Updated Invoice Attachment",
        "accounts@abcsupplies.co.za",
        "The updated invoice is attached for your records.",
        False
    ),

    (
        "Revised Payment Schedule",
        "accounts@abcsupplies.co.za",
        "Please review the revised payment schedule for this quarter.",
        False
    ),

    (
        "Account Details Unchanged",
        "accounts@abcsupplies.co.za",
        "The account details are unchanged. No amendments are required.",
        False
    ),

    (
        "Updated Pricing",
        "accounts@abcsupplies.co.za",
        "The new invoice reflects the updated pricing.",
        False
    ),

    (
        "Updated Transfer Document",
        "accounts@abcsupplies.co.za",
        "The transfer document has been updated. Please use the latest version.",
        False
    ),

    (
        "Existing Payment Account",
        "accounts@abcsupplies.co.za",
        "Please use the existing payment account for today's invoice.",
        False
    ),

    (
        "Real Beneficiary Change",
        "accounts@abcsupplies.co.za",
        "We have changed our beneficiary details. Please use the new account for payment.",
        True
    ),

    (
        "Real Receiving Account Change",
        "accounts@abcsupplies.co.za",
        "Our receiving account has changed. Please update your payment records.",
        True
    ),

    (
        "Real Payment Destination Change",
        "accounts@abcsupplies.co.za",
        "The payment destination has changed. Please use the revised details.",
        True
    ),

    (
        "Real Redirection",
        "accounts@abcsupplies.co.za",
        "Please route the next payment using the details below.",
        True
    )
]


passes = 0
false_positives = 0
missed_detections = 0


print("=" * 75)
print("CYBERGUARD - FALSE-POSITIVE / ADVERSARIAL TEST SUITE")
print("=" * 75)


for number, test in enumerate(TESTS, start=1):

    name = test[0]
    sender = test[1]
    message_text = test[2]
    expected_destination_change = test[3]

    message = (
        f"From: {sender}\n\n"
        f"{message_text}"
    )

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        SUPPLIER
    )

    destination_detected = any(
        factor.get("name") in (
            "Beneficiary change",
            "Payment destination change"
        )
        for factor in factors
    )

    print()
    print("=" * 75)
    print(f"TEST {number:02d} - {name}")
    print("-" * 75)

    print(f"From: {sender}")
    print()
    print(message_text)
    print()

    print(f"SCORE: {score}")
    print(f"RISK LEVEL: {risk_level}")
    print(f"DESTINATION CHANGE DETECTED: {destination_detected}")

    if destination_detected == expected_destination_change:
        print("RESULT: PASS")
        passes += 1

    elif destination_detected and not expected_destination_change:
        print("RESULT: FALSE POSITIVE")
        false_positives += 1

    else:
        print("RESULT: MISSED DETECTION")
        missed_detections += 1

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
print("=" * 75)
print("FALSE-POSITIVE / ADVERSARIAL TESTING COMPLETE")
print("=" * 75)

print(f"TOTAL TESTS: {len(TESTS)}")
print(f"PASSED: {passes}")
print(f"FALSE POSITIVES: {false_positives}")
print(f"MISSED DETECTIONS: {missed_detections}")

print("=" * 75)

if (
    passes == len(TESTS)
    and false_positives == 0
    and missed_detections == 0
):
    print("STATUS: ALL TESTS PASSED")
else:
    print("STATUS: REGRESSION DETECTED")