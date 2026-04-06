"""
Run once per account to generate OAuth tokens.
Store the resulting token JSON in environment variables.
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def setup_oauth(account_hint="robert"):
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",  # Download from Google Cloud Console
        SCOPES
    )
    creds = flow.run_local_server(port=0)
    token_data = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        creds.scopes,
    }
    filename = f"token_{account_hint}.json"
    with open(filename, "w") as f:
        json.dump(token_data, f)
    print(f"Saved to {filename} — store this in your environment variables.")

if __name__ == "__main__":
    setup_oauth("robert")
    setup_oauth("katerina")