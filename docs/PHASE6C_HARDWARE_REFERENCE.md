# PARVAT NETRA / PAHAD AI — PHASE 6C
## In-Situ Geotechnical Sensor Hardware Reference Architecture

**Document**: `docs/PHASE6C_HARDWARE_REFERENCE.md`  
**System**: PARVAT NETRA — National Landslide Disaster Intelligence  
**AI Engine**: PAHAD AI  
**Status**: APPROVED REFERENCE ARCHITECTURE  
**Target Deployment**: North-Eastern Himalayan Strategic Corridors (NH-10 Sikkim, Tupul Manipur, Melthum Mizoram)  
**Date**: 2026-09-10  

---

## 1. System Overview & Hierarchy

The PARVAT NETRA hillslope monitoring infrastructure employs an edge-resilient hierarchical topology engineered to survive extreme precipitation ($>300\text{ mm/24h}$), freezing conditions ($-10^\circ\text{C}$ to $+45^\circ\text{C}$), and total telecommunication blackouts in Himalayan gorges:

```
[ TRANSDUCER LAYER ]
  Vibrating Wire Piezometer (Pore Pressure)
  In-Place MEMS Inclinometer (Shear Displacement)
  Biaxial MEMS Surface Tiltmeter (Slope Deflection)
  Tipping-Bucket Rain Gauge (Rain Intensity)
  TDR Soil Moisture Probe (Volumetric Water Content)
  Pt100 RTD Thermistor (Ground Temperature)
            │
            ▼ (Analog 4-20mA, RS-485 Modbus RTU, SDI-12, Pulse Interrupt)
[ REFERENCE SENSOR NODE (ESP32-Class) ]
  - MCU: Espressif ESP32-S3 or ESP32-WROOM-32D (Dual Xtensa LX7 @ 240 MHz)
  - Transceiver: Semtech SX1262 LoRa (865–867 MHz IN865 Band)
  - Local Buffer: 4 MB SPI NOR Flash (Circular FIFO buffer)
  - Power: 3.6V Li-SOCl2 Primary Battery or 12V LiFePO4 with 10W MPPT Solar
  - Local Maintenance: BLE 5.0 (Commissioning & Diagnostics)
            │
            ▼ (LoRaWAN IN865 Uplink: 18-Byte Compact Binary OTA Frame)
[ CONCENTRATOR GATEWAY (Raspberry Pi-Class) ]
  - Platform: Raspberry Pi Compute Module 4 (CM4) / Industrial NXP i.MX8
  - Baseband Concentrator: Semtech SX1302 / SX1303 LoRaWAN Gateway HAT
  - Local Database: SQLite In-Memory / Persistent Write-Ahead Log (`edge_buffer.db`)
  - Autonomous Alert Policy: Edge Corridor Policy Engine (Zero-latency siren evaluation)
  - Local Acoustic Siren: Dual-tone 110 dB Horn via Optocoupled Relay
            │
            ├─────────────────────────────────────────┐
            ▼ (Primary: 4G/LTE Cat-M1 or Fiber)       ▼ (Autonomous Edge Fallback)
[ CENTRAL CLOUD / REGIONAL EOC ]           [ CORRIDOR SIREN & VMS ]
  - PAHAD AI Live Prediction Engine          - 110 dB Physical Siren Horn
  - Multi-Modal Observation Store            - Local Traffic Gate Closure
  - Common Alerting Protocol (CAP v1.2)      - Zero Cloud Dependency
```

---

## 2. Sensor Transducer Integration Architecture

### 2.1 Vibrating-Wire Piezometer (`piezometer`)
- **Primary Measurement**: Pore-water pressure ($u$) at the failure slip surface ($0\text{--}250\text{ kPa}$).
- **Interface Circuit**: Plucked coil frequency excitation ($1200\text{--}3500\text{ Hz}$) conditioned via an operational amplifier schmitt-trigger circuit into an ESP32 hardware timer/counter pin.
- **Formula**:
  $$u = K \times (f_0^2 - f^2) - B \times (P_0 - P) + C_T \times (T - T_0)$$
  Where $K$ is gauge factor ($\text{kPa/Hz}^2$), $f$ is resonant frequency, $B$ is barometric factor, and $C_T$ is temperature correction.
- **Excitation Interval**: 15 minutes (Normal); 1 minute (Triggered/Hazard).

### 2.2 In-Place MEMS Inclinometer (`inclinometer`)
- **Primary Measurement**: Subsurface horizontal displacement and creep velocity ($\text{mm/day}$).
- **Digital Interface**: Differential RS-485 bus running Modbus RTU at 9600 baud (8N1).
- **Wiring**: M12 5-Pin connector (Pin 1: +12V, Pin 2: RS485-A, Pin 3: GND, Pin 4: RS485-B, Pin 5: Shield).
- **ESP32 Interface**: Hardware UART2 connected to a 3.3V RS-485 transceiver (e.g. MAX3485 / SP3485) with automatic directional control.

### 2.3 Biaxial Surface MEMS Tiltmeter (`tilt`)
- **Primary Measurement**: Orthogonal tilt axes $\theta_X$ (downslope) and $\theta_Y$ (cross-slope) within $\pm 45.0^\circ$.
- **Transducer Interface**: Ultra-low noise MEMS accelerometer (e.g. ADXL355 / SCA103T) interfaced via SPI or I2C bus.
- **Resultant Angle**:
  $$\theta_R = \sqrt{\theta_X^2 + \theta_Y^2}$$
- **Rate Calculation**: Firmware calculates rolling 24-hour tilt acceleration:
  $$\Delta \theta / \Delta t = \frac{\theta_R(t) - \theta_R(t - 24\text{h})}{24}\quad [^\circ/\text{day}]$$

### 2.4 Digital Tipping-Bucket Rain Gauge (`rain_gauge`)
- **Primary Measurement**: Incremental rainfall accumulation and instantaneous intensity ($0\text{--}300\text{ mm/hr}$).
- **Transducer Interface**: Magnetically actuated reed switch ($0.2\text{ mm}$ per tip).
- **Circuit**: Pulled up to 3.3V with $10\text{ k}\Omega$ resistor + hardware RC low-pass filter ($100\ \Omega$, $0.1\ \mu\text{F}$) providing $50\text{ ms}$ software debounce on ESP32 GPIO interrupt pin (`GPIO_NUM_14`).

### 2.5 Time-Domain Reflectometry Soil Moisture (`soil_moisture`)
- **Primary Measurement**: Volumetric Water Content ($\text{VWC}$) in regolith ($0.05\text{--}0.70\text{ m}^3/\text{m}^3$).
- **Digital Interface**: SDI-12 single-wire bidirectional asynchronous serial bus operating at 1200 baud.
- **Power**: 12V DC power switched via low-side MOSFET to conserve battery during sleep.

### 2.6 Ambient & Ground Temperature (`temperature`)
- **Primary Measurement**: Ambient and ground temperature ($-30^\circ\text{C}$ to $+70^\circ\text{C}$).
- **Transducer**: Precision Pt100 RTD via MAX31865 RTD-to-digital converter SPI amplifier.

---

## 3. Reference Edge Controller (ESP32-Class Node)

### 3.1 Hardware Specifications
- **Processor**: Espressif ESP32-S3-WROOM-1 / ESP32-WROOM-32D.
- **Core Clock**: 80 MHz in active acquisition; 240 MHz during cryptographic operations; 32.768 kHz RTC during deep sleep.
- **SRAM**: 512 KB internal SRAM.
- **Flash Memory**: 4 MB SPI NOR Flash (partitioned: 1.5 MB Factory App, 1.5 MB OTA App, 512 KB SPIFFS/LittleFS for offline circular buffer, 512 KB NVS/Certificates).
- **Radio Transceiver**: Semtech SX1262 LoRa module connected via SPI (NSS: GPIO5, SCK: GPIO18, MISO: GPIO19, MOSI: GPIO23, RST: GPIO14, DIO1: GPIO2).
- **Real-Time Clock**: Maxim Integrated DS3231 high-accuracy I2C RTC ($\pm 2\text{ ppm}$ temperature-compensated) for accurate timestamping across cellular/LoRa blackouts.
- **Power Management**:
  - Sleep Current: $14\ \mu\text{A}$ in deep sleep mode.
  - Active Transmission Current: $110\text{ mA}$ at $+14\text{ dBm}$ LoRa transmit.
  - Average Daily Consumption: $3.2\text{ mAh/day}$ at 15-minute sampling interval.
  - Expected Battery Life: $>5.2\text{ years}$ on $19\text{ Ah}$ $\text{Li-SOCl}_2$ D-cell.

### 3.2 GPIO Pin Allocation Matrix
| Pin Number | Function / Label | Connected Subsystem | Notes |
| :--- | :--- | :--- | :--- |
| **GPIO 0** | `BOOT / FLASH` | Dev button / Pull-up | Strapping pin |
| **GPIO 2** | `LORA_DIO1` | SX1262 LoRa Interrupt | Uplink/Downlink event flag |
| **GPIO 4** | `SENSOR_PWR_EN` | P-Channel MOSFET Gate | Switches +12V transducer boost rail |
| **GPIO 5** | `LORA_CS` | SX1262 SPI Chip Select | Active LOW |
| **GPIO 14** | `RAIN_INTERRUPT` | Rain Gauge Reed Switch | Hardware debounce + edge interrupt |
| **GPIO 15** | `VW_FREQ_IN` | Piezometer Frequency | Schmitt-trigger pulse counter |
| **GPIO 16** | `RS485_RX` | MAX3485 RS-485 Receiver | Hardware UART2 RX |
| **GPIO 17** | `RS485_TX` | MAX3485 RS-485 Driver | Hardware UART2 TX |
| **GPIO 18** | `SPI_SCK` | SX1262 & Flash SCK | Shared SPI Bus |
| **GPIO 19** | `SPI_MISO` | SX1262 & Flash MISO | Shared SPI Bus |
| **GPIO 21** | `I2C_SDA` | DS3231 RTC & ADXL355 | Shared I2C Bus |
| **GPIO 22** | `I2C_SCL` | DS3231 RTC & ADXL355 | Shared I2C Bus |
| **GPIO 23** | `SPI_MOSI` | SX1262 & Flash MOSI | Shared SPI Bus |
| **GPIO 34** | `BATTERY_ADC` | Resistor Divider (1/2 Vbat) | Analog-to-Digital Converter ADC1_CH6 |
| **GPIO 35** | `SOLAR_V_ADC` | MPPT Solar Input Divider | Analog-to-Digital Converter ADC1_CH7 |

---

## 4. Edge Concentrator Gateway (Raspberry Pi-Class)

### 4.1 Hardware Architecture
- **Single Board Computer**: Raspberry Pi Compute Module 4 (CM4004032: 4GB RAM, 32GB eMMC, On-board WiFi/BLE) mounted on an Industrial Waveshare PoE 4G Baseboard.
- **LoRaWAN Concentrator**: Waveshare SX1302 / SX1303 8-Channel LoRaWAN Gateway HAT with dual SX1250 front-end mixers.
- **RF Filter & Antenna**: 865–867 MHz Cavity Bandpass Filter ($1.2\text{ dB}$ insertion loss) + $5.8\text{ dBi}$ Fiberglass Collinear Omni Antenna mounted $6\text{ m}$ above corridor roadway.
- **Enclosure**: IP66 Die-Cast Aluminum Weatherproof Housing with Gore-Tex pressure equalization vent and dual cable glands.
- **Power System**:
  - $12\text{V } 100\text{Ah}$ LiFePO4 Battery Bank with Victron SmartSolar MPPT 75/15 Charge Controller.
  - $100\text{W}$ Monocrystalline Solar PV Panel oriented South at $40^\circ$ tilt.
  - Continuous Autonomy: 14 consecutive sunless monsoon days.

### 4.2 Gateway Software Stack
- **OS**: Raspberry Pi OS Lite (64-bit Debian Bullseye / Bookworm).
- **LoRa Packet Forwarder**: Semtech `sx1302_hal` packet forwarder interfacing with local ChirpStack LoRaWAN Network Server.
- **PARVAT NETRA Edge Service**: Python 3.11 `services/edge_gateway.py` operating under systemd.
- **Persistent Local Buffer**: SQLite 3 database (`data/edge/edge_buffer.db`) in WAL mode for zero loss during internet dropouts.
- **Corridor Acoustic Siren**: Optocoupled solid-state relay driving $12\text{V DC } 110\text{ dB}$ pneumatic dual-tone siren horn.

---

## 5. Wireless Communication Architecture

### 5.1 LoRaWAN IN865 Regulatory Framework
All transmissions comply with the Department of Telecommunications (DoT) / Wireless Planning & Coordination (WPC) Wing specifications for the Indian license-exempt $865.0\text{--}867.0\text{ MHz}$ band:
- **Default Channels**:
  - Channel 0: $865.0625\text{ MHz}$, Spreading Factor SF7 to SF12, Bandwidth $125\text{ kHz}$
  - Channel 1: $865.4025\text{ MHz}$, Spreading Factor SF7 to SF12, Bandwidth $125\text{ kHz}$
  - Channel 2: $865.9850\text{ MHz}$, Spreading Factor SF7 to SF12, Bandwidth $125\text{ kHz}$
- **Transmit Power**: $+14\text{ dBm}$ standard ($+20\text{ dBm}$ max allowable EIRP $+30\text{ dBm}$).
- **Duty Cycle**: Firmly constrained to $<1\%$ airtime budget to ensure high co-located node density.

### 5.2 Backhaul Transport
- **Primary**: 4G/LTE Cat-M1 cellular uplink using Quectel EC25-E modem via PPP/QMI interface directly to central PARVAT NETRA cloud via MQTT over TLS (`pahad/{state}/{sector}/{device_id}/telemetry`).
- **Secondary / Maintenance**: Local WiFi hotspot and Bluetooth Low Energy (BLE 5.0).
- **Disconnection Fallback**: Autonomous local caching in SQLite `edge_buffer.db` with FIFO restoration replay.

---

## 6. Bluetooth Low Energy (BLE 5.0) Local Maintenance Architecture

### 6.1 Scope & Safety Boundaries
- **Strict Limitation**: BLE is deployed **exclusively** for initial on-site physical commissioning, zero-offset calibration uploads, and diagnostic readouts by authorized SDRF / BRO technicians.
- **Safety Invariant**: BLE is **never** used as a public or corridor emergency warning broadcast channel.

### 6.2 Custom GATT Service Specification
The ESP32 node advertises the custom PARVAT NETRA Maintenance Service:
- **Service UUID**: `0000FE60-0000-1000-8000-00805F9B34FB`

| Characteristic UUID | Property | Data Format | Description |
| :--- | :---: | :---: | :--- |
| `0000FE61-...` (`CONFIG_CHAR`) | Read / Write | JSON String | Device ID, Gateway ID, Sector ID, LoRa channels |
| `0000FE62-...` (`CALIB_CHAR`) | Read / Write | Binary (16B) | Zero Offset (float), Scale Factor (float), Expiry Epoch |
| `0000FE63-...` (`TELEMETRY_CHAR`)| Notify / Read | Binary (18B) | Real-time 18-byte telemetry frame for technician field meter |
| `0000FE64-...` (`STATUS_CHAR`) | Read | JSON String | Battery %, RSSI, Clock Offset, 8-Stage Commissioning State |
