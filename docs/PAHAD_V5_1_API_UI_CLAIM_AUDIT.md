# PARVAT NETRA / PAHAD AI — PHASE V5.1 API & UI CLAIM AUDIT

**Audit Date**: September 21, 2026  
**Phase**: V5.1 Cross-Phase Scientific Consistency Audit  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering  
**Scope**: REST Endpoints, Dashboard Cards, Template Badges, and Claim Freeze Governance  

---

## 1. Executive Summary

This audit establishes the four-tier **Claim Freeze System** across all public and internal interfaces of PARVAT NETRA:
1. `SUPPORTED`: Rigorously verified against disk artifacts and reproducibility scripts.
2. `PARTIALLY_SUPPORTED`: Architecturally demonstrated or in pre-contractual staging.
3. `UNSUPPORTED`: Uncorroborated, demoted, or untraced narrative claims.
4. `FORBIDDEN`: Strict negative boundaries that must never be presented as truth.

---

## 2. Four-Tier Claim Classification Ledger

### Tier 1: SUPPORTED CLAIMS
- Production V3 model is frozen and serving under SHA-256 `7cb823888646ca2b074389de3719c9d9385197bbdf6763cf9e4e69bc3c15c183`.
- Research V4.5 model demonstrates superior long-range infiltration skill (48h–168h).
- Exact documented historical landslide event count is strictly 17 (`EV-01` to `EV-17`).
- Exact documented historical negative control count is strictly 20 (`CTRL-01` to `CTRL-20`).
- Dataset contains exactly 105 continuous 168-hour empirical sequences (17,640 rows).
- Event classifier GBDT is calibrated on 36 real observation samples (16 train, 12 val, 8 test).
- Demo dataset of 25 synthetic sequences is strictly quarantined under `PAHAD_DEMO_MODE=1`.
- Bench HIL test framework successfully processes 8,640 frames with zero crashes.
- Store-and-forward deduplication achieves 0% observation loss and 0 duplicate creation.
- Platform operates as Smart India Hackathon (SIH) 2026 AI-assisted research prototype.
- Public siren and alert dispatch are locked to require manual human approval.
- V3 and V4.5 model weights are cryptographically verified bit-for-bit unchanged.
- CRI feature leakage is eliminated in V4.4/V4.5 feature specifications.
- Deterministic Mohr-Coulomb Factor of Safety (FoS) remains primary physical line of defense.

### Tier 2: PARTIALLY SUPPORTED CLAIMS
- BRO Project Swastik collaboration is planned for NH-10 KM48 instrumentation (pre-contractual planning, no signed legal contract).
- SSDMA emergency integration is architecturally ready via CAP schema (public dispatch disabled pending drill).
- OASIS CAP v1.2 schema compliance verified (operational dispatch authority missing).
- 17-Fold LOEO cross-validation executed (single-class test fold limitation disclosed).
- Multi-horizon historical median lead time is 14.5 hours (applies to regional synoptic events, not in-situ IoT).

### Tier 3: UNSUPPORTED CLAIMS
- Claim of 52 real historical events (UNSUPPORTED: strictly 17 documented events).
- Claim of 41 training, 11 validation, 11 test samples (UNSUPPORTED: untraced placeholder).
- Claim of ROC-AUC 0.81, PR-AUC 0.74, POD 0.78, FAR 0.22, CSI 0.64 (UNSUPPORTED: untraced placeholder).
- Claim of 4.2 hours median warning lead time (UNSUPPORTED: 4.2h was historical minimum / demo formula).
- Claim of NABL/ISO-17025 accredited calibration (UNSUPPORTED: `CALIBRATION_EVIDENCE_MISSING`).
- Claim of `BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026` operational clearance (UNSUPPORTED: `AUTHORIZATION_UNVERIFIED`).

### Tier 4: FORBIDDEN CLAIMS
- Claiming physical downhole or surface sensors are installed in the field before drilling occurs.
- Claiming live mountain field telemetry is streaming when only bench/HIL simulation is running.
- Claiming Kinematic In-Situ ML is trained or production-ready before real field data is collected.
- Claiming V4.5 research baseline is active in production without formal commissioning.
- Claiming official Government of India or National Disaster Management Authority operational status.

---

## 3. REST API Endpoint Governance

- `GET /api/scientific-truth/ledger`: Returns complete immutable truth ledger.
- `GET /api/scientific-truth/audit-summary`: Returns executive summary of model invariance, dataset counts, and conflict resolutions.
- `GET /api/pahad/event-model/status`: Returns transparent model status (`TRAINED_LIMITED_DATA`), dataset hash, and training rows (36).
- `GET /api/pahad/event-model/data-quality`: Returns real events count (17) and negative controls (20).
