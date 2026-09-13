# PARVAT NETRA / PAHAD AI — Phase 3.5 Completion Report

**Title:** Intelligent Alerting, 15 km Geofencing, Multi-Channel Push/SMS/CAP & Notification Center  
**Platform:** PARVAT NETRA — NER Sentinel  
**AI System:** PAHAD AI (Predictive AI for Hillslope Analysis & Disaster-response)  
**Problem Statement:** Smart India Hackathon (SIH 26001)  
**Date:** September 2026  
**Status:** **PHASE 3.5 COMPLETE & CERTIFIED**  

---

## 1. Executive Summary

Phase 3.5 establishes the complete operational notification and alerting pipeline for PARVAT NETRA. It successfully bridges the continuous predictive intelligence of PAHAD AI (physics-based Factor of Safety, calibrated GBDT event classification, IMD rainfall thresholds, and in-situ borehole telemetry) to a national-grade, multi-channel disaster warning orchestration architecture.

The entire implementation enforces strict physical safety invariants:
- **No autonomous public warnings**: Machine learning predictions must pass human-in-the-loop authority sign-off before public broadcast.
- **2-of-3 Independent Confirmation Rule**: Requires at least two independent physical, meteorological, or ML modalities before recommending critical alert tiers.
- **Privacy-Preserving Geofencing**: Default 15 km impact zones with zero exposure of personal PII.
- **DRY_RUN Safety Guarantee**: Operates in simulated safety mode by default to prevent unauthorized telecom charges or citizen panic during drills.

---

## 2. Key Subsystems Delivered

### 2.1 Multi-Signal Alert Policy Engine (`engine/pahad_alert_policy.py`)
- **Tiers Supported**: `LOW` (Monitoring), `MODERATE` (Watch), `HIGH` (Warning), `VERY_HIGH` (Severe Warning), `EXTREME` (Extreme Alert).
- **2-of-3 Concordance Gate**: If raw risk scores evaluate to `EXTREME` but fewer than two independent signals confirm, the alert is automatically downgraded to `VERY_HIGH` with an explicit explainability note.
- **Non-Causal "Why This Alert?" Explainability**: Synthesizes exact contributing signals (e.g. `Physical Mohr-Coulomb FoS Critical (0.72 <= 1.05)`, `Regional Rainfall Threshold Exceeded (I-D Curve Breach)`, `High ML Landslide Event Probability (85.0%)`).
- **Escalation Damping & Hysteresis**: Protects against rapid oscillation across alert tiers by enforcing multi-cycle dwell times on de-escalation.

### 2.2 Spatial Geofencing & Impact Zone Engine (`engine/pahad_geofence.py`)
- **Configurable Radius**: Defaults to 15.0 km via `PAHAD_ALERT_RADIUS_KM`.
- **Multi-Geometry Support**:
  1. **Point (Radial Circle)**: Great-circle Haversine evaluation around landslide rupture scarp.
  2. **Corridor (Buffered Line)**: Multi-waypoint buffer along Himalayan highway axes (e.g. NH-10 Singtam-Rangpo).
  3. **Polygon (Catchment Boundary)**: Shapely point-in-polygon containment with buffer zones for high-susceptibility basins.
- **Recipient Proximity Bands**: Classifies recipients into `IMPACT_DIRECT` ($\le 3$ km), `BUFFER_ZONE` ($\le 15$ km), and `OUTSIDE` ($> 15$ km).

### 2.3 Privacy-Preserving Notification Registry (`services/notification_registry.py`)
- **Cryptographic Phone Hashing**: Recipient phone numbers are hashed using SHA-256 (`phone_hash`) and presented only as masked references (`+91-XXXXX-3210`).
- **Consent Governance**: Tracks explicit `SMS_OPT_IN` and `PUSH_OPT_IN` preferences.
- **Zero-PII Zone Aggregates**: Exposes only aggregated counts (`total_eligible`, `authorities_count`, `field_teams_count`, `sms_eligible_count`, `push_eligible_count`) to public dashboards and REST APIs.

### 2.4 Multi-Channel Dissemination Pipeline
- **Web & Mobile Push (`services/push_service.py`)**: Standards-compliant W3C Push/VAPID payloads and FCM/APNs token abstractions with lifecycle tracking.
- **Emergency SMS Gateway (`services/sms_service.py`)**: Provider-abstracted gateway (C-DAC Mobile Seva and MockSMSProvider) with concise multilingual templates strictly enforced $\le 160$ characters in English, Hindi, Nepali, Bhutia, Lepcha, and Assamese.
- **OASIS CAP v1.2 Gateway (`engine/pahad_cap.py`)**: ITU-T X.1303 / NDMA SACHET compliant XML payloads with geospatial polygon descriptors.
- **Local Edge & Siren Gateway (`engine/pahad_alert_gateway.py`)**: Sub-GHz LoRa mesh emergency packets and dual EAS acoustic tones (853 Hz / 960 Hz).

### 2.5 Master Notification Orchestrator (`engine/pahad_notification_orchestrator.py`)
- **Deterministic Deduplication**: Computes SHA-256 fingerprints across 30-minute windows to eliminate alert storms, while allowing instant escalation if severity increases.
- **Strict Lifecycle State Machine**: Enforces `CREATED` $\to$ `READY_FOR_AUTHORIZATION` $\to$ `AUTHORIZED` $\to$ `DISPATCHING` $\to$ `DISPATCHED` $\to$ `ACKNOWLEDGED` $\to$ `RESOLVED`.
- **Tamper-Evident Audit Logging**: Logs every transition with actor, timestamp, channel, and result.
- **Deterministic SIH Demo Scenario & Isolated Reset**: Powers interactive evaluator demonstrations without mutating operational production data.

### 2.6 Mission-Control Notification Center UI (`templates/notifications.html`)
- High-contrast obsidian slate theme (`#070B10` to `#0B132B`) with Inter & JetBrains Mono typography.
- Filterable alert queue (`ALL`, `ACTIVE`, `AUTHORIZED`, `DISPATCHED`, `ACKNOWLEDGED`).
- Live assessment pane with 15 km impact zone telemetry, why-this-alert explainability card, zero-PII recipient counts, and authority action buttons (`Authorize Public Dispatch`, `Dispatch Multi-Channel Broadcast`, `Acknowledge Alert`, `Mark Resolved`).
- Live audit log stream and channel delivery status ribbon.

### 2.7 REST APIs & Dashboard Integration (`backend/notifications_routes.py` & `templates/index.html`)
- 13 comprehensive REST endpoints (`/api/notifications`, `/api/notifications/status`, `/api/notifications/active`, `/api/notifications/<id>/authorize`, `/api/notifications/<id>/dispatch`, `/api/push/subscribe`, `/api/alert-policy/<sector_id>`, etc.).
- Compact `PAHAD AI ALERT ORCHESTRATOR` status card on homepage below the Edge Network module.
- `Notifications` link in the main navigation bar and `Alert Center (15km)` chip in the SIH evidence bar.

---

## 3. Test Suite Verification & Quality Assurance

A dedicated suite of 9 new test modules comprising 46 test cases was implemented and executed:

| Test Module | Coverage Area | Tests | Status | Execution Time |
| :--- | :--- | :---: | :---: | :---: |
| `tests/test_alert_policy.py` | Multi-signal evaluation, 2-of-3 rule, hysteresis, explainability | 7 | **PASS** | 0.000s |
| `tests/test_geofence.py` | Haversine distance, 15km radial, corridor, polygon, eligibility | 8 | **PASS** | 0.003s |
| `tests/test_notification_orchestrator.py` | End-to-end ingest, deduplication, authorization, dispatch, SIH demo | 4 | **PASS** | 0.003s |
| `tests/test_push_service.py` | Subscription lifecycle, VAPID payload, dry-run safety | 4 | **PASS** | 0.000s |
| `tests/test_sms_service.py` | Multilingual templates (< 160 chars), CDAC/mock providers | 5 | **PASS** | 0.000s |
| `tests/test_alert_deduplication.py` | Fingerprinting, window updating, escalation bypass | 3 | **PASS** | 0.002s |
| `tests/test_alert_authorization.py` | Authority sign-off gate, unauthorized dispatch rejection | 3 | **PASS** | 0.002s |
| `tests/test_alert_lifecycle.py` | Full state machine transitions, state query filters, closure rules | 3 | **PASS** | 0.003s |
| `tests/test_notification_api.py` | Full REST API contracts, UI rendering, push subscribe, demo reset | 9 | **PASS** | 0.037s |
| **Total Phase 3.5 Test Suite** | **Comprehensive Alert Orchestration Layer** | **46** | **100% PASS** | **0.050s** |

---

## 4. Operational Invariants Verified

- [x] **Prediction is distinct from alert recommendation, authorization, and dispatch**.
- [x] **2-of-3 signal rule enforced** before critical public alerts can be recommended.
- [x] **15 km geofence radius configurable** via `PAHAD_ALERT_RADIUS_KM`.
- [x] **Zero personal PII exposed**; all phone numbers hashed with SHA-256 and masked.
- [x] **Multilingual SMS templates strictly under 160 characters** across 6 regional languages.
- [x] **OASIS CAP v1.2 XML compliant** with NDMA SACHET standards.
- [x] **Deterministic deduplication window** prevents notification storms while allowing immediate escalation.
- [x] **DRY_RUN safety guaranteed**; no external network charges incurred in development or testing.
- [x] **Homepage and mission-control navigation unified**.
- [x] **Zero regressions across existing codebase**.
