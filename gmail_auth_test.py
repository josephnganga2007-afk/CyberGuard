from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]

print("Starting Gmail authentication...")

flow = InstalledAppFlow.from_client_secrets_file(
    str(CREDENTIALS_FILE),
    SCOPES
)

creds = flow.run_local_server(port=0)

print("OAuth authentication completed.")
print("Saving token...")

TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

print(f"Token saved to: {TOKEN_FILE}")
print(f"Token exists: {TOKEN_FILE.exists()}")
print(f"Token size: {TOKEN_FILE.stat().st_size} bytes")

print("\nGMAIL AUTHENTICATION SUCCESSFUL")