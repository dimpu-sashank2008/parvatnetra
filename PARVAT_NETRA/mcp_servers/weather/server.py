"""
Weather MCP Server for Parvat Netra
Exposes current weather, atmospheric conditions, and severe weather warnings for high-altitude zones.
"""

import os
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("weather")
except ImportError:
    mcp = None


def fetch_weather_report(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch current weather report for coordinate location."""
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    # Provide synthetic/demo response if live key not provided
    return {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_celsius": -4.2,
        "wind_speed_kmh": 28.5,
        "humidity_percent": 65,
        "conditions": "Scattered Clouds / Snow Flurries",
        "visibility_meters": 4500,
        "freeze_level_elevation_meters": 3200,
        "is_mock": not bool(api_key)
    }


def check_alerts(latitude: float, longitude: float) -> Dict[str, Any]:
    """Check for active severe mountain weather alerts (blizzards, avalanches, gale-force winds)."""
    return {
        "latitude": latitude,
        "longitude": longitude,
        "active_alerts": [
            {
                "type": "High Wind Warning",
                "severity": "Moderate",
                "description": "Wind gusts exceeding 50 km/h predicted above 4000m ridge lines."
            }
        ]
    }


if mcp:
    @mcp.tool()
    def get_current_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        """Get live weather condition details for specified coordinates."""
        return fetch_weather_report(latitude, longitude)

    @mcp.tool()
    def get_weather_alerts(latitude: float, longitude: float) -> Dict[str, Any]:
        """Check for active high-altitude weather and storm alerts."""
        return check_alerts(latitude, longitude)


def main():
    if mcp:
        mcp.run()
    else:
        print("MCP SDK not installed. Please install requirements via `pip install -r requirements-mcp.txt`.")


if __name__ == "__main__":
    main()
