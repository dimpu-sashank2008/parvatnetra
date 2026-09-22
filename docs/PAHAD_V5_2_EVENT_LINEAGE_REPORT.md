# PARVAT NETRA / PAHAD AI — PHASE V5.2
# EVENT LINEAGE & CRYPTOGRAPHIC PROVENANCE REPORT

**Document ID:** `PN-DOC-V5.2-LINEAGE`  
**Phase:** `V5.2`  
**Status:** `VERIFIED & TRACKED`

---

## 1. Executive Summary
To achieve full traceability from raw government bulletins to ML feature vectors, Phase V5.2 binds every landslide record to a dual SHA-256 cryptographic lineage hash.

---

## 2. Lineage Architecture

### 2.1 Raw Record Hash (`raw_record_hash`)
Calculated from the immutable primary source documentation attributes:
$$\text{raw\_record\_hash} = \text{SHA256}(\text{event\_id} \mathbin{\Vert} \text{timestamp} \mathbin{\Vert} \text{lat} \mathbin{\Vert} \text{lon} \mathbin{\Vert} \text{source} \mathbin{\Vert} \text{source\_reference})$$

### 2.2 Canonical Hash (`canonical_hash`)
Calculated from the normalized administrative and verification record:
$$\text{canonical\_hash} = \text{SHA256}(\text{event\_id} \mathbin{\Vert} \text{timestamp} \mathbin{\Vert} \text{lat} \mathbin{\Vert} \text{lon} \mathbin{\Vert} \text{state} \mathbin{\Vert} \text{district} \mathbin{\Vert} \text{verification\_status})$$

---

## 3. Persistent Manifests
The canonical lineage ledger is permanently tracked in:
- `data/manifests/canonical_event_lineage.json` (Schema version: 5.2.0)
- `data/manifests/v5_2_external_data_manifest.json`
- `data/manifests/scientific_truth_ledger.json`

Every canonical record displays the provenance badge `[HISTORICAL]` and is strictly isolated from demo and synthetic datasets.
