from risk_engine import analyze_transaction


supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "4821"
}


tests = [
    (
        "Payment destination changed",
        """
        From: accounts@abcsupplies.co.za

        Please amend the payment destination for future payments.
        """
    ),

    (
        "Receiving account changed",
        """
        From: accounts@abcsupplies.co.za

        Our receiving account has changed.
        Please use the new details for the next payment.
        """
    ),

    (
        "Redirect payment",
        """
        From: accounts@abcsupplies.co.za

        Please redirect the outstanding payment to our new
        receiving details.
        """
    ),

    (
        "Revised banking recipient",
        """
        From: accounts@abcsupplies.co.za

        Kindly route the outstanding balance to the revised
        banking recipient.
        """
    ),

    (
        "New remittance destination",
        """
        From: accounts@abcsupplies.co.za

        Future remittances should be sent to our new destination.
        """
    ),

    (
        "Account replacement",
        """
        From: accounts@abcsupplies.co.za

        Please replace the account currently used for payments.
        """
    ),

    (
        "Change receiving details",
        """
        From: accounts@abcsupplies.co.za

        Our receiving details have been updated.
        Please use them for today's payment.
        """
    ),

    (
        "Urgent destination change",
        """
        From: attacker@example.com

        URGENT: Please redirect today's payment to the revised
        receiving account immediately.
        """
    ),

    (
        "Existing destination",
        """
        From: accounts@abcsupplies.co.za

        Please continue using the existing payment destination.
        """
    ),

    (
        "No change",
        """
        From: accounts@abcsupplies.co.za

        Our banking information remains unchanged.
        """
    ),
        (
        "Redirect funds",
        """
        From: attacker@example.com

        Please redirect the funds for invoice 4582 to the
        revised receiving account.
        """
    ),

    (
        "New receiving account",
        """
        From: accounts@abcsupplies.co.za

        Our receiving account has changed.
        Please use the new account for future payments.
        """
    ),

    (
        "Revised destination",
        """
        From: attacker@example.com

        URGENT: Please use the revised payment destination
        for today's transfer.
        """
    ),

    (
        "Existing destination remains",
        """
        From: accounts@abcsupplies.co.za

        Please continue using our existing payment destination.
        No changes are required.
        """
    ),
]


for name, message in tests:

    score, risk_level, warnings, factors = analyze_transaction(
        message,
        supplier
    )

    print("=" * 70)
    print(name)
    print("-" * 70)
    print(message.strip())
    print()
    print("SCORE:", score)
    print("RISK LEVEL:", risk_level)

    print()
    print("FACTORS:")

    if factors:
        for factor in factors:
            print(
                f"- {factor['name']}: +{factor['points']}"
            )
    else:
        print("- None")

    print()