# Claude Routines

Routine definitions for Claude in Chrome automation.
Triggered by typing the routine name in a Claude conversation.

Base URL:
`https://raw.githubusercontent.com/robikus/prompts/refs/heads/main/claude_routines/routines/{routine_name}.yaml`

---

## Routines

### `gmail`

**Trigger:** type `gmail`

**What it does:**
1. Cleans AliExpress marketing from Robert's inbox
2. Scans both accounts for important emails
3. Sends a formatted HTML summary to each account via webhook
4. Shows the full summary as tables in chat

**Accounts:**
- polakovic.robert@gmail.com
- katerina.chuda2@gmail.com

**Subroutines:**

| Subroutine | Description | Window |
|------------|-------------|--------|
| `cleanup` | Delete AliExpress marketing (Robert only) | all time |
| `unpaid` | Invoices, payment reminders, overdue | 2 months |
| `contracts` | Contracts, agreements, T&C changes | 2 months |
| `urgent` | Security alerts, urgent notices | 2 months |
| `deliveries` | PPL, Balíkovna, AlzaBox, DPD parcels | 1 month |

---

## HTML Email — Google Apps Script Webhook

Summaries are sent as HTML via a Google Apps Script web app.

**Webhook URL** (safe to store — protected by secret):
```
https://script.google.com/macros/s/AKfycbzy4lt0Ra6b4LXbAmWEtQ8Vb7hCINdz5XSdvc9TtP2DAFfeJo6FF7D1JYfrX4Bl8mgEQQ/exec
```

**Secret:** stored in Claude memory only — never committed to this repo.

**Apps Script code:**
```javascript
function doPost(e) {
  const data = JSON.parse(e.postData.contents);

  if (data.secret !== 'YOUR_SECRET_HERE') {
    return ContentService
      .createTextOutput(JSON.stringify({status: 'unauthorized'}))
      .setMimeType(ContentService.MimeType.JSON);
  }

  GmailApp.sendEmail(
    data.to,
    data.subject,
    '',
    {
      htmlBody: '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>'
                + data.body + '</body></html>',
      name: 'Claude Gmail Routine'
    }
  );

  return ContentService
    .createTextOutput(JSON.stringify({status: 'sent'}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

**Important notes:**
- The webhook fetch must run from a `script.google.com` page
  — Gmail's CSP blocks cross-origin fetch to `script.google.com`
- HTML body must use ASCII-safe text only (no emoji, no Czech diacritics)
  — these cause `?` rendering issues in email clients
- To redeploy after code changes: Deploy → Manage deployments →
  Edit (pencil) → New version → Deploy (URL stays the same)

---

## Adding New Routines

1. Create `claude_routines/routines/{name}.yaml`
2. Follow the same structure as `gmail.yaml`
3. No memory update needed — Claude fetches by name automatically
4. Trigger by typing the routine name in chat

---

## Secrets Management

| Secret | Where stored |
|--------|-------------|
| Gmail webhook secret | Claude memory only |

Never commit secrets to this repo.