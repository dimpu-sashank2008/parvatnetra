# Parvat Netra Agent Configuration

This directory contains configuration files and guidelines for connecting AI agents to the **Parvat Netra** MCP (Model Context Protocol) ecosystem.

---

## Directory Overview

```
.agents/
├── mcp_config.json    # Standard MCP client configuration for local/remote servers
└── README.md          # Agent integration guidelines and tool reference
```

---

## Connected MCP Servers

| Server Name | Module | Primary Capabilities |
| :--- | :--- | :--- |
| **`gis_cloud`** | `mcp_servers.gis_cloud.server` | Geospatial mapping, terrain coordinates, elevation profiles, area bounding |
| **`weather`** | `mcp_servers.weather.server` | Mountain weather conditions, snow/wind alerts, temperature forecasts |
| **`data_analytics`** | `mcp_servers.data_analytics.server` | Sensor data aggregation, trend identification, anomaly detection |
| **`observability`** | `mcp_servers.observability.server` | Agent metrics, health-checks, system resource tracking, latency logs |
| **`notifications`** | `mcp_servers.notifications.server` | Multi-channel alerting (Slack, Email, SMS, Webhooks) for emergency signals |

---

## Agent Setup Instructions

### 1. Environment Preparation
Ensure your `.env` file at the root of `PARVAT_NETRA/` is populated with the required keys:
```bash
cp .env.example .env
```

### 2. Configuration (`mcp_config.json`)
The `mcp_config.json` file uses standard MCP client format. You can link or copy this file into your MCP client configuration (e.g. Claude Desktop, Antigravity, or Cursor settings):

```json
{
  "mcpServers": {
    "gis_cloud": {
      "command": "python",
      "args": ["-m", "mcp_servers.gis_cloud.server"],
      "env": {
        "GIS_CLOUD_API_KEY": "${GIS_CLOUD_API_KEY}"
      }
    }
  }
}
```

### 3. Agent Tool Invocation Best Practices
- **Geospatial & Terrain Queries**: Always query `gis_cloud` first to resolve coordinates, elevation, and terrain constraints.
- **Weather Advisory**: Cross-reference high-altitude terrain points with `weather` forecast tools.
- **Critical Threshold Alerts**: Trigger `notifications` whenever `data_analytics` flags high-risk anomalies or adverse weather indicators.
