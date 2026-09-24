from email_pipeline import process_email


# Use the real ABC Supplies trusted details
supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "4821"
}


def print_result(email, result):

    print("=" * 70)

    print("FROM:", email["sender"])
    print("SUBJECT:", email["subject"])

    print()

    print("TRIAGE:")
    print("Category:", result["category"])
    print("Action:", result["action"])
    print("Reason:", result["triage"]["reason"])
    print("Signals:", result["triage"]["signals"])

    print()

    if result["risk"] is None:

        print("RISK ENGINE:")
        print("NOT RUN")

    else:

        print("RISK ENGINE:")
        print("Score:", result["risk"]["score"])
        print("Risk level:", result["risk"]["risk_level"])
        print("Warnings:", result["risk"]["warnings"])
        print("Factors:", result["risk"]["factors"])

    print()


test_emails = [

    # 1. Completely irrelevant
    {
        "sender": "hr@company.co.za",
        "subject": "Account manager meeting",
        "body": (
            "Our account manager will join the meeting tomorrow."
        )
    },

    # 2. Financial document but no explicit action
    {
        "sender": "supplier@example.com",
        "subject": "Invoice 4582",
        "body": (
            "Please find attached invoice 4582."
        )
    },

    # 3. Payment-related banking change
    {
        "sender": "accounts@abcsupplies.co.za",
        "subject": "Urgent banking details change",
        "body": (
            "URGENT ACTION REQUIRED. "
            "We have changed our banking details. "
            "Please update the beneficiary and pay invoice 4582 "
            "to our new account. "
            "Account Number: 73918462. "
            "Please make payment immediately."
        )
    },

    # 4. Beneficiary change + financial obligation
    {
        "sender": "supplier@example.com",
        "subject": "Updated beneficiary",
        "body": (
            "Please use the new beneficiary details "
            "for the outstanding amount."
        )
    },

    # 5. Irrelevant security communication
    {
        "sender": "security@example.com",
        "subject": "Banking fraud awareness webinar",
        "body": (
            "Our banking partner is hosting a webinar "
            "about payment fraud prevention."
        )
    },

    # 6. Simple funds transfer request
    {
        "sender": "supplier@example.com",
        "subject": "Funds transfer",
        "body": (
            "Please transfer the funds to the account provided."
        )
    },

]


for email in test_emails:

    result = process_email(
        email,
        supplier
    )

    print_result(
        email,
        result
    )