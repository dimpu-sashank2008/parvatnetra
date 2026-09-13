# PARVAT NETRA / PAHAD AI — PHASE 6D
## Comprehensive Field Verification & Operational Test Plan

**Document Reference**: `docs/PHASE6D_FIELD_TEST_PLAN.md`  
**Classification**: Test Engineering Master Plan  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Date**: September 2026  

---

## 1. Overview & Verification Objectives

This test plan governs operational validation of in-situ geotechnical telemetry, edge concentration, radio propagation, power autonomy, and safety gates across monitored Himalayan corridors prior to operational commissioning.

---

## 2. Test Battery Structure

### Test Block 1: Corridor & Topology Verification
- Verify `CorridorRegistry` status transitions and lifecycle constraints.
- Confirm 5 strategic Himalayan corridors seeded and addressable.
- Validate GeoJSON coordinates and BRO bypass routes.

### Test Block 2: Physical Inventory & Asset Tracking
- Ensure serial numbers, manufacturers, and calibration records are persisted.
- Verify status machine: `PLANNED` $\to$ `DELIVERED` $\to$ `INSTALLED` $\to$ `CALIBRATED` $\to$ `CONNECTED` $\to$ `ACTIVE`.
- Confirm status defaults to `PHYSICAL_DEPLOYMENT_PENDING` when no physical hardware is deployed.

### Test Block 3: Field Commissioning & Mobile Sync
- Execute 7-step technician sequence: `REGISTER`, `LOCATE`, `INSTALL`, `CALIBRATE`, `CONNECT`, `TEST`, `ACCEPT`.
- Enforce sub-25m GPS accuracy and photo SHA-256 evidence.
- Verify batch synchronization via `/api/field/evidence/sync` with idempotency guarantees.

### Test Block 4: LoRa RF Propagation & Link Margins
- Execute `scripts/test_radio_link.py` evaluating RSSI, SNR, PDR, and latency.
- Enforce `PASS`, `DEGRADED`, and `FAIL` boundary conditions.
- Log results to persistent SQLite database.

### Test Block 5: Power Autonomy & LiFePO4 Chemistry
- Verify State of Charge (SoC) estimation across voltage plateau (10.5V to 13.6V).
- Validate 5.0-day minimum continuous autonomous reserve without solar input.
- Enforce provenance labeling: `THEORETICAL` vs `BENCH` vs `FIELD-MEASURED`.

### Test Block 6: Safety Siren & Field Shadow Mode
- Verify `scripts/test_siren.py` defaults to `DRY_RUN` with relay de-energized.
- Enforce HMAC authorization rejection for unauthenticated physical tests.
- Confirm `FIELD_SHADOW_ACTIVE` mode evaluates live FoS and CRI while suppressing public alarms (`SUPPRESSED_FIELD_SHADOW_TRIAL`).
