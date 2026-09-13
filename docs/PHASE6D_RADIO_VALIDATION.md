# PARVAT NETRA / PAHAD AI — PHASE 6D
## LoRa Radio Propagation & Backhaul Validation Specification

**Document Reference**: `docs/PHASE6D_RADIO_VALIDATION.md`  
**Classification**: RF Telecommunications Engineering Specification  
**Standard**: SIH 26001 / LoRaWAN Regional Parameters IN865 / EU868  
**Date**: September 2026  

---

## 1. Topographic RF Propagation in Mountain Corridors

Steep V-shaped Himalayan valleys (e.g. Teesta gorge, Ijei river valley) introduce severe multipath fading, knife-edge diffraction over rocky ridges, and heavy monsoonal atmospheric attenuation.

### 1.1 First Fresnel Zone Clearance
To avoid path obstruction losses, at least 60% of the 1st Fresnel zone must remain clear of terrain obstacles:
$$R_1 = 8.656 \times \sqrt{\frac{D}{f_{\text{GHz}}}}$$
- For $f = 0.868$ GHz at $D = 2.0$ km: $R_1 \approx 13.14$ m clearance required.
- Gateway masts are positioned on prominent topographic ridges (12–18 m mast height) to ensure positive elevation differential ($\Delta h \ge 15$ m).

### 1.2 Free Space Path Loss (FSPL)
$$\text{FSPL (dB)} = 32.44 + 20 \log_{10}(d_{\text{km}}) + 20 \log_{10}(f_{\text{MHz}})$$
At 868.1 MHz:
- 1.0 km: 91.2 dB
- 3.5 km: 102.1 dB
- 5.0 km: 105.2 dB

---

## 2. Quantitative Link Quality Standards

| Metric | PASS (Optimal) | DEGRADED (Marginal) | FAIL (Unacceptable) |
| :--- | :--- | :--- | :--- |
| **RSSI** | $\ge -105$ dBm | $-118 \text{ to } -105$ dBm | $< -118$ dBm |
| **SNR** | $\ge -5.0$ dB | $-12.0 \text{ to } -5.0$ dB | $< -12.0$ dB |
| **PDR** | $\ge 90.0\%$ | $70.0\% \text{ to } 89.9\%$ | $< 70.0\%$ |
| **Latency** | $\le 1500$ ms | $1500 \text{ to } 4000$ ms | $> 4000$ ms |

---

## 3. CLI Validation Tool (`scripts/test_radio_link.py`)

Technicians evaluate links on site using the CLI utility:
```bash
# Optimal link test
python scripts/test_radio_link.py --device-id SN-PIEZ-NH10-01 --gateway-id GW-NH10-SINGTAM-01 --json

# Manual field test measurement ingestion
python scripts/test_radio_link.py --device-id SN-TILT-NH10-01 --gateway-id GW-NH10-SINGTAM-01 --rssi -92.0 --snr 4.5 --pdr 0.98 --latency 240
```
All measurements are persisted to `field_radio_tests` in `pahad_observations.db`.
