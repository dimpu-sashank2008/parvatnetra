# PARVAT NETRA • PAHAD AI — Phase 12F Final Forensic Signoff

**Signoff Timestamp**: September 16, 2026  
**Auditing Authority**: Autonomous Pre-Freeze Forensic Gatekeeper  
**Baseline Git Commit**: `fd1512af4f595e448b43bde0f8420e13514423bf`  
**Evaluation Scope**: Pre-Freeze Forensic Consistency Audit  

---

## 1. Forensic Verification Matrix

### 1.1 Git Status & Commit Truth
- **Branch**: `main`
- **Authoritative Commit SHA**: `fd1512af4f595e448b43bde0f8420e13514423bf`
- **Working Tree**: Completely clean (`git status --short` returns zero uncommitted changes).
- **Whitespace / Diff Check**: Clean (`git diff --check` returns 0).

---

### 1.2 Model & Dataset Hashes
The authoritative SHA-256 cryptographic digests computed directly from disk:
- `models/pahad_event_model.pkl`:  
  `46c1f2f8106074d1c8c9ef19880533fd0faa3ece3f2296fe47785a8ee7ffff35`
- `models/fos_predictor.pkl`:  
  `21206e6f98ed77c16a3375a0e3de582bf05ad0dadfc12dd1c95f911d45ad816c`
- `data/features/real_train.csv`:  
  `79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`
- `data/features/real_val.csv`:  
  `ed732e2054f1b028cab9380a35ad31affbbb5e93a3cb207fda1582665aa0bd81`
- `data/features/real_test.csv`:  
  `29f84cf974241844a16086736e1cab833484a9587519946dd24ee09ae09d28da`

#### Forensic Hash Audit Finding:
- The training dataset hash in `models/pahad_event_model.metadata.json` (`79ece554fd0d2fc62d69a21fd4d39172f7dd4995d5645e126a91d1a08c1c579e`) **EXACTLY MATCHES** `data/features/real_train.csv`.
- **Inconsistency**: In `data/manifests/phase12f_release_manifest.json`, `model_hash` was recorded as `65f0d6d78b59f79e1f6b50ce271db95398ad3dcd75303b38fdcfec41405192f8`. The authoritative disk hash is `46c1f2f8106074d1c8c9ef19880533fd0faa3ece3f2296fe47785a8ee7ffff35`. Result: **MISMATCH** between manifest and disk.

---

### 1.3 Statutory Safety Interlocks
Verified in runtime environment and Flask application:
- `ENABLE_PUBLIC_DISPATCH`: `0` (PASS)
- `SIREN_DRY_RUN`: `1` (PASS)
- `CAP_PRODUCTION_DISPATCH`: `0` (PASS)
- `SACHET_PRODUCTION_DISPATCH`: `0` (PASS)
- `CELL_BROADCAST_PRODUCTION`: `0` (PASS)
- `PUBLIC_DEMO_TEST_ONLY`: `1` (PASS)
- **Result**: **PASS** (100% compliance with DMA 2005 Sections 30 & 34).

---

### 1.4 Provider Audit Summary
Forensic inspection of live code and API responses (`docs/PHASE12F_PROVIDER_FORENSIC_AUDIT.md`):
- **Open-Meteo**: `LIVE` (HTTP 200 OK)
- **USGS**: `LIVE` (HTTP 200 OK, M4.2 regional event received)
- **PostGIS**: `LIVE` (Connected to Supabase PostgreSQL 15)
- **SQLite**: `LIVE` (117,218 stored observations)
- **NCS**: `AUTH_REQUIRED` (Unconfigured `NCS_API_BASE_URL`; fallback to USGS is active)
- **IMD**: `AUTH_REQUIRED` (Unconfigured credentials; fallback to Open-Meteo is active)
- **Copernicus**: `HISTORICAL / PROCESSED` (InSAR features derived from archive; raw tile downloads are `AUTH_REQUIRED`)
- **NRSC / Bhoonidhi**: `HISTORICAL / CATALOG` (CartoDEM v3.1 baseline)
- **In-Situ IoT**: `SIMULATED` (Physical hardware deployment is NOT VERIFIED)

#### Forensic Provider Audit Finding:
- `data/manifests/phase12f_release_manifest.json` labeled NCS as `LIVE`, whereas code and runtime truth prove it is `AUTH_REQUIRED` falling back to USGS.
- **Result**: **PARTIAL** (Inconsistency between manifest label and actual runtime auth state).

---

### 1.5 Scientific Claim Audit
Audited all docs, UI templates, and manifests for prohibited and exaggerated claims:
- "100% accuracy": **ZERO occurrences** (all 6 mentions are explicit repudiations/disclaimers).
- "production-grade AI": **ZERO occurrences**.
- "trained LSTM": **ZERO occurrences** (all 4 mentions explicitly describe the LSTM as an un-trained surrogate).
- "live NCS": **ZERO occurrences**.
- "live IMD": Accurately bounded as what-if historical threshold analysis tool in UI and explicitly labeled as fallback in data architecture.
- "physical sensors deployed": Audited as FALSE; verified explicitly labeled as `SIMULATED`.
- "government deployment": Refers only to future roadmap.
- "official Government of India service": **ZERO occurrences**.
- "autonomous alerting": Explicitly repudiated as human-in-the-loop decision support under DMA 2005.
- "independent signals": Refers to multi-signal heuristic corroboration ($A, B, C$), explicitly avoiding false claims of statistical independence.
- **Result**: **PASS** (Zero unsubstantiated scientific claims).

---

### 1.6 Blocker Forensics (Target vs. Requirement)
1. **"300+ Northeast highway corridors"**:
   - **Classification**: **FUTURE DEPLOYMENT TARGET** (pan-NER strategic road network envisioned for multi-year national rollout; NOT a current runtime requirement).
2. **"12+ months continuous IoT sequence collection"**:
   - **Classification**: **PREREQUISITE FOR RECURRENT LSTM TRAINING** (required scientific gate before training an LSTM on temporal sequences; NOT a current runtime requirement for the GBDT tabular classifier or physics FoS engine).

---

### 1.7 Role & GIS Final Check
- **Role Isolation**:
  - `PUBLIC`: Safe read-only advisory, siren actuation suppressed (HTTP 403).
  - `FIELD`: Ground-truth incident observation.
  - `AUTHORITY`: Full EOC incident command, human-in-the-loop authorization.
  - `ADMIN`: System diagnostics and audit logs.
- **GIS Behavior**:
  - NER 8 states bounding box default view verified.
  - Zero auto-zoom to Bhalukpong or highest-risk corridor.
  - Viewport preservation on polling cycles verified (`center` and `zoom` remain fixed).
  - Risk Evolution compact on-map playback verified.
  - Risk Evaluation separate analytical drawer verified.
- **Result**: **PASS** (44/44 role and GIS tests passed).

---

### 1.8 Scoped Test Suite Results
Executed the authoritative 23-file Phase 12F scoped test suite:
- **Total Tests Executed**: **220**
- **Passed**: **220**
- **Failed**: **0**
- **Skipped**: **0**
- **Errors**: **0**
- **Execution Time**: 165.08s

---

## 2. Freeze Decision

Under Rule 11 of the Forensic Audit Protocol:
> *"Do not optimize for FREEZE_READY. If provider inconsistency or unsupported claim is found: FREEZE_BLOCKED."*

Because the existing manifest `data/manifests/phase12f_release_manifest.json` contains:
1. Provider inconsistency: `ncs_india` labeled as `LIVE` when runtime inspection proves it is `AUTH_REQUIRED` with USGS fallback.
2. Hash inconsistency: `model_hash` in manifest (`65f0d6d7...`) does not match actual on-disk pickle hash (`46c1f2f8...`).

The pre-freeze forensic decision is strictly:
**`FREEZE_BLOCKED`**

To unblock the release freeze:
1. Update `data/manifests/phase12f_release_manifest.json` to accurately record NCS as `AUTH_REQUIRED` (USGS Fallback) and record the authoritative model hash (`46c1f2f8...`).
2. Re-commit and re-tag the release baseline.
