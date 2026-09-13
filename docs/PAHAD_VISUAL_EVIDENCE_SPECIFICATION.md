# PARVAT NETRA / PAHAD AI — Visual Evidence Layer Specification

## Provenance-Controlled Visual & Remote-Sensing Evidence Architecture

```
Document ID     : PARVAT-DOC-HIST-VISUAL-01
Classification  : SIH-GRADE SCIENTIFIC & DISASTER MANAGEMENT STANDARD
System          : PARVAT NETRA / PAHAD AI
Layer           : Historical Recurrence & Event Observation Media
Security Status : PUBLIC DISPATCH DISABLED (ENABLE_PUBLIC_DISPATCH=0)
Siren Mode      : DRY RUN (SIREN_DRY_RUN=1)
GIGW Compliance : GIGW 3.0 Strict (Zero Unicode Emojis)
```

---

## 1. Executive Summary & Core Engineering Problem

The historical recurrence dataset in PAHAD AI links physical hill-slope telemetry, precipitation thresholds, and geological mechanics across chronic landslide corridors in the North Eastern Region (NER) of India. Previously, historical disaster entries included tabular metadata (precipitation, failure mechanism, coordinates, fatalities) but lacked a structured, provenance-controlled visual evidence layer.

### The Zero-Fabrication Mandate
Under SIH and National Disaster Management Authority (NDMA) standards:
- **NO FABRICATED IMAGERY**: Arbitrary stock photos, AI-generated synthetic collapse pictures, or broken image placeholders are strictly forbidden.
- **NO ARBITRARY EMBEDS**: Third-party video links or unauthorized streams (including mock YouTube links) are prohibited.
- **NON-MANDATORY MEDIA INVARIANT**: Photographic or video assets are **never mandatory** for historical event validity. If an event occurred in a remote sector without digital photographic archiving, the event remains 100% scientifically valid (`event_label=1`) grounded in Geological Survey of India (GSI) and National Remote Sensing Centre (NRSC) statutory reports.
- **EXPLICIT NOT_AVAILABLE STATUS**: Missing media is honestly displayed with status `NOT_AVAILABLE` and provenance `[NOT_AVAILABLE]`.

---

## 2. Evidence Taxonomy & Schema

Every visual or remote sensing record linked to a historical disaster or canonical event follows the `VisualEvidenceRecord` schema:

### 2.1 Evidence Types (`evidence_type`)
1. `BEFORE_AFTER_PHOTO`: Satellite/aerial comparative pairs (Cartosat, Sentinel-2, UAV) contrasting pre-failure hillslope geometry with post-failure runout.
2. `FIELD_PHOTO`: Ground-truth inspection photographs captured by Geological Survey of India (GSI) or District Disaster Management Authority (DDMA) survey teams.
3. `FIELD_VIDEO`: UAV drone reconnaissance or State Disaster Response Force (SDRF) aerial tactical survey footage.
4. `SATELLITE_IMAGERY`: Optical, multispectral, or false-color scar extraction maps (ISRO Bhuvan, Sentinel-2 MSI).
5. `INSAR_DEFORMATION`: Sentinel-1 C-band synthetic aperture radar interferometric Line-of-Sight (LOS) displacement profiles documenting pre-collapse slope creep.
6. `GEOTECHNICAL_SKETCH`: Engineering cross-sections, borehole inclinometer deflection logs, or structural geological sketches.

### 2.2 Verification Statuses (`verification_status`)
- `VERIFIED`: Formally authenticated by statutory authority report (GSI Special Report, NRSC Landslide Atlas, BRO Project Report) with documented provenance and cryptographic SHA-256 hash.
- `NOT_AVAILABLE`: Confirmed lack of digital photographic media in open archives; ground truth preserved through geological survey field logs.
- `PENDING`: Field team upload currently queued for review by the district geotechnical officer.
- `UNVERIFIED`: Crowdsourced citizen report or unauthenticated field log. **Strictly barred from auto-promotion to VERIFIED**.
- `DEMO_QUARANTINED`: Synthetic walkthrough sequence or demonstration mock. Quarantined from operational views and excluded from model training.

### 2.3 Record Schema
```json
{
  "evidence_id": "EVID-DIS-2022-NONEY-01",
  "event_id": "DIS-2022-NONEY",
  "evidence_type": "FIELD_PHOTO",
  "title": "Tupul Railway Yard Debris Avalanche Scar",
  "description": "Field photograph documenting translational slide along Disang shale/sandstone contact.",
  "source_reference": "GSI Disaster Investigation Report GSI-NER-MN-2022-004 Plate II-A",
  "source_url": null,
  "capture_date": "2022-07-01",
  "verification_status": "VERIFIED",
  "provenance": "[OFFICIAL_GOI]",
  "sha256_hash": "c35edc22deb0513356db707cb971e892111375c4262fa6e6430f7239fe4d4de4",
  "metadata": {
    "camera": "Survey Grade Optical",
    "archived_by": "GSI State Unit Manipur"
  }
}
```

---

## 3. Mandatory Safety & Operational Invariants

### Invariant 1: Non-Mandatory Media
An event record with empty `visual_evidence: []` or `verification_status: "NOT_AVAILABLE"` retains full operational status:
- `event_label = 1`
- Fully included in operational GBDT model training sets (`data/features/real_train.csv`, `real_val.csv`, `real_test.csv`).
- Included in spatial recurrence interval calculations and return period curves.

### Invariant 2: Anti-Fabrication & Media Quarantine
- All synthetic demonstration samples are quarantined with status `DEMO_QUARANTINED` and provenance tag `[DEMO]`.
- Operational API queries reject or filter quarantined records unless `PAHAD_DEMO_MODE=1`.
- Production training pipelines discard any samples with provenance `[DEMO]` or status `DEMO_QUARANTINED`.

### Invariant 3: Zero Auto-Promotion of Submissions
- When an external field team or citizen submits evidence via `POST /api/pahad/history/evidence/submit`, even if the payload maliciously claims `verification_status: "VERIFIED"`, the system automatically demotes it to `UNVERIFIED` and tags it `[UNVERIFIED_FIELD]`.
- Only requests authenticated with statutory headers (`X-Authority-Role: DISTRICT_AUTHORITY|STATE_AUTHORITY|ADMIN` or authenticated `X-Authority-Token`) can promote submissions to `VERIFIED`.

### Invariant 4: Cryptographic Traceability
- Every verified statutory record includes a 64-character SHA-256 hash computed from the authenticated source reference or source document binary.
- This provides tamper-evident validation for historical ground truth.

---

## 4. Disaster Inventory & Evidence Coverage

The platform catalogues 6 major catastrophic disasters in the North Eastern Region alongside 17 canonical training events:

| Disaster ID | Name & Location | State | Date | Verified Media Assets | NOT_AVAILABLE Count | Primary Statutory Source |
|---|---|---|---|:---:|:---:|---|
| `DIS-2022-NONEY` | Tupul Railway Yard Landslide | Manipur | 2022-06-29 | 4 | 0 | GSI-NER-MN-2022-004 |
| `DIS-2024-AIZAWL` | Cyclone Remal Quarry Collapses | Mizoram | 2024-05-28 | 3 | 0 | GSI-NER-MZ-2024-019 |
| `DIS-2025-MIZORAM` | Statewide Monsoon Deluge | Mizoram | 2025-05-30 | 2 | 0 | NRSC-LSA-MZ-2025-BATCH |
| `DIS-2024-NH10` | 29th Mile Teesta Scour | Sikkim | 2024-07-02 | 3 | 0 | GSI-NER-SK-2024-048 |
| `DIS-2022-DIMAHASAO`| Jatinga-Lumpur Railway Collapse | Assam | 2022-05-16 | 2 | 0 | GSI-NER-AS-2022-077 |
| `DIS-2025-SIKKIM` | South Sikkim Highway Slumps | Sikkim | 2025-06-18 | 2 | 0 | BRO Project Swastik |

### Canonical Events Inventory (`canonical_event_inventory.json`)
- **Total Canonical Events**: 17 events (`EV-01` through `EV-17`) across 8 NER states.
- **Verified Visual Evidence**: 19 records.
- **Explicit NOT_AVAILABLE Media**: 3 events (`EV-13`, `EV-15`, `EV-17`) documenting remote historical slips where digital photography was not archived.
- **Pending Field Validations**: 2 records (`EV-07`, `EV-11`).

---

## 5. REST API Interface

### 5.1 Catalog Retrieval
```http
GET /api/pahad/history/catalog
```
**Response Summary Block**:
```json
{
  "status": "SUCCESS",
  "disasters_count": 6,
  "visual_evidence_summary": {
    "total_evidence_items": 16,
    "verified_count": 16,
    "not_available_count": 0,
    "pending_count": 0,
    "unverified_count": 0
  }
}
```

### 5.2 Event Evidence Inspection
```http
GET /api/pahad/history/events/<event_id>/evidence?status=VERIFIED&type=FIELD_PHOTO
```
**Parameters**:
- `status` *(optional)*: `VERIFIED`, `NOT_AVAILABLE`, `PENDING`, `UNVERIFIED`
- `type` *(optional)*: `BEFORE_AFTER_PHOTO`, `FIELD_PHOTO`, `FIELD_VIDEO`, `SATELLITE_IMAGERY`, `INSAR_DEFORMATION`, `GEOTECHNICAL_SKETCH`

### 5.3 Field Team Evidence Submission
```http
POST /api/pahad/history/evidence/submit
Content-Type: application/json
X-Authority-Role: PUBLIC
```
```json
{
  "event_id": "DIS-2024-NH10",
  "evidence": {
    "evidence_type": "FIELD_PHOTO",
    "description": "Tension crack widening along KM 48.2 outer road shoulder",
    "source_url": "https://field.example.org/photo123.jpg",
    "capture_date": "2026-09-11"
  }
}
```
**Enforcement Result**: Returns HTTP 201 with `verification_status: "UNVERIFIED"` and provenance `"[UNVERIFIED_FIELD]"`.

---

## 6. Frontend UI Rendering & GIGW 3.0 Compliance

1. **Clean Operational Styling**:
   - High-contrast obsidian slate styling (`bg-slate-50 dark:bg-slate-950`).
   - Monospace cryptographic hashes (`font-mono text-[9px]`).
   - Clean status badges:
     - `VERIFIED`: Emerald badge (`border-emerald-600 bg-emerald-50 text-emerald-700`)
     - `NOT_AVAILABLE`: Neutral dashed slate box (`border-dashed border-slate-400 bg-slate-100 text-slate-600`)
     - `PENDING`: Amber badge (`border-amber-500 bg-amber-50 text-amber-700`)
     - `UNVERIFIED`: Orange badge (`border-orange-500 bg-orange-50 text-orange-700`)
     - `DEMO_QUARANTINED`: Purple badge (`border-purple-500 bg-purple-50 text-purple-700`)
2. **Zero Unicode Emojis**:
   - In accordance with GIGW 3.0 government accessibility standards, unicode pictographs/emojis are strictly barred from UI templates, modals, and backend logs. Enforced by automated test `test_08_verify_zero_emojis_in_templates_and_modal`.
