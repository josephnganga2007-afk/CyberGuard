from email_connector import get_gmail_emails
from email_pipeline import process_email


# Test supplier profile
supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "4821"
}


def main():

    print("=" * 60)
    print("CYBERGUARD — LIVE GMAIL RISK PIPELINE")
    print("=" * 60)

    print("\nConnecting to Gmail...\n")

    emails = get_gmail_emails(max_results=10)

    print(f"Retrieved {len(emails)} emails.\n")

    for index, email in enumerate(emails, start=1):

        print("=" * 60)
        print(f"EMAIL {index}")
        print("=" * 60)

        print(f"FROM: {email['sender']}")
        print(f"SUBJECT: {email['subject']}")

        result = process_email(
            email,
            supplier
        )

        print("\nTRIAGE:")
        print(f"Category: {result['category']}")
        print(f"Action: {result['action']}")
        print(f"Reason: {result['triage']['reason']}")

        if result["risk"] is not None:

            risk = result["risk"]

            print("\nRISK ANALYSIS:")
            print(f"Score: {risk['score']}/100")
            print(f"Risk Level: {risk['risk_level']}")

            print("\nWarnings:")

            for warning in risk["warnings"]:
                print(f"- {warning}")

            print("\nRisk Factors:")

            for factor in risk["factors"]:
                print(
                    f"- {factor['name']}: "
                    f"{factor['points']} points"
                )

        else:

            print("\nRisk analysis skipped.")

        print()


if __name__ == "__main__":
    main()