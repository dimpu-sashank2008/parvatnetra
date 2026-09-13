# Parvat Netra - MCP Infrastructure Setup Guide

Welcome to **Parvat Netra** (पर्वत नेत्र - *Mountain Eye*), an AI-driven high-altitude observation, GIS tracking, weather monitoring, and early warning notification platform built on the **Model Context Protocol (MCP)**.

---

## 1. Prerequisites

- **Python**: Version 3.10 or higher
- **Virtual Environment Tool**: `venv` or `uv`
- **MCP Client**: Claude Desktop, Antigravity, Cursor, or any MCP-compatible agent host

---

## 2. Environment Setup

### Clone or Open the Repository
Navigate to the `PARVAT_NETRA` root directory:
```bash
cd PARVAT_NETRA
```

### Create and Activate a Virtual Environment
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements-mcp.txt
```

### Configure Environment Variables
Copy `.env.example` to `.env` and configure your API credentials:
```bash
cp .env.example .env
```

Key environment variables:
| Variable | Description |
| :--- | :--- |
| `GIS_CLOUD_API_KEY` | API Key for GIS Cloud services |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API Key for live weather metrics |
| `ANALYTICS_DATABASE_URL` | PostgreSQL / TimescaleDB connection URI |
| `PROMETHEUS_METRICS_PORT` | Port for scraping observability metrics (default: `9090`) |
| `SLACK_WEBHOOK_URL` | Webhook URL for alerting in Slack channels |

---

## 3. MCP Servers Architecture

Parvat Netra provides 5 specialized MCP servers located in `mcp_servers/`:

```
mcp_servers/
├── gis_cloud/         # Geospatial, coordinates, distance, elevation
├── weather/           # Altitude weather, temperatures, storm warnings
├── data_analytics/    # Telemetry statistics, anomaly detection
├── observability/     # Subsystem health status, latency, metrics
└── notifications/     # Multi-channel alerts (Slack, Email, Emergency)
```

---

## 4. Running & Testing Servers Locally

You can run each MCP server in stdio mode directly with Python:

### Test GIS Cloud Server
```bash
python -m mcp_servers.gis_cloud.server
```

### Test Weather Server
```bash
python -m mcp_servers.weather.server
```

### Test Data Analytics Server
```bash
python -m mcp_servers.data_analytics.server
```

### Test Observability Server
```bash
python -m mcp_servers.observability.server
```

### Test Notifications Server
```bash
python -m mcp_servers.notifications.server
```

> **Tip:** You can also use the MCP Inspector for interactive browser-based testing:
> ```bash
> npx @modelcontextprotocol/inspector python -m mcp_servers.weather.server
> ```

---

## 5. Connecting AI Agents

Agent configuration is maintained in `.agents/mcp_config.json`.

To connect an MCP client:
1. Copy the contents of `.agents/mcp_config.json` into your MCP client configuration file:
   - **Claude Desktop (Windows)**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Claude Desktop (macOS)**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Antigravity / Custom Agent**: Reference `.agents/mcp_config.json` directly.
2. Ensure the virtual environment's Python executable path is specified if running outside an activated shell.

---

## 6. Troubleshooting

- **ImportError: No module named 'mcp'**: Run `pip install -r requirements-mcp.txt` within the active virtual environment.
- **Missing API Keys**: Server tools will fall back to simulated/synthetic data if live API credentials are empty in `.env`.
