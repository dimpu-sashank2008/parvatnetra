# PARVAT NETRA / PAHAD AI — PHASE 3.4
## Bluetooth Low Energy (BLE 5.3) Alert Bridge Protocol

**Document Reference**: `PAHAD_BLE_PROTOCOL.md`  
**Problem Statement ID**: SIH 26001 (Smart India Hackathon)  
**Security Standard**: Authorized Device Allowlist & HMAC Signed Telemetry

---

## 1. Scope & Honest Platform Disclaimer

> [!WARNING]
> **CRITICAL ARCHITECTURAL BOUNDARY**:
> Bluetooth Low Energy (BLE) operates on a point-to-point physical connection model with a transmission range of $10 - 80\,\text{meters}$ depending on hillslope terrain and transceiver antenna gain.
> 
> **BLE is NOT a universal mass public emergency broadcast system.**
> Smartphones cannot arbitrarily receive unsolicited BLE alert broadcasts without active app foregrounding and hardware pairing.
> 
> In PARVAT NETRA, BLE is strictly utilized for:
> 1. Interfacing with **paired local hardware** (e.g. handheld field test units, gateway relay adapters).
> 2. Connecting with **roadside variable-message signs (VMS)** along NH-10.
> 3. Mobile diagnostic edge testing via the Flutter `EdgeTestScreen`.
> 
> Mass public civilian alerting is governed exclusively by **OASIS CAP v1.2 XML cell broadcast and DDMA/SDMA channels**.

---

## 2. Device Allowlist Security Architecture

To prevent malicious spoofing of evacuation orders by unauthorized radio transmitters in border corridors, the gateway maintains an explicit device allowlist:
```python
AUTHORIZED_ALLOWLIST = {
    "DEV-BRO-FIELD-01",
    "DEV-SDRF-COMMAND-02",
    "DEV-ROAD-BEACON-LIKHU",
    "MOBILE-TACTICAL-GATEWAY"
}
```
Any connection request from a device UUID not present in the allowlist is rejected immediately with `REJECTED_UNAUTHORIZED` status.

---

## 3. Alert Packet Payload & HMAC Signature

When an emergency alert is triggered, the gateway dispatches a compact signed payload:

```json
{
  "alert_id": "PN-ALERT-001",
  "severity": "CRITICAL",
  "timestamp": "2026-09-09T14:35:00Z",
  "gateway_id": "GW-01",
  "sequence": 42,
  "checksum": "a8f3b9c24e107d81",
  "disclaimer": "Local device point-to-point alert only. Official warnings issued via CAP/SDMA."
}
```

### HMAC Signature Computation:
```python
msg = f"{alert_id}:{severity}:{timestamp}:{sequence}:{gateway_id}".encode("utf-8")
checksum = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:16]
```
The receiving device independently recomputes the HMAC digest over the received fields using its provisioned local secret. If the checksum mismatches or the monotonic sequence number has already been seen (replay attempt), the frame is discarded.

---

## 4. Test Event Mode (`PN-TEST-001`)

For field testing via mobile or dashboard:
- The default payload identifier is `PN-TEST-001`.
- Severity is set to `VERY_HIGH`.
- Action is tagged as `SIREN_TEST`.
- Hardware buzzer actuation remains disabled unless physical test override is toggled by an authorized operator.
