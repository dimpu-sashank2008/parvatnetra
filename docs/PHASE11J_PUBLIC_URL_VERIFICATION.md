# PARVAT NETRA / PAHAD AI — PHASE 11J
# PUBLIC URL & EVALUATOR VERIFICATION GUIDE
**Document ID**: `PN-PHASE11J-PUBLIC-VERIFY-001`  
**Target Audience**: SIH 2026 Grand Finale Evaluation Jury & Technical Assessors  
**Platform Classification**: National Geotechnical & Hillslope Hazard Intelligence Platform  

---

## 1. Overview for Judges & Evaluators
This guide provides direct, read-only, non-destructive verification endpoints for the **PARVAT NETRA / PAHAD AI** deployment. Assessors can safely verify system functionality, model provenance, geospatial fusion, and fail-closed safety interlocks without creating false alarms or altering state.

---

## 2. Safe Inspector URL Directory

| Route / Endpoint | Description | Primary Verification Target | Expected Response / Indicator |
| :--- | :--- | :--- | :--- |
| `GET /` | Main National Sentinel Command Center | GIS multi-hazard corridor map, CRI telemetry, and corridor selector | Obsidian slate theme (`#070B10`), 26 corridors rendered, telemetry live |
| `GET /health` | Public Health & Service Status Check | Serverless/container operational status | HTTP 200, `{"status": "UP", "version": "3.1.0"}` |
| `GET /demo` | 50m Geofence & Mobile Siren Evaluation Portal | Live GPS distance calculation, evacuation guidance, acoustic test | Interactive simulation, geofence radius check, dry-run siren toggle |
| `GET /api/pahad/highest-risk-corridor` | Authoritative Highest-Risk Ranking | Cross-phase corridor prioritization and deterministic tie-breaking | JSON with top-ranked corridor (e.g., East Khasi Hills / NH-10) with exact $CRI$ |
| `GET /api/pahad/data-status` | Data Quality & Provenance Transparency | Live feed status for Weather, Seismic, IoT, InSAR, and Event Model | Full breakdown of data sources with explicit provenance tags (`[LIVE]`, `[CACHED]`) |
| `GET /api/pahad/forecast` | Multi-Horizon Forecast Horizon | 6h, 12h, 24h, 48h forward probability projection | Explicit limitation notes for small-N training dataset |
| `GET /api/authority/siren-access` | Safety Interlock Verification | Public safety gate and fail-closed siren controls | `{"physical_siren_interlock": "LOCKED", "human_authorization_required": true}` |
| `GET /api/eoc/incidents` | Incident Command Queue | Prioritized multi-hazard incident list with triage scoring | Ranked operational incidents sorted by risk score and road criticality |
| `GET /api/eoc/command-brief` | Executive SitRep Briefing | One-screen commander briefing aggregating sensor, model, and dispatch | Integrated executive summary with signal agreement metrics |

---

## 3. Step-by-Step Evaluator Walkthrough

### 3.1 Step 1: Verify Core Scientific Invariants
1. Navigate to `/` on the deployed instance.
2. In the right-hand panel, inspect the **Composite Risk Index ($CRI$)** card.
3. Verify that the three distinct metrics are clearly delineated:
   - **Infinite Slope Factor of Safety ($FoS$)**: Mohr-Coulomb physics based on pore pressure, soil friction, and slope geometry.
   - **PAHAD Event Probability**: GBDT classifier trained on documented historical events.
   - **Composite Risk Index ($CRI$)**: Multi-criteria weighted synthesis:
     $$H = 0.40 \times S + 0.35 \times P + 0.25 \times A$$
     $$CRI = H \times V \times 100$$
4. Verify that $FoS$ and Event Probability are **never conflated or renamed**.

### 3.2 Step 2: Verify Real Data Provenance & Model Limitations
1. Execute `curl -s https://<DEPLOYED_URL>/api/pahad/data-status`.
2. Inspect the returned JSON:
   - Event model status is explicitly marked: `"TRAINED_LIMITED_DATA"`.
   - Training sample count is transparently declared: $N = 16$ real historical events, $N = 12$ validation, $N = 8$ test.
   - Provenance note clearly states: `[SIMULATED] in demo mode. [LIVE] when external APIs are authenticated and responding. [CACHED] when serving from local disk cache within TTL.`

### 3.3 Step 3: Verify Fail-Closed Alert Safety (Siren & CAP)
1. Execute `curl -s https://<DEPLOYED_URL>/api/authority/siren-access`.
2. Verify that:
   - `"physical_siren_interlock": "LOCKED"`
   - `"human_authorization_required": true`
   - `"emergency_rollback": "AVAILABLE"`
3. Confirm that no public sirens or CAP broadcast alerts can trigger autonomously without verified dual human authority credentials (2-of-3 consensus).

### 3.4 Step 4: Verify 50m Geofence & Evacuation Guidance
1. Open `/demo` on a smartphone or browser with geolocation enabled.
2. The interactive map displays the 50-meter safety perimeter and active evacuation routes.
3. Test distance calculation to the nearest hazard zone; verify that alerts display clear emergency guidance without triggering external public networks.
