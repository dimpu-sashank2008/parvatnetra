# PARVAT NETRA / PAHAD AI — PHASE 8: NOTIFICATION REPORT
**Multi-Channel Emergency Notification Orchestration, Subscription Registry, and Acknowledgement Tracking**
*Pilot Corridor: NH-10 KM 48 (29th Mile, Pakyong District, Sikkim)*
*Date: 2026-09-11 | Authority: Emergency Operations Center & CDAC Telecom Gateway*

---

## 1. Multi-Platform Subscription Registry (Checkpoint 8-07)
The subscription registry securely manages registered devices within the Himalayan pilot corridor without storing invasive personal identifiable information (PII):
- **Schema Fields**: `user_id`, `device_id`, `platform`, `notification_endpoint`, `language`, `latitude`, `longitude`, `subscription_timestamp`, `last_seen`, `consent_state`, `geofence_state`, `role`.
- **Supported Platforms**:
  - `WEB_PUSH`: Desktop and mobile browsers (VAPID Push API).
  - `MOBILE_PUSH`: Native Flutter mobile field and citizen applications.
  - `SMS`: Cryptographically hashed carrier mobile targets.
  - `LOCAL_EDGE`: LoRaWAN concentrators & village edge acoustic sirens.

Consent is mandatory (`consent_state = 'CONSENTED'`). Users who revoke consent are strictly excluded from automated notification queries.

---

## 2. Multi-Channel Fan-Out & Independent Delivery States (Checkpoint 8-13)
When an emergency incident is authorized by the statutory authority, the EOC orchestrator fans out the warning across five parallel delivery channels. Each channel reports its operational status independently:

```
                  +--------------------------------+
                  |    AUTHORIZED EOC INCIDENT     |
                  +---------------+----------------+
                                  |
         +------------+-----------+-----------+------------+
         |            |           |           |            |
         v            v           v           v            v
    +---------+  +---------+  +-------+   +-------+   +---------+
    | WEB     |  | MOBILE  |  |  SMS  |   |  CAP  |   | SIREN   |
    | Push    |  | Flutter |  | CDAC  |   | SACHET|   | Relay   |
    +----+----+  +----+----+  +---+---+   +---+---+   +----+----+
         |            |           |           |            |
         v            v           v           v            v
      [SENT/       [SENT/    [SIMULATED]   [TEST/      [DRY_RUN_
      QUEUED]     QUEUED]                 DRY_RUN]      LOCKED]
```

### Critical Channel Status Integrity Rule
A test or simulated channel must **never** be conflated with live carrier transmission:
- `SMS = SIMULATED` strictly prevents `SMS = DELIVERED` without carrier delivery receipts.
- `CAP = GENERATED` indicates valid OASIS CAP v1.2 XML creation, strictly labeled `[TEST / DRY_RUN]`.
- `SIREN = DRY_RUN` indicates software simulation with zero physical acoustic actuation.

---

## 3. SMS Gateway Abstraction & Multilingual Templates (Checkpoint 8-10 & 8-11)
The SMS gateway abstraction enforces 5 operational states:
1. `CONFIGURED`: Carrier gateway credentials (CDAC / Sandes) verified and active.
2. `UNCONFIGURED`: No carrier credentials present; dispatches fail closed.
3. `SIMULATED`: Default development state. Logs payload tagged with `[SIMULATED SMS]`.
4. `FAILED`: Upstream carrier network error or timeout.
5. `BLOCKED`: Prevented by statutory safety gate (`ENABLE_PUBLIC_DISPATCH = 0`).

### Himalayan Multilingual Templates (< 160 Characters)
All templates are engineered to fit within a single 160-character SMS segment across all regional dialects:
- **English (`en`)**: `[SIMULATED SMS] PARVAT NETRA: Landslide Warning CRITICAL at NH-10 KM 48. Immediate evacuation advised. Follow BRO emergency diversion to NH-717A.` (148 chars)
- **Hindi (`hi`)**: `[SIMULATED SMS] पर्वत नेत्रा: NH-10 KM 48 पर गंभीर भूस्खलन चेतावनी। तुरंत सुरक्षित स्थान पर जाएं।` (104 chars)
- **Nepali (`ne`)**: `[SIMULATED SMS] पर्वत नेत्रा: NH-10 KM 48 मा पहिरोको उच्च जोखिम। सुरक्षित स्थानमा जानुहोस्।` (102 chars)
- **Bhutia (`bh`)**: `[SIMULATED SMS] སྦས་ཡུལ་ཉེན་བརྡ: NH-10 KM 48 རི་ཉིལ་ཉེན་ཁ། ཐུགས་ཟོན་གནང་རོགས།` (98 chars)
- **Lepcha (`lp`)**: `[SIMULATED SMS] ᰛᰪᰵᰕᰤᰩ: NH-10 KM 48 ᰜᰤᰵᰊᰤᰩᰵ ᰈᰦᰵ ᰕᰦᰵᰊᰩᰵᰓᰪ ᰕᰤᰩᰰ ᰊᰤᰩᰵ.` (96 chars)
- **Assamese (`as`)**: `[SIMULATED SMS] পৰ্বত নেত্ৰা: NH-10 KM 48 ত ভূমিস্খলনৰ সতৰ্কবাণী। তৎক্ষণাৎ স্থান ত্যাগ কৰক।` (108 chars)

---

## 4. Mobile & Web Push Contracts (Checkpoint 8-08 & 8-09)
### Flutter Mobile Notification Contract
Dispatched to mobile responders and citizens with 7 structured fields:
```json
{
  "incident_id": "INC-1789093482-DC78A2",
  "severity": "CRITICAL",
  "location": "NH-10 KM 48 (SK-NH10-KM48)",
  "action": "EVACUATE",
  "time": "2026-09-11T08:30:00Z",
  "language": "en",
  "provenance": "[SIMULATED]"
}
```

---

## 5. Recipient Safety Acknowledgement Tracking (Checkpoint 8-15)
To support search-and-rescue prioritization, citizens and responders submit real-time safety status back to the EOC:
- `RECEIVED`: Alert viewed on device.
- `SAFE`: Civilian is outside hazard zone in a safe location.
- `NEED_ASSISTANCE`: Civilian is stranded or injured; requires immediate SDRF rescue.
- `EVACUATING`: Civilian is currently in transit along designated evacuation corridor.
- `UNABLE_TO_RESPOND`: Automated watchdog flag for unresponsive registered devices.

EOC displays aggregate counts (e.g., 42 Evacuating, 3 Need Assistance, 185 Safe) without exposing sensitive personal names or phone numbers on public overview screens.
