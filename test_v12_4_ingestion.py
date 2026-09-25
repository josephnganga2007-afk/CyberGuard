from email_connector import get_gmail_emails
from gmail_ingestion import ingest_email


def main():
    emails = get_gmail_emails(max_results=5)

    print("GMAIL EMAILS:", len(emails))

    for email in emails:
        result = ingest_email(email)

        print("\n" + "=" * 60)
        print("FROM:", email["sender"])
        print("SUBJECT:", email["subject"])
        print("STATUS:", result["status"])
        print("GMAIL ID:", result["gmail_message_id"])
        print("REASON:", result["reason"])


if __name__ == "__main__":
    main()