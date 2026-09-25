import base64
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

BASE_DIR = Path(__file__).resolve().parent

TOKEN_FILE = BASE_DIR / "token.json"


def get_gmail_service():
    """
    Load the saved Gmail OAuth token and create
    a Gmail API service.
    """

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "token.json was not found. "
            "Run gmail_auth_test.py first."
        )

    creds = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        SCOPES
    )

    if creds.expired and creds.refresh_token:

        creds.refresh(Request())

        TOKEN_FILE.write_text(
            creds.to_json(),
            encoding="utf-8"
        )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )

def get_gmail_account_email():
    """
    Return the email address of the authenticated Gmail account.
    """
    service = get_gmail_service()

    profile = service.users().getProfile(
        userId="me"
    ).execute()

    return profile.get(
        "emailAddress",
        ""
    ).strip().lower()

def decode_body(data):
    """
    Decode Gmail's base64url encoded message body.
    """

    if not data:
        return ""

    padding = "=" * (-len(data) % 4)

    return base64.urlsafe_b64decode(
        data + padding
    ).decode(
        "utf-8",
        errors="replace"
    )


def get_header(headers, name):
    """
    Find a Gmail message header by name.
    """

    for header in headers:

        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def extract_plain_text(payload):
    """
    Recursively search a Gmail message for
    its plain-text body.
    """

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":

        body = payload.get("body", {})

        return decode_body(
            body.get("data")
        )

    for part in payload.get("parts", []):

        text = extract_plain_text(part)

        if text:
            return text

    return ""


def get_gmail_emails(max_results=5):
    """
    Retrieve recent inbox emails from Gmail.

    Each email includes:
        sender
        subject
        body
        message_id
        thread_id
        gmail_account
    """

    service = get_gmail_service()

    # Identify the Gmail account authenticated by OAuth.
    gmail_account = get_gmail_account_email()

    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=max_results
    ).execute()

    messages = response.get(
        "messages",
        []
    )

    emails = []

    for message in messages:

        message_id = message["id"]

        full_message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        payload = full_message.get(
            "payload",
            {}
        )

        headers = payload.get(
            "headers",
            []
        )

        sender = get_header(
            headers,
            "From"
        )

        subject = get_header(
            headers,
            "Subject"
        )

        body = extract_plain_text(
            payload
        )

        emails.append(
            {
                "sender": sender,
                "subject": subject,
                "body": body,
                "message_id": message_id,
                "thread_id": full_message.get(
                    "threadId"
                ),
                "gmail_account": gmail_account
            }
        )

    return emails


def get_demo_emails():
    """
    Return CyberGuard's original demo emails.

    These are kept for development and testing.
    """

    return [

        {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Meeting confirmation",
            "body": (
                "Hi Joseph, "
                "just confirming our meeting tomorrow at 10:00."
            )
        },

        {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Urgent banking details change",
            "body": (
                "Hi Joseph, "
                "we have changed our banking details. "
                "Please update the account and pay invoice 4582 "
                "as soon as possible."
            )
        },

        {
            "sender": "accounts@abcsupplies.co.za",
            "subject": "Invoice update",
            "body": (
                "Hi Joseph, "
                "please see the updated information regarding "
                "our latest invoice."
            )
        }

    ]