# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Offline Last-Known GPS Position Tracking Cache for Search and Rescue (SAR)
Phase 7: Offline Device Cache & NDRF Rescue Targeting
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Features:
1. Ingests client telemetry heartbeats: { device_id, lat, lng, timestamp, battery_level }.
2. Tracks devices within the 15 km hazard perimeter (NH-10 Km 48 epicenter).
3. If a device inside the hazard zone has no heartbeat for > 120 seconds,
   flags as OFFLINE_DISCONNECTED and marks as a high-priority SAR TARGET for NDRF.
"""

import math
import time
import logging
import threading
from datetime import datetime, timezone

logger = logging.getLogger("PARVAT_NETRA_SAR")

# Earth radius in kilometers
R_EARTH_KM = 6371.0


def calculate_haversine_km(lat1, lon1, lat2, lon2):
    """Accurate great-circle distance between two GPS coordinates."""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2.0) ** 2 +
         math.cos(p1) * math.cos(p2) * (math.sin(dl / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R_EARTH_KM * c, 3)


class SARTrackingService:
    """
    In-memory tracking cache with persistent state for disconnected devices.
    """

    HAZARD_EPICENTER_LAT = 27.2010
    HAZARD_EPICENTER_LNG = 88.5180
    HAZARD_RADIUS_KM = 15.0
    DISCONNECT_TIMEOUT_SEC = 120.0  # Silent > 120s indicates signal severance or slide burial

    def __init__(self):
        self.lock = threading.Lock()
        self.devices = {}
        self._seed_initial_targets()

    def _seed_initial_targets(self):
        """Seed realistic mountain corridor vehicles and devices for instant operational demonstration."""
        now = time.time()
        
        # Target 1: Tourist Taxi stranded near Likhu Veer / 29th Mile
        self.devices["DEV-SAR-088"] = {
            "device_id": "DEV-SAR-088",
            "name": "Tourist Taxi SK-01-T-4912",
            "type": "LIGHT_COMMERCIAL_VEHICLE",
            "driver_or_contact": "Pema Lepcha (+91 98320-41982)",
            "passengers": 4,
            "lat": 27.2035,
            "lng": 88.5160,
            "altitude_m": 420.0,
            "battery_level": 34,
            "last_seen_epoch": now - 145.0,  # 145s silent (> 120s threshold)
            "sector": "NH-10 Km 48 (Likhu Veer Chasm)",
            "status": "OFFLINE_DISCONNECTED",
            "is_sar_target": True,
            "ndrf_dispatched": True,
            "notes": "Vehicle GPS signal severed abruptly following rockfall report."
        }

        # Target 2: Sikkim Nationalised Transport Bus
        self.devices["DEV-SAR-104"] = {
            "device_id": "DEV-SAR-104",
            "name": "SNT Bus Gangtok-Siliguri (SNT-219)",
            "type": "HEAVY_PASSENGER_BUS",
            "driver_or_contact": "Subash Rai (SNT Central Control)",
            "passengers": 18,
            "lat": 27.1980,
            "lng": 88.5210,
            "altitude_m": 395.0,
            "battery_level": 62,
            "last_seen_epoch": now - 210.0,  # 210s silent (> 120s threshold)
            "sector": "NH-10 Km 48 (29th Mile Road Cut)",
            "status": "OFFLINE_DISCONNECTED",
            "is_sar_target": True,
            "ndrf_dispatched": False,
            "notes": "Cell tower telemetry dropped. Last ping indicates stalled near slip zone."
        }

        # Target 3: Field Volunteer Doma (Active & Online)
        self.devices["DEV-SAR-205"] = {
            "device_id": "DEV-SAR-205",
            "name": "Field Volunteer Doma (Singtam)",
            "type": "MOBILE_VOLUNTEER_APP",
            "driver_or_contact": "Doma Bhutia (Disaster Response Cell)",
            "passengers": 1,
            "lat": 27.2340,
            "lng": 88.4980,
            "altitude_m": 350.0,
            "battery_level": 91,
            "last_seen_epoch": now - 12.0,  # 12s silent (Online)
            "sector": "Singtam Safe Staging Area",
            "status": "ONLINE",
            "is_sar_target": False,
            "ndrf_dispatched": False,
            "notes": "Active field observer reporting telemetry from safe staging outpost."
        }

    def record_ping(self, device_id, lat, lng, battery_level=100, name=None, driver_or_contact=None, passengers=1, notes=None):
        """
        Receives client telemetry ping, computes distance to hazard centroid,
        and updates device position in cache.
        """
        now = time.time()
        lat = float(lat)
        lng = float(lng)
        battery_level = int(battery_level)

        dist_km = calculate_haversine_km(self.HAZARD_EPICENTER_LAT, self.HAZARD_EPICENTER_LNG, lat, lng)
        inside_hazard = dist_km <= self.HAZARD_RADIUS_KM

        with self.lock:
            existing = self.devices.get(device_id, {})
            device_record = {
                "device_id": device_id,
                "name": name or existing.get("name") or f"Device-{device_id}",
                "type": existing.get("type") or "CITIZEN_MOBILE",
                "driver_or_contact": driver_or_contact or existing.get("driver_or_contact") or "Citizen Traveler",
                "passengers": passengers or existing.get("passengers", 1),
                "lat": lat,
                "lng": lng,
                "altitude_m": existing.get("altitude_m", 410.0),
                "battery_level": battery_level,
                "last_seen_epoch": now,
                "last_seen_iso": datetime.now(timezone.utc).isoformat(),
                "distance_to_epicenter_km": dist_km,
                "inside_hazard_zone": inside_hazard,
                "sector": existing.get("sector") or ("NH-10 Km 48 Sector" if inside_hazard else "Regional Corridor"),
                "status": "ONLINE",
                "is_sar_target": False,
                "ndrf_dispatched": existing.get("ndrf_dispatched", False),
                "notes": notes or existing.get("notes") or "Telemetry heartbeat active."
            }
            self.devices[device_id] = device_record
            logger.debug(f"[SAR TRACKING] Heartbeat recorded for {device_id} ({lat}, {lng}, Bat: {battery_level}%)")
            return dict(device_record)

    def get_devices(self):
        """
        Returns all tracked devices, evaluating offline disconnection status in real time.
        """
        now = time.time()
        results = []

        with self.lock:
            for dev_id, dev in self.devices.items():
                rec = dict(dev)
                elapsed = max(0.0, now - rec["last_seen_epoch"])
                rec["seconds_since_ping"] = int(elapsed)

                # Recompute distance
                dist_km = calculate_haversine_km(
                    self.HAZARD_EPICENTER_LAT, self.HAZARD_EPICENTER_LNG,
                    rec["lat"], rec["lng"]
                )
                rec["distance_to_epicenter_km"] = dist_km
                rec["inside_hazard_zone"] = (dist_km <= self.HAZARD_RADIUS_KM)

                # Offline Disconnect Rule:
                # If inside 15 km hazard zone and silent for > 120 seconds -> OFFLINE_DISCONNECTED
                if rec["inside_hazard_zone"] and elapsed > self.DISCONNECT_TIMEOUT_SEC:
                    rec["status"] = "OFFLINE_DISCONNECTED"
                    rec["is_sar_target"] = True
                elif elapsed <= self.DISCONNECT_TIMEOUT_SEC:
                    rec["status"] = "ONLINE"
                    rec["is_sar_target"] = False

                # Format human readable elapsed time
                if elapsed < 60:
                    rec["elapsed_display"] = f"{int(elapsed)}s ago"
                elif elapsed < 3600:
                    rec["elapsed_display"] = f"{int(elapsed // 60)}m {int(elapsed % 60)}s ago"
                else:
                    rec["elapsed_display"] = f"{round(elapsed / 3600.0, 1)}h ago"

                results.append(rec)

        # Sort with SAR targets first, then most recently seen
        results.sort(key=lambda x: (not x.get("is_sar_target", False), x.get("seconds_since_ping", 0)))
        return results

    def simulate_disconnect(self, device_id, silent_seconds=150.0):
        """
        Forces a device into OFFLINE_DISCONNECTED state for testing/demonstration.
        """
        with self.lock:
            if device_id in self.devices:
                dev = self.devices[device_id]
                dev["last_seen_epoch"] = time.time() - float(silent_seconds)
                dist_km = calculate_haversine_km(
                    self.HAZARD_EPICENTER_LAT, self.HAZARD_EPICENTER_LNG,
                    dev["lat"], dev["lng"]
                )
                dev["distance_to_epicenter_km"] = dist_km
                dev["inside_hazard_zone"] = (dist_km <= self.HAZARD_RADIUS_KM)
                if dev["inside_hazard_zone"] and float(silent_seconds) > self.DISCONNECT_TIMEOUT_SEC:
                    dev["status"] = "OFFLINE_DISCONNECTED"
                    dev["is_sar_target"] = True
                return dev
            else:
                # Create and disconnect
                now = time.time()
                self.devices[device_id] = {
                    "device_id": device_id,
                    "name": f"Vehicle {device_id}",
                    "type": "SIMULATED_VEHICLE",
                    "driver_or_contact": "Simulated Traveler",
                    "passengers": 2,
                    "lat": 27.2020,
                    "lng": 88.5175,
                    "altitude_m": 415.0,
                    "battery_level": 45,
                    "last_seen_epoch": now - float(silent_seconds),
                    "sector": "NH-10 Km 48 Chasm",
                    "status": "OFFLINE_DISCONNECTED",
                    "is_sar_target": True,
                    "ndrf_dispatched": False,
                    "notes": "Simulated abrupt communication failure."
                }
                return self.devices[device_id]

    def flag_devices_in_hazard_zone(self, sector=None, radius_km=15.0):
        """Flags offline and high-risk traveler devices within the hazard radius for NDRF SAR extrication."""
        flagged = []
        with self.lock:
            for dev_id, dev in self.devices.items():
                dist = dev.get("distance_to_epicenter_km", 0.0)
                if dist <= radius_km or dev.get("inside_hazard_zone"):
                    dev["is_sar_target"] = True
                    flagged.append(dict(dev))
        logger.info(f"[SAR TRACKING] Proactively flagged {len(flagged)} traveler devices for SAR in {sector or 'corridor'}")
        return flagged


# Global singleton
SAR_TRACKING_SERVICE = SARTrackingService()
