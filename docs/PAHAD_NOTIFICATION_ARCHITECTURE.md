# PARVAT NETRA / PAHAD AI — Notification & Alert Orchestration Architecture

**Document Version:** 1.0  
**Phase:** 3.5 — Intelligent Alerting + 15 km Geofencing + Push + SMS + CAP + Notification Center  
**Classification:** Disaster-Intelligence Technical Specification  
**Standard:** Smart India Hackathon (SIH) Grade • National Early Warning Architecture  

---

## 1. System Overview

PARVAT NETRA's Phase 3.5 Alert Orchestration Layer bridges predictive landslide modeling (PAHAD AI) with last-mile emergency dissemination across the 8 states of the North Eastern Region (NER). It enforces strict physical safety invariants, multi-channel broadcast synchronization, privacy-preserving recipient registry, and tamper-evident audit logging.

```
       ┌─────────────────────────────────────────────────────────────┐
       │                 PAHAD AI PREDICTIVE CORE                    │
       │  • Infinite-Slope FoS (Mohr-Coulomb)                        │
       │  • Calibrated GBDT Event Probability (6h/12h/24h/48h)       │
       │  • IMD Intensity-Duration (I-D) Rainfall Threshold          │
       │  • In-Situ Borehole Inclinometer / Piezometer Telemetry     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             PAHAD ALERT POLICY ENGINE (Section 3-5)         │
       │  • 2-of-3 Independent Signal Gate (Physical / Rain / ML)    │
       │  • Multi-Signal Concordance (LOW/MOD/HIGH/VERY_HIGH/EXTREME)│
       │  • "Why This Alert?" Non-Causal Explainability Drivers      │
       │  • Escalation Damping & Multi-Cycle Hysteresis              │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │        NOTIFICATION ORCHESTRATOR & GEOFENCE ENGINE          │
       │  • Deterministic SHA-256 Fingerprint Deduplication (30 min) │
       │  • Multi-Geometry 15 km Geofence (Point, Corridor, Polygon) │
       │  • Zero-PII Privacy Registry (Hashed Phones, Role Bundling) │
       │  • Lifecycle State Machine (READY_FOR_AUTH → AUTHORIZED)    │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                ┌─────────────────────┴─────────────────────┐
                ▼                                           ▼
       [AUTHORITY GATE]                            [MULTI-CHANNEL DISPATCH]
   District Magistrate / SDMA              ┌─────────────────────────────────────┐
   Incident Commander Sign-Off             │ 1. Web Push (VAPID / ServiceWorker) │
   (Explicit Digital Audit Trail)          │ 2. Mobile Push (FCM / APNs Token)   │
                                           │ 3. Emergency SMS (CDAC / Multiling) │
                                           │ 4. OASIS CAP v1.2 XML (SACHET)      │
                                           │ 5. Local Edge Gateway / Siren Mesh  │
                                           └─────────────────────────────────────┘
```

---

## 2. Core Safety Invariants

1. **Constitutional Separation of Stages**:
   $$\text{Prediction} \ne \text{Alert Recommendation} \ne \text{Authorized Alert} \ne \text{Dispatch} \ne \text{Delivered} \ne \text{Acknowledged}$$
   No autonomous algorithm is permitted to bypass the civil authority sign-off gate for life-critical public warnings.
2. **2-of-3 Independent Confirmation Rule**:
   A single sensor spike or anomalous AI probability cannot trigger an `EXTREME` public evacuation alert. At least 2 of 3 independent modalities (`Mohr-Coulomb FoS \le 1.05`, `Rainfall I-D breach`, or `ML P(event) \ge 0.70`) must corroborate the event.
3. **DRY_RUN Invariant**:
   To prevent accidental panic or unauthorized telecom charges during development and demonstration, the pipeline operates in `DRY_RUN=true` by default. Live telecommunications require explicit environment provisioning (`DRY_RUN=false`).
4. **Data Honesty & Provenance**:
   Every transmission, report, and UI element carries an explicit provenance tag: `[LIVE]`, `[SIMULATED]`, `[HISTORICAL]`, or `[DEMO]`.

---

## 3. Delivery Channels & Gateway Specifications

### 3.1 Web Push & Mobile Push
- **Technology**: W3C Push API, VAPID (Voluntary Application Server Identification) for web browsers; FCM/APNs token abstractions for Android/iOS mobile apps.
- **Payload Schema**:
  - `title`: Institutional headline (`PAHAD AI EXTREME ALERT`).
  - `severity`: Standardized risk band (`EXTREME`, `VERY_HIGH`, `HIGH`).
  - `location`: Hillslope sector reference (`NH-10 Km 48, Singtam`).
  - `short_message`: Action-oriented advisory (`Evacuate lower slopes immediately`).
  - `issued_at`: UTC ISO timestamp.
  - `alert_id`: Unique identifier (`PN-ALERT-XXXXXX`).
  - `deep_link`: In-app routing URL (`/notifications?alert_id=...`).

### 3.2 Emergency SMS Gateway
- **Technology**: C-DAC Mobile Seva (Govt of India National SMS Gateway) integration with fallback to MockSMSProvider.
- **Single-Segment Length Constraint**: All SMS messages are strictly enforced $\le 160$ characters.
- **Multilingual Support**: Compact, localized templates in 6 regional languages:
  1. **English (`en`)**: Universal coordination lingua franca.
  2. **Hindi (`hi`)**: National official language.
  3. **Nepali (`ne`)**: Primary regional language of Sikkim and Darjeeling hills.
  4. **Bhutia (`bh`)**: Indigenous language of North/West Sikkim.
  5. **Lepcha (`lp`)**: Indigenous language of Dzongu and Teesta valley.
  6. **Assamese (`as`)**: Regional language of Assam valley and Brahmaputra basin.

### 3.3 OASIS CAP v1.2 XML Gateway
- **Compliance**: OASIS Standard CAP v1.2 and ITU-T Recommendation X.1303.
- **National Ingestion**: Designed for NDMA SACHET all-India emergency alert feeder.
- **Payload Enclosures**: Includes `<identifier>`, `<sender>`, `<sent>`, `<status>`, `<msgType>`, `<scope>`, `<category>Geo</category>`, `<urgency>`, `<severity>`, `<certainty>`, and `<polygon>` coordinate sets.

### 3.4 Local Edge & Siren Mesh
- **Resilience**: Operates via Sub-GHz LoRa (865 MHz) and Bluetooth Low Energy (BLE) relays when optical fiber or cellular infrastructure collapses.
- **Dual-Tone EAS Siren**: Generates 853 Hz / 960 Hz acoustic warning patterns at vulnerable bridge piers and tunnel portals.

---

## 4. Privacy-Preserving Recipient Registry

To comply with Indian data protection norms (DPDP Act) and GIGW 3.0 standards:
1. **Zero Cleartext Phone Numbers**: Recipient telephone numbers are irreversibly hashed using SHA-256 (`phone_hash`) with a server salt.
2. **Masked Telemetry References**: Frontend interfaces only receive masked representations (`+91-XXXXX-3210`).
3. **Explicit Consent Records**: Recipients explicitly register opt-in states (`SMS_OPT_IN`, `PUSH_OPT_IN`).
4. **Aggregate Zone Statistics**: APIs exposed to public or web views return only anonymized counts:
   - `total_eligible`: Total people within the active geofence.
   - `authorities_count`: Registered emergency managers and district magistrates.
   - `field_teams_count`: SDRF, NDRF, BRO, and civil defense quick-reaction units.
   - `sms_eligible_count` & `push_eligible_count`.

---

## 5. Deduplication Algorithm

To prevent alert fatigue and notification storms during continuous sensor telemetry loops:
1. A deterministic fingerprint is computed:
   $$\text{Fingerprint} = \text{SHA-256}\left(\text{sector\_id} \,\|\, \text{alert\_level} \,\|\, \lfloor \text{timestamp} / \text{window} \rfloor\right)[:16]$$
   where $\text{window}$ is configurable via `PAHAD_ALERT_DEDUP_MINUTES` (default: 30 minutes).
2. If an identical fingerprint is registered, the existing `OrchestratedAlert` object is updated in-place with latest sensor readings (`cri`, `event_probability`, `factor_of_safety`) without broadcasting a duplicate alert.
3. If risk level escalates (e.g., `MODERATE` $\to$ `EXTREME`), a new fingerprint is generated, immediately bypassing deduplication to guarantee life safety.
