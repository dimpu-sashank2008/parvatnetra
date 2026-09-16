# PARVAT NETRA • PHASE 12 REPORT
# ROLE-BASED EXPERIENCE SEPARATION & DMA 2005 RBAC INTEGRITY

**Standard:** Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform  
**Authority:** National Disaster Management Authority (NDMA) & Disaster Management Act (DMA 2005)  
**Status:** **OPERATIONAL & VERIFIED**  
**Date:** September 2026  

---

## 1. Executive Summary

Phase 12 enforces strict, statutory **Role-Based Experience Separation** across PARVAT NETRA without rewriting existing authentication, routing, or EOC architectures. 

Under the Disaster Management Act, 2005 (DMA 2005), emergency powers—specifically authorizing mandatory evacuations, issuing civil defense sirens, and publishing public Common Alerting Protocol (CAP) alerts—are strictly statutory and vested solely in designated authorities (District Magistrate / DDMA / SDMA). Public visitors, citizens, field operators (BRO / SDRF), and system administrators MUST NOT possess unilateral emergency authorization privileges.

This release achieves complete separation across six canonical personas while strictly preserving all existing login behavior, map/GIS functionality, mobile API contracts, and safety doctrine gates.

---

## 2. Institutional Persona Matrix & Privilege Boundaries

| Persona | Canonical Role | UI Viewport | Permitted Actions | Strictly Forbidden Actions |
| :--- | :--- | :--- | :--- | :--- |
| **Public Visitor** | `PUBLIC` | Citizen Advisory Mode | View hazard maps, view evacuation corridors, consult multilingual AI assistant, view safe shelters | Authorize decisions, broadcast alerts, dispatch sirens, verify reports |
| **Citizen Resident** | `CITIZEN` | Citizen Advisory Mode | Submit geo-tagged photo hazard reports, track report status, calculate bypass routes | Authorize decisions, broadcast alerts, arm tactical sirens, verify reports |
| **Field Operator** | `FIELD_OPERATOR` | Field Ops / Corridor Matrix | Verify field incident reports (`CONFIRMED`, `REJECTED`), inspect corridor telemetry, update site observations | Authorize decisions, trigger public broadcasts, dispatch tactical sirens |
| **District Authority** | `DISTRICT_AUTHORITY` | Full EOC Command | Authorize risk decisions, dispatch tactical siren protocols, issue localized CAP broadcasts, triage incident queue | Bypass 2-of-3 corroboration rules, override physical siren dry-run lock |
| **State Authority** | `STATE_AUTHORITY` | Full EOC Command | Authorize inter-district risk decisions, trigger state-wide CAP broadcasts, coordinate SDRF/NDRF staging | Direct hardware actuation without physical key confirmation |
| **System Admin** | `ADMIN` | Dev / Maintenance Console | Inspect system telemetry, audit SSE message bus, monitor database connection pools and sync logs | Authorize emergency alerts, trigger public broadcasts, dispatch sirens |

---

## 3. Statutory DMA 2005 & Safety Gate Invariants

1. **Elevation Bypass Prevention**:
   - Query parameter `?mode=authority` cannot elevate an unauthenticated visitor.
   - `app.py` resolves roles strictly from verified session state (`session.get('role')`). Unauthenticated requests default to `CITIZEN` advisory mode.
2. **UI Safety Shielding**:
   - The `#btn-citizen-sos` ("ARM TACTICAL SIREN") button is hidden from public and citizen sessions (`style="display:none !important;" class="hidden"`).
   - Institutional authority toolbar options (Civil Defense Siren, CAP Broadcast) require `is_authority` session state.
3. **Admin Privilege Isolation**:
   - System administrators (`ADMIN`) have console maintenance access only. Under DMA 2005, IT personnel cannot legally authorize civilian hazard warnings.
4. **Physical Siren Lock-Out**:
   - Physical siren actuation remains hard-locked in dry-run mode (`SIREN_DRY_RUN=1`). Zero software roles can directly actuate physical audible horns.

---

## 4. Protected Backend Endpoints & Route Guards

| Endpoint | Method | Permitted Personas | HTTP Status for Forbidden Roles |
| :--- | :--- | :--- | :--- |
| `/api/decisions/<id>/authorize` | `POST` | `DISTRICT_AUTHORITY`, `STATE_AUTHORITY`, valid `X-Authority-Token` | `HTTP 403 FORBIDDEN` |
| `/api/alerts/broadcast-trigger` | `POST` | `DISTRICT_AUTHORITY`, `STATE_AUTHORITY`, valid `X-Authority-Token` | `HTTP 403 FORBIDDEN` |
| `/api/alerts/dispatch-siren` | `POST` | `DISTRICT_AUTHORITY`, `STATE_AUTHORITY`, valid `X-Authority-Token` | `HTTP 403 FORBIDDEN` |
| `/api/reports/verify` | `POST` | `FIELD_OPERATOR`, `DISTRICT_AUTHORITY`, `STATE_AUTHORITY`, valid token | `HTTP 403 FORBIDDEN` (blocked for Citizen/Public) |
| `/` (Dashboard Viewport) | `GET` | All (Adapts view: Citizen Advisory vs EOC Node) | `HTTP 200 OK` (unauthenticated defaults to Citizen) |

---

## 5. Verification & Test Evidence

### Dedicated Test Suite: `tests/test_role_experience_separation.py`
- **20 / 20 Tests Passed (100%)**
  - `test_unauthenticated_visitor_defaults_to_citizen` — **PASS**
  - `test_unauthenticated_cannot_elevate_via_query_param` — **PASS**
  - `test_citizen_siren_dispatch_forbidden` — **PASS**
  - `test_citizen_decision_authorization_forbidden` — **PASS**
  - `test_citizen_broadcast_trigger_forbidden` — **PASS**
  - `test_citizen_report_verification_forbidden` — **PASS**
  - `test_citizen_ui_hides_siren_button` — **PASS**
  - `test_field_operator_can_verify_reports` — **PASS**
  - `test_field_operator_cannot_authorize_decisions` — **PASS**
  - `test_field_operator_cannot_trigger_broadcast` — **PASS**
  - `test_field_operator_cannot_dispatch_siren` — **PASS**
  - `test_district_authority_can_authorize_decision` — **PASS**
  - `test_state_authority_can_trigger_broadcast` — **PASS**
  - `test_authority_can_dispatch_siren` — **PASS**
  - `test_authority_ui_shows_node_badge` — **PASS**
  - `test_admin_cannot_authorize_decisions` — **PASS**
  - `test_admin_cannot_trigger_broadcast` — **PASS**
  - `test_admin_cannot_dispatch_siren` — **PASS**
  - `test_authority_token_header_authorizes_siren` — **PASS**
  - `test_invalid_authority_token_header_rejected` — **PASS**

### Combined RBAC & Security Test Suite (49 / 49 Passed):
- `tests/test_role_experience_separation.py` (20 tests) — **PASS**
- `tests/test_phase7g_rbac.py` (7 tests) — **PASS**
- `tests/test_phase10e_authority.py` (7 tests) — **PASS**
- `tests/test_phase10i_authorization.py` (4 tests) — **PASS**
- `tests/test_safety_subsystems.py` (5 tests) — **PASS**
- `tests/test_ui_redesign.py` (6 tests) — **PASS**

### Core Regression Test Suite (80 / 80 Passed):
- `tests/test_pahad_engine.py` (11 tests) — **PASS**
- `tests/test_pahad_phase2.py` (12 tests) — **PASS**
- `tests/test_pahad_phase3.py` (10 tests) — **PASS**
- `tests/test_pahad_data_fusion.py` (7 tests) — **PASS**
- `tests/test_weather_service.py` (8 tests) — **PASS**
- `tests/test_seismic_service.py` (6 tests) — **PASS**
- `tests/test_terrain_api.py` (12 tests) — **PASS**
- `tests/test_i18n_localization.py` (10 tests) — **PASS**
- `tests/test_model_regression.py` (4 tests) — **PASS**

---

## 6. Files Modified & Added

1. `app.py`:
   - Enforced session-based role resolution in `dashboard()` (`/`), blocking unauthenticated elevation via `?mode=authority`.
   - Updated `login()`, `login_authority()`, and `login_citizen()` to route personas correctly.
   - Enforced RBAC guardrails with resilient database offline fallback on `/api/decisions/<id>/authorize`, `/api/alerts/broadcast-trigger`, `/api/alerts/dispatch-siren`, and `/api/reports/verify`.
2. `templates/login_authority.html`:
   - Added designation selector dropdown for `DISTRICT_AUTHORITY`, `STATE_AUTHORITY`, `FIELD_OPERATOR`, and `ADMIN`.
3. `templates/index.html`:
   - Conditionally hidden `#btn-citizen-sos` for citizen sessions while preserving DOM testing hooks.
   - Enforced role guard in `switchPortalMode()` preventing unauthenticated visitors from opening authority view.
4. `tests/test_role_experience_separation.py`:
   - Created comprehensive 20-test test suite covering all 6 personas and API guardrails.
5. `docs/PHASE12_ROLE_BASED_EXPERIENCE_REPORT.md`:
   - Authoritative technical report and audit summary.
