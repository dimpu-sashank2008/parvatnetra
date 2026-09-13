#!/usr/bin/env python3
"""
PARVAT NETRA -- Dynamic Emergency Bypass Rerouting & Critical Habitation Isolation Engine
Phase 13 / Research Sprint 3 (SIH Problem Statement ID: 26001)

Features:
  1. Habitation Critical Isolation Index (HCII) under Pillar 5 of Research Dossier:
       HCII = 100 * [ w_f*(1 - R_f/R_f,safe) + w_e*(1 - R_e/R_e,safe) + w_h*H_s + w_a*(1 - A_o) ]
  2. IRC SP:84 / SP:48 / MoRTH Mountain Freight Routing Cost Function:
       RouteCost = sum(T_base + P_gradient(G_eff, GVW) + P_curve(75/R) + P_closure(FS, rain) + P_overload)
  3. MoRTH Vehicle Classes: LIGHT_UTILITY, MEDIUM_RIGID_2AXLE, HEAVY_CONVOY_3AXLE, MULTI_AXLE_RELIEF_TRAIN.
  4. Multi-Bypass Comparison: NH-10 vs. Lava-Gorubathan vs. Mungpoo with vehicle-class routing.
  5. PostGIS State Synchronization and Resilient Connection Pooling.
"""

import os
import sys
import logging
import time
import psycopg2
from psycopg2.extras import RealDictCursor

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PARVAT_NETRA_ROUTING")

# -----------------------------------------------------------------------------
# MoRTH VEHICLE CLASSES & LOAD CEILINGS (April 2026 WIM / FASTag Standard)
# -----------------------------------------------------------------------------
MORHT_VEHICLE_CLASSES = {
    "LIGHT_UTILITY": {
        "class_id": "LIGHT_UTILITY",
        "name": "Light Utility / Ambulance / 4x4",
        "gvw_tonnes": 3.5,
        "max_limit_tonnes": 7.5,
        "description": "Ambulance, Quick Response Team, Small 4x4 Bolero/Gypsy"
    },
    "MEDIUM_RIGID_2AXLE": {
        "class_id": "MEDIUM_RIGID_2AXLE",
        "name": "Medium Rigid 2-Axle Truck",
        "gvw_tonnes": 16.2,
        "max_limit_tonnes": 18.5,
        "description": "Tata 407 / 1613 standard supply trucks"
    },
    "HEAVY_CONVOY_3AXLE": {
        "class_id": "HEAVY_CONVOY_3AXLE",
        "name": "Heavy Convoy 3-Axle Truck",
        "gvw_tonnes": 28.5,
        "max_limit_tonnes": 28.5,
        "description": "Army / NDRF 6x6 Heavy Logistics Carrier"
    },
    "MULTI_AXLE_RELIEF_TRAIN": {
        "class_id": "MULTI_AXLE_RELIEF_TRAIN",
        "name": "Multi-Axle Heavy Relief Train",
        "gvw_tonnes": 40.0,
        "max_limit_tonnes": 49.0,
        "description": "Modular bridge launcher, heavy earthmoving equipment, 40T grain convoy"
    }
}


def load_env(filepath='.env'):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())


def get_db_connection(max_retries=3, retry_delay=1.5):
    """
    Acquires a database connection to Neon PostGIS with retry logic
    and explicit connect_timeout for resilience.
    """
    load_env()
    db_url = os.environ.get('NEON_DB_URL') or os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("NEON_DB_URL environment variable is missing.")

    last_err = None
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor, connect_timeout=20)
            return conn
        except Exception as e:
            last_err = e
            logger.warning(f"DB connection attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
            time.sleep(retry_delay * (attempt + 1))

    raise RuntimeError(f"Failed to connect to Neon PostgreSQL after {max_retries} attempts: {last_err}")


# -----------------------------------------------------------------------------
# TASK 1: HABITATION CRITICAL ISOLATION INDEX (HCII)
# -----------------------------------------------------------------------------
def calculate_hcii(
    food_reserve_days: float,
    fuel_reserve_days: float,
    critical_patients: int,
    bed_capacity: int,
    helipad_operational_fraction: float,
    rf_safe: float = 15.0,
    re_safe: float = 10.0,
    w_f: float = 0.30,
    w_e: float = 0.25,
    w_h: float = 0.30,
    w_a: float = 0.15
):
    """
    Computes the Habitation Critical Isolation Index (HCII) under Pillar 5 of Research Dossier:
      HCII = 100 * [ w_f*(1 - R_f/R_f,safe) + w_e*(1 - R_e/R_e,safe) + w_h*H_s + w_a*(1 - A_o) ]

    Priors:
      - R_f,safe = 15.0 days (FCI godown food grain threshold)
      - R_e,safe = 10.0 days (Fuel / LPG emergency buffer)
      - H_s = min(critical_patients / max(bed_capacity, 1), 1.0)
      - A_o in [0.0, 1.0]: Helipad operational readiness fraction

    Tiers:
      - HCII >= 75.0: CRITICAL_AIR_DROP_REQUIRED (Helicopter airlift mandatory)
      - 50.0 <= HCII < 75.0: ACUTE_SHORTAGE_THREATENED (Secondary ridge foot/mule track supply)
      - 25.0 <= HCII < 50.0: MONITORED_WATCH
      - HCII < 25.0: STABLE_RESERVES
    """
    # 1. Food grain depletion term: clamped in [0.0, 1.0]
    food_ratio = min(max(float(food_reserve_days) / max(rf_safe, 1.0), 0.0), 1.0)
    food_depletion = 1.0 - food_ratio
    food_term = w_f * food_depletion

    # 2. Fuel / energy depletion term: clamped in [0.0, 1.0]
    fuel_ratio = min(max(float(fuel_reserve_days) / max(re_safe, 1.0), 0.0), 1.0)
    fuel_depletion = 1.0 - fuel_ratio
    fuel_term = w_e * fuel_depletion

    # 3. Healthcare surge saturation stress ratio: clamped in [0.0, 1.0]
    eff_capacity = max(int(bed_capacity), 1)
    health_stress = min(max(float(critical_patients) / eff_capacity, 0.0), 1.0)
    health_term = w_h * health_stress

    # 4. Helipad operational readiness fraction A_o: clamped in [0.0, 1.0]
    helipad_frac = min(max(float(helipad_operational_fraction), 0.0), 1.0)
    airlift_deficit = 1.0 - helipad_frac
    airlift_term = w_a * airlift_deficit

    # Composite sum
    composite = food_term + fuel_term + health_term + airlift_term
    hcii_score = round(max(min(composite * 100.0, 100.0), 0.0), 1)

    if hcii_score >= 75.0:
        hcii_tier = "CRITICAL_AIR_DROP_REQUIRED"
    elif hcii_score >= 50.0:
        hcii_tier = "ACUTE_SHORTAGE_THREATENED"
    elif hcii_score >= 25.0:
        hcii_tier = "MONITORED_WATCH"
    else:
        hcii_tier = "STABLE_RESERVES"

    breakdown = {
        "food_term": round(food_term * 100.0, 2),
        "fuel_term": round(fuel_term * 100.0, 2),
        "health_term": round(health_term * 100.0, 2),
        "airlift_term": round(airlift_term * 100.0, 2),
        "weights": {"w_f": w_f, "w_e": w_e, "w_h": w_h, "w_a": w_a},
        "inputs": {
            "food_reserve_days": float(food_reserve_days),
            "fuel_reserve_days": float(fuel_reserve_days),
            "critical_patients": int(critical_patients),
            "bed_capacity": int(bed_capacity),
            "helipad_operational_fraction": float(helipad_operational_fraction)
        }
    }

    return hcii_score, hcii_tier, breakdown


# -----------------------------------------------------------------------------
# TASK 2: IRC SP:84 / SP:48 / MoRTH FREIGHT ROUTING COST FUNCTION
# -----------------------------------------------------------------------------
def calculate_effective_gradient(nominal_gradient_pct: float, curve_radius_m: float) -> float:
    """
    IRC SP:48 / SP:84 curve-compensated gradient:
      G_eff = G - 75 / R (minimum 4.0% to preserve surface drainage).
    """
    comp = 75.0 / max(float(curve_radius_m), 1.0)
    g_eff = float(nominal_gradient_pct) - comp
    return round(max(g_eff, 4.0), 2)


def calculate_route_cost(
    base_duration_hrs: float,
    length_km: float,
    nominal_gradient_pct: float,
    curve_radius_m: float,
    gvw_tonnes: float,
    max_tonnage_tonnes: float,
    is_closed: bool = False,
    fs_val: float = 1.5,
    rainfall_breached: bool = False
) -> dict:
    """
    Evaluates segment RouteCost under IRC SP:84 / MoRTH Mountain Freight Routing:
      RouteCost = T_base + P_gradient(G_eff, GVW) + P_curve(75/R) + P_closure(FS, rain) + P_overload(GVW, max_tonnage)
    """
    g_eff = calculate_effective_gradient(nominal_gradient_pct, curve_radius_m)
    ruling_gradient = 5.0  # IRC SP:84 ruling gradient (1:20)

    # 1. Gradient penalty for heavy convoys exceeding ruling gradient (GVW > 28.5 t)
    p_gradient = 0.0
    if gvw_tonnes > 28.5 and g_eff > ruling_gradient:
        p_gradient = round(15.0 * ((g_eff - ruling_gradient) ** 2), 2)

    # 2. Curve compensation penalty
    curve_comp = 75.0 / max(float(curve_radius_m), 1.0)
    p_curve = round(0.05 * curve_comp, 2)

    # 3. Closure penalty (landslide debris or physics instability FS < 1.0)
    p_closure = 0.0
    if is_closed or fs_val < 1.0 or rainfall_breached:
        p_closure = 999.0

    # 4. Overload penalty under April 2026 automated WIM / FASTag rules
    p_overload = 0.0
    overload_pct = 0.0
    if gvw_tonnes > max_tonnage_tonnes and max_tonnage_tonnes > 0:
        overload_ratio = (gvw_tonnes - max_tonnage_tonnes) / max_tonnage_tonnes
        overload_pct = round(overload_ratio * 100.0, 1)
        if overload_ratio > 0.40:
            p_overload = round(4.0 * float(base_duration_hrs), 2)
        elif overload_ratio > 0.10:
            p_overload = round(2.0 * float(base_duration_hrs), 2)
        else:
            p_overload = round(0.5 * float(base_duration_hrs), 2)

    total_cost_hrs = round(float(base_duration_hrs) + p_gradient + p_curve + p_closure + p_overload, 2)

    return {
        "base_duration_hrs": float(base_duration_hrs),
        "length_km": float(length_km),
        "nominal_gradient_pct": float(nominal_gradient_pct),
        "curve_radius_m": float(curve_radius_m),
        "effective_gradient_pct": g_eff,
        "gvw_tonnes": float(gvw_tonnes),
        "max_tonnage_tonnes": float(max_tonnage_tonnes),
        "p_gradient_hrs": p_gradient,
        "p_curve_hrs": p_curve,
        "p_closure_hrs": p_closure,
        "p_overload_hrs": p_overload,
        "overload_pct": overload_pct,
        "total_route_cost_hrs": total_cost_hrs,
        "is_passable": (p_closure == 0.0) and (total_cost_hrs < 500.0)
    }


# -----------------------------------------------------------------------------
# ROUTING ENGINE CLASS
# -----------------------------------------------------------------------------
class EmergencyRoutingEngine:
    """
    Evaluates highway connectivity, IRC mountain freight corridors, and settlement isolation states.
    """
    def __init__(self, conn=None):
        self.conn = conn or get_db_connection()
        self.normal_nh10_duration_hrs = 2.0
        self.normal_nh10_length_km = 52.0

    def check_primary_road_blockage(self):
        """
        Determines if strategic NH-10 is impassable by inspecting:
          1. AI detected scars intersecting lifeline roads (is_road_blocked = True).
          2. Recent RED hazard evaluations in ml_risk_scores with road buffer collision.
        """
        cur = self.conn.cursor()
        
        # Check active AI detected scars
        cur.execute("""
            SELECT COUNT(*) AS count
            FROM ai_detected_scars
            WHERE is_road_blocked = TRUE;
        """)
        scar_blockage_count = cur.fetchone()["count"]

        # Check recent RED ML risk scores intersecting NH-10
        cur.execute("""
            SELECT COUNT(*) AS count
            FROM ml_risk_scores m
            JOIN static_terrain t ON m.region_name = t.region_name
            JOIN lifeline_roads r ON ST_Intersects(t.geom, ST_Buffer(r.geom::geography, 500)::geometry)
            WHERE m.severity_label = 'RED' AND r.road_code = 'NH-10';
        """)
        red_zone_count = cur.fetchone()["count"]
        cur.close()

        is_blocked = (scar_blockage_count > 0) or (red_zone_count > 0)
        status_text = "BLOCKED / PASSAGE DENIED" if is_blocked else "CLEAR / NORMAL FLOW"
        
        reasons = []
        if scar_blockage_count > 0:
            reasons.append(f"{scar_blockage_count} Active Satellite AI Debris Blockage(s)")
        if red_zone_count > 0:
            reasons.append(f"{red_zone_count} Critical RED Hazard Zone(s) on NH-10 Corridor")

        # Evaluate route cost for NH-10
        cost_info = calculate_route_cost(
            base_duration_hrs=self.normal_nh10_duration_hrs,
            length_km=self.normal_nh10_length_km,
            nominal_gradient_pct=3.5,
            curve_radius_m=120.0,
            gvw_tonnes=28.5,
            max_tonnage_tonnes=45.0,
            is_closed=is_blocked
        )

        return {
            "road_code": "NH-10",
            "road_name": "Siliguri-Gangtok National Highway 10",
            "is_blocked": is_blocked,
            "status": status_text,
            "normal_duration_hrs": self.normal_nh10_duration_hrs,
            "normal_length_km": self.normal_nh10_length_km,
            "route_cost_hrs": cost_info["total_route_cost_hrs"],
            "cost_breakdown": cost_info,
            "primary_driver": " | ".join(reasons) if reasons else "No major hazards detected on primary axis."
        }

    def evaluate_bypass_routes(self, gvw_class="LIGHT_UTILITY"):
        """
        Queries bypass_corridors, calculates IRC SP:84 RouteCosts across vehicle classes,
        and determines optimal detour recommendations.
        """
        v_info = MORHT_VEHICLE_CLASSES.get(gvw_class, MORHT_VEHICLE_CLASSES["LIGHT_UTILITY"])
        current_gvw = v_info["gvw_tonnes"]

        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                route_id,
                corridor_code,
                name,
                via_settlements,
                surface_type,
                max_tonnage_tonnes::float AS max_tonnage_tonnes,
                length_km::float AS length_km,
                normal_duration_hrs::float AS normal_duration_hrs,
                COALESCE(ruling_gradient_pct, 5.0)::float AS ruling_gradient_pct,
                COALESCE(min_curve_radius_m, 50.0)::float AS min_curve_radius_m,
                status,
                ST_AsGeoJSON(geom)::json AS geometry
            FROM bypass_corridors
            ORDER BY normal_duration_hrs ASC;
        """)
        rows = cur.fetchall()
        cur.close()

        bypasses = []
        for r in rows:
            dur = r["normal_duration_hrs"]
            delay = round(dur - self.normal_nh10_duration_hrs, 1)
            is_heavy_feasible = r["max_tonnage_tonnes"] >= 28.5

            # Compute route cost for the requested GVW class
            cost_info = calculate_route_cost(
                base_duration_hrs=dur,
                length_km=r["length_km"],
                nominal_gradient_pct=r["ruling_gradient_pct"],
                curve_radius_m=r["min_curve_radius_m"],
                gvw_tonnes=current_gvw,
                max_tonnage_tonnes=r["max_tonnage_tonnes"],
                is_closed=(r["status"] != "OPEN")
            )

            tonnage_advisory = (
                f"Heavy Multi-Axle Approved (Up to {r['max_tonnage_tonnes']}T)"
                if is_heavy_feasible
                else f"RESTRICTED: Light/Medium Axle Only (Max {r['max_tonnage_tonnes']}T)"
            )

            bypasses.append({
                "route_id": r["route_id"],
                "corridor_code": r["corridor_code"],
                "name": r["name"],
                "via_settlements": r["via_settlements"],
                "surface_type": r["surface_type"],
                "max_tonnage_tonnes": r["max_tonnage_tonnes"],
                "length_km": r["length_km"],
                "duration_hrs": dur,
                "delay_penalty_hrs": delay,
                "ruling_gradient_pct": r["ruling_gradient_pct"],
                "min_curve_radius_m": r["min_curve_radius_m"],
                "effective_gradient_pct": cost_info["effective_gradient_pct"],
                "route_cost_hrs": cost_info["total_route_cost_hrs"],
                "cost_breakdown": cost_info,
                "status": r["status"],
                "is_heavy_feasible": is_heavy_feasible,
                "tonnage_advisory": tonnage_advisory,
                "geometry": r["geometry"]
            })

        # Multi-class Fleet Matrix Evaluation
        fleet_matrix = {}
        for cls_key, cls_spec in MORHT_VEHICLE_CLASSES.items():
            gvw = cls_spec["gvw_tonnes"]
            evaluated = []
            for b in bypasses:
                cost = calculate_route_cost(
                    base_duration_hrs=b["duration_hrs"],
                    length_km=b["length_km"],
                    nominal_gradient_pct=b["ruling_gradient_pct"],
                    curve_radius_m=b["min_curve_radius_m"],
                    gvw_tonnes=gvw,
                    max_tonnage_tonnes=b["max_tonnage_tonnes"],
                    is_closed=(b["status"] != "OPEN")
                )
                evaluated.append({
                    "corridor_code": b["corridor_code"],
                    "name": b["name"],
                    "route_cost_hrs": cost["total_route_cost_hrs"],
                    "cost_breakdown": cost,
                    "is_passable": cost["is_passable"]
                })
            
            # Select best corridor for this vehicle class
            passable = [e for e in evaluated if e["is_passable"]]
            passable.sort(key=lambda x: x["route_cost_hrs"])
            best = passable[0] if passable else (evaluated[0] if evaluated else None)

            fleet_matrix[cls_key] = {
                "vehicle_name": cls_spec["name"],
                "gvw_tonnes": gvw,
                "recommended_corridor": best["corridor_code"] if best else None,
                "recommended_name": best["name"] if best else None,
                "route_cost_hrs": best["route_cost_hrs"] if best else None,
                "all_corridor_costs": {e["corridor_code"]: e["route_cost_hrs"] for e in evaluated}
            }

        # Select top recommendation for current requested gvw_class
        passable_current = [b for b in bypasses if b["cost_breakdown"]["is_passable"]]
        passable_current.sort(key=lambda x: x["route_cost_hrs"])

        if passable_current:
            recommended = passable_current[0]
        else:
            recommended = bypasses[0] if bypasses else None

        return bypasses, recommended, fleet_matrix, v_info

    def evaluate_and_update_habitations(self, is_primary_blocked):
        """
        Evaluates HCII (Habitation Critical Isolation Index) for all settlements,
        maps isolation tiers, and persists state to Neon PostGIS.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 
                habitation_id,
                name,
                district,
                population,
                primary_road_id,
                has_functional_phc,
                has_helipad,
                grain_reserve_days,
                fuel_reserve_days,
                COALESCE(critical_patients, 0) AS critical_patients,
                COALESCE(bed_capacity, 10) AS bed_capacity,
                COALESCE(helipad_operational_fraction, 1.0)::float AS helipad_operational_fraction,
                COALESCE(hcii_score, 0.0)::float AS hcii_score,
                COALESCE(hcii_tier, 'STABLE_RESERVES') AS hcii_tier,
                isolation_status,
                ST_AsGeoJSON(geom)::json AS geometry
            FROM critical_habitations
            ORDER BY habitation_id ASC;
        """)
        habs = cur.fetchall()

        updated_habs = []
        for h in habs:
            # 1. Compute standardized HCII score & tier
            score, tier, breakdown = calculate_hcii(
                food_reserve_days=h["grain_reserve_days"],
                fuel_reserve_days=h["fuel_reserve_days"],
                critical_patients=h["critical_patients"],
                bed_capacity=h["bed_capacity"],
                helipad_operational_fraction=h["helipad_operational_fraction"]
            )

            # 2. Legacy isolation_status mapping for Phase 13 compatibility
            has_heli = bool(h["has_helipad"])
            is_depleted = (h["fuel_reserve_days"] < 5) or (h["grain_reserve_days"] < 5)
            
            if is_primary_blocked:
                if is_depleted and has_heli:
                    legacy_status = "ISOLATED_AIR_ONLY"
                elif tier == "CRITICAL_AIR_DROP_REQUIRED" and has_heli:
                    legacy_status = "ISOLATED_AIR_ONLY"
                else:
                    legacy_status = "THREATENED"
            else:
                if tier in ("CRITICAL_AIR_DROP_REQUIRED", "ACUTE_SHORTAGE_THREATENED"):
                    legacy_status = "THREATENED"
                else:
                    legacy_status = "NORMAL"

            # Persist updated HCII and legacy status to PostGIS
            cur.execute("""
                UPDATE critical_habitations
                SET hcii_score = %s,
                    hcii_tier = %s,
                    isolation_status = %s
                WHERE habitation_id = %s;
            """, (score, tier, legacy_status, h["habitation_id"]))

            # Evacuation and Humanitarian Channel Advisory
            if tier == "CRITICAL_AIR_DROP_REQUIRED":
                evac_channel = (
                    "IAF/Army Aviation ALH & Mi-17 Tactical Helipad Air-Drop Mandatory"
                    if has_heli else
                    "IAF/Army Aviation ALH Tactical Winch Drop (Helipad Grounded/None) & Emergency Foot Porters"
                )
            elif tier == "ACUTE_SHORTAGE_THREATENED":
                evac_channel = (
                    "Secondary Ridge Foot/Mule Track Emergency Supply & Tactical Helipad Standby"
                    if has_heli else
                    "Secondary Ridge Foot/Mule Track Porter Delivery Only (No Air Capability)"
                )
            elif tier == "MONITORED_WATCH":
                evac_channel = "Secondary Feeder Corridor & Monitored Commercial Reserves"
            else:
                evac_channel = "Primary Arterial Highway Flow (Stable FCI & Civil Buffer)"

            updated_habs.append({
                "habitation_id": h["habitation_id"],
                "name": h["name"],
                "district": h["district"],
                "population": h["population"],
                "has_functional_phc": bool(h["has_functional_phc"]),
                "has_helipad": has_heli,
                "grain_reserve_days": h["grain_reserve_days"],
                "fuel_reserve_days": h["fuel_reserve_days"],
                "critical_patients": h["critical_patients"],
                "bed_capacity": h["bed_capacity"],
                "helipad_operational_fraction": h["helipad_operational_fraction"],
                "hcii_score": score,
                "hcii_tier": tier,
                "isolation_tier": tier,
                "hcii_breakdown": breakdown,
                "isolation_status": legacy_status,
                "evacuation_channel": evac_channel,
                "geometry": h["geometry"]
            })

        self.conn.commit()
        cur.close()
        return updated_habs

    def run_routing_cycle(self, gvw_class="LIGHT_UTILITY"):
        """
        Executes complete routing cycle: checks primary road, evaluates bypasses, updates habitations.
        """
        primary = self.check_primary_road_blockage()
        bypasses, recommended, fleet_matrix, vspec = self.evaluate_bypass_routes(gvw_class=gvw_class)
        habitations = self.evaluate_and_update_habitations(primary["is_blocked"])

        isolated_count = sum(1 for h in habitations if h["isolation_status"] == "ISOLATED_AIR_ONLY")
        threatened_count = sum(1 for h in habitations if h["isolation_status"] == "THREATENED")

        return {
            "primary_road": primary,
            "recommended_detour": recommended,
            "bypass_routes": bypasses,
            "fleet_matrix": fleet_matrix,
            "gvw_class": gvw_class,
            "vehicle_spec": vspec,
            "habitations": habitations,
            "isolation_summary": {
                "total_monitored": len(habitations),
                "isolated_air_only": isolated_count,
                "threatened": threatened_count,
                "normal": len(habitations) - isolated_count - threatened_count,
                "critical_air_drop": sum(1 for h in habitations if h.get("hcii_tier") == "CRITICAL_AIR_DROP_REQUIRED"),
                "acute_shortage": sum(1 for h in habitations if h.get("hcii_tier") == "ACUTE_SHORTAGE_THREATENED"),
                "monitored_watch": sum(1 for h in habitations if h.get("hcii_tier") == "MONITORED_WATCH"),
                "stable_reserves": sum(1 for h in habitations if h.get("hcii_tier") == "STABLE_RESERVES")
            }
        }


def get_evacuation_plan(conn=None, gvw_class="LIGHT_UTILITY"):
    engine = EmergencyRoutingEngine(conn)
    cycle = engine.run_routing_cycle(gvw_class=gvw_class)
    return {
        "status": "SUCCESS",
        "primary_road": cycle["primary_road"],
        "recommended_detour": cycle["recommended_detour"],
        "bypass_routes": cycle["bypass_routes"],
        "gvw_class": cycle["gvw_class"],
        "vehicle_spec": cycle["vehicle_spec"],
        "fleet_matrix": cycle["fleet_matrix"]
    }


def get_isolation_matrix(conn=None):
    engine = EmergencyRoutingEngine(conn)
    cycle = engine.run_routing_cycle()
    return {
        "status": "SUCCESS",
        "summary": cycle["isolation_summary"],
        "primary_road_status": cycle["primary_road"]["status"],
        "habitations": cycle["habitations"]
    }


if __name__ == "__main__":
    print("=" * 80)
    print("PARVAT NETRA -- DYNAMIC EMERGENCY BYPASS REROUTING & ISOLATION MATRIX")
    print("Phase 13 / Research Sprint 3 (SIH Problem Statement ID: 26001)")
    print("=" * 80)

    engine = EmergencyRoutingEngine()
    
    # Test for LIGHT_UTILITY and MULTI_AXLE_RELIEF_TRAIN
    for test_class in ["LIGHT_UTILITY", "MULTI_AXLE_RELIEF_TRAIN"]:
        print(f"\n" + "-" * 70)
        print(f"EVALUATING FLEET PROFILE: [{test_class}]")
        print("-" * 70)
        result = engine.run_routing_cycle(gvw_class=test_class)
        rec = result["recommended_detour"]
        vspec = result["vehicle_spec"]
        
        print(f"Vehicle: {vspec['name']} | GVW: {vspec['gvw_tonnes']}T (Max Limit: {vspec['max_limit_tonnes']}T)")
        if rec:
            cb = rec["cost_breakdown"]
            print(f"Recommended Corridor : {rec['corridor_code']} - {rec['name']}")
            print(f"  Length / Duration  : {rec['length_km']} km | Base Time: {rec['duration_hrs']} hrs")
            print(f"  Effective Gradient : {cb['effective_gradient_pct']}% (Ruling: 5.0%)")
            print(f"  Gradient Penalty   : +{cb['p_gradient_hrs']} hrs")
            print(f"  Overload Penalty   : +{cb['p_overload_hrs']} hrs (Overload: {cb['overload_pct']}%)")
            print(f"  Total Route Cost   : {cb['total_route_cost_hrs']} hrs")

    # Habitation Matrix
    print(f"\n" + "=" * 80)
    print("[HABITATION CRITICAL ISOLATION MATRIX (HCII)]")
    print("=" * 80)
    for h in result["habitations"]:
        b = h["hcii_breakdown"]
        print(f"\n* [{h['hcii_tier']}] {h['name']} ({h['district']}) -- HCII Score: {h['hcii_score']}/100")
        print(f"    Food Depletion : {b['food_term']:.2f} pts (Reserves: {h['grain_reserve_days']} days)")
        print(f"    Fuel Depletion : {b['fuel_term']:.2f} pts (Reserves: {h['fuel_reserve_days']} days)")
        print(f"    Health Stress  : {b['health_term']:.2f} pts (Patients: {h['critical_patients']}/{h['bed_capacity']})")
        print(f"    Airlift Deficit: {b['airlift_term']:.2f} pts (Helipad Fraction: {h['helipad_operational_fraction']})")
        print(f"    Channel        : {h['evacuation_channel']}")
