# PARVAT NETRA / PAHAD AI — PHASE 8: AUTHORITY HANDOVER REPORT
**Statutory Authorization Gates, Escalation Governance, and Controlled All-Clear Protocols**
*Pilot Corridor: NH-10 KM 48 (29th Mile, Pakyong District, Sikkim)*
*Date: 2026-09-11 | Authority: District Disaster Management Authority (DDMA) Pakyong*

---

## 1. Statutory Handover Doctrine
PARVAT NETRA is designed as an autonomous intelligence and decision-support platform, **not** an autonomous emergency dispatch authority. Statutory executive authority over civilian lives, mass evacuations, and road closures remains exclusively vested in constitutional disaster authorities:
- **District Level**: District Magistrate (DM) / Deputy Commissioner / DDMA Chairperson.
- **State Level**: State Relief Commissioner / SDMA Secretary / BRO Task Force Commander.
- **National Level**: National Executive Committee (NEC) / NDMA.

```
+----------------------------------------------------------------------------------------------------+
|                                    STATUTORY HANDOVER PIPELINE                                     |
+----------------------------------------------------------------------------------------------------+
|  [PAHAD AI Core]       -> Evaluates Multimodal Telemetry (FoS, Rainfall, ML Prob, InSAR)          |
|  [Alert Candidate]     -> Verifies Mandatory 2-of-3 Corroboration Gate                             |
|  [Ground Tasking]      -> Dispatches BRO / SDRF Field Unit for Physical Inspection                 |
|  [EOC Dossier]         -> Synthesizes 18-Point Evidence Dossier for Watchstander Triage            |
|  [Statutory Review]    -> District Magistrate Evaluates Dossier & Cryptographic Audit Trail        |
|  [Handover Signature]  -> DM Issues HMAC-SHA256 Signed Approval Token                              |
|  [Dissemination]       -> EOC Dispatches Geo-Fenced Web, Mobile, SMS, CAP, and Siren Notifications |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Multi-Tier Escalation Engine (Checkpoint 8-18)
To prevent emergency alerts from languishing unreviewed during off-hours, the system enforces automated escalation:
1. **Watchstander Reminder (10 minutes)**: EOC audio-visual chime and high-priority console prompt.
2. **District Escalation (20 minutes)**: Automated escalation SMS and alert to District Magistrate / Superintendent of Police.
3. **State Escalation (30 minutes)**: Handover to Sikkim State Relief Commissioner and BRO Project Swastik Commander.

### Fail-Closed Invariant
Under no circumstances does timeout expiration trigger automated public alert broadcast. Expiration strictly **fails closed**, elevating the review tier while keeping civilian channels completely locked.

---

## 3. Controlled All-Clear Protocol (Checkpoint 8-19)
Premature stand-down following a landslide event frequently leads to secondary casualties if the hillslope suffers progressive creep or secondary toe failure. PARVAT NETRA enforces a mandatory **Triple-Gate All-Clear Verification Protocol**:

| Verification Gate | Mandatory Criterion | Evaluation Source |
| :--- | :--- | :--- |
| **Gate 1: Physical Stabilization** | Mohr-Coulomb $FoS \ge 1.25$ AND 24h Rainfall $< 50\,\text{mm}$ | In-situ piezometers, inclinometers, and IMD telemetry |
| **Gate 2: Field Ground Clearance** | Physical inspection confirms crack arrest, debris clearance, toe berm intact | BRO / SDRF on-site inspection team |
| **Gate 3: Statutory Executive Approval** | Formal signed stand-down order | District Magistrate / State Authority |

$$\text{All-Clear Validated} \iff (\text{Gate 1} \land \text{Gate 2} \land \text{Gate 3})$$
An AI risk decrease alone can **never** issue an all-clear notification without human confirmation.

---

## 4. False Alarm & Withdrawal Retraction (Checkpoint 8-20)
When contradictory ground evidence demonstrates that a sensor anomaly triggered an erroneous warning, the platform executes a verified withdrawal:
1. **Evidence Ingestion**: Field team submits zero-displacement inclinometer logs and camera footage.
2. **Withdrawal Review**: EOC Incident Commander prepares retraction order.
3. **Statutory Approval**: District Magistrate signs withdrawal directive.
4. **Retraction Broadcast**: Targeted broadcast sent to all previously alerted users:
   `[RETRACTION] Prior advisory for INC-XXXX withdrawn. Inclinometer telemetry confirms zero movement. Normal corridor transit resumed.`
5. **Tamper-Evident Logging**: Reason for retraction recorded in SHA-256 audit chain.

---

## 5. Executive Command Brief Screen (Checkpoint 8-22)
The EOC Command Brief screen provides a single-glance briefing display for executive commanders:
```
+-----------------------------------------------------------------------------------------+
| PARVAT NETRA -- EXECUTIVE COMMAND BRIEFING [PILOT CORRIDOR NH-10 KM 48]                 |
+-----------------------------------------------------------------------------------------+
| ACTIVE INCIDENT     : INC-1789093482-DC78A2          | STATUS    : AUTHORITY_REVIEW     |
| COMPOSITE RISK (CRI): 78.5 / 100.0 (HIGH)            | PHYS FoS  : 0.990 (CRITICAL)     |
| ML PROBABILITY      : 81.0% (GBDT Baseline)          | RAIN 24H  : 172.0 mm (MONSOON)   |
| SEISMIC STATE       : QUIET (No tremor)              | DATA QUAL : 96.0% (Fresh)        |
| SIGNAL AGREEMENT    : 2-of-3 Corroborated [FoS < 1.10, Rain > 150mm]                     |
| FIELD VERIFICATION  : BRO Unit Confirmed 12mm Tension Cracks and Toe Slumping           |
| RECOMMENDATION      : EVACUATE 29th Mile & Reroute NH-10 to NH-717A Bypass              |
| AUTHORITY STATUS    : Awaiting Statutory Signature (DM Pakyong)                         |
| DISPATCH STATUS     : LOCKED (DRY_RUN Isolated)                                         |
+-----------------------------------------------------------------------------------------+
```
