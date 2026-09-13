# PARVAT NETRA / PAHAD AI — PHASE 6A
## Geotechnical In-Situ Sensor Hardware Specification & Transducer Matrix

**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**Document**: `docs/PHASE6A_SENSOR_SPECIFICATION.md`  
**Standard**: SIH 26001 / Phase 6A Field Infrastructure  
**Status**: APPROVED SPECIFICATION  
**Target Geographic Scope**: North-Eastern Himalayan Corridors (NH-10 Sikkim, Tupul Manipur, Melthum Mizoram)

---

## 1. Architectural Scope & Physical Constraints

Himalayan hillslope monitoring presents extreme physical constraints:
- **Steep Topography**: $30^\circ$ to $65^\circ$ slope angles with talus, phyllite, and schists.
- **Precipitation**: Monsoon rainfall up to $300\text{ mm/24h}$ with intense cloudbursts ($>50\text{ mm/hr}$).
- **Temperature Range**: $-10^\circ\text{C}$ to $+45^\circ\text{C}$ with severe diurnal freezing and thawing cycles.
- **Power Constraints**: Off-grid solar photovoltaic (PV) with seasonal cloud cover extending up to 7 consecutive days.
- **Telemetry Constraints**: Zero terrestrial cellular backhaul in deep gorges (NH-10 Teesta Gorge, Noney valley).

Every deployed sensor transducer must interface cleanly with either:
1. **LoRaWAN Class A/C Node**: $865\text{--}867\text{ MHz}$ (India ISM Band) transmitting to local edge concentrators.
2. **RS-485 / Modbus RTU Sub-bus**: Daisy-chained digital interface directly into the corridor concentrator.

---

## 2. Transducer Matrix & Engineering Specifications

### 2.1 Vibrating-Wire Piezometer (`piezometer`)
- **Primary Function**: Measures pore-water pressure ($u$) at the potential failure shear plane. Directly informs Mohr-Coulomb effective stress:
  $$\sigma' = \sigma_n - u$$
  $$\tau_f = c' + (\sigma_n - u) \tan \phi'$$
- **Target Transducer Model**: Geokon Model 4500HD / Sisgeo Piezometer.
- **Operating Range**: $-10.0\text{ kPa}$ to $+250.0\text{ kPa}$ (Standard Range: $0\text{--}350\text{ kPa}$).
- **Overpressure Capacity**: $200\%$ of rated range.
- **Resolution**: $0.025\%\text{ F.S.}$ ($\pm 0.06\text{ kPa}$).
- **Linearity**: $\pm 0.1\%\text{ F.S.}$
- **Excitation**: Plucked coil frequency pulse ($1200\text{--}3500\text{ Hz}$).
- **Output**: Natural resonant frequency ($Hz$ or $G = f^2 / 1000$).
- **Thermal Range**: $-20^\circ\text{C}$ to $+80^\circ\text{C}$ with integral $3\text{ k}\Omega$ thermistor for temperature compensation.
- **Ingress Protection**: IP68 hermetically sealed electron-beam welded stainless steel casing (rated to $3\text{ MPa}$ water depth).
- **Physical Installation**: Installed inside a perforated PVC standpipe borehole, surrounded by filter sand ($0.5\text{--}1.0\text{ mm}$) and sealed above with bentonite pellet seals.

---

### 2.2 In-Place MEMS Inclinometer (`inclinometer`)
- **Primary Function**: Deep subsurface shear displacement and horizontal creep velocity ($\text{mm/day}$) across slipping strata.
- **Target Transducer Model**: Durham Geo Slope Indicator Digitilt In-Place Inclinometer (IPI) / Sisgeo MEMS IPI.
- **Operating Range**: $\pm 500.0\text{ mm}$ cumulative deflection; sensor angular range $\pm 15^\circ$ from vertical.
- **Velocity Limit**: Operational alerts triggered at $>5\text{ mm/day}$ (Warning) and $>15\text{ mm/day}$ (Critical).
- **Resolution**: $\pm 0.005\text{ mm/m}$ ($1\text{ arc-sec}$).
- **Repeatability**: $\pm 0.01\%\text{ F.S.}$
- **Digital Interface**: RS-485 Modbus RTU / SDI-12 digital daisy-chain up to 24 sensors in a single vertical casing.
- **Power Consumption**: $12\text{V DC}$, $15\text{ mA}$ active per gauge; sleep mode $<50\ \mu\text{A}$.
- **Casing Standard**: Standard $70\text{ mm}$ or $85\text{ mm}$ grooved ABS inclinometer casing grouted into solid bedrock below slip horizon.

---

### 2.3 Biaxial Surface MEMS Tiltmeter (`tilt`)
- **Primary Function**: Measures surface rotational deflection and slope rotation rates on retaining structures, rock blocks, and bridge piers.
- **Target Transducer Model**: RST Instruments CXT Biaxial MEMS Tiltmeter / Jewell Emerald Series.
- **Measurement Axes**: Orthogonal dual-axis ($X = \text{down-slope}$, $Y = \text{cross-slope}$). Resultant calculated as:
  $$\theta_R = \sqrt{\theta_X^2 + \theta_Y^2}$$
- **Operating Range**: $\pm 45.0^\circ$ deflection.
- **Rate-of-Change Bounds**: Maximum physical rate $10.0^\circ/\text{day}$; alert warning at $>1.0^\circ/\text{day}$; critical at $>2.5^\circ/\text{day}$.
- **Resolution**: $0.001^\circ$ ($3.6\text{ arc-seconds}$).
- **Enclosure**: IP67 / NEMA 4X cast aluminium or marine-grade stainless housing with mounting bracket for anchor bolts.
- **Power Supply**: Internal $3.6\text{V}$ D-cell Lithium Thionyl Chloride ($\text{Li-SOCl}_2$) with 5-year battery life at 15-minute telemetry intervals.

---

### 2.4 Digital Tipping-Bucket Rain Gauge (`rain_gauge`)
- **Primary Function**: Ultra-localized hillslope precipitation accumulation and rainfall intensity.
- **Target Model**: Campbell Scientific TE525MM / Davis 7852 Metric Rain Collector.
- **Orifice Diameter**: $200\text{ mm}$ ($8\text{ inches}$) meeting WMO standards.
- **Bucket Calibration**: $0.2\text{ mm}$ per tip (factory calibrated).
- **Intensity Range**: $0\text{--}300\text{ mm/hr}$.
- **Accuracy**: $\pm 1\%$ at rates up to $50\text{ mm/hr}$; $\pm 3\%$ at rates up to $100\text{ mm/hr}$.
- **Switch Type**: Hermetically sealed reed switch with magnetic actuator.
- **Pulse Debounce**: Hardware RC circuit + $50\text{ ms}$ software debounce filter on edge concentrator.
- **Debris Protection**: Removable stainless steel mesh filter funnel with bird deterrent spikes.

---

### 2.5 Time-Domain Reflectometry Soil Moisture Probe (`soil_moisture`)
- **Primary Function**: Volumetric Water Content ($\text{VWC}$ in $\text{m}^3/\text{m}^3$) of the shallow hillslope regolith ($0.5\text{--}1.5\text{ m}$ depth).
- **Target Model**: Campbell Scientific CS655 / Decagon TEROS 12.
- **Operating Range**: $0.05\text{--}0.70\text{ m}^3/\text{m}^3$ ($5\%\text{--}70\%\text{ VWC}$).
- **Accuracy**: $\pm 0.03\text{ m}^3/\text{m}^3$ in standard mineral soils.
- **Probe Geometry**: 2-rod or 3-rod parallel stainless steel waveguides ($120\text{ mm}$ length).
- **Interface**: SDI-12 protocol over 3-wire bus (Power, Ground, Bidirectional Data).

---

### 2.6 Crack Aperture Meter / Joint Extensometer (`crack_sensor`)
- **Primary Function**: Monitors crown tension cracks and active joint dilation across rock bluffs above roads.
- **Target Model**: Geokon Model 4420 Vibrating Wire Crackmeter / Sisgeo Linear Potentiometric Transducer.
- **Operating Range**: $0.0\text{ mm}$ to $100.0\text{ mm}$ (optional extension to $200.0\text{ mm}$).
- **Resolution**: $0.025\%\text{ F.S.}$ ($0.025\text{ mm}$).
- **Thermal Coefficient**: Integral thermistor compensation ($\text{ppm/}^\circ\text{C}$).
- **Mounting**: 3D ball joints anchored across tension crack boundaries into sound rock with expansion anchors.

---

### 2.7 Ultrasonic Channel Stage Meter (`water_level`)
- **Primary Function**: Non-contact flash flood and debris flow surge detection in steep mountain torrents (e.g., Teesta tributaries, Rangpo chu).
- **Target Model**: Ott RLS Radar Level Sensor / Pulsar dBi Ultrasonic Transducer.
- **Operating Range**: $0.4\text{ m}$ to $35.0\text{ m}$ standoff distance.
- **Beam Angle**: $12^\circ$ conical narrow beam for gorge profiling.
- **Accuracy**: $\pm 3\text{ mm}$.
- **Output**: 4--20 mA loop or SDI-12.

---

### 2.8 Ambient & Ground Temperature Thermistor (`temperature`)
- **Primary Function**: Freeze-thaw detection, ice wedging warning, and temperature drift compensation for all vibrating-wire strain sensors.
- **Transducer Type**: Pt100 RTD (Class A) or $3\text{ k}\Omega$ NTC Thermistor.
- **Range**: $-30^\circ\text{C}$ to $+70^\circ\text{C}$.
- **Accuracy**: $\pm 0.2^\circ\text{C}$.

---

## 3. Wiring, Electrical Pinouts & Surge Protection

### 3.1 Standard Field Sensor Connector (M12 5-Pin A-Coded)
```
         Pin 1: +12V DC Regulated Power (Brown)
         Pin 2: RS-485-A / SDI-12 Data (White)
         Pin 3: Ground / DC Return (Blue)
         Pin 4: RS-485-B / Pulse Input (Black)
         Pin 5: Earth Chassis Ground / Shield (Drain Wire)
```

### 3.2 Lightning & Surge Suppression (IS/IEC 62305 Standard)
Himalayan ridgelines experience severe cloud-to-ground lightning discharge:
1. **Primary Surge Arrestor**: Gas Discharge Tube (GDT) rated for $20\text{ kA}$ ($8/20\ \mu\text{s}$) placed at cable entry glands.
2. **Secondary Suppression**: Fast Transient Voltage Suppressor (TVS) diodes (clamping at $15\text{V}$) on all signal and RS-485 differential lines.
3. **Earth Grounding**: Heavy copper bonding braid ($16\text{ mm}^2$) connecting transducer casings to dedicated earth grounding rods ($<5\ \Omega$ earth resistance achieved with bentonite chemical ground enhancement).
4. **Galvanic Isolation**: $1.5\text{ kV}$ optocoupled isolation between sensor inputs and edge microprocessor.

---

## 4. Sampling Schedules & Battery Autonomy

| Sensor Type | Normal Interval | Triggered / Hazard Interval | Expected Battery Life (Li-SOCl2) |
| :--- | :---: | :---: | :---: |
| **Piezometer** | 15 minutes | 1 minute | 4.8 years |
| **Inclinometer** | 60 minutes | 5 minutes | 3.5 years |
| **Tiltmeter** | 15 minutes | 30 seconds | 5.2 years |
| **Rain Gauge** | Event-driven (tip) | Immediate uplink ($>5\text{ tips/min}$) | 6.0 years |
| **Soil Moisture** | 30 minutes | 5 minutes | 4.1 years |
| **Crack Sensor** | 15 minutes | 1 minute | 4.5 years |
| **Stream Gauge** | 10 minutes | 1 minute | External Solar ($12\text{V}$) |

---

## 5. Verification & Environmental Certifications

All field hardware deployed in Phase 6A must satisfy:
1. **IP Rating**: IEC 60529 IP67 minimum (surface electronics); IP68 (downhole piezometers and subsurface probes).
2. **Vibration**: MIL-STD-810G Method 514.6 for heavy rock blast and highway vibratory loads.
3. **Electromagnetic Compatibility**: EN 61326-1 (Industrial EMC immunity and emissions).
4. **WPC ETA Certification**: Wireless Planning & Coordination (WPC) Wing of Ministry of Communications, Government of India for $865\text{--}867\text{ MHz}$ band transmission.
