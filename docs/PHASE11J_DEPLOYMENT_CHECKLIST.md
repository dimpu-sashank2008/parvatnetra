# PARVAT NETRA / PAHAD AI — PHASE 11J
# PRE-DEPLOYMENT, DEPLOYMENT & POST-DEPLOYMENT VERIFICATION CHECKLIST
**Document ID**: `PN-PHASE11J-CHECKLIST-001`  
**Classification**: National Early Warning System Deployment Protocol (SIH 2026)  
**Status**: ACTIVE VERIFIED  

---

## 1. Stage 1: Pre-Deployment Hardening Verification (Local / CI)

| Step | Check Item | Command / Procedure | Expected Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1.1 | Git Tree Hygiene | `git status --porcelain` | No untracked secrets, no unwanted debris | [x] PASS |
| 1.2 | Secret & Credential Audit | `python scripts/security_audit.py` | 0 secrets found across all tracked files | [x] PASS |
| 1.3 | Model Artifact Parity | `python scripts/verify_phase11j_model_parity.py` | 10/10 models match 64-char SHA-256 | [x] PASS |
| 1.4 | Data Artifact Integrity | Check `reports/PHASE11J_DATA_ARTIFACT_PARITY.json` | 6/6 datasets verified with SHA-256 | [x] PASS |
| 1.5 | Static Assets Existence | `python scripts/audit_phase11j_assets_and_hosts.py` | 0 missing static assets in templates | [x] PASS |
| 1.6 | Localhost References | `python scripts/audit_phase11j_assets_and_hosts.py` | 0 hardcoded localhost URLs in templates/static | [x] PASS |
| 1.7 | Smoke Test Suite | `python -m pytest tests/test_phase11j_smoke.py -v` | 10/10 endpoints return HTTP 200/expected schema | [x] PASS |
| 1.8 | Performance Latency | `python scripts/phase11j_perf_smoke.py` | Core API latencies < 100ms | [x] PASS |
| 1.9 | Safety Interlock Verification | Confirm `SIREN_DRY_RUN=1`, `ENABLE_PUBLIC_DISPATCH=0` | Fail-closed defaults verified in configuration | [x] PASS |

---

## 2. Stage 2: Deployment Configuration Verification

| Step | Configuration Target | Requirement | Verification Method | Status |
| :---: | :--- | :--- | :--- | :---: |
| 2.1 | Vercel Serverless | `vercel.json` routes all paths `/(.*)` to `app.py` with `maxDuration: 30` | Inspect `vercel.json` | [x] PASS |
| 2.2 | Render Container | `render.yaml` specifies `dockerfilePath: Dockerfile` with health check `/health` | Inspect `render.yaml` | [x] PASS |
| 2.3 | Multi-Stage Dockerfile | Multi-stage builder/runner with GIS C-libraries and `/health` curl check | Inspect `Dockerfile` | [x] PASS |
| 2.4 | Environment Variables | Strict isolation of Tier A-G variables; secrets injected via cloud dashboard only | Inspect `.env.example` | [x] PASS |
| 2.5 | Fail-Safe Resilience | Autonomous degradation to standalone mode when PostgreSQL is absent | Verified via test suite | [x] PASS |

---

## 3. Stage 3: Post-Deployment Smoke Verification (Remote URL)

*(To be executed immediately after operator initiates manual cloud deployment)*

```bash
# Set base target URL (e.g. https://parvatnetra.vercel.app or https://parvatnetra-app.onrender.com)
export TARGET_URL="https://<YOUR_DEPLOYMENT_URL>"

# 1. Healthcheck & Version Integrity
curl -s -f "$TARGET_URL/health" | grep '"status": "UP"'

# 2. Public Evaluation Demo Portal
curl -s -f "$TARGET_URL/demo" | grep -i "PARVAT NETRA"

# 3. Authoritative Highest-Risk Corridor Identification
curl -s -f "$TARGET_URL/api/pahad/highest-risk-corridor" | grep '"status": "SUCCESS"'

# 4. Data Provenance & Model Status Transparency
curl -s -f "$TARGET_URL/api/pahad/data-status" | grep '"data_streams"'

# 5. Live Geotechnical + ML Inference Pipeline
curl -s -X POST "$TARGET_URL/api/pahad/live-inference" \
  -H "Content-Type: application/json" \
  -d '{"sector_id":"SK-NH10-KM48","latitude":27.33,"longitude":88.61,"horizon_hours":24}' \
  | grep '"status": "SUCCESS"'

# 6. Safety Gate & Siren Interlock Verification (MUST be LOCKED / DRY RUN)
curl -s -f "$TARGET_URL/api/authority/siren-access" | grep '"physical_siren_interlock": "LOCKED"'

# 7. EOC Incident Management Queue
curl -s -f "$TARGET_URL/api/eoc/incidents" | grep '"status": "SUCCESS"'
```

---

## 4. Go / No-Go Criteria for SIH 2026 Evaluation

- [x] **GO**: `/health` returns HTTP 200 with `status: "UP"`.
- [x] **GO**: Models load cleanly with status `TRAINED_LIMITED_DATA` and 100% hash parity.
- [x] **GO**: Siren interlock is verified `LOCKED` with `human_authorization_required: True`.
- [x] **GO**: Live inference returns separate $FoS$, Event Probability, and $CRI$ with explicit provenance badges (`[LIVE]`, `[CACHED]`, `[SIMULATED]`).
- [x] **GO**: Deterministic tie-breaking on highest-risk corridor ranking functions consistently.
- [ ] **NO-GO**: Any crash or unhandled 500 error on `/health` or `/demo`.
- [ ] **NO-GO**: Public sirens or CAP alerts dispatching without 2-of-3 human authorization.
- [ ] **NO-GO**: Model artifacts modified without traceability or data provenance.
