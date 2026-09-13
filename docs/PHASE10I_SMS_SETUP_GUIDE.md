# PARVAT NETRA • PHASE 10I: CARRIER SMS ONBOARDING & SETUP GUIDE

**Audience:** State EOC IT Administrators, NDMA/SDMA Telecom Liaisons, System Integrators  
**Scope:** Configuration, CDAC Mobile Seva Credential Onboarding, and Telecom DLT Compliance  

---

## 1. Overview
PARVAT NETRA operates an India Government-compliant, provider-neutral Emergency SMS Dissemination Gateway. By default, the system runs with:
```bash
REAL_PUBLIC_SMS=DISABLED
SMS_DRY_RUN=1
```
This guarantees that development, testing, and evaluator walkthroughs execute without costs, carrier penalties, or live RF broadcast.

---

## 2. Environment Variables Configuration

Create or update `.env` in the repository root:

```env
# ==============================================================================
# PARVAT NETRA • Emergency SMS Gateway Configuration
# ==============================================================================

# Safety Locks (MUST remain DISABLED and 1 unless deploying to certified production)
REAL_PUBLIC_SMS=DISABLED
SMS_DRY_RUN=1

# Telecom Provider Selection (cdac / mock / sandes)
SMS_PROVIDER=cdac

# India Government CDAC Mobile Seva Gateway Credentials
CDAC_PE_ID=1101234567890123456
CDAC_SENDER_ID=PARVAT
CDAC_USER_ID=parvat_netra_eoc
CDAC_PASSWORD=your_secure_cdac_password
CDAC_SECURE_KEY=your_cdac_secure_hmac_key
CDAC_API_URL=https://mgov.gov.in/epramaan/service/sendSMS.action

# TRAI Entity Identification
TRAI_ENTITY_ID=1101234567890123456

# DLT Registered Template Identifiers (Approved by Telecom Regulatory Authority of India)
DLT_LANDSLIDE_WARNING=DLT-TE-110716-001
DLT_HIGH_RISK_ADVISORY=DLT-TE-110716-002
DLT_ROAD_CLOSURE=DLT-TE-110716-003
DLT_EVACUATION_ADVISORY=DLT-TE-110716-004
DLT_ALL_CLEAR=DLT-TE-110716-005
DLT_TEST_ALERT=DLT-TE-110716-006

# Asynchronous Delivery Receipt Webhook URL
SMS_DLR_WEBHOOK_URL=https://parvatnetra.gov.in/api/sms/dlr
```

---

## 3. TRAI DLT Registration Steps

1. **Enterprise Registration**:
   - Register the State Disaster Management Authority (SDMA) or National Disaster Management Authority (NDMA) on a TRAI-authorized DLT portal (e.g., Jio, Airtel, Vodafone Idea, BSNL).
   - Obtain the 19-digit **Principal Entity ID (PE ID)**.

2. **Header Registration**:
   - Register the 6-character alphabetic Header: `PARVAT` (Category: Government / Emergency Alerts).

3. **Content Template Registration**:
   - Register the 6 canonical templates with variable tags `{1}`, `{2}`, etc. matching the template formats defined in `services/production_sms_service.py`.
   - Category: **Explicit Consent / Service Implicit / Emergency Alert**.

---

## 4. Operational API Workflow

### 4.1 Check Gateway Status
```bash
curl -X GET http://localhost:8080/api/sms/status
```
Expected response:
```json
{
  "status": "success",
  "data": {
    "configuration_state": "UNCONFIGURED",
    "provider_name": "CDAC",
    "safety_mode": "TEST/DRY_RUN",
    "real_public_sms_enabled": false,
    "sms_dry_run": true,
    "india_government_readiness": {
      "registered_header": "PARVAT",
      "registered_templates_count": 6,
      "dlr_webhook_endpoint": "/api/sms/dlr"
    }
  }
}
```

### 4.2 Queue Authorized Emergency SMS Broadcast
```bash
curl -X POST http://localhost:8080/api/sms/queue-emergency \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-2026-001",
    "actor_id": "DM_PAKYONG",
    "actor_role": "DISTRICT_AUTHORITY",
    "auth_token": "<cryptographic_hmac_token>",
    "geofence_polygon": [
      [27.3200, 88.6000],
      [27.3400, 88.6000],
      [27.3400, 88.6200],
      [27.3200, 88.6200],
      [27.3200, 88.6000]
    ],
    "template_type": "LANDSLIDE_WARNING",
    "jurisdiction": "Pakyong"
  }'
```

### 4.3 Carrier Delivery Receipt (DLR) Webhook Callback
Telecom carriers will post delivery confirmations to:
```bash
POST /api/sms/dlr
Content-Type: application/json

{
  "dispatch_id": "SMS-DISP-A1B2C3D4E5F6",
  "provider_reference": "CDAC-MSG-987654",
  "carrier_status": "DELIVRD"
}
```

### 4.4 Inquire Delivery Status
```bash
curl -X GET http://localhost:8080/api/sms/delivery/SMS-DISP-A1B2C3D4E5F6
```

---

## 5. Security Invariants
1. **Never commit `.env` credentials to git**. Run `python mcp/scripts/validate_config.py`.
2. **Never change `REAL_PUBLIC_SMS=ENABLED` on staging or evaluation environments**.
3. **Always verify 2-of-3 corroboration before dispatch**.
