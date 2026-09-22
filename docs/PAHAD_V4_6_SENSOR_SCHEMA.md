# PARVAT NETRA / PAHAD AI — PHASE V4.6
# Canonical In-Situ Sensor Telemetry Schema & Corridor Registry

**Document Version**: 1.0.0  
**Schema Artifact**: `data/processed/live_sensor_schema.json`  
**Registry Artifact**: `data/processed/corridor_sensor_registry.json`  
**Standard**: JSON Schema Draft 2020-12  

---

## 1. Schema Overview

The canonical in-situ telemetry observation schema governs all measurements entering the PARVAT NETRA platform from field sensors, edge gateways, bench simulators, and reanalysis replay streams.

### Mandatory Field Specifications

| Field Name | Type | Allowed Values / Range | Description |
| :--- | :--- | :--- | :--- |
| `observation_id` | `string` | Unique UUID or deterministic tag | Unique identifier for observation instance |
| `sensor_id` | `string` | e.g. `PIEZO-NH10-KM48-01` | Identifier of physical instrument node |
| `corridor_id` | `string` | e.g. `CORR-NH10-SIKKIM-KM48` | Monitored highway/transit corridor |
| `site_id` | `string` | e.g. `SITE-NH10-KM48` | Monitored slope section / borehole station |
| `sensor_type` | `string` | `PIEZOMETER`, `INCLINOMETER`, `TILTMETER`, `RAIN_GAUGE`, `GATEWAY` | Instrument engineering class |
| `timestamp_utc` | `string` | ISO 8601 UTC string | Measurement capture timestamp at sensor |
| `value` | `number` | Physical engineering limits | Primary calibrated observation value |
| `unit` | `string` | `kPa`, `mm`, `deg`, `mm/h`, `V`, `dBm`, `C` | Physical engineering unit |
| `quality` | `string` | `GOOD`, `DEGRADED`, `BAD`, `UNKNOWN` | Data quality indicator |
| `source` | `string` | `PHYSICAL_SENSOR`, `BENCH_SIMULATOR`, `REPLAY`, `SYNTHETIC` | Physical origin of packet |
| `provenance` | `string` | `LIVE`, `SIMULATED`, `HISTORICAL`, `TEST`, `BENCH` | Trustworthiness badge |
| `status` | `string` | `LIVE`, `CACHED`, `SIMULATED`, `DERIVED`, `UNAVAILABLE`, `INVALID`, `STALE` | Operational state |
| `sequence_number` | `integer` | $\ge 0$ | Monotonic incrementing packet index |
| `received_at` | `string` | ISO 8601 UTC string | Server ingestion arrival timestamp |
| `gateway_id` | `string` | e.g. `GW-NH10-KM48-01` | Edge concentrator forwarding the packet |
| `firmware_version`| `string` | SemVer string | Running firmware on sensor/node |

---

## 2. Pilot Corridor Registry: `CORR-NH10-SIKKIM-KM48`

The authoritative sensor registry file `data/processed/corridor_sensor_registry.json` defines the instrumentation blueprint for the pilot landslide corridor along the NH-10 highway:

```json
{
  "corridor_id": "CORR-NH10-SIKKIM-KM48",
  "corridor_name": "NH-10 Rangpo–Singtam Geological Corridor, Sikkim",
  "highway_code": "NH-10",
  "chainage_km": 48.2,
  "state": "Sikkim",
  "district": "Pakyong",
  "latitude": 27.2023,
  "longitude": 88.5147,
  "elevation_msl": 620.0,
  "physical_status": "BENCH_VALIDATED",
  "telemetry_status": "PHYSICAL_TELEMETRY_PENDING",
  "field_deployment_pending": true
}
```

### Sensor Node Roster

1. **`PIEZO-NH10-KM48-01`**:
   - Depth: $12.0\text{ m}$ (in-casing)
   - Parameter: Pore water pressure ($0.0$ to $50.0\text{ kPa}$ nominal, $-50.0$ to $500.0\text{ kPa}$ max)
   - Status: `BENCH_VALIDATED` | `PHYSICAL_TELEMETRY_PENDING`

2. **`INCL-NH10-KM48-01`**:
   - Depth: $15.0\text{ m}$ (borehole shear zone)
   - Parameter: Lateral shear displacement ($-100.0$ to $100.0\text{ mm}$)
   - Status: `BENCH_VALIDATED` | `PHYSICAL_TELEMETRY_PENDING`

3. **`TILT-NH10-KM48-01`**:
   - Mount: Surface bedrock plate anchor
   - Parameter: Biaxial angular deflection ($-45.0^\circ$ to $45.0^\circ$)
   - Status: `BENCH_VALIDATED` | `PHYSICAL_TELEMETRY_PENDING`

4. **`RAIN-NH10-KM48-01`**:
   - Mount: Surface meteorology mast
   - Parameter: Tipping bucket rainfall rate ($0.0$ to $250.0\text{ mm/h}$)
   - Status: `BENCH_VALIDATED` | `PHYSICAL_TELEMETRY_PENDING`

5. **`GW-NH10-KM48-01`**:
   - Mount: Solar mast with dual battery pack
   - Parameter: System battery voltage ($9.0$ to $15.0\text{ V}$)
   - Status: `BENCH_VALIDATED` | `PHYSICAL_TELEMETRY_PENDING`

---

## 3. Freshness Threshold Configuration

Freshness is evaluated dynamically using elapsed time since the last accepted observation:
- **`PIEZOMETER`**: $900\text{ s}$ ($15\text{ min}$)
- **`INCLINOMETER`**: $900\text{ s}$ ($15\text{ min}$)
- **`TILTMETER`**: $900\text{ s}$ ($15\text{ min}$)
- **`RAIN_GAUGE`**: $900\text{ s}$ ($15\text{ min}$)
- **`GATEWAY`**: $300\text{ s}$ ($5\text{ min}$)

If elapsed time exceeds $2\times$ the threshold, the sensor transitions from `STALE` to `UNAVAILABLE`. For uninstalled physical nodes, the initial state is strictly `UNAVAILABLE` with reason `PHYSICAL_TELEMETRY_PENDING`.
