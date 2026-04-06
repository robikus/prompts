import os
import json
import base64
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ── Config ────────

ACCOUNTS = [
    "polakovic.robert@gmail.com",
    "katerina.chuda2@gmail.com",
]

ALIEXPRESS_SENDERS = [
    "@newarrival.aliexpress.com",
    "@deals.aliexpress.com",
    "@selections.aliexpress.com",
]

EXCLUDE_SENDERS = ["allegro", "reas.cz", "alkohol.cz", "bulios", "coinmate"]

SUBROUTINES = {
    "unpaid": {
        "days": 60,
        "query": "faktura OR neuhrazeny OR nezaplaceno OR zaplatit OR uhradit OR upominka OR dluh OR splatnost OR upozorneni OR vyzva OR prodlouzeni",
    },
    "contracts": {
        "days": 60,
        "query": "smlouva OR dohoda OR dodatek OR objednavka",
    },
    "urgent": {
        "days": 60,
        "query": "urgence OR okamzite OR neprodlene",
    },
    "deliveries": {
        "days": 30,
        "query": "PPL OR Balikovna OR AlzaBox OR DPD OR zasilka OR doruceni OR vyzvednout OR expedovano OR tracking",
    },
}

# ── Entry point ───────────────────────────────────────────────────────────────

def run_gmail_routine(request=None):
    """Cloud Function entry point. Also callable directly."""
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    # Secrets loaded from environment variables (set in Cloud Function config)

    for account in ACCOUNTS:
        service = get_gmail_service(account)
        if account == ACCOUNTS[0]:  # Robert only
            cleanup_aliexpress(service)
        results = scan_account(service)
        html = build_html_via_claude(results, account, anthropic_key)
        send_summary(service, account, html)
        print(f"Done: {account}")

    return "OK"

# ── Gmail service ─────────────────────────────────────────────────────────────

TOKEN_ENV = {
    "polakovic.robert@gmail.com": "GMAIL_TOKEN_ROBERT",
    "katerina.chuda2@gmail.com":  "GMAIL_TOKEN_KATERINA",
}

def get_gmail_service(account):
    token_data = json.loads(os.environ[TOKEN_ENV[account]])
    credentials = Credentials.from_authorized_user_info(token_data)
    return build("gmail", "v1", credentials=credentials)

# ── Cleanup ───────────────────────────────────────────────────────────────────

def cleanup_aliexpress(service):
    for domain in ALIEXPRESS_SENDERS:
        query = f"from:{domain}"
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        for msg in messages:
            service.users().messages().trash(userId="me", id=msg["id"]).execute()
    print(f"AliExpress cleanup done, trashed {len(messages)} messages")

# ── Scanning ──────────────────────────────────────────────────────────────────

def scan_account(service):
    results = {}
    for name, cfg in SUBROUTINES.items():
        cutoff = (datetime.now() - timedelta(days=cfg["days"])).strftime("%Y/%m/%d")
        query = f"{cfg['query']} after:{cutoff}"
        results[name] = fetch_emails(service, query)
    return results

def fetch_emails(service, query):
    response = service.users().messages().list(
        userId="me", q=query, maxResults=50
    ).execute()
    messages = response.get("messages", [])
    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        sender = headers.get("From", "")
        if any(ex in sender.lower() for ex in EXCLUDE_SENDERS):
            continue
        emails.append({
            "sender":  sender,
            "subject": headers.get("Subject", ""),
            "date":    headers.get("Date", "")[:16],
        })
    return emails

# ── Claude summarization ───────────────────────────────────────────────────

def build_html_via_claude(results, account, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""You are generating an HTML email summary for {account}.

Build a single HTML email body (no <html>/<head>/<body> tags - just inner content).
4 sections: UNPAID/INVOICES, CONTRACTS, URGENT, DELIVERIES.
Each section: colored <h2> header, then a table: Sender | Subject | Date.
Highlight overdue/urgent rows in light red (#fff0f0).
Empty sections show: "No items found."

CRITICAL: ASCII text only - no emoji, no Czech diacritics.

UNPAID/INVOICES (60 days): {json.dumps(results['unpaid'])}
CONTRACTS (60 days): {json.dumps(results['contracts'])}
URGENT (60 days): {json.dumps(results['urgent'])}
DELIVERIES (30 days): {json.dumps(results['deliveries'])}

Return only HTML, no markdown, no explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

# ── Send summary ──────────────────────────────────────────────────────────────

def send_summary(service, to_account, html_body):
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"Gmail Summary - {to_account} - {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "me"
    msg["To"] = to_account
    msg.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"Summary sent to {to_account}")