# PARVAT NETRA — Core Project Constitution & Agent Rules

This document establishes the binding architectural and engineering rules for all autonomous AI agents working within the **PARVAT NETRA** repository.

---

## 1. Project Mission & Identity
- **Project**: PARVAT NETRA — NER Sentinel
- **Tagline**: “See the risk. Act before the disaster.”
- **Standard**: Smart India Hackathon (SIH) Grade National Disaster-Intelligence Platform.
- **Paradigm**: **Predict → Detect → Explain → Warn → Prioritise → Respond → Recover**

---

## 2. The Core Technical Invariant: Multimodal Evidence Fusion
PARVAT NETRA never relies on single-threshold heuristics or unexplainable black-box AI. All risk scores must correlate:
1. **Physical Mechanics**: Infinite Slope Factor of Safety (FoS) based on Mohr-Coulomb shear strength.
2. **In-Situ Geotechnical Telemetry**: Piezometer pore-water pressure, borehole inclinometer displacement, tilt, and vibration.
3. **Precipitation**: Real-time rainfall intensity + 24h/72h Antecedent Precipitation Index (API).
4. **Earth Observation**: InSAR satellite deformation velocities and vegetation loss.
5. **Computer Vision**: CCTV/drone tension crack and mudflow detection.
6. **Community Intelligence**: Geo-tagged verified citizen reports.

Every warning MUST be accompanied by an **Explainability Breakdown ("Why")** showing exact modality contribution percentages.

---

## 3. Strict Visual & Design Guidelines
- **Atmosphere**: Calm, scientific, operational, national emergency authority grade.
- **Theme**: Deep obsidian slate (`#070B10` to `#0F172A`) with crisp, high-contrast typography (`Inter` + `JetBrains Mono` for telemetry).
- **PROHIBITED TROPES**:
  - NO cyberpunk neon glows or grid scans.
  - NO video-game target reticles or decorative HUDs.
  - NO heavy glassmorphism blurring critical sensor curves.
  - NO decorative, meaningless AI animation widgets.

---

## 4. Data Honesty & Provenance Protocol
Never fabricate live connectivity. Every metric, map layer, and incident feed must display an explicit provenance badge:
- `[LIVE]`: Authenticated real-time sensor/API feed.
- `[SIMULATED]`: Statistically realistic physics simulation based on historical rainfall.
- `[HISTORICAL]`: Archival ground truth from GSI/IMD records.
- `[DEMO]`: Synthetic walkthrough sequence for evaluator inspection.

---

## 5. Safe Routes Engine Invariants
1. Provides **FASTEST**, **SHORTEST**, and **SAFEST** (hazard-aware cost optimization).
2. Selecting a route updates the vector layer dynamically; **never reload the whole page or remount the map**.
3. If external routing APIs (Mapbox/Google) are unavailable, fall back deterministically to the local PostGIS geometric road network graph. **Never render straight-line routes.**

---

## 6. Security & Credential Isolation
- All secrets, tokens, and database passwords belong in `.env`.
- Never hardcode credentials into source code, test files, or MCP configs.
- Run `python mcp/scripts/validate_config.py` to confirm zero leaks before committing.

---

## 7. OmniRoute Local AI Gateway Protocol
- OmniRoute runs locally on `http://localhost:20128` (OpenAI-compatible inference base: `http://localhost:20128/v1`).
- Used for natural language SitRep synthesis, multilingual safety broadcasts (Nepali, Lepcha, Bhutia, Hindi, English), and tactical decision intelligence.
- **Fail-Safe Invariant**: Never block or halt platform telemetry if OmniRoute is offline. Services must gracefully fall back to deterministic geotechnical formulas with transparent provenance badges (`[LIVE / DETERMINISTIC]`).

---

## 8. Specialized AI Agent Swarm
The repository deploys five specialized engineering and operational agents in `.agents/agents/`:
1. **`geotechnical_physics_agent`**: Mohr-Coulomb shear strength, Factor of Safety ($FoS$), pore-water pressure, and slope mechanics.
2. **`gis_hydrology_sentinel_agent`**: PostGIS spatial queries, Sentinel-1 InSAR LOS ground deformation, and CWC Teesta river hydrometry.
3. **`tactical_evacuation_routing_agent`**: BRO mountain highway corridors (NH-10, NH-717A bypasses), Dijkstra/A* multi-modal hazard penalty graphs, and relief convoy staging.
4. **`multi_source_triage_coordinator`**: Citizen field evidence clustering, drone/CCTV vision crack apertures, automated SDRF/NDRF dispatch, and OASIS CAP v1.2 alerts.
5. **`omniroute_agent_bridge`**: OmniRoute LLM gateway orchestration, multilingual translations, structured output validation, and local resilience.

