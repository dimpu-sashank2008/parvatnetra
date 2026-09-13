# PARVAT NETRA / PAHAD AI — PHASE 6D
## In-Situ Sensor Site Commissioning Standard Operating Procedure (SOP)

**Document Reference**: `docs/PHASE6D_SITE_COMMISSIONING.md`  
**Classification**: Engineering Standard Operating Procedure  
**Standard**: SIH 26001 / NDMA Himalayan Geotechnical Early Warning Guidelines  
**Author**: Geotechnical Field Operations & Metrology Team  
**Date**: September 2026  

---

## 1. 7-Step Field Commissioning Workflow

Field technicians must execute the 7 stages sequentially. Bypassing any step prevents transition to `ACTIVE` status.

```
[1. REGISTER] -> [2. LOCATE] -> [3. INSTALL] -> [4. CALIBRATE] -> [5. CONNECT] -> [6. TEST] -> [7. ACCEPT]
```

### Stage 1: REGISTER
- Verify physical barcode / QR code and equipment serial number against corridor staging inventory.
- Ensure device record exists in `physical_sensor_inventory` in `STATUS_PLANNED` or `STATUS_DELIVERED`.

### Stage 2: LOCATE
- Acquire multi-constellation GNSS (GPS/NavIC) fix with survey-grade receiver.
- Required accuracy: Horizontal error $\le 10.0$ m (strict maximum threshold 25.0 m).
- Record latitude, longitude, elevation (m ASL), and terrain aspect.

### Stage 3: INSTALL
- Borehole grouting or surface mechanical anchoring according to geotechnical specification.
- Capture at least one high-resolution digital photograph of the anchor/collar assembly.
- Record photo SHA-256 hash in commissioning evidence.

### Stage 4: CALIBRATE
- Perform in-situ zero-reading and span verification against portable calibrator.
- Bind accredited ISO/IEC 17025 metrology calibration certificate number.
- Record polynomial constants ($A, B, C$) into `SensorCalibration` store.

### Stage 5: CONNECT
- Pair node transceiver with designated corridor LoRa concentrator gateway.
- Measure and record RSSI ($\ge -118$ dBm) and SNR ($\ge -12$ dB).

### Stage 6: TEST
- Trigger live transmission of compact 18-byte binary frame.
- Confirm reception at edge gateway with valid CRC-16-CCITT and canonical JSON schema decode.

### Stage 7: ACCEPT
- Metrology engineer and field supervisor dual sign-off.
- Deterministic SHA-256 digital signature generated.
- Sensor asset transitioned from `CONNECTED` to `ACTIVE` in `SENSOR_INVENTORY`.

---

## 2. Mobile Offline Sync Architecture

In remote Himalayan gorges without cellular reception:
1. Field technician records stages 1–7 locally on the PARVAT NETRA Flutter mobile client.
2. Evidence records (GPS, notes, photo hashes, signatures) are queued in SQLite/Hive local storage.
3. Upon returning to BRO base camp or Wi-Fi hotspot, client issues `POST /api/field/evidence/sync`.
4. Endpoint processes records idempotently, validating stage progressions and updating asset statuses.
