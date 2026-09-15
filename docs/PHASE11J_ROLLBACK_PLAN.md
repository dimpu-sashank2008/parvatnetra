# PARVAT NETRA / PAHAD AI — PHASE 11J
# COMPREHENSIVE ROLLBACK & DISASTER RECOVERY PLAN
**Document ID**: `PN-PHASE11J-ROLLBACK-001`  
**Classification**: National Early Warning System Operational Procedure (SIH 2026)  
**Target Release**: Phase 11J Deployment Baseline (`4c439af` + 11I/11J Hardening)  

---

## 1. Executive Summary & Rollback Philosophy
PARVAT NETRA operates on a **fail-closed, safety-first** architecture. If an anomaly, regression, security breach, or infrastructure degradation occurs during or post-deployment:
1. **Zero Siren / Public Dispatch Risk**: Rollback will never cause spurious acoustic or CAP alert transmissions because all sirens and public dispatch systems default to fail-closed (`ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`).
2. **Deterministic Fallback**: If external connectors (IMD, USGS, PostGIS) fail during rollback, the platform autonomously degrades to the local canonical spatial catalog and in-memory observation cache.
3. **Data Preservation**: Historical observations stored in SQLite (`pahad_observations.db`) or PostgreSQL remain intact; rollback never deletes telemetry.

---

## 2. Platform-Specific Rollback Procedures

### 2.1 Vercel Serverless Deployment
- **Mechanism**: Instant Deployment Promotion / Rollback.
- **Console Workflow**:
  1. Log into Vercel Dashboard -> Project `parvatnetra`.
  2. Navigate to **Deployments**.
  3. Locate the previous known-good deployment (e.g., Phase 11H/11I verified deployment).
  4. Click the three dots (`...`) -> **Instant Rollback** (or **Promote to Production**).
  5. Rollback completes in < 5 seconds; traffic switches instantly at edge CDN nodes.
- **CLI Workflow**:
  ```bash
  vercel rollback [DEPLOYMENT_ID]
  ```
- **Post-Rollback Verification**:
  ```bash
  curl -s -f https://<your-vercel-domain>/health | grep '"status": "UP"'
  ```

### 2.2 Render Container / Web Service Deployment
- **Mechanism**: Render Instant Rollback / Deploy Previous Commit.
- **Console Workflow**:
  1. Open Render Dashboard -> Web Service `parvatnetra-app`.
  2. Select **Events** or **Deploys** tab.
  3. Identify the prior successful deploy.
  4. Click **Rollback to this deploy**.
  5. The previous Docker container image is redeployed with zero rebuild time.
- **Post-Rollback Verification**:
  ```bash
  curl -s -f https://<your-render-domain>/health
  ```

---

## 3. Git Version Control Rollback

### 3.1 Non-Destructive Git Revert (Recommended)
To roll back code changes while preserving immutable audit logs:
```bash
# Identify the commit to revert
git log --oneline -n 5

# Revert the latest commit cleanly
git revert HEAD --no-edit

# Verify regression test suite passes
python -m pytest tests/test_phase11j_smoke.py -v
```

### 3.2 Emergency Checkout to Pinned Baseline Commit
To return the workspace immediately to the pre-phase commit (`4c439af`):
```bash
git checkout 4c439af
```

---

## 4. Database & State Recovery

### 4.1 PostgreSQL / PostGIS Resilience
- PARVAT NETRA does not execute destructive schema migrations on boot.
- If PostgreSQL becomes unreachable or corrupted:
  - Application logs: `Health check error: ... db_status = STANDALONE_FALLBACK`.
  - The application automatically switches to in-memory spatial corridors and local static geo-registries (`engine/canonical_registry.py`).
  - No system crash occurs; `/health` reports HTTP 200 with `database_status: "STANDALONE_FALLBACK"`.

### 4.2 SQLite Observation Store (`pahad_observations.db`)
- In serverless runtimes (Vercel), SQLite is mounted on ephemeral storage (`/tmp/observations/`). Fresh instances start cleanly with table auto-initialization.
- In persistent container environments (Render / Docker):
  ```bash
  # Backup observation store before deployment
  cp data/observations/pahad_observations.db data/observations/pahad_observations.db.bak

  # Restore if needed
  cp data/observations/pahad_observations.db.bak data/observations/pahad_observations.db
  ```

---

## 5. Rollback Trigger Matrix (Go / No-Go Decision)

| Symptom / Anomaly | Severity | Trigger Rollback? | Recovery Action |
| :--- | :--- | :--- | :--- |
| `/health` returns HTTP 5xx or fails to respond | CRITICAL | **YES** | Immediate instant rollback to previous deployment. |
| Model hash mismatch on startup | CRITICAL | **YES** | Restore model artifacts from `models/` baseline. |
| `ENABLE_PUBLIC_DISPATCH=1` in production without 2-of-3 auth | CRITICAL | **YES** | Revert environment variable to `0` and redeploy. |
| PostGIS connection failure | MEDIUM | **NO** | Automatic fallback to `STANDALONE_FALLBACK`; investigate DB credentials. |
| Open-Meteo external timeout | LOW | **NO** | Automatic fallback to cached weather / seasonal prior. |
| Memory leak or worker recycling loop | HIGH | **YES** | Revert to previous container image. |

---

## 6. Verification Checklist Following Rollback
1. Execute health check: `curl -I https://<DEPLOYED_URL>/health` (must return HTTP 200).
2. Execute live inference test: `curl -X POST https://<DEPLOYED_URL>/api/pahad/live-inference -H "Content-Type: application/json" -d '{"sector_id":"SK-NH10-KM48","latitude":27.33,"longitude":88.61}'` (must return `{"status": "SUCCESS"}`).
3. Verify siren interlock is locked: `curl -s https://<DEPLOYED_URL>/api/authority/siren-access | grep '"physical_siren_interlock": "LOCKED"'`.
4. Check EOC queue: `curl -s https://<DEPLOYED_URL>/api/eoc/incidents | grep '"status": "SUCCESS"'`.
5. Notify incident commander and log event in EOC audit log.
