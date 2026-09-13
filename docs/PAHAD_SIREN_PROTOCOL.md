# PARVAT NETRA / PAHAD AI — PHASE 3.4
## Tactical Siren & Acoustic Alert Controller Protocol

**Document Reference**: `PAHAD_SIREN_PROTOCOL.md`  
**Problem Statement ID**: SIH 26001 (Smart India Hackathon)  
**Safety Classification**: Fail-Safe Hardware Actuation & Audit Trail Standard

---

## 1. Safety Core Philosophy & Fail-Safe Invariants

High-decibel sirens ($> 110\,\text{dB}$) deployed in Himalayan mountain settlements can induce severe public panic, traffic stampedes, and accidental road blockages if triggered by software glitches, network noise, or developmental testing.

The `SirenController` enforces three mandatory architectural invariants:
1. **Suppression by Default**: `SIREN_HARDWARE_ENABLED` is `false` by default. Physical siren activation is disabled in software.
2. **Dry Run Enforcement**: When `SIREN_HARDWARE_ENABLED=false`, all activation and test triggers execute in `dry_run=True` mode, recording telemetry without driving hardware relays.
3. **Dedicated Test Event Schema**: Operator testing generates `SIREN_TEST_EVENT` audit entries rather than operational emergency alerts.

---

## 2. Siren Controller State Machine

```
               [ INITIALIZATION ]
                       |
                       v
                 +------------+
  +------------> |   ARMED    | <------------+
  |              +------------+              |
  |                    |                     |
  | (disarm())         | (threshold breach)  | (timeout / clear)
  |                    v                     |
  |              +------------+              |
  |              |   ACTIVE   | -------------+
  |              +------------+
  |                    ^
  | (arm())            | (test())
  |                    v
+------------+   +------------+
|  DISARMED  |   |  TESTING   |
+------------+   +------------+
```

### States:
- **`ARMED`**: Gateway is actively monitoring sensor thresholds and prepared to evaluate emergency conditions.
- **`DISARMED`**: Siren is deliberately suppressed by incident commanders during road maintenance or controlled rock blasting.
- **`ACTIVE`**: Threshold breach has occurred; siren acoustic pattern is firing (or simulated in dry-run).
- **`TESTING`**: 5-second diagnostic audit run without emergency sound.

---

## 3. Warning Levels & Acoustic Signatures

| Warning Tier | Trigger Criteria | Acoustic Profile | Intended Response |
|---|---|---|---|
| `WATCH` | 1 watch threshold exceeded. | Intermittent chime (5s on, 30s off). | Local beat engineers inspect slope toe. |
| `WARNING` | 2 warnings OR anomaly score $\ge 0.40$. | Rising dual-tone warble (15s on, 15s off). | Traffic halted at checkposts; BRO mobilized. |
| `CRITICAL` | 1 critical limit OR anomaly score $\ge 0.80$. | Continuous 120 dB wail with strobe. | Immediate civilian evacuation to designated shelters. |

---

## 4. Local Audit Trail

Every siren event is persisted into the SQLite `edge_alerts` table:
```sql
CREATE TABLE edge_alerts (
    alert_id TEXT PRIMARY KEY,
    severity TEXT NOT NULL,
    state TEXT NOT NULL,
    anomaly_score REAL NOT NULL,
    reasons TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    gateway_id TEXT NOT NULL,
    dry_run INTEGER NOT NULL,
    acknowledged INTEGER DEFAULT 0
);
```

### Audit Invariant:
All test events include `operator`, `requested_by`, `activation_type="TEST"`, and `dry_run=1`. Remote unauthorized activation is blocked by the API layer.
