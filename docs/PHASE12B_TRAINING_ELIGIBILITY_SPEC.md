# PARVAT NETRA • PAHAD AI — Phase 12B Training Eligibility Specification

**Standard**: SIH 26001 / Project Constitution Section 10 & 12  
**System**: PARVAT NETRA — Northeast Region Sentinel  
**Subsystem**: PAHAD AI — Predictive AI for Hillslope Analysis & Disaster-response  
**Document Version**: 12.0.0-phase12b  
**Status**: FORMAL ENGINEERING ELIGIBILITY SPECIFICATION  

---

## 1. Foundational Principle

Machine learning models deployed for high-stakes public disaster early warning cannot rely on synthetic data, upsampled snapshots, or severely under-parameterized datasets. A false negative costs human lives; a false positive leads to public warning fatigue and economic disruption.

This specification details the mathematical and field requirements that must be satisfied before transitioning the recurrent neural network from `DATA_COLLECTION_REQUIRED` to `TRAINING_ELIGIBLE`.

---

## 2. Degrees-of-Freedom & Parameter Budget Analysis

A standard 2-layer Bidirectional Long Short-Term Memory (BiLSTM) network with hidden dimension $H = 64$ processing $D = 26$ input features has the following parameter counts:

1. **Layer 1 (Forward + Backward)**:
   $$N_1 = 2 	imes 4 	imes \left(H 	imes D + H^2 + Hight) = 8 	imes (64 	imes 26 + 64^2 + 64) = 8 	imes (1664 + 4096 + 64) = 46,592	ext{ weights}$$
2. **Layer 2 (Forward + Backward)**:
   $$N_2 = 2 	imes 4 	imes \left(H 	imes 2H + H^2 + Hight) = 8 	imes (64 	imes 128 + 64^2 + 64) = 8 	imes (8192 + 4096 + 64) = 98,816	ext{ weights}$$
3. **Dense Classification Head**:
   $$N_{	ext{head}} = 2H 	imes 4 + 4 = 128 	imes 4 + 4 = 516	ext{ weights}$$
4. **Total Parameter Count**: $pprox 145,924	ext{ weights}$ (or $pprox 25,000$ for a compact $H=24$ architecture).

### Statistical Learning Constraint
In statistical learning theory, fitting $P pprox 25,000$ parameters requires at least $N \ge 10 	imes P$ observations to prevent catastrophic overfitting:
- With current data ($N = 105$ snapshots, 17 events), each parameter would have less than **0.004 samples**.
- Fitting a neural sequence model under these conditions constitutes severe empirical fabrication.
- Therefore, the project target of **500 independent event sequences** and **2,000 control sequences** represents the absolute lower bound for defensible deep recurrent optimization.

---

## 3. Physical Field Telemetry Requirements

Before recurrent sequence models can be trained, real-time in-situ telemetry nodes must be deployed across high-risk corridors:

1. **Sensor Node Instrument Package**:
   - Piezometer: Vibrating-wire transducer (pore-water pressure in kPa, accuracy $\pm 0.1\%$)
   - Borehole Inclinometer: Dual-axis MEMS (tilt in degrees, angular resolution $0.001^\circ$)
   - Tipping Bucket Rain Gauge: 0.2mm resolution with integrated solar heating
   - Volumetric Soil Moisture: Frequency-Domain Reflectometry (VWC % at 0.5m, 1.0m, 1.5m depths)
2. **Transmission Cadence**:
   - Nominal: Every 15 minutes via LoRaWAN / 4G cellular telemetry
   - Event Trigger: Real-time interrupt on tilt acceleration $> 0.05^\circ/	ext{hr}$
3. **Network Synchronization**:
   - NTP hardware time-stamping with maximum allowable jitter $\le 15.0	ext{ seconds}$
4. **Power Autonomy**:
   - Solar panel + LiFePO4 battery pack providing min 14 days of continuous operation without sunlight (monsoon resilience).

---

## 4. Multi-Basin Geographical Diversity Standards

Candidate training sequences must be distributed across diverse geological and morphological domains in the Northeast Region:

| Zone / Basin | Characteristic Geology | Target Event Sequences |
| :--- | :--- | :---: |
| **Sikkim Himalaya** (Teesta Basin) | High-grade gneiss, schists, glacial moraines, extreme relief | 100 |
| **Arunachal Western Range** (Kameng / Tawang) | Thrust belts, quartzite, fractured dolomite | 100 |
| **Arunachal Eastern Corridor** (Siang / Dibang) | Ophiolite belt, seismic rupture zones, heavy cloudbursts | 75 |
| **Assam Sub-Himalayan Foot-hills** | Siwalik molasse, uncemented sandstone, river toe erosion | 75 |
| **Meghalaya Plateau** (Khasi / Jaintia Hills) | Precambrian granite, karst limestone, world's highest rainfall | 75 |
| **Indo-Burma Range** (Manipur, Nagaland, Mizoram) | Disang-Barail flysch, shale, strike-slip seismic faults | 75 |
| **Total Project Target** | **Comprehensive NER Coverage** | **500** |

---

## 5. Transition Gate Checklist

Transitioning the status from `DATA_COLLECTION_REQUIRED` to `TRAINING_ELIGIBLE` requires:

- [ ] Minimum 500 validated independent failure sequences collected
- [ ] Minimum 2,000 verified non-event control sequences recorded
- [ ] Continuous telemetry duration $\ge 48.0	ext{ hours}$ per sequence
- [ ] 15-minute sensor sampling cadence verified across all nodes
- [ ] Two complete annual monsoon cycles (min 24 contiguous months) recorded
- [ ] Sequence completeness score $C_{	ext{comp}} \ge 95.0\%$ without synthetic imputation
- [ ] Sequence quality score $Q \ge 0.85$ across all candidate sequences
- [ ] Zero cross-corridor leakage verified by `TemporalLeakageDetector`
- [ ] Formal certification signed by Geological Survey of India (GSI) / State Disaster Management Authority (SDMA) technical liaisons.

Until all conditions above are met, `engine/pahad_temporal_gate.py` maintains `KEEP_SURROGATE` and guarantees the operational deployment uses only the scientifically verified Calibrated Gradient Boosting Classifier.
