"""
GIS Cloud MCP Server for Parvat Netra
Exposes geospatial, terrain, elevation, and boundary calculation tools.
"""

import os
import math
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

# Attempt FastMCP or provide fallback runner
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("gis_cloud")
except ImportError:
    mcp = None


def get_elevation_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Retrieve estimated elevation and terrain category for given coordinates."""
    # Placeholder terrain calculation logic
    base_elevation = 2000.0 + abs(math.sin(latitude) * 3000.0) + abs(math.cos(longitude) * 2000.0)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation_meters": round(base_elevation, 2),
        "terrain_type": "mountainous" if base_elevation > 2500 else "foothills",
        "source": "Parvat Netra GIS Synthetic/API Provider"
    }


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
    """Calculate great-circle distance between two geographical points in kilometers."""
    r = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = r * c
    return {
        "point_a": {"latitude": lat1, "longitude": lon1},
        "point_b": {"latitude": lat2, "longitude": lon2},
        "distance_km": round(distance_km, 3)
    }


if mcp:
    @mcp.tool()
    def get_elevation(latitude: float, longitude: float) -> Dict[str, Any]:
        """Get terrain elevation in meters for a given latitude and longitude."""
        return get_elevation_data(latitude, longitude)

    @mcp.tool()
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
        """Calculate spatial distance between two coordinate pairs."""
        return haversine_distance(lat1, lon1, lat2, lon2)


def main():
    if mcp:
        mcp.run()
    else:
        print("MCP SDK not installed. Please install requirements via `pip install -r requirements-mcp.txt`.")


if __name__ == "__main__":
    main()
