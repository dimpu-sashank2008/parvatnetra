# PARVAT NETRA • PAHAD AI — PHASE V5.3
# DATASET VERSIONING & CRYPTOGRAPHIC MANIFEST REPORT

**Phase**: V5.3 — External Source Evidence Verification & Canonical Event Forensics  
**Status**: VERIFIED & AUDITED  
**Corridor**: CORR-NH10-SIKKIM-KM48 & NER Regional Network  
**Overall Verdict**: `V5_3_EVIDENCE_VERIFIED`  
**Date**: September 2026  

---

## 1. Executive Summary

This report establishes the dataset versioning hierarchy, cryptographic provenance hashes, and immutable artifact registry for Phase V5.3 of PARVAT NETRA / PAHAD AI.

Scientific reproducibility requires that every model prediction, training run, or audit claim can be traced back to the exact byte-level state of the dataset used.
- **Dataset Version**: `v5.3.0`
- **Manifest File**: `data/processed/v5_3_dataset_manifest.json`
- **Hash Algorithm**: SHA-256 (64 hex characters)
- **Historical Manifest Preservation**: 100% (V5.0, V5.1, V5.2 manifests preserved unchanged)
- **Cryptographic Audit Status**: All files match manifest hashes bit-for-bit

---

## 2. Phase V5.3 Artifact Cryptographic Manifest

The following immutable files constitute the Phase V5.3 evidence and dataset release:

| Artifact Path | Record Count / Content | SHA-256 Hash |
|:---|:---:|:---|
| `data/processed/v5_3_event_evidence_registry.json` | 59 Evidence Docs | `110fa547dca9c94f202b62f83b57e1952ae814b5e6b54b0260e6becceddf6a2f` |
| `data/processed/canonical_event_inventory_v5_3.json` | 42 Events, 20 Controls | `183e76ccd42c94c6fc27a6a2432412cb433c4086b1dd4b93baf6abfbd7f43e86` |
| `data/processed/v5_3_event_lineage.json` | 42 Events, 1 Duplicate | `76671bf1e0ca1a5ffe8dc8390a700995b3740a4b54f7fbc5652bd7e890244813` |
| `data/processed/v5_3_dataset_manifest.json` | Manifest & Metadata | `ab3b1b21b288a315e9ce13a157fc4b0e8dbeef0320478059b4a723647edf29c1` |
| `reports/pahad_v5_3_result.json` | Master Audit Verdict | `adf198595bfa00737b8a27c5b1139620267b81cdee96bbdf838cea188751672f` |

---

## 3. Historical Dataset Immutability

Historical datasets from prior phases are preserved to guarantee backwards reproducibility:
- `data/raw/historical_landslides_ner.csv`
- `data/manifests/canonical_event_lineage.json`
- `data/processed/canonical_event_inventory_v5_2.json`
- `data/processed/v5_2_dataset_manifest.json`

No modifications or deletions were performed on historical baseline files. New canonical forensic layers are versioned strictly under `_v5_3` suffixes.

---

## 4. Automated Verification Results

Assertions in `tests/test_v5_3_dataset_versioning.py` verify that:
- `test_historical_datasets_exist_unmodified`: PASSED
- `test_v5_3_versioned_files_exist`: PASSED
- `test_v5_3_manifest_hashes_match_files`: PASSED
