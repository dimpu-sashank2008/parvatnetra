# -*- coding: utf-8 -*-
"""
engine/terrain_analysis.py
==========================
PARVAT NETRA • Topographic & Terrain Derivative Engine
------------------------------------------------------
Calculates physical morphometric slope features directly from Digital Elevation Models:
  1. Slope Angle (degrees) - Horn's 3x3 finite-difference convolution
  2. Aspect Angle (degrees clockwise from North)
  3. Planform and Profile Curvature (Zevenbergen-Thorne polynomial coefficients)
  4. Analytical Hillshade Shading (Azimuth 315°, Altitude 45°)
  5. Elevation Contours (5m, 10m, 20m, 50m selectable intervals)

Author: PARVAT NETRA / PAHAD AI Core Engineering Team
Problem Statement: SIH 26001
"""

from __future__ import annotations

import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


def calculate_slope(elevation_grid: np.ndarray, cell_size_m: float = 30.0) -> np.ndarray:
    """
    Computes terrain slope angle in degrees using Horn's 3x3 finite difference convolution:
      dz/dx = ((c + 2f + i) - (a + 2d + g)) / (8 * cell_size)
      dz/dy = ((g + 2h + i) - (a + 2b + c)) / (8 * cell_size)
      slope_rad = arctan(sqrt((dz/dx)^2 + (dz/dy)^2))
      slope_deg = slope_rad * (180 / pi)
    """
    z = np.asarray(elevation_grid, dtype=np.float64)
    rows, cols = z.shape
    dx = float(cell_size_m)
    dy = float(cell_size_m)

    slope_deg = np.zeros_like(z)

    # Interior pixels
    #   [a b c]
    #   [d e f]
    #   [g h i]
    a = z[0:-2, 0:-2]
    b = z[0:-2, 1:-1]
    c = z[0:-2, 2:]
    d = z[1:-1, 0:-2]
    f = z[1:-1, 2:]
    g = z[2:, 0:-2]
    h = z[2:, 1:-1]
    i = z[2:, 2:]

    dz_dx = ((c + 2.0 * f + i) - (a + 2.0 * d + g)) / (8.0 * dx)
    dz_dy = ((g + 2.0 * h + i) - (a + 2.0 * b + c)) / (8.0 * dy)

    grad = np.sqrt(dz_dx ** 2 + dz_dy ** 2)
    slope_deg[1:-1, 1:-1] = np.degrees(np.arctan(grad))

    # Pad boundary with adjacent inner values
    slope_deg[0, :] = slope_deg[1, :]
    slope_deg[-1, :] = slope_deg[-2, :]
    slope_deg[:, 0] = slope_deg[:, 1]
    slope_deg[:, -1] = slope_deg[:, -2]

    return np.clip(slope_deg, 0.0, 89.9)


def calculate_aspect(elevation_grid: np.ndarray, cell_size_m: float = 30.0) -> np.ndarray:
    """
    Computes topographic aspect angle in degrees (0° - 360° clockwise from North,
    with -1 for flat surfaces).
    """
    z = np.asarray(elevation_grid, dtype=np.float64)
    dx = float(cell_size_m)
    dy = float(cell_size_m)

    aspect_deg = np.full_like(z, 135.0)  # Default southeast (Himalayan monsoon facing)

    a = z[0:-2, 0:-2]
    c = z[0:-2, 2:]
    d = z[1:-1, 0:-2]
    f = z[1:-1, 2:]
    g = z[2:, 0:-2]
    i = z[2:, 2:]
    b = z[0:-2, 1:-1]
    h = z[2:, 1:-1]

    dz_dx = ((c + 2.0 * f + i) - (a + 2.0 * d + g)) / (8.0 * dx)
    dz_dy = ((g + 2.0 * h + i) - (a + 2.0 * b + c)) / (8.0 * dy)

    # Mathematical aspect in radians
    aspect_rad = np.arctan2(dz_dy, -dz_dx)
    # Convert to compass degrees (clockwise from North)
    compass = 90.0 - np.degrees(aspect_rad)
    compass = np.where(compass < 0.0, compass + 360.0, compass)
    compass = np.where((dz_dx == 0) & (dz_dy == 0), -1.0, compass)

    aspect_deg[1:-1, 1:-1] = compass
    aspect_deg[0, :] = aspect_deg[1, :]
    aspect_deg[-1, :] = aspect_deg[-2, :]
    aspect_deg[:, 0] = aspect_deg[:, 1]
    aspect_deg[:, -1] = aspect_deg[:, -2]

    return aspect_deg


def calculate_curvature(
    elevation_grid: np.ndarray,
    cell_size_m: float = 30.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates planform and profile curvature using Zevenbergen & Thorne (1987) coefficients:
      Planform curvature: perpendicular to maximum slope direction (flow convergence/divergence)
      Profile curvature: parallel to maximum slope direction (flow acceleration/deceleration)
    Returns: (plan_curvature, profile_curvature)
    """
    z = np.asarray(elevation_grid, dtype=np.float64)
    L = float(cell_size_m)
    rows, cols = z.shape

    plan_curv = np.zeros_like(z)
    prof_curv = np.zeros_like(z)

    # Extract 3x3 neighborhood
    z1 = z[0:-2, 0:-2]
    z2 = z[0:-2, 1:-1]
    z3 = z[0:-2, 2:]
    z4 = z[1:-1, 0:-2]
    z5 = z[1:-1, 1:-1]
    z6 = z[1:-1, 2:]
    z7 = z[2:, 0:-2]
    z8 = z[2:, 1:-1]
    z9 = z[2:, 2:]

    # Partial derivative polynomial parameters
    D = ((z4 + z6) / 2.0 - z5) / (L ** 2)
    E = ((z2 + z8) / 2.0 - z5) / (L ** 2)
    F = (-z1 + z3 + z7 - z9) / (4.0 * (L ** 2))
    G = (-z4 + z6) / (2.0 * L)
    H = (z2 - z8) / (2.0 * L)

    denom = (G ** 2 + H ** 2)
    denom = np.where(denom <= 1e-9, 1e-9, denom)

    # Profile Curvature
    prof = -2.0 * (D * (G ** 2) + E * (H ** 2) + F * G * H) / denom
    # Planform Curvature
    plan = 2.0 * (D * (H ** 2) + E * (G ** 2) - F * G * H) / denom

    prof_curv[1:-1, 1:-1] = np.clip(prof, -0.2, 0.2)
    plan_curv[1:-1, 1:-1] = np.clip(plan, -0.2, 0.2)

    # Boundary padding
    for arr in (plan_curv, prof_curv):
        arr[0, :] = arr[1, :]
        arr[-1, :] = arr[-2, :]
        arr[:, 0] = arr[:, 1]
        arr[:, -1] = arr[:, -2]

    return plan_curv, prof_curv


def generate_hillshade(
    elevation_grid: np.ndarray,
    cell_size_m: float = 30.0,
    azimuth_deg: float = 315.0,
    altitude_deg: float = 45.0
) -> np.ndarray:
    """
    Computes analytical hillshade illumination surface (values 0 - 255):
      Hillshade = 255.0 * ((cos(Zenith) * cos(Slope)) + (sin(Zenith) * sin(Slope) * cos(Azimuth - Aspect)))
    """
    slope = calculate_slope(elevation_grid, cell_size_m)
    aspect = calculate_aspect(elevation_grid, cell_size_m)

    zenith_rad = math.radians(90.0 - altitude_deg)
    slope_rad = np.radians(slope)
    azimuth_math = 360.0 - azimuth_deg + 90.0
    if azimuth_math >= 360.0:
        azimuth_math -= 360.0
    azimuth_rad = math.radians(azimuth_math)
    aspect_rad = np.radians(aspect)

    shaded = (
        (math.cos(zenith_rad) * np.cos(slope_rad)) +
        (math.sin(zenith_rad) * np.sin(slope_rad) * np.cos(azimuth_rad - aspect_rad))
    )
    shaded = np.clip(shaded, 0.0, 1.0)
    return (shaded * 255.0).astype(np.uint8)


def generate_contours(
    elevation_grid: np.ndarray,
    bounds: Dict[str, float],
    interval_m: float = 20.0
) -> Dict[str, Any]:
    """
    Generates elevation contour lines as a standard GeoJSON FeatureCollection.
    Accepts intervals such as 5m, 10m, 20m, or 50m.
    """
    interval = float(interval_m)
    if interval < 5.0:
        interval = 5.0

    z = np.asarray(elevation_grid, dtype=np.float64)
    min_elev = float(np.min(z))
    max_elev = float(np.max(z))

    start_elev = math.ceil(min_elev / interval) * interval
    end_elev = math.floor(max_elev / interval) * interval

    levels = np.arange(start_elev, end_elev + interval, interval)
    # Cap total levels to avoid overwhelming vector payload
    if len(levels) > 40:
        levels = levels[::math.ceil(len(levels) / 40)]

    rows, cols = z.shape
    min_lat, max_lat = bounds["min_lat"], bounds["max_lat"]
    min_lon, max_lon = bounds["min_lon"], bounds["max_lon"]

    lats = np.linspace(max_lat, min_lat, rows)
    lons = np.linspace(min_lon, max_lon, cols)

    features: List[Dict[str, Any]] = []

    # Fast iso-line segment trace across grid rows
    for elev_level in levels:
        segments: List[List[List[float]]] = []
        for r in range(rows - 1):
            for c in range(cols - 1):
                # 4 cell corners: TL, TR, BR, BL
                z_tl, z_tr = z[r, c], z[r, c + 1]
                z_bl, z_br = z[r + 1, c], z[r + 1, c + 1]

                z_min_cell = min(z_tl, z_tr, z_bl, z_br)
                z_max_cell = max(z_tl, z_tr, z_bl, z_br)

                if z_min_cell <= elev_level <= z_max_cell:
                    # Linear interpolation of intersection points along cell edges
                    pts: List[List[float]] = []
                    # Top edge
                    if (z_tl - elev_level) * (z_tr - elev_level) <= 0 and z_tl != z_tr:
                        t = (elev_level - z_tl) / (z_tr - z_tl)
                        pts.append([round(float(lons[c] + t * (lons[c + 1] - lons[c])), 5), round(float(lats[r]), 5)])
                    # Bottom edge
                    if (z_bl - elev_level) * (z_br - elev_level) <= 0 and z_bl != z_br:
                        t = (elev_level - z_bl) / (z_br - z_bl)
                        pts.append([round(float(lons[c] + t * (lons[c + 1] - lons[c])), 5), round(float(lats[r + 1]), 5)])
                    # Left edge
                    if (z_tl - elev_level) * (z_bl - elev_level) <= 0 and z_tl != z_bl:
                        t = (elev_level - z_tl) / (z_bl - z_tl)
                        pts.append([round(float(lons[c]), 5), round(float(lats[r] + t * (lats[r + 1] - lats[r])), 5)])
                    # Right edge
                    if (z_tr - elev_level) * (z_br - elev_level) <= 0 and z_tr != z_br:
                        t = (elev_level - z_tr) / (z_br - z_tr)
                        pts.append([round(float(lons[c + 1]), 5), round(float(lats[r] + t * (lats[r + 1] - lats[r])), 5)])

                    if len(pts) >= 2:
                        segments.append([pts[0], pts[1]])

        if segments:
            # Combine into MultiLineString or LineStrings
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "MultiLineString",
                    "coordinates": segments
                },
                "properties": {
                    "elevation_m": round(float(elev_level), 1),
                    "interval_m": interval,
                    "is_index_contour": (round(float(elev_level)) % (interval * 5) == 0)
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "interval_m": interval,
            "min_elevation_m": min_elev,
            "max_elevation_m": max_elev,
            "feature_count": len(features)
        }
    }
