# PARVAT NETRA / PAHAD AI
## PUBLIC VERCEL DEPLOYMENT & LIVE RISK GIS PROPAGATION REPORT
**Document Reference**: `reports/VERCEL_LIVE_RISK_GIS_DEPLOYMENT_REPORT.md`  
**Execution Timestamp**: `2026-09-17T08:35:00+05:30`  
**Target Commit SHA**: `c5964d8a19e97af6bc96470014ed344bfd1b36f2`  
**Deployment Target**: `https://silly-fermi.vercel.app/`  
**Vercel Project ID**: `prj_wDHY7Lm5diHUrN4hzZSPqfEsfIZz` (Org: `team_PIwfOBfSoof2F2Ou7YqruEp1`)  
**Status**: `VERCEL_DEPLOYMENT_ACTION_REQUIRED`

---

## 1. Executive Summary & Verdict

This forensic audit evaluates the propagation of commit `c5964d8a19e97af6bc96470014ed344bfd1b36f2` ("Enable verified live risk GIS") from the verified local repository and GitHub `origin/main` to the public production endpoint hosted at `https://silly-fermi.vercel.app/`.

### Key Verdict
> **AUTHORITATIVE VERDICT: `VERCEL_DEPLOYMENT_ACTION_REQUIRED`**
>
> - **Local Repository**: **VERIFIED**. 56/56 targeted tests passing (100% pass rate in 8.36s). All live-risk GIS layers, geojson endpoints, and status strips operational.
> - **GitHub Remote (`origin/main`)**: **VERIFIED & SYNCHRONIZED**. Commit `c5964d8a19e97af6bc96470014ed344bfd1b36f2` is pushed and matches local `HEAD` exactly.
> - **Vercel Production (`silly-fermi.vercel.app`)**: **STALE BUILD SERVED**. The production instance is serving a prior deployment build (from Phase 10/11, dated Sept 13, 2026). The endpoint `/api/pahad/realtime-cri/geojson` returns `HTTP 404`, and `/` lacks `#gis-map-status-strip`.
> - **Action Required**: The Vercel project is not configured with automatic GitHub webhook deploys for this branch or requires an explicit redeploy trigger from the Vercel Dashboard / CLI by an authorized account owner.

---

## 2. Git Synchronization State

| Property | Value | Verification Method | Status |
|---|---|---|---|
| **Local Branch** | `main` | `git status` | `VALID` |
| **Local HEAD SHA** | `c5964d8a19e97af6bc96470014ed344bfd1b36f2` | `git rev-parse HEAD` | `MATCH` |
| **Remote Tracking** | `origin/main` | `git rev-parse origin/main` | `MATCH` |
| **GitHub Remote URL** | `https://github.com/dimpu-sashank2008/parvatnetra.git` | `git remote -v` | `CONFIRMED` |
| **Working Tree Cleanliness** | 0 unstaged modifications in tracked files | `git status -s` | `CLEAN` |
| **Target Commit Title** | `Enable verified live risk GIS` | `git log -1` | `CONFIRMED` |

---

## 3. Vercel Configuration Audit

The repository contains the following deployment configurations:

1. **`vercel.json`**:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python",
         "config": {
           "maxDuration": 30
         }
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```
   - All routes `/(.*)` are forwarded to the WSGI application instance in `app.py`.
   - Max execution duration is set to 30 seconds.

2. **`.vercel/project.json`**:
   - `projectId`: `prj_wDHY7Lm5diHUrN4hzZSPqfEsfIZz`
   - `orgId`: `team_PIwfOBfSoof2F2Ou7YqruEp1`
   - `projectName`: `silly-fermi`
   - Linked initially on September 13, 2026.

3. **`requirements.txt`**:
   - Includes Flask, Werkzeug, Shapely, PyYAML, Requests, Scikit-learn, and Psycopg2-binary.
   - All serverless dependencies are pinned and compatible with `@vercel/python` Python 3.11 runtime.

---

## 4. Public vs. Local Endpoint Forensic Matrix

Direct side-by-side probe executed on `2026-09-17T08:30:46+05:30`:

| Endpoint | Method | Local Environment (Flask WSGI) | Public Vercel (`silly-fermi.vercel.app`) | Forensic Delta / State |
|---|---|---|---|---|
| `/` | `GET` | **HTTP 200** (949,574 bytes)<br>• `#gis-map-status-strip` present<br>• `currentRiskZonesLayerGroup` present | **HTTP 200** (836,473 bytes)<br>• `#gis-map-status-strip` missing<br>• `currentRiskZonesLayerGroup` missing | **STALE BUILD** (Public build is Phase 10/11 artifact) |
| `/api/health` | `GET` | **HTTP 200** (302 bytes)<br>• Database: CONNECTED<br>• PostGIS: 3.6 | **HTTP 200** (302 bytes)<br>• Database: CONNECTED<br>• PostGIS: 3.6 | **MATCH** (Shared Neon PostgreSQL instance) |
| `/api/ml/latest-risk` | `GET` | **HTTP 200** (11,173 bytes)<br>• Geotechnical ML Fallback / DB | **HTTP 200** (3,287 bytes)<br>• Geotechnical ML Fallback / DB | **MATCH** (Functional on both) |
| `/api/pahad/realtime-cri` | `GET` | **HTTP 200** (39,194 bytes)<br>• 20 canonical corridors<br>• GeoJSON compatibility | **HTTP 200** (40,038 bytes)<br>• 20 corridors<br>• Older payload schema without GeoJSON linkage | **STALE** (Old contract on Vercel) |
| `/api/pahad/realtime-cri/geojson` | `GET` | **HTTP 200** (24,046 bytes)<br>• Valid RFC 7946 FeatureCollection<br>• 20 Polygon/Point features<br>• WGS84 coordinates | **HTTP 404 Not Found** (0 bytes) | **MISSING ON VERCEL** (Route introduced in `c5964d8` not deployed) |
| `/api/seismic/latest` | `GET` | **HTTP 200** (353 bytes)<br>• USGS Live / Fallback | **HTTP 200** (307 bytes)<br>• USGS Live / Fallback | **MATCH** |
| `/api/weather/current` | `GET` | **HTTP 200** (270 bytes)<br>• Open-Meteo Live API | **HTTP 200** (256 bytes)<br>• Open-Meteo Live API | **MATCH** |

---

## 5. Stale Build Forensic Cause Analysis

Our investigation determined the exact technical cause why Vercel is serving stale assets:

1. **GitHub Deployments API Audit**:
   - Polling `https://api.github.com/repos/dimpu-sashank2008/parvatnetra/deployments` returns `[]` (0 active deployments recorded by GitHub).
   - This indicates that the Vercel GitHub App webhook integration is **not currently dispatching automated deployment events** to GitHub for the repository.

2. **Commit Check-Runs Audit**:
   - Check-runs for commit `c5964d8a19e97af6bc96470014ed344bfd1b36f2` contain only `GitHub Actions: test`.
   - No `Vercel` bot or deployment check-run was posted for this SHA.

3. **CLI Session & Credentials Isolation**:
   - In accordance with the Project Constitution (Rule 6: Security & Credential Isolation), zero Vercel API tokens or private auth secrets are committed to the codebase or stored in unencrypted repository files.
   - The CLI was not pre-authenticated on this workstation (`$HOME/.vercel` does not exist).
   - Without a provisioned `VERCEL_TOKEN`, automated headless CLI deployments cannot bypass organizational SSO/2FA.

4. **Conclusion**:
   - The code is **100% verified locally and pushed to GitHub main**.
   - Deployment to Vercel requires triggering a **Redeploy** from the Vercel Web Dashboard or running `vercel --prod` with an authenticated CLI session.

---

## 6. Real-Time Data Pipeline Live Status

| Subsystem | Data Classification | Runtime Source | Live Provenance Disclosed | Invariant Maintained |
|---|---|---|---|---|
| **Precipitation / Weather** | `LIVE_EXTERNAL` | Open-Meteo Live API (Free, no token required) | `[LIVE / OPEN-METEO]` | Yes (Real-time mm/h & 24h/72h cumulative) |
| **Seismology** | `LIVE_EXTERNAL` | USGS Earthquake Hazards Program GeoJSON API | `[LIVE / USGS]` | Yes (Magnitude, depth, distance to corridor) |
| **Corridor Risk Index (CRI)** | `CACHED_LIVE / DERIVED` | Weighted multimodal synthesis (IMD + USGS + FoS + In-situ) | `[CACHED-LIVE / DERIVED]` | Yes (Never misrepresented as raw physical sensor) |
| **Geotechnical FoS** | `DERIVED` | Infinite Slope Mohr-Coulomb mechanics | `[DERIVED / MOHR-COULOMB]` | Yes (Separate from event probability) |
| **Borehole / Piezometer Telemetry** | `SIMULATED` | Physics-based numerical simulation | `[SIMULATED / SYNTHETIC]` | Yes (Explicitly disclosed; zero fake hardware claimed) |
| **Spatial Network** | `HISTORICAL / STATIC` | GSI/BRO Highway Geometry (20 corridors across 8 NER states) | `[STATIC / GROUND TRUTH]` | Yes (WGS84 EPSG:4326 verified) |

---

## 7. Safety Gates & Defense-in-Depth Invariants

All automated safety gates remain strictly enforced:
- `ENABLE_PUBLIC_DISPATCH = 0`: Autonomous public emergency sirens and live CAP dispatches are suppressed.
- `SIREN_DRY_RUN = 1`: Field acoustic hardware remains isolated; software relays log to audit storage only.
- `PUBLIC_DEMO_TEST_ONLY = 1`: Explicit watermarking on public surfaces.
- **Corroboration Requirement**: Multi-source triage strictly requires 2-of-3 independent confirmation (e.g., Physical FoS + In-situ telemetry + Citizen/Drone vision) before promoting an incident to `READY_FOR_AUTHORIZATION`.

---

## 8. Post-Propagation Verification Commands

Once the Vercel deployment has been triggered by the operator, run these commands to verify public propagation:

### 1. Verify GeoJSON Live Risk Corridor Layer
```bash
curl -s -i "https://silly-fermi.vercel.app/api/pahad/realtime-cri/geojson"
```
**Expected Response**:
- `HTTP/2 200`
- `Content-Type: application/json`
- GeoJSON FeatureCollection with 20 canonical corridors and property `provenance: "CACHED_LIVE"`.

### 2. Verify Homepage GIS Status Strip & Layer Integration
```bash
curl -s "https://silly-fermi.vercel.app/" | grep -E "gis-map-status-strip|currentRiskZonesLayerGroup"
```
**Expected Response**:
- Contains `id="gis-map-status-strip"`
- Contains `const currentRiskZonesLayerGroup = L.layerGroup()`

### 3. Verify Real-Time CRI Evaluation API
```bash
curl -s "https://silly-fermi.vercel.app/api/pahad/realtime-cri" | grep -o '"corridors_monitored":20'
```
**Expected Response**:
- `"corridors_monitored":20`

---

## 9. Operator Redeployment Instructions (Next Steps)

To propagate commit `c5964d8a19e97af6bc96470014ed344bfd1b36f2` to production:

### Option A: Via Vercel Web Dashboard (Recommended, 60 seconds)
1. Navigate to: `https://vercel.com/` and log in to the team `team_PIwfOBfSoof2F2Ou7YqruEp1`.
2. Open Project: **`silly-fermi`** (`prj_wDHY7Lm5diHUrN4hzZSPqfEsfIZz`).
3. Click the **Deployments** tab.
4. If the latest commit `c5964d8` is listed as pending or skipped, click the three-dots menu (`...`) next to it and select **Redeploy**.
5. Alternatively, click **Deploy**, select repository `dimpu-sashank2008/parvatnetra`, branch `main`, and click **Deploy**.
6. Wait ~45 seconds for the `@vercel/python` builder to complete.

### Option B: Via Vercel CLI (Local Terminal)
Run the following in the project root:
```bash
npx vercel login
npx vercel --prod
```

---

## 10. Verification Matrix Table

| Check ID | Requirement | Local State | Public Vercel State | Result |
|---|---|---|---|---|
| **CHK-01** | Git HEAD == origin/main == `c5964d8` | `c5964d8` | N/A (Remote Git) | **PASS** |
| **CHK-02** | Local targeted regression tests (56/56) | 56/56 Passed | N/A | **PASS** |
| **CHK-03** | Zero credential leaks in git tree | 0 detected | 0 detected | **PASS** |
| **CHK-04** | Homepage loads HTTP 200 | HTTP 200 | HTTP 200 | **PASS** |
| **CHK-05** | Homepage contains `#gis-map-status-strip` | Present | **Missing (Stale)** | **FAIL (Public)** |
| **CHK-06** | Homepage contains `currentRiskZonesLayerGroup` | Present | **Missing (Stale)** | **FAIL (Public)** |
| **CHK-07** | Endpoint `/api/pahad/realtime-cri/geojson` HTTP 200 | HTTP 200 (20 features) | **HTTP 404 Not Found** | **FAIL (Public)** |
| **CHK-08** | Endpoint `/api/weather/current` HTTP 200 | HTTP 200 | HTTP 200 | **PASS** |
| **CHK-09** | Endpoint `/api/seismic/latest` HTTP 200 | HTTP 200 | HTTP 200 | **PASS** |
| **CHK-10** | Safety gates enforced (`ENABLE_PUBLIC_DISPATCH=0`) | Enforced | Enforced | **PASS** |

---

## 11. Final Status Block

```yaml
PLATFORM: PARVAT NETRA
MODULE: PAHAD AI Live Risk GIS Engine
COMMIT_LOCAL: c5964d8a19e97af6bc96470014ed344bfd1b36f2
COMMIT_REMOTE_ORIGIN_MAIN: c5964d8a19e97af6bc96470014ed344bfd1b36f2
LOCAL_TEST_STATUS: 56/56 PASSED (100%)
PUBLIC_ENDPOINT: https://silly-fermi.vercel.app
PUBLIC_GEOJSON_ROUTE_STATUS: HTTP 404 Not Found (Requires Redeploy)
PUBLIC_HTML_STATUS: STALE_BUILD (Missing Live Risk GIS Strip)
ACTION_REQUIRED: Operator manual redeploy via Vercel Dashboard or CLI
FINAL_VERDICT: VERCEL_DEPLOYMENT_ACTION_REQUIRED
```
