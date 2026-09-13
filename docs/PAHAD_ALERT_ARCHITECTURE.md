# PAHAD AI — Emergency Alert & Last-Mile Notification Architecture
**Geofenced Notification Orchestration, Multi-Channel Routing & Acoustic Gateway**

---

## 1. Multi-Tier Alert Flow

```text
PAHAD AI Fused Risk Decision (2-of-3 Safety Invariant)
                    │
                    ▼
          Geofencing Engine
     (Haversine Great-Circle Filter, Default 15 km)
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   OASIS CAP      Push / SMS   Last-Mile Wireless
    v1.2 XML     Multilingual       Gateway
  (NDMA / SDMA)   (9 Dialects)  (LoRa / Acoustic Siren)
```

---

## 2. Channels & Protocols

1. **OASIS Common Alerting Protocol (CAP v1.2)**:
   - Validated standard XML output consumable by the National Disaster Management Authority (NDMA) Sachet portal.
2. **Multilingual Push & SMS**:
   - Ultra-compact format (< 160 characters) translated into 9 NER languages and dialects (Nepali, Lepcha, Bhutia, Assamese, Meitei/Manipuri, Khasi, Garo, Mizo, Nagamese) plus Hindi and English.
3. **Acoustic Industrial Siren Gateway (`SirenGateway`)**:
   - Emulates high-decibel dual EAS acoustic tones ($853\text{ Hz} / 960\text{ Hz}$) for mountain highway closure barriers.
4. **LoRa Emergency Mesh Node (`MeshAlertNode`)**:
   - Off-grid sub-gigahertz (865 MHz Indian ISM band) ad-hoc mesh packet broadcast (< 64 bytes) for post-disaster communication when cellular base stations are downed.

---

## 3. Operational Safety Invariants

- **`DRY_RUN=true` Guarantee**:
  - The alert gateway operates in dry-run simulation mode by default during all evaluation and development workflows.
  - No real telecommunication SMS credits are consumed and no physical sirens are energized without explicit production credentials configured in `.env`.
- **Configurable Radius**:
  - Default corridor geofencing radius is set to 15 km, dynamically adjustable per valley geomorphology.
