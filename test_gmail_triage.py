from email_connector import get_gmail_emails
from triage_engine import triage_email


def get_action(category):
    """
    Convert the triage category into the next
    CyberGuard pipeline action.
    """

    if category == "IRRELEVANT":
        return "STOP"

    if category == "PAYMENT_RELATED":
        return "ANALYZE"

    if category == "UNCERTAIN":
        return "HOLD_FOR_REVIEW"

    return "HOLD_FOR_REVIEW"


def main():

    print("=" * 60)
    print("CYBERGUARD — REAL GMAIL TRIAGE TEST")
    print("=" * 60)

    print("\nConnecting to Gmail...\n")

    emails = get_gmail_emails(max_results=5)

    print(f"Retrieved {len(emails)} emails.\n")

    for index, email in enumerate(emails, start=1):

        print("=" * 60)
        print(f"EMAIL {index}")
        print("=" * 60)

        print(f"FROM: {email['sender']}")
        print(f"SUBJECT: {email['subject']}")

        triage_result = triage_email(email)

        category = triage_result["category"]
        action = get_action(category)

        print("\nTRIAGE RESULT:")
        print(f"Category: {category}")
        print(f"Action: {action}")
        print(f"Reason: {triage_result['reason']}")
        print(f"Signals: {triage_result['signals']}")

        print()


if __name__ == "__main__":
    main()