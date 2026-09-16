# PARVAT NETRA / PAHAD AI — PHASE 11E BASELINE
**PERFORMANCE, RELIABILITY, RESILIENCE & RESOURCE-SAFETY AUDIT BASELINE**

- **Date:** September 15, 2026
- **Audit Phase:** Phase 11E (Performance, Reliability, Resilience & Resource Safety)
- **Current Branch:** `main`
- **Baseline Git Commit:** `dbde2f7`
- **Commit Message:** `feat: Phase 15 Chrome DevTools capture, autonomous scheduler, OpenAPI docs, and Docker containerization`
- **Python Version:** Python 3.11.0 (Windows x64 [MSC v.1933 64 bit])
- **Node Runtime Version:** v24.19.0
- **Flask Route Inventory:** 229 registered REST & View endpoints
- **Prior Phases Preserved:** Phase 11A, 11B, 11C, 11D, 11H, 11I, 11J, 11K, 11L, 11M (verified intact)

---

## 1. Git Repository State

### Branch Information (`git branch`)
```text
* main
  staging
```

### Git Status (`git status`)
```text
On branch main
Your branch is ahead of 'origin/main' by 3 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   app.py
	modified:   data/cache/seismic/latest_events.json
	modified:   data/cache/weather/25_67_94_02_NL-DZUDZA-01.json
	modified:   data/cache/weather/25_76_93_91_NL-PIPHEMA-01.json
	modified:   data/cache/weather/27_33_88_61_SK-NH10-KM48.json
	modified:   docs/PHASE11M_FINAL_SUBMISSION_FREEZE.md
	modified:   docs/PHASE11M_RELEASE_MANIFEST.md
	modified:   public/static/css/parvat_theme.css
	modified:   public/static/js/theme.js
	modified:   reports/PHASE11M_RELEASE_CANDIDATE.json
	modified:   services/authority_review_service.py
	modified:   services/pahad_voice_assistant.py
	modified:   static/css/parvat_theme.css
	modified:   static/js/theme.js
	modified:   templates/climate_map.html
	modified:   templates/console.html
	modified:   templates/demo.html
	modified:   templates/edge_network.html
	modified:   templates/index.html
	modified:   templates/login.html
	modified:   templates/login_authority.html
	modified:   templates/login_citizen.html
	modified:   templates/notifications.html
	modified:   templates/seismic.html
	modified:   templates/terrain_3d.html

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	data/geospatial/
	docs/PHASE11D_SECURITY_BASELINE.md
	docs/PHASE11D_SECURITY_HARDENING_REPORT.md
	public/static/data/ner_state_boundaries.geojson
	static/data/ner_state_boundaries.geojson
	tests/test_ner_gis_default_view.py
```

### Recent Commit (`git log -1 --oneline`)
```text
dbde2f7 feat: Phase 15 Chrome DevTools capture, autonomous scheduler, OpenAPI docs, and Docker containerization
```

### Git Diff Statistics (`git diff --stat`)
```text
 app.py                                            |  23 +-
 data/cache/seismic/latest_events.json             |  50 +-
 data/cache/weather/25_67_94_02_NL-DZUDZA-01.json  |  86 +--
 data/cache/weather/25_76_93_91_NL-PIPHEMA-01.json | 112 ++--
 data/cache/weather/27_33_88_61_SK-NH10-KM48.json  | 114 ++--
 docs/PHASE11M_FINAL_SUBMISSION_FREEZE.md          |   2 +-
 docs/PHASE11M_RELEASE_MANIFEST.md                 |   2 +-
 public/static/css/parvat_theme.css                | 739 +++++++++++++++++++++-
 public/static/js/theme.js                         |   4 +-
 reports/PHASE11M_RELEASE_CANDIDATE.json           |   3 +-
 services/authority_review_service.py              |  13 +
 services/pahad_voice_assistant.py                 |  21 +-
 static/css/parvat_theme.css                       | 611 +++++++++++++++++-
 static/js/theme.js                                |   4 +-
 templates/climate_map.html                        |   5 +-
 templates/console.html                            |   2 +-
 templates/demo.html                               |   5 +
 templates/edge_network.html                       |   5 +-
 templates/index.html                              | 232 +++++--
 templates/login.html                              |   5 +-
 templates/login_authority.html                    |   5 +-
 templates/login_citizen.html                      |   5 +-
 templates/notifications.html                      |  11 +-
 templates/seismic.html                            |   5 +-
 templates/terrain_3d.html                         |   5 +-
 25 files changed, 1803 insertions(+), 266 deletions(-)
```

---

## 2. Deployment Configuration
- **Production Server Descriptor:** `Procfile` (`web: gunicorn app:app --workers 4 --threads 2 --timeout 120`)
- **Render Descriptor:** `render.yaml` (`env: python`, `startCommand: gunicorn app:app`, `autoDeploy: true`)
- **Vercel Serverless Descriptor:** `vercel.json` (`@vercel/python` pointing to `api/index.py`, `maxDuration: 30`)
- **Containerization:** `Dockerfile` (Multi-stage non-root container with gunicorn entrypoint)
- **Database Connection:** PostgreSQL / Neon Cloud (`ep-wild-wave-awpqskzf`) with SQLite local observation fallback (`data/observations/pahad_observations.db`)

---

## 3. Reliability & Safety Invariants Verified Prior to Phase 11E
- `ENABLE_PUBLIC_DISPATCH = 0` (Fail-Closed: civilian broadcast gates locked)
- `SIREN_DRY_RUN = 1` (Fail-Closed: acoustic siren physical relay isolated)
- `CAP_PRODUCTION_DISPATCH = 0` (Fail-Closed: OASIS CAP 1.2 sandbox mode)
- `SACHET_PRODUCTION_DISPATCH = 0` (Fail-Closed: NDMA SACHET sandbox mode)
- `CELL_BROADCAST_PRODUCTION = 0` (Fail-Closed: telecom cell broadcast emulator mode)
- `SMS_DRY_RUN = 1` (Fail-Closed: emergency SMS dry-run mode)
- `REAL_PUBLIC_SMS = DISABLED` (Fail-Closed: civilian SMS broadcast disabled)
- `PAHAD_DEMO_MODE = 0` (Scientific live pipeline: operational feature sets isolated from demo features)
