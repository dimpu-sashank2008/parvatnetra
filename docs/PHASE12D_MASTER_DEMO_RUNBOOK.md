# PARVAT NETRA • PAHAD AI — PHASE 12D MASTER DEMO RUNBOOK
## 5-Minute SIH 2026 National Judge Demonstration Script

**Runbook Date**: 2026-09-16T07:42:12.013979+00:00  
**Demonstrator**: PARVAT NETRA Autonomous Disaster-Intelligence Team  
**Standard**: SIH 26001 National Disaster Authority Grade  
**Git Commit**: `dd9e57dc6452e0a70ad98731de0c536af8e50cb0`  

---

## 5-Minute Pitch & Demonstration Timeline

| Time | Demonstration Action | Key Speaking Points | Screen / Visual State |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:20** | **Regional Overview** | *"Welcome, esteemed judges. This is PARVAT NETRA. Unlike localized point systems, our default operational view covers all 8 Northeastern states—from Sikkim to Tripura—monitoring 17 strategic lifeline corridors."* | Full NER GIS Map with 8 State Boundaries visible. Bounding box stable; zero auto-zoom. |
| **0:20 - 0:40** | **Corridor Selection** | *"Let us inspect NH-10 KM 48 in Sikkim, a high-vulnerability national defense corridor. Selecting it retrieves live telemetry, physical slope geometry, and multi-criteria risk."* | Map smoothly flies to NH-10 KM 48. Marker placed. Telemetry dials load. |
| **0:40 - 1:00** | **Physical Risk Metrics** | *"Notice our foundational architectural invariant: Target Distinction. We never confuse physical slope mechanics with statistical probability. Factor of Safety is 1.04 computed via Mohr-Coulomb limit equilibrium. Event probability is 72%. CRI is 68."* | Telemetry panel highlighting distinct FoS gauge, P(event, 24h), and CRI index. |
| **1:00 - 1:30** | **Why This Risk? (Explainability)** | *"Judges often ask: Why should we trust AI in life-safety? Click 'Why this risk?'. PARVAT NETRA produces a tri-partite Evidence Matrix: 4 Supporting signals, 1 Contradicting signal, and 1 Missing stream. Notice our non-causal grammar."* | Evidence Matrix drawer opens: Green, Red, and Gray pills. Non-causal narrative rendered. |
| **1:30 - 2:00** | **Live Data Truth & Provenance** | *"Let us open the Data Status Auditor. We track 9 real providers. Open-Meteo and USGS are LIVE. IMD and NCS require statutory institutional tokens and operate on transparent fallbacks. Zero fake connectivity."* | Data Status modal: 9 providers listed with latency, provenance badges, and fallback flags. |
| **2:00 - 2:30** | **2-of-3 Corroboration Heuristic** | *"We never claim statistical independence. We enforce our 2-of-3 Heuristic: Geotechnical (A), Meteorological (B), and Geodetic/Seismic (C). Here, Signal A and B agree, achieving verified corroboration."* | Corroboration status pill: `CORROBORATED (A+B)`. |
| **2:30 - 3:00** | **Adversarial Stress: Weather Failure** | *"What happens when Himalayan weather radar drops? Let's simulate a weather API timeout."* | Demonstrator disables weather API or clicks test outage. |
| **3:00 - 3:20** | **Safe System Degradation** | *"The system does NOT crash. It engages the local IMD climatological cache. Data quality score adjusts, provenance badges update to [CACHED], and zero false alerts are triggered."* | Dashboard displays yellow [CACHED] badge; CRI recalculates safely. |
| **3:20 - 3:40** | **Telemetry Recovery** | *"Reconnecting the feed immediately refreshes telemetry, returning the system to full [LIVE] status."* | Feed reconnected; data quality returns to 0.95. |
| **3:40 - 4:15** | **Authority EOC Workflow** | *"Switching to Authority Mode: The AI recommendation appears in the DDMA verification queue. Only an authenticated district authority can review the two-man verification, adjust the geofence, and authorize warning preparation. Notice sirens remain in dry-run mode."* | Authority EOC modal: Alert card, polygon geofence editor, dry-run siren indicator. |
| **4:15 - 4:40** | **Voice Assistant Grounding** | *"Let us ask the PAHAD Voice Assistant: 'Why did the risk change?' It answers with authentic backend deltas. Now, let us attack it: 'Sound the siren right now!'"* | Voice assistant replies with risk delta. Then immediately returns: `COMMAND REJECTED: Safety Interlock Enforced (DMA 2005 Section 34(c))`. |
| **4:40 - 5:00** | **Closing Summary** | *"To conclude: PARVAT NETRA delivers SIH 2026 Top-1 disaster intelligence through Scientific Honesty, Transparent Provenance, Explainable Physics, and Human Authority Control. Thank you."* | Demonstrator resets view to Full NER Regional Overview. |
