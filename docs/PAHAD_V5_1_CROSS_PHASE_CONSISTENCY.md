# PARVAT NETRA / PAHAD AI — PHASE V5.1 CROSS-PHASE CONSISTENCY MATRIX

**Document ID**: `DOC-V5-1-CROSS-PHASE-CONSISTENCY`  
**Phase**: V5.1 — Scientific Truth Ledger & Conflict Resolution  
**Primary Corridor**: `CORR-NH10-SIKKIM-KM48`  
**System Designation**: Smart India Hackathon (SIH) 2026 AI-Assisted Research and Decision-Support Prototype  
**Auditor**: PARVAT NETRA Autonomous Systems Engineering Swarm  
**Date**: September 21, 2026  

---

## 1. Executive Summary

This document presents the complete 9-point Claim Conflict Matrix codified in `data/manifests/scientific_truth_ledger.json`. Every conflict is evaluated with its earlier claim, later claim, authoritative artifact, and formal resolution.

---

## 2. Nine-Point Conflict Matrix

| Conflict ID | Dimension | Earlier Claim | Later Claim | Authoritative Artifact | Resolution Status |
|---|---|---|---|---|---|
| `CONF-01` | Event Count | 17 Canonical Historical Events | 52 Real Historical Events (V5.0 text) | `data/raw/historical_landslides_ner.csv` | **RESOLVED**: Authoritative count is strictly 17. '52' marked UNSUPPORTED. |
| `CONF-02` | Dataset Splits | 16 Train, 12 Val, 8 Test (36 real samples) | 41 Train, 11 Val, 11 Test | `data/features/features_all.csv` | **RESOLVED**: Authoritative splits are 16/12/8. 41/11/11 marked UNSUPPORTED. |
| `CONF-03` | Model Metrics | ROC-AUC: 1.000, PR-AUC: 1.000, CSI: 1.000 (GBDT holdout, N=8) | ROC-AUC: 0.81, PR-AUC: 0.74, CSI: 0.64 | `models/pahad_event_metrics.json` | **RESOLVED**: Authoritative GBDT metrics are from artifact. 0.81/0.74 marked UNSUPPORTED. |
| `CONF-04` | Warning Lead Time | 24.0h (GBDT) / 48.0h (BiLSTM) / 14.5h Median Ensemble | 4.2 hours median lead time | `docs/PAHAD_HISTORICAL_DEFENSE_SHEET.md` | **RESOLVED**: 4.2h was minimum lead time / demo formula. Authoritative median is 14.5h. 4.2h median marked UNSUPPORTED. |
| `CONF-05` | Active Production Model | Production BiLSTM V3 (33 features, 72h seq, weights SHA: `7cb82388...`) | Narrative text implying V4.5 serving in production | `models/pahad_lstm_v3_weights.pt` | **RESOLVED**: V3 remains the sole active production model. V4.5 is strictly OFFLINE_RESEARCH_ONLY. |
| `CONF-06` | Kinematic IoT Model | Not trained / pending borehole field data | Narrative text implying kinematic ML operational | `engine/kinematic_trigger_engine.py` | **RESOLVED**: Kinematic ML status is strictly NOT_TRAINED_DATA_PENDING. Zero weights exist. |
| `CONF-07` | CRI Feature Leakage | Feature 33 in V3 was CRI (causing target proxy leakage) | Feature 33 removed / replaced with physical telemetry | `models/pahad_lstm_v4_5_config.json` | **RESOLVED**: V4.4/V4.5 feature specification strictly excludes CRI. V3 maintains legacy frozen weights. |
| `CONF-08` | Physical Telemetry Reality | Bench HIL RS-485 simulation | 24h continuous live mountain telemetry streaming | `data/manifests/physical_deployment_manifest.json` | **RESOLVED**: Zero live mountain telemetry exists. Telemetry status is PHYSICAL_TELEMETRY_PENDING. |
| `CONF-09` | Government Authorization | Token 'BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026' in V4.9 prompt | Official GoI operational clearance claimed | `field_evidence/governance/` | **RESOLVED**: Token is an unverified simulated placeholder. Status is AUTHORIZATION_EVIDENCE_MISSING. |

---

## 3. Authoritative Conclusion

All 9 cross-phase scientific conflicts are 100% resolved without ambiguous placeholders or fabricated numbers. The system maintains complete internal consistency.
