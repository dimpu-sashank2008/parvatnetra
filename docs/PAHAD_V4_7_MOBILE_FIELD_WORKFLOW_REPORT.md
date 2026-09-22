# PARVAT NETRA / PAHAD AI — PHASE V4.7
# Mobile Field Workflow, Offline Protocol & Sensor Commissioning Application Report

**Document Version**: 1.0.0  
**Phase**: V4.7 Engineering Commissioning  
**System Status**: BENCH_READY_FIELD_EVIDENCE_PENDING  
**Target User Roles**: SDRF Field Engineers, BRO Project Swastik Inspectors, SSDMA Geotechnical Officers  
**Platform**: Cross-Platform Flutter Mobile / Progressive Web Application (PWA)  

---

## 1. Field Operational Context: Rugged Himalayan Corridors

Field engineers deploying geotechnical sensors along Himalayan transport corridors (such as NH-10 Singtam–Rangpo or NH-717A) face severe operational constraints:
- Zero cellular coverage in steep gorges and rockfall chutes.
- Torrential monsoon precipitation and high humidity.
- Hazardous slope conditions requiring rapid, tamper-proof data capture.

The PARVAT NETRA Mobile Field Application is engineered with an **Offline-First Architecture** ensuring 100% functional autonomy without active network connectivity.

---

## 2. 6-Step Standard Operating Procedure (SOP) for Field Commissioning

```
  [Step 1: Hardware Scan]      ---> Barcode / QR scan of sensor serial number
            |                       (Checks against registry; blocks placeholders)
            v
  [Step 2: Calibration Check]  ---> Verify NABL certificate and expiration date
            |
            v
  [Step 3: Downhole Logging]   ---> Record depth (m), casing orientation, soil profile
            |
            v
  [Step 4: Visual Evidence]    ---> Capture 3 geo-tagged high-res photos:
            |                       1. Collar head & casing
            |                       2. Downhole sensor placement
            |                       3. Solar mast & lightning arrestor
            v
  [Step 5: Handheld RF Test]   ---> Ingest >= 10 packets via portable LoRa wand
            |                       (Verifies CRC16, RSSI >= -115 dBm, battery >= 11V)
            v
  [Step 6: Tri-Party Sign-Off] ---> Digital signatures: Field Engineer, BRO Swastik, SSDMA
```

---

## 3. Offline Data Integrity & Storage Protocol

1. **Local SQLite / Encrypted Keystore**:
   - All captured telemetry samples, photos, borehole survey coordinates, and operator logs are written immediately to an AES-256 encrypted local SQLite database.
   - Images are automatically downsampled to $1920\times1080$ JPEG with embedded EXIF GPS tags and SHA-256 digests calculated prior to local storage.
2. **Deterministic UUIDv4 Transition Bundles**:
   - Each completed commissioning workflow generates a self-contained, signed JSON bundle containing the state transition request, evidence manifests, and operator credentials.
3. **Store-and-Forward Synchronization**:
   - When the field unit re-enters cellular coverage (or connects to the basecamp VSAT terminal), the application executes a mutual-TLS sync with the backend endpoint:
     $$\textbf{POST } \texttt{/api/telemetry/evidence}$$
     $$\textbf{POST } \texttt{/api/telemetry/commission}$$
   - The backend validates the package SHA-256 bitstream before committing transitions into the immutable PostgreSQL/PostGIS database.

---

## 4. Hardware Identity Validation at Edge

To eliminate human error or deceptive labeling:
- The mobile app integrates regex validation against known manufacturer formats (`GK-4500AL-[0-9]{4}`, `RST-MEMS-[0-9]{4}`, `ENC-92M-[0-9]{4}`).
- The app strictly disables the "Proceed" action if an operator inputs a placeholder string (`TBD`, `UNKNOWN`, `NONE`, `PENDING`, `""`).
- If an unknown serial number is encountered, the app flags the instrument as `STATE_UNVERIFIED_IDENTITY` and demands administrative override with supervisory authorization.

---

## 5. Security & Multi-Party Cryptographic Sign-Off

In compliance with life-critical early warning regulations:
- Software-only commissioning is strictly rejected by the backend.
- The transition to `FIELD_COMMISSIONED` requires an authorization key adhering to authorized inter-agency protocols (e.g., `BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026`).
- All transition records record the operator's digital badge ID, GPS lock coordinates, and UTC timestamp to maintain an unbroken audit trail.
