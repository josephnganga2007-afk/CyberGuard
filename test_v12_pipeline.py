from email_connector import get_gmail_emails
from email_pipeline import process_email


def main():
    emails = get_gmail_emails(max_results=5)

    print("GMAIL EMAILS:", len(emails))

    for email in emails:
        result = process_email(email)

        print("\n" + "=" * 60)
        print("FROM:", email["sender"])
        print("SUBJECT:", email["subject"])
        print("GMAIL ID:", result["gmail_message_id"])
        print("CATEGORY:", result["category"])
        print("ACTION:", result["action"])

        supplier = result["supplier"]

        if supplier:
            print("SUPPLIER:", supplier["name"])
            print("TRUSTED EMAIL:", supplier["email"])
        else:
            print("SUPPLIER: UNKNOWN")

        if result["risk"]:
            print("RISK SCORE:", result["risk"]["score"])
            print("RISK LEVEL:", result["risk"]["risk_level"])

            print("WARNINGS:")
            for warning in result["risk"]["warnings"]:
                print(" -", warning)


if __name__ == "__main__":
    main()