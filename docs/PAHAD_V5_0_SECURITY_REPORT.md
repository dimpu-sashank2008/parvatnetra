# PARVAT NETRA / PAHAD AI — PHASE V5.0
## SECURITY, GOVERNANCE & INSTITUTIONAL CLAIMS AUDIT

**Compliance Level**: SIH 2026 / National Disaster Management Authority (NDMA) OASIS CAP  
**Authority Evidence Status**: `AUTHORIZATION_EVIDENCE_MISSING`  

---

### 1. Threat Mitigation Matrix

| Threat Vector | Potential Impact | Enforced Architectural Defense | Test Suite Verification | Defense Status |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry Spoofing** | Rogue transmitter fabricating slope pore pressure | LoRa MIC checks + hardware serial verification gate | `test_v5_0_hardware_provenance.py` | `ACTIVE` |
| **Replay Attacks** | Injecting delayed packets during network reconnection | Deterministic SHA-256 deduplication ledger | `test_v5_0_lora.py` | `ACTIVE` |
| **Future Timestamps** | Desynchronized clocks injecting out-of-order predictions | ±30s drift boundary enforcement | `test_v5_0_time_sync.py` | `ACTIVE` |
| **Data Tampering** | Silent modification of raw logs | SHA-256 manifest custody verification | `test_v5_0_raw_custody.py` | `ACTIVE` |
| **Premature Public Alert** | Unverified AI triggering highway sirens | Mandatory human sign-off; `public_dispatch=False` | `test_v5_0_authorization.py` | `ACTIVE` |
| **Government Overclaiming** | Misrepresenting SIH project as official GOI service | Explicit downgrade to SIH prototype designation | `test_v5_0_claim_audit.py` | `ACTIVE` |

---

### 2. Institutional Claims Governance

To avoid misleading evaluators or disaster management authorities:
1. **BRO Project Swastik**: Classified as `PARTIALLY_SUPPORTED` (prospective corridor pilot partner for NH-10 instrumentation; no signed commercial contract).
2. **SSDMA (Sikkim State DMA)**: Classified as `PARTIALLY_SUPPORTED` (regional emergency coordination partner; direct public dispatch hardcoded to disabled).
3. **NDMA Placeholder Token**: The token string `BRO_NDMA_AUTHORIZED_ACCEPTANCE_2026` is formally flagged as `AUTHORIZATION_UNVERIFIED` and barred from conferring operational clearance.
4. **Platform Identity**: Designated strictly as "Smart India Hackathon (SIH) 2026 AI-assisted research and decision-support prototype".
