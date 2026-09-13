# PARVAT NETRA / PAHAD AI — PHASE 6A
## Bluetooth Low Energy (BLE) Capability Boundaries & Maintenance Protocol

**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**Document**: `docs/PHASE6A_BLE_CAPABILITY.md`  
**Standard**: SIH 26001 / Phase 6A Wireless Architecture  
**Status**: APPROVED POLICY DOCUMENT  

---

## 1. Architectural Scope & Explicit Invariants

### 1.1 Authorized Scope of BLE
Bluetooth Low Energy (BLE 5.0 / 5.2) within the PARVAT NETRA ecosystem is designed and authorized **strictly for localized point-to-point field technician maintenance**:
- In-situ sensor diagnostic inspection.
- Borehole transducer zero-offset calibration.
- Battery and solar charging telemetry verification.
- Firmware Over-The-Air (FOTA) updates for edge gateways.
- Local buffer diagnostic retrieval when physical backhaul is severed.

### 1.2 Prohibited Anti-Patterns (What BLE Is NOT)
- **BLE is NOT a Mass Public Warning Broadcast System**:
  - BLE advertising packets cannot reliably penetrate vehicle windshields, heavy rainfall, or mountain rock formations beyond $15\text{--}30\text{ meters}$.
  - Regional public emergency alerts are delivered exclusively through:
    1. **OASIS CAP v1.2 Cell Broadcast / SMS** (National Disaster Management Authority - NDMA / Sachet Portal).
    2. **Local Autonomous High-Decibel Acoustic Sirens** ($110\text{ dB}$ dual-tone electro-mechanical horns positioned at chokepoints).
    3. **Sub-GHz LoRaWAN Broadcasts** ($865\text{--}867\text{ MHz}$) across mountain corridor repeaters.
- **BLE is NOT a Continuous Sensor Telemetry Backhaul**:
  - Continuous BLE streaming rapidly depletes off-grid battery packs. Transducers stream via low-power LoRaWAN or RS-485.

---

## 2. Physical Propagation Limitations in Himalayan Terrain

| Factor | Technical Impact on BLE (2.4 GHz) | Mitigation / Protocol Rule |
| :--- | :--- | :--- |
| **Heavy Monsoon Rain ($>50\text{ mm/hr}$)** | High absorption by water droplets ($>12\text{ dB/100m}$ attenuation at $2.4\text{ GHz}$). | Restrict technician pairing standoff distance to $<5\text{ meters}$. |
| **Dense Pine / Rhododendron Foliage** | Foliage path loss and multipath fading. | External dipole antennas mounted on mast above understory brush. |
| **Rock Bluffs & Debris Slopes** | Total RF shadowing behind protruding cliffs. | Technicians must establish direct line-of-sight to the gateway node. |
| **Subsurface Transducers** | Soil and rock block $2.4\text{ GHz}$ completely ($>40\text{ dB/m}$ loss). | Downhole sensors connect via armored shielded cable to surface junction box; BLE transceiver resides in surface enclosure. |

---

## 3. BLE GATT Service Architecture

The Edge Gateway and Transceiver Nodes expose a single standardized custom BLE Service:

### Service UUID: `18507e1e-0001-4b2a-89a1-000000000001` (PARVAT_NETRA_EDGE_SVC)

| Characteristic UUID | Type | Properties | Description |
| :--- | :---: | :---: | :--- |
| `...-0002` | `DeviceInfo` | Read | Device ID, firmware version, hardware serial, uptime. |
| `...-0003` | `TelemetrySnapshot` | Read / Notify | Current real-time sensor measurements, battery %, RSSI. |
| `...-0004` | `CalibrationControl` | Write | Set zero offset and scale factors with auth challenge. |
| `...-0005` | `DiagnosticLog` | Read | Retrieve last 50 error events and drop statistics. |
| `...-0006` | `SirenSafetyTest` | Write | Executes momentary dry-run siren test (physical audio suppressed). |

---

## 4. Security, Pairing & Access Control

To prevent unauthorized tampering by unauthorized road users or malicious actors:
1. **Passkey Pairing**: BLE connections require standard 6-digit numeric passkey authentication generated dynamically or matching the tamper-evident physical QR code inside the locked gateway enclosure.
2. **Session Inactivity Timeout**: The BLE radio automatically terminates active pairing after **15 minutes of inactivity**.
3. **Advertising Sleep Mode**: To eliminate RF emissions and conserve power, BLE advertising is dormant until a physical magnetic reed switch on the enclosure is triggered with a technician maintenance wand.
4. **Non-Elevated Siren Control**: Siren triggers executed over BLE default strictly to `dry_run = True` and generate a `SIREN_TEST_EVENT` without audible relay contact closure unless accompanied by a verified cryptographically signed authorization token.
