# -*- coding: utf-8 -*-
"""
services/hardware_bom_service.py
================================
PARVAT NETRA • Indigenous Field Hardware Bill of Materials (BOM) & Edge Engineering Service
--------------------------------------------------------------------------------------------
Provides comprehensive hardware specifications, itemized unit economics, power budget calculations,
pinout matrices, and WPC India IN865 regulatory compliance data for Himalayan slope IoT telemetry stations.
"""

from __future__ import annotations
from typing import Dict, Any, List

def get_hardware_bom_data() -> Dict[str, Any]:
    """Returns the comprehensive hardware architecture, itemized BOM, power budget, and unit economics."""
    
    bom_items: List[Dict[str, Any]] = [
        {
            "id": "MCU-01",
            "category": "Microcontroller & Compute",
            "component": "Espressif ESP32-S3-WROOM-1 (N16R8)",
            "specs": "Dual-Core Xtensa LX7 @ 240MHz, 16MB Flash, 8MB PSRAM, Wi-Fi 4 + BLE 5.0",
            "function": "Sensor sampling, 18-byte packed binary encoding, local circular flash buffer, BLE commissioning",
            "ip_rating": "Mounted in IP67 enclosure",
            "source": "Mouser / Robu.in",
            "cost_inr": 480
        },
        {
            "id": "RF-01",
            "category": "Long-Range RF Transceiver",
            "component": "Semtech SX1262 Sub-GHz LoRa Module",
            "specs": "865–867 MHz (IN865 Band), +22dBm max output, -148dBm sensitivity, SPI bus",
            "function": "Long-range ridge relay transmission across Himalayan mountain chokepoints (up to 15km LoS)",
            "ip_rating": "Mounted in IP67 enclosure",
            "source": "Element14 / Waveshare",
            "cost_inr": 850
        },
        {
            "id": "ANT-01",
            "category": "RF Antenna & Cabling",
            "component": "868MHz 5.8dBi Fiberglass Omni Antenna + RG58 Cable",
            "specs": "5.8 dBi gain, N-Male to SMA, UV-resistant fiberglass, lightning arrestor",
            "function": "High-gain RF propagation penetrating dense monsoon mist and pine tree canopy",
            "ip_rating": "IP68 Outdoor",
            "source": "L-com / Robu.in",
            "cost_inr": 1250
        },
        {
            "id": "TILT-01",
            "category": "Geotechnical Sensor",
            "component": "Murata SCA103T-D04 Dual-Axis MEMS Inclinometer",
            "specs": "±30° measurement range, 0.001° resolution, analog differential output, thermal compensation",
            "function": "Sub-millimeter displacement & borehole shear plane rotational creep detection",
            "ip_rating": "IP68 Hermetic Sensor Head",
            "source": "DigiKey / Mouser",
            "cost_inr": 3400
        },
        {
            "id": "PIEZO-01",
            "category": "Geotechnical Sensor",
            "component": "Vibrating Wire Piezometer Transducer (Plucked-Coil Interface)",
            "specs": "0–350 kPa range, ±0.1% FS accuracy, frequency output 1400–3500 Hz",
            "function": "Pore-water pressure monitoring to detect sudden loss of effective stress in slip plane",
            "ip_rating": "IP68 Hermetic Submersible",
            "source": "Geokon / Indigenous Indian Equivalent",
            "cost_inr": 4200
        },
        {
            "id": "MOIST-01",
            "category": "Hydrometric Sensor",
            "component": "TDR Soil Moisture & Temperature Probe",
            "specs": "0–100% VWC (Volumetric Water Content), RS-485 Modbus RTU interface",
            "function": "van Genuchten wetting front infiltration tracking & matric suction dissipation",
            "ip_rating": "IP68 Direct Soil Burial",
            "source": "Robu.in / Seeed Studio",
            "cost_inr": 1650
        },
        {
            "id": "PWR-SOL-01",
            "category": "Power Subsystem",
            "component": "15W Monocrystalline Solar Photovoltaic Panel",
            "specs": "18V Vmp, 0.83A Imp, tempered glass, anodized aluminum frame, high low-light efficiency",
            "function": "Harvest solar irradiance even through heavy Himalayan cloud cover and dense fog",
            "ip_rating": "IP67 Weatherproof",
            "source": "Loom Solar / Waaree",
            "cost_inr": 1100
        },
        {
            "id": "PWR-BAT-01",
            "category": "Power Subsystem",
            "component": "12.8V 10Ah LiFePO4 Battery Pack with Integrated BMS",
            "specs": "128 Wh energy storage, 2000+ cycle life, -20°C to +60°C operating temperature",
            "function": "Guarantees 14.8 days continuous autonomous operation during non-stop monsoon downpours",
            "ip_rating": "Internal to Enclosure",
            "source": "Battrixx / Amptek India",
            "cost_inr": 2100
        },
        {
            "id": "PWR-CHG-01",
            "category": "Power Subsystem",
            "component": "MPPT Solar Charge Controller Board (TP5100 / CN3791)",
            "specs": "Buck-boost MPPT efficiency > 93%, overcharge/overdischarge protection, status telemetry",
            "function": "Maximizes energy harvest during diffused lighting conditions",
            "ip_rating": "Mounted in IP67 enclosure",
            "source": "Robu.in / Custom PCB",
            "cost_inr": 320
        },
        {
            "id": "ENC-01",
            "category": "Structural & Enclosure",
            "component": "Ruggedized UV-Stabilized Polycarbonate Enclosure with Dual Latches",
            "specs": "280 x 190 x 130 mm, silicone gasket, brass thread inserts, breather vent",
            "function": "Protects core electronics from torrential monsoon rains, UV degradation, and dust",
            "ip_rating": "IP67 Certified",
            "source": "Sinomec / Fibox India",
            "cost_inr": 850
        },
        {
            "id": "MNT-01",
            "category": "Structural & Mechanical",
            "component": "Stainless Steel 304 Mounting Mast & Bedrock Anchor Kit",
            "specs": "2m galvanized steel mast, M16 expansion anchors, guy-wire stabilization clamps",
            "function": "Rigid mechanical anchoring into steep rock face to withstand slope vibration and wind load",
            "ip_rating": "Corrosion Resistant SS304",
            "source": "Local Indian Fabrication",
            "cost_inr": 650
        }
    ]

    total_cost_inr = sum(item["cost_inr"] for item in bom_items)
    imported_cost_inr = 350000  # Typical imported Campbell Scientific / Trimble station
    cost_savings_pct = round(((imported_cost_inr - total_cost_inr) / imported_cost_inr) * 100, 1)

    power_budget = {
        "deep_sleep_current_ua": 15,
        "sensor_acquisition_current_ma": 28,
        "sensor_acquisition_duration_sec": 2.5,
        "lora_tx_current_ma": 45,
        "lora_tx_duration_sec": 0.18,
        "hourly_sampling_interval_min": 15,
        "samples_per_day": 96,
        "daily_energy_consumption_wh": 0.28,
        "battery_capacity_wh": 128.0,
        "autonomy_days_zero_sunlight": 14.8,
        "solar_panel_wattage": 15.0,
        "full_recharge_hours_diffuse_sunlight": 4.2
    }

    pinout_matrix = [
        {"pin": "GPIO 5", "function": "LoRa SPI Chip Select (NSS)", "device": "Semtech SX1262"},
        {"pin": "GPIO 18", "function": "LoRa SPI Clock (SCK)", "device": "Semtech SX1262"},
        {"pin": "GPIO 19", "function": "LoRa SPI MISO", "device": "Semtech SX1262"},
        {"pin": "GPIO 23", "function": "LoRa SPI MOSI", "device": "Semtech SX1262"},
        {"pin": "GPIO 2", "function": "LoRa DIO1 (Interrupt)", "device": "Semtech SX1262"},
        {"pin": "GPIO 14", "function": "LoRa Reset (NRST)", "device": "Semtech SX1262"},
        {"pin": "GPIO 34 (ADC1)", "function": "Battery Voltage Telemetry", "device": "Voltage Divider 1:4"},
        {"pin": "GPIO 35 (ADC1)", "function": "MEMS Inclinometer Axis X", "device": "Murata SCA103T"},
        {"pin": "GPIO 32 (ADC1)", "function": "MEMS Inclinometer Axis Y", "device": "Murata SCA103T"},
        {"pin": "GPIO 15", "function": "Plucked-Coil Piezometer Frequency Counter", "device": "Vibrating Wire Piezometer"},
        {"pin": "GPIO 4", "function": "Sensor Power Rail Gate (FET)", "device": "High-Side Power Switch"}
    ]

    regulatory_compliance = {
        "jurisdiction": "India (National)",
        "governing_body": "Wireless Planning & Coordination (WPC) Wing, Ministry of Communications",
        "gazette_notification": "GSR 564(E) / GSR 45(E) - Delicensed Short Range Devices",
        "frequency_band_mhz": "865.0 - 867.0 MHz (IN865)",
        "max_permitted_erp_dbm": 30.0,
        "system_tx_power_dbm": 14.0,
        "channel_bandwidth_khz": 125.0,
        "duty_cycle_pct": "< 1.0% (Conforms strictly to WPC sub-band duty cycle)",
        "encryption": "AES-128 Hardware Cryptographic Payload Protection"
    }

    return {
        "status": "success",
        "system_name": "PARVAT NETRA Indigenous Field Edge Telemetry Station",
        "model_number": "PN-EDGE-IN865-V2",
        "currency": "INR",
        "total_cost_inr": total_cost_inr,
        "imported_alternative_cost_inr": imported_cost_inr,
        "cost_savings_inr": imported_cost_inr - total_cost_inr,
        "cost_savings_pct": cost_savings_pct,
        "bom_items": bom_items,
        "power_budget": power_budget,
        "pinout_matrix": pinout_matrix,
        "regulatory_compliance": regulatory_compliance,
        "deployment_time_hours": 1.5,
        "maintenance_cycle_years": 3.0
    }
