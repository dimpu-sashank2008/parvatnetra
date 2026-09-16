# PARVAT NETRA / PAHAD AI — PHASE 12C
# Authoritative Explainability Engine & Evidence Architecture Report

**Platform:** PARVAT NETRA — NER Sentinel  
**Component:** PAHAD AI Explainability & Risk Change Engine  
**Standard:** SIH Grade National Disaster-Intelligence Platform (DMA 2005 Compliant)  
**Baseline Status:** Phase 12A (`PHASE12A_SCIENTIFIC_CORE_PASS_WITH_LIMITATIONS`), Phase 12B (`PHASE12B_INFRASTRUCTURE_READY`)  
**Phase 12C Status:** `PHASE12C_EXPLAINABILITY_VERIFIED`  

---

## 1. Executive Summary
Phase 12C implements an authoritative, non-causal explainability layer for PAHAD AI across the North-Eastern Region (NER). Grounded in empirical geotechnical physics and strict data provenance, the system explains *why* risk scores change without ever claiming causal certainty or generating synthetic explanations.

The system upholds three core architectural invariants:
1. **Separation of Explanation and Prediction:** The explanation engine consumes existing runtime objects; it does NOT alter predictions, FoS, or CRI.
2. **Zero Manufactured Deltas:** When past baselines are unavailable or mismatched, the engine reports `COMPARISON_UNAVAILABLE` rather than hallucinating changes.
3. **Strict Safety Interlocks:** The AI provides decision intelligence only; all actuation (sirens, public warnings) is strictly reserved for statutory human authorities under the Disaster Management Act (DMA 2005).

---

## 2. Runtime Data Pipeline Trace
The explanation pipeline traces deterministically from telemetry to voice dispatch:
```mermaid
flowchart LR
    Telemetry[In-Situ IoT / IMD / NCS / Sentinel-1] --> Ingest[Data Connectors & Normalizer]
    Ingest --> Engine[Physics Engine FoS & Event Model ML]
    Engine --> Fusion[Multi-Modal CRI Fusion]
    Fusion --> ExplainEngine[PahadExplanationEngine]
    ExplainEngine --> UI[Tripartite Evidence Matrix UI]
    ExplainEngine --> API[/api/pahad/explanation/<id>]
    ExplainEngine --> Voice[Grounded Voice Assistant]
```

Authoritative Runtime Objects:
- `corridor_id`: Canonical corridor identifier (e.g., `SK-NH10-KM48`, `ML-SONAPUR-01`)
- `timestamp`: ISO-8601 UTC timestamp of telemetry acquisition
- `CRI`: Composite Risk Index fused score (0–100)
- `FoS`: Factor of Safety (Mohr-Coulomb limit equilibrium)
- `event_probability`: Calibrated Gradient Boosting probability (6h/12h/24h/48h)
- `risk_band`: Canonical classification (`STABLE`, `WATCH`, `WARNING`, `CRITICAL`)
- `corroboration_state`: 2-of-3 Multi-Signal Corroboration Heuristic state
- `data_provenance`: Live provenance tags (`[LIVE]`, `[SIMULATED]`, `[HISTORICAL]`, `[DEMO]`)

---

## 3. Authoritative Contract Schema
The `ExplanationContract` defines the immutable data interface returned by `/api/pahad/explanation/<corridor_id>`:
```python
@dataclass
class ExplanationContract:
    corridor_id: str
    corridor_name: str
    timestamp: str
    cri: float
    fos: float
    event_probability: float
    risk_band: str
    risk_change: Dict[str, Any]
    top_drivers: List[Dict[str, Any]]
    supporting_evidence: List[str]
    contradicting_evidence: List[str]
    missing_evidence: List[str]
    corroboration_state: str
    corroboration_detail: str
    data_quality_score: float
    confidence_level: str
    causal_honesty_note: str
    authority_recommendation: str
    statutory_requirement: str
    provenance_summary: str
    model_governance: Dict[str, Any]
```

---

## 4. Non-Causal Explanation Grammar
To avoid scientifically unverified claims of direct causation, PAHAD AI enforces a strict non-causal grammar across all summaries, UI text, and voice responses:

| Forbidden Causal Phrasing | Enforced Non-Causal Phrasing |
| :--- | :--- |
| "Heavy rain caused the landslide risk to spike." | "CRI increased alongside higher hydrological loading (68.4 mm/24h) and lower computed FoS (0.926)." |
| "The earthquake triggered the slope failure." | "Regional seismic acceleration (M3.8, 42 km) coincided with an elevated geotechnical destabilization signal." |
| "Poor drainage made the slope unstable." | "Increased pore-water pressure telemetry (26.4 kPa) correlates with diminished shear strength reserves." |

---

## 5. Tri-Partite Evidence Matrix
Every assessment partitions available intelligence into three distinct buckets:
1. **Supporting Evidence (Risk Elevators):**
   - Mohr-Coulomb limit equilibrium failure ($FoS < 1.0$)
   - Mandal-Sarkar empirical rainfall threshold exceedance ($I \ge 50	ext{ mm/24h}$)
   - Calibrated GBDT event likelihood exceeding baseline ($P(E) \ge 0.50$)
   - Regional seismic ground acceleration within 100 km radius
2. **Contradicting Evidence (Stabilizing Factors):**
   - High factor of safety ($FoS > 1.30$)
   - Stable pore-water pressure within historical seasonal bounds
   - Low recent cumulative precipitation ($< 10	ext{ mm/24h}$)
   - InSAR line-of-sight velocity within linear creep threshold ($< 5	ext{ mm/yr}$)
3. **Missing Evidence (Data Gaps):**
   - Missing in-situ piezometer or borehole inclinometer telemetry
   - Offline IMD weather station defaulting to numerical reanalysis
   - InSAR optical cloud cover or radar temporal decorrelation ($> 12	ext{ days}$)

---

## 6. 2-of-3 Multi-Signal Corroboration Heuristic
The platform implements a strict corroboration heuristic to prevent single-modality false alarms:
- **Signal A:** Physical Slope Factor of Safety ($FoS \le 1.0$)
- **Signal B:** Empirical Rainfall Threshold ($Rain \ge 50	ext{ mm/24h}$)
- **Signal C:** Calibrated Geotechnical ML ($P(E) \ge 0.50$)

States:
- `A+B+C (TRIPLE_SIGNAL_CORROBORATED)`: Maximum confidence; all independent modalities agree.
- `A+B (PHYSICAL_HYDRO_CORROBORATED)`: High confidence; physics and weather agree.
- `A+C (PHYSICAL_ML_CORROBORATED)`: High confidence; physics and ML agree.
- `B+C (HYDRO_ML_CORROBORATED)`: High confidence; weather and ML agree.
- `SINGLE_SIGNAL`: Low confidence; only one modality indicates elevated risk.
- `INSUFFICIENT_CORROBORATION`: No modalities meet trigger criteria.

---

## 7. Zero Manufactured Deltas Protocol
The `RiskChangeEngine` maintains an in-memory chronological state history. When tracking risk transitions:
- If previous observations exist within a valid temporal window ($< 7	ext{ days}$) under the same provider configuration:
  $$\Delta CRI = CRI_{now} - CRI_{prev}, \quad \Delta FoS = FoS_{now} - FoS_{prev}, \quad \Delta Rain = Rain_{now} - Rain_{prev}$$
- If comparing across divergent providers, discontinuous timestamps ($> 7	ext{ days}$), or initial observation cycles:
  $$	ext{status} = 	ext{"COMPARISON_UNAVAILABLE"}$$
  The engine reports: *"Baseline established. Telemetry tracking initiated."* Hallucinating deltas is strictly prohibited.

---

## 8. Statutory Authority Decision Gate (DMA 2005)
Under the Disaster Management Act (DMA 2005), AI recommendations never bypass statutory human authority:
- **Stage 1 (Monitor):** Autonomous sensor sampling and numerical assimilation.
- **Stage 2 (AI Advisory):** Multi-modal triage recommending specific operational protocols (e.g., heavy vehicle restrictions, SDRF patrol dispatch).
- **Stage 3 (Statutory Sign-off):** Emergency warning issuance, siren activation, and highway closure require explicit sign-off from the District Disaster Management Authority (DDMA / District Magistrate) or State Emergency Operations Centre (SEOC).
