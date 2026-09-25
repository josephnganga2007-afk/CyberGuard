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
    """Load the saved OAuth token and create a Gmail API service."""

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


def decode_body(data):
    """Decode Gmail's base64url message body."""

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
    """Find a Gmail message header."""

    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def extract_plain_text(payload):
    """Recursively find the plain-text portion of a Gmail message."""

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        body = payload.get("body", {})
        return decode_body(body.get("data"))

    for part in payload.get("parts", []):
        text = extract_plain_text(part)

        if text:
            return text

    return ""


def main():

    print("Connecting to Gmail...")

    service = get_gmail_service()

    print("Gmail connection successful.\n")

    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=5
    ).execute()

    messages = response.get("messages", [])

    if not messages:
        print("No inbox messages found.")
        return

    print(f"Found {len(messages)} inbox messages.\n")

    for index, message in enumerate(messages, start=1):

        message_id = message["id"]

        full_message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        payload = full_message.get("payload", {})

        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")

        body = extract_plain_text(payload)

        print("=" * 60)
        print(f"EMAIL {index}")
        print("=" * 60)

        print(f"FROM: {sender}")
        print(f"SUBJECT: {subject}")

        print("\nBODY PREVIEW:")

        preview = body.strip()

        if len(preview) > 500:
            preview = preview[:500] + "..."

        print(preview)

        print()


if __name__ == "__main__":
    main()