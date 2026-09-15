# PARVAT NETRA / PAHAD AI — PHASE 11J RELEASE SOURCE OF TRUTH INVENTORY
**Standard: Smart India Hackathon (SIH) 2026 Pre-Submission Hardening**  
**Classification: Authoritative Implementation Mapping & Duplication Defense**  
**Release Target: Final Production Deployment Integrity**

---

## 1. Authoritative Implementation Architecture

To ensure zero divergence between the server runtime, machine learning inference engine, database, and client dashboards, the authoritative source of truth for every core system calculation and state is mapped below:

| Function / Signal | Authoritative Implementation File | Authoritative Runtime Endpoint | Primary Frontend Consumer | Notes & Secondary Implementations |
|---|---|---|---|---|
| **Factor of Safety ($FoS$)** | `engine/pahad_models.py:calculate_infinite_slope_fs()` | `POST /api/pahad/evaluate-sector`<br>`GET /api/pahad/live-inference` | `templates/index.html`<br>`#primary-fos-val` | Closed-form Mohr-Coulomb equation with pore-water pressure ratio $m$. Continuous, non-clamped physics. |
| **Composite Risk Index ($\text{CRI}$)** | `engine/pahad_fusion.py:PahadFusionEngine.fuse()` | `GET /api/pahad/live-inference`<br>`GET /api/pahad/highest-risk-corridor` | `templates/index.html`<br>`#primary-cri-val` | $H = 0.40S + 0.35P + 0.25A$, $\text{CRI} = H \cdot V \cdot 100$. Evaluates false-alarm suppression. |
| **Risk Band Classification** | `engine/pahad_models.py:ALERT_LEVEL_MAPPINGS` | `GET /api/pahad/live-inference`<br>`GET /api/pahad/highest-risk-corridor` | `templates/index.html`<br>`#primary-risk-badge` | Strict intervals: `LOW` (0-20), `MODERATE` (20-40), `HIGH` (40-60), `VERY_HIGH` (60-80), `EXTREME` (80-100). |
| **Event Probability ($P_{\text{event}}$)** | `engine/model_registry.py:ModelRegistry.predict_proba()` | `POST /api/pahad/predict-event`<br>`GET /api/pahad/live-inference` | `templates/index.html`<br>`#hf-prob-24h` | Platt-calibrated GBDT (`models/pahad_event_model.pkl`). Evaluated on 34 geotechnical-hydrological features. |
| **Highest-Risk Corridor Prioritization** | `app.py:api_pahad_highest_risk_corridor()` | `GET /api/pahad/highest-risk-corridor` | `templates/index.html`<br>`initHighestRiskCorridor()` | Deterministic sorting across all 26 canonical corridors: `[-CRI, +FoS, +ID]`. Dynamic live Open-Meteo telemetry. |
| **Data Provenance & Badging** | `engine/pahad_live_inference.py:LiveInferenceResult` | `GET /api/pahad/live-inference`<br>`GET /api/pahad/data-status` | `templates/index.html`<br>`[LIVE / MODELLED]` badge | Tracks modality-level provenance: `[LIVE]`, `[HISTORICAL]`, `[SIMULATED]`, `[DEMO]`. |
| **Evidence Confidence Score** | `engine/pahad_fusion.py:evidence_confidence` | `GET /api/pahad/live-inference` | `templates/index.html`<br>`#evidence-conf-val` | Decoupled from hazard magnitude ($0.30\text{--}0.98$). Formed from signal agreement (60%) + data freshness (40%). |
| **Operational Authority State** | `engine/operational_state_machine.py` | `POST /api/authority/siren-access`<br>`POST /api/authority/incident-commander/override` | `templates/index.html`<br>`#eoc-authority-panel` | Validates statutory role (DM / SEOC), session nonces, and append-only audit trail logging. |
| **Public Dispatch Safety Flags** | `app.py` & `.env` (`ENABLE_PUBLIC_DISPATCH`) | `GET /api/siren/status`<br>`POST /api/siren/activate` | `templates/index.html`<br>`#safety-gate-banner` | Fail-closed defaults: `ENABLE_PUBLIC_DISPATCH=0`, `SIREN_DRY_RUN=1`. Blocks unauthorized civilian sirens / SMS / CAP dispatches. |

---

## 2. Deprecation & Duplication Defense

1. **No Rogue Client Calculations:**
   - Client scripts in `templates/index.html` function purely as visual consumers. No JavaScript file calculates CRI, FoS, or risk bands independently.
2. **Canonical Corridor Catalog:**
   - All 26 corridors are defined exclusively in `engine/canonical_registry.py`. Redundant static dictionaries in legacy routes are subordinated to `CANONICAL_REGISTRY.get_location()`.
3. **Model Artifact Authority:**
   - All operational inference models are loaded exclusively through `engine/model_registry.py:GLOBAL_MODEL_REGISTRY` or `engine/pahad_event_predictor.py`, referencing SHA-256 verified files in `models/`.
