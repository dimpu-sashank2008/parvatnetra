# PARVAT NETRA • PAHAD AI — PHASE 7H: MOBILE HARDENING REPORT
**Flutter Field Responder Client & Offline Synchronization Contract**

---

## 1. Executive Summary
Sub-phase 7H hardens the offline mobile field application contract used by Border Roads Organisation (BRO), State Disaster Response Force (SDRF), and community volunteers in remote Himalayan gorges with intermittent connectivity.

The field client operates on an **Offline-First SQLite Architecture**, allowing responders to log tension crack apertures, rockfall debris, and mudflows without cellular coverage, queuing records for automatic synchronization upon regaining network connectivity.

---

## 2. Synchronization API Contract

### 2.1 Push Endpoint (`POST /api/sync/push`)
- **Payload**: Batch of mobile SQLite `field_reports` records including `local_id`, `lat`, `lon`, `hazard_type`, `severity`, `description`, `photo_paths`, `reporter_role`, and `sync_status`.
- **Response**: Batch of acknowledgements mapping `local_id` $\to$ `server_id`, `sync_status = SYNCED`, and authoritative tracking ref (e.g. `PN-REPORT-2026-XXXX`).
- **Idempotency**: Retried submissions of identical `local_id` return the existing server acknowledgement without creating duplicate reports.

### 2.2 Pull Endpoint (`GET /api/sync/pull`)
- **Query Parameter**: `sector_id`
- **Response**:
  - `active_alerts`: Active statutory emergency warnings.
  - `critical_snapshots`: Sector geotechnical and hydrologic telemetry.
  - `pulled_at`: UTC synchronization timestamp.
  - `bundle_version`: Semantic schema version.

---

## 3. Multilingual Localization Coverage (6 Himalayan Languages)
The frontend and mobile dictionary (`static/js/i18n.js`) provides 100% key parity across:
1. **English (`en`)**: Operational standard for national agencies.
2. **Hindi (`hi`)**: National language and inter-agency coordination.
3. **Nepali (`ne`)**: Widely spoken across Sikkim, North Bengal, and Eastern Nepal.
4. **Bhutia (`bh`)**: Indigenous language of Northern and Western Sikkim.
5. **Lepcha (`lp`)**: Indigenous language of Dzongu and central Sikkim valleys.
6. **Assamese (`as`)**: Regional standard for Brahmaputra valley and Assam corridor.

---

## 4. Current Status
- **Sub-phase 7H Status**: **COMPLETE**
- **Artifacts**: `services/sync_service.py`, `static/js/i18n.js`, `tests/test_phase7_mobile_contract.py` (4/4 passed)
