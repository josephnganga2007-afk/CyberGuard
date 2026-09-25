from email_connector import get_gmail_emails
from email_pipeline import process_email


supplier = {
    "name": "ABC Supplies",
    "email": "accounts@abcsupplies.co.za",
    "account_last_four": "4821"
}


def main():

    print("=" * 60)
    print("CYBERGUARD — GMAIL → FULL PIPELINE HANDOFF")
    print("=" * 60)

    emails = get_gmail_emails(max_results=10)

    print(f"\nRetrieved {len(emails)} emails.\n")

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

        print("\nPIPELINE RESULT:")
        print(f"Stage: {result['stage']}")
        print(f"Category: {result['category']}")
        print(f"Action: {result['action']}")

        if result["risk"]:

            print("\nRISK:")
            print(f"Score: {result['risk']['score']}/100")
            print(
                f"Level: {result['risk']['risk_level']}"
            )

            print("\nWarnings:")

            for warning in result["risk"]["warnings"]:
                print(f"- {warning}")

        else:

            print("\nRisk analysis: SKIPPED")

        print()


if __name__ == "__main__":
    main()