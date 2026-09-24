from email_pipeline import process_email


SUPPLIER = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "1234"
}


TEST_EMAILS = [

    # ============================================================
    # LEGITIMATE EMAILS
    # ============================================================

    {
        "name": "Legitimate Invoice",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice 4582",
            "body": """
Hi Joseph,

Please find invoice 4582 attached for the goods supplied this month.

The invoice is due according to our normal payment terms.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": False
    },

    {
        "name": "Payment Confirmation",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Payment received",
            "body": """
Hi Joseph,

We confirm receipt of your payment for invoice 4511.

Thank you.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": False
    },

    {
        "name": "Meeting Confirmation",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Meeting confirmation",
            "body": """
Hi Joseph,

Just confirming our meeting tomorrow at 10:00.

Regards,
ABC Supplies
"""
        },
        "expected_category": "IRRELEVANT",
        "expected_destination": False
    },

    {
        "name": "Invoice Records",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Updated invoice records",
            "body": """
Hi Joseph,

The updated invoice is attached for your records.

No changes have been made to our payment information.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": False
    },


    # ============================================================
    # CLEAR PAYMENT DIVERSION
    # ============================================================

    {
        "name": "Urgent Banking Change",
        "email": {
            "sender": "attacker@example.com",
            "subject": "URGENT - Banking details changed",
            "body": """
Hi Joseph,

URGENT: We have changed our banking details.

Please update the account immediately and pay invoice 4582 using
the new account details below.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "New Beneficiary",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "New beneficiary details",
            "body": """
Hi Joseph,

Our beneficiary details have changed.

Please use the new beneficiary for all future payments.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "Payment Redirection",
        "email": {
            "sender": "attacker@example.com",
            "subject": "Payment instructions",
            "body": """
Hi Joseph,

Please redirect the outstanding payment to the receiving account
provided below.

This should be used for the current invoice.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "Revised Instructions",
        "email": {
            "sender": "attacker@example.com",
            "subject": "Revised payment instructions",
            "body": """
Hi Joseph,

Our payment instructions have been revised.

Please process the next transfer using the new details.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },


    # ============================================================
    # SOCIAL ENGINEERING
    # ============================================================

    {
        "name": "Executive Pressure",
        "email": {
            "sender": "attacker@example.com",
            "subject": "Payment required immediately",
            "body": """
Joseph,

I am currently unavailable by phone.

Please settle the outstanding invoice immediately using the
updated receiving details in the attachment.

Do not delay this payment.

Regards,
Managing Director
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "Deadline Pressure",
        "email": {
            "sender": "attacker@example.com",
            "subject": "Payment deadline",
            "body": """
Hi Joseph,

The invoice is due today.

Please transfer the outstanding amount using the alternative
payment account listed below.

Regards,
Accounts
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },


    # ============================================================
    # SUBTLE DESTINATION LANGUAGE
    # ============================================================

    {
        "name": "Alternative Route",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Payment processing",
            "body": """
Hi Joseph,

For the next settlement, please use the alternative payment
route provided below.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "Receiving Details",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Settlement details",
            "body": """
Hi Joseph,

Please use the receiving details below when processing the
outstanding amount.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

    {
        "name": "New Remittance Destination",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Remittance update",
            "body": """
Hi Joseph,

Future remittances should be sent to our new destination.

Please update your records.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },


    # ============================================================
    # LEGITIMATE ACCOUNT CONTEXT
    # ============================================================

    {
        "name": "Existing Account",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice payment",
            "body": """
Hi Joseph,

Please use the existing payment account for today's invoice.

No changes are required.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": False
    },

    {
        "name": "Banking Unchanged",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice information",
            "body": """
Hi Joseph,

Please find the invoice attached.

Our banking information remains unchanged.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": False
    },


    # ============================================================
    # AMBIGUOUS EMAILS
    # ============================================================

    {
        "name": "Account Update",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Account update",
            "body": """
Hi Joseph,

Please update the account information in your records.

Regards,
ABC Supplies
"""
        },
        "expected_category": "UNCERTAIN",
        "expected_destination": False
    },

    {
        "name": "New Account",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Account update",
            "body": """
Hi Joseph,

Please use the new account going forward.

Regards,
ABC Supplies
"""
        },
        "expected_category": "UNCERTAIN",
        "expected_destination": False
    },

    {
        "name": "Account Manager",
        "email": {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Account manager update",
            "body": """
Hi Joseph,

Our account manager has changed.

Please direct future correspondence to the new contact.

Regards,
ABC Supplies
"""
        },
        "expected_category": "IRRELEVANT",
        "expected_destination": False
    },


    # ============================================================
    # ATTACHMENT / INDIRECT ATTACK
    # ============================================================

    {
        "name": "Attachment Redirection",
        "email": {
            "sender": "attacker@example.com",
            "subject": "Updated settlement document",
            "body": """
Hi Joseph,

Please see the updated settlement document attached.

The payment should be processed using the receiving account
specified in the document.

Regards,
ABC Supplies
"""
        },
        "expected_category": "PAYMENT_RELATED",
        "expected_destination": True
    },

]


print("=" * 75)
print("CYBERGUARD - V8 ADVERSARIAL EMAIL CORPUS")
print("=" * 75)


passed = 0
failed = 0


for i, test in enumerate(TEST_EMAILS, start=1):

    result = process_email(
        test["email"],
        SUPPLIER
    )

    actual_category = result["category"]

    risk = result.get("risk")

    if risk:
        factors = risk.get("factors", [])

        actual_destination = any(
            factor.get("name") in (
                "Beneficiary change",
                "Payment destination change"
            )
            for factor in factors
        )
    else:
        actual_destination = False

    category_ok = actual_category == test["expected_category"]
    destination_ok = actual_destination == test["expected_destination"]

    test_passed = category_ok and destination_ok

    if test_passed:
        result_status = "PASS"
        passed += 1
    else:
        result_status = "FAIL"
        failed += 1

    print()
    print("=" * 75)
    print(f"TEST {i:02d} - {test['name']}")
    print("-" * 75)

    print(f"SENDER:   {test['email']['sender']}")
    print(f"SUBJECT:  {test['email']['subject']}")
    print()
    print(test["email"]["body"].strip())
    print()

    print(f"EXPECTED CATEGORY:      {test['expected_category']}")
    print(f"ACTUAL CATEGORY:        {actual_category}")

    print(f"EXPECTED DESTINATION:   {test['expected_destination']}")
    print(f"DETECTED DESTINATION:   {actual_destination}")

    print(f"RESULT: {result_status}")


print()
print("=" * 75)
print("V8 ADVERSARIAL EMAIL CORPUS COMPLETE")
print("=" * 75)

print(f"TOTAL:  {len(TEST_EMAILS)}")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")

print("=" * 75)

if failed == 0:
    print("STATUS: ALL TESTS PASSED")
else:
    print("STATUS: ADVERSARIAL FAILURES DETECTED")