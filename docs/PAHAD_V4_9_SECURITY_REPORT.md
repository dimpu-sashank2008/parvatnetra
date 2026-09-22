# PARVAT NETRA / PAHAD AI — PHASE V4.9 SECURITY REPORT
## Telemetry Ingestion Security, Replay Defense, Credential Isolation & Public Alert Safety

**Corridor**: `CORR-NH10-SIKKIM-KM48`  
**Phase**: V4.9 — Joint Field Installation, LoRa Gateway Alignment & First Live Telemetry Commissioning  
**Security Posture**: `STRICT LOCALHOST-ONLY / ZERO PUBLIC EXPOSURE`  
**Public Dispatch**: `DISABLED (DRY-RUN ENFORCED)`  

---

### 1. Threat Matrix & Defense Controls (Section 33)

| Threat Vector | Attack Scenario | Implemented Defense Mechanism | Test Verification Suite | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Sensor Spoofing** | Rogue node injecting fabricated pressure | AES-128 / LoRaWAN MIC check + Verified Serial Enforcement | `test_v4_9_field_evidence.py` | `ACTIVE` |
| **Gateway Spoofing** | Unauthorized gateway attempting MQTT injection | Authenticated TLS + client certificate mutual authentication | `test_v4_9_gateway_alignment.py` | `ACTIVE` |
| **Replay Attack** | Resending valid packets during network recovery | Observation deduplication tuple `(sensor, time, seq)` | `test_v4_9_gateway_alignment.py` | `ACTIVE` |
| **Unauthorized Commissioning** | Software script attempting `FIELD_COMMISSIONED` | Demotion of placeholder tokens (`AUTHORIZATION_UNVERIFIED`) | `test_v4_9_field_evidence.py` | `ACTIVE` |
| **Corrupted Payload** | Radio noise altering sensor reading | CRC-16 hardware checksum verification | `test_v4_9_first_live_packet.py` | `ACTIVE` |
| **Premature Public Alert** | AI recommendation triggering siren | 2-of-3 confirmation rule + Public dispatch hardcoded `0` | `test_v4_9_field_evidence.py` | `ACTIVE` |
| **Public Exposure** | Accidental deployment or tunnel creation | Localhost bind (`127.0.0.1`) + Zero tunnel execution | `test_v4_9_time_sync.py` | `ACTIVE` |

---

### 2. Localhost-Only Invariant (Section 0)
In accordance with Section 0 of the Phase V4.9 Master Engineering Prompt:
- Development and test executions bind strictly to `127.0.0.1` / `localhost`.
- No public cloud deployments (Vercel, Render, Railway, AWS, GCP, Azure) are permitted during Phase V4.9.
- No public tunnels (ngrok, Cloudflare Tunnel, localhost.run) are enabled.
- Public deployment is a separate future phase requiring explicit instruction from the project owner.

---

### 3. Public Emergency Dispatch Isolation (Section 27)
To prevent accidental panic during prototype verification:
- **Human In-The-Loop**: Mandatory operator authorization required before any advisory can be promoted to alert.
- **`ENABLE_PUBLIC_DISPATCH = 0`**: Master software kill-switch permanently disables outbound public dispatchers.
- **`SIREN_DRY_RUN = 1`**: Physical and virtual siren actuators log intent locally without sounder activation.
- **CAP / SACHET Broadcasts**: OASIS CAP v1.2 XML messages are serialized as internal audit artifacts only. Zero packets are emitted to NDMA SACHET or public cellular broadcast gateways.
