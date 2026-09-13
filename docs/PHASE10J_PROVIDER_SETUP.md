# PARVAT NETRA • PHASE 10J: LIVE PROVIDER CONFIGURATION GUIDE
## Production Email & CDAC / Telecom SMS Gateway Onboarding

**System:** PARVAT NETRA — NER Sentinel  
**Phase:** 10J — Live Emergency Notification Provider Setup  
**Standard:** National Disaster Management Guidelines / TRAI DLT Mandates  

---

## 1. Overview

PARVAT NETRA supports dual-channel emergency notification dispatch via:
1. **Email Dissemination**: High-throughput SMTP (NIC Gov Mail, AWS SES, Postmark) or REST API (SendGrid, Mailgun).
2. **SMS Dissemination**: C-DAC / Government Emergency Push SMS Gateway or Tier-1 Indian Telecom Aggregators with TRAI Distributed Ledger Technology (DLT) compliance.

By default, when credentials are absent, the system operates in **SAFE DEMO / SIMULATION MODE** (`DEMO_EMAIL_GATEWAY` and `DEMO_SMS_GATEWAY`). To enable live delivery for production or judge demonstrations with live recipients, configure the environment variables described below.

---

## 2. Real Email Provider Configuration

### Option A: Standard SMTP (Recommended for Gov Mail / NIC / SES)
Set the following variables in your `.env` file:
```ini
# Real SMTP Configuration
SMTP_HOST=smtp.mailgov.in
SMTP_PORT=587
SMTP_USER=alerts@parvatnetra.gov.in
SMTP_PASSWORD=YourSecureSMTPPasswordHere
SMTP_USE_TLS=true
EMAIL_FROM="PARVAT NETRA Emergency Operations <alerts@parvatnetra.gov.in>"
```

### Option B: REST API Provider (SendGrid / Mailgun)
```ini
# Real Email API Configuration
EMAIL_API_PROVIDER=SENDGRID
EMAIL_API_KEY=SG.your_sendgrid_api_key_here
EMAIL_API_URL=https://api.sendgrid.com/v3/mail/send
EMAIL_FROM=alerts@parvatnetra.gov.in
```

### Invariant:
If credentials are provided and valid, live dispatches will return status `SENT`. If credentials fail authentication or are omitted, the service falls back gracefully to `DEMO_EMAIL_GATEWAY` (or fails closed when `force_real_email=true`).

---

## 3. Real SMS Gateway Configuration (CDAC / Indian Telecom DLT)

Emergency SMS in India is strictly governed by the **Disaster Management Act (2005)** and **TRAI DLT Regulations**.

Set the following variables in your `.env` file:
```ini
# CDAC Emergency Push SMS Gateway
CDAC_SMS_ENDPOINT=https://mgov.gov.in/esms/api/pushsms
CDAC_USERNAME=parvat_netra_ner
CDAC_PASSWORD=YourCdacEncryptedKey
CDAC_SENDER_ID=PARVAT
CDAC_SECURE_KEY=YourHmacAuthKey
TRAI_DLT_PE_ID=1101552390000012345
```

### Registered TRAI DLT Templates
| Template ID | Content Template Summary | Header |
| :--- | :--- | :--- |
| `110716892000001` | `[PARVAT NETRA TEST ALERT] Scenario: {#var#}. CRI: {#var#}. FoS: {#var#}.` | `PARVAT` |
| `110716892000002` | `[PARVAT NETRA EVACUATION ADVISORY] Sector: {#var#}. Take immediate shelter.` | `PARVAT` |

### Safety Flags:
```ini
# Production Controls
REAL_PUBLIC_SMS=0     # Must remain 0 to prevent accidental bulk public dissemination
SMS_DRY_RUN=0         # Set to 0 to enable live RF telecom emissions to test recipient phone
PAHAD_DEMO_MODE=0     # Set to 0 to force live provider routing
```

---

## 4. Live Judge Demonstration Mode vs Production Mode

### Live Judge Demonstration (Real Individual Test Phone & Email):
To send a real email and SMS to a specific judge's mobile phone and inbox during an evaluation:
1. Provide valid SMTP credentials and/or CDAC credentials in `.env`.
2. Keep `REAL_PUBLIC_SMS=0` (ensures whole geofence bulk broadcast remains safely locked).
3. Set `SMS_DRY_RUN=0`.
4. In the UI (`/notifications`), enter the judge's email and phone number.
5. Click **`RUN SCENARIO + SEND`**.
6. The test message will be delivered directly to the entered phone number and email address with tag `[PARVAT NETRA TEST ALERT]`.

### Simulation / Offline Mode:
When credentials are not supplied:
- Email executes via `DEMO_EMAIL_GATEWAY` returning simulated references (`EML-DEMO-*`).
- SMS executes via `DEMO_SMS_GATEWAY` returning simulated references (`SMS-REF-*`).
- Status is explicitly badged as `SIMULATED`.
- Never fakes carrier delivery (`DELIVERED`).

---

## 5. Security & Rate Limiting

- **Rate Limiting**: The demo endpoint enforces an in-memory limit of **20 dispatches per minute** to prevent resource exhaustion or carrier flooding.
- **HMAC Tokens**: Operational public dispatches require an authenticated HMAC signature from an authorized Incident Commander.
- **PII Zero-Storage**: Recipient telephone numbers and email addresses are masked before logging to the immutable journal.

---

## 6. Troubleshooting

| Symptom | Cause | Remediation |
| :--- | :--- | :--- |
| `Status: BLOCKED` | `force_real_email=true` but SMTP unconfigured | Add valid `SMTP_HOST` or toggle demo mode. |
| `Status: FAILED (SMTPAuthenticationError)` | Bad SMTP username or application password | Verify app-specific password for Gmail/Gov Mail. |
| `Status: DUPLICATE_SUPPRESSED` | Sent twice within 60s window | Wait 60s or change recipient/scenario parameters. |
| `SMS Carrier Webhook 401` | Invalid HMAC signature on carrier webhook | Ensure carrier webhook URL includes `?secret=...`. |
