# PARVAT NETRA — Agent & MCP Architecture

This directory defines the Model Context Protocol (MCP) configuration for autonomous AI engineering agents (such as Antigravity) working on **PARVAT NETRA — NER Sentinel**.

---

## The Core Distinction: Agent MCPs vs Application APIs

An essential architectural rule for PARVAT NETRA is maintaining a strict separation between **Agent Tooling** and **Application Integrations**:

```
+---------------------------------------------------------------------------------+
|                               ANTIGRAVITY AGENT                                 |
|                                                                                 |
|   Consumes MCP Servers (via .agents/mcp_config.json):                           |
|   - StitchMCP (Visual exploration & UI generation)                              |
|   - Figma (Design system & token inspection)                                    |
|   - Spline (3D terrain scene inspection & embedding)                            |
|   - GitHub (Pull requests, repository commits, branch management via npx)       |
|   - Neon / PostgreSQL (Database schema management & queries)                    |
|   - Chrome DevTools (Live browser testing, automated UI verification)           |
|   - Cloud Run (Container deployment & service status)                           |
+---------------------------------------------------------------------------------+
                                      |
                                      | Generates, tests & deploys
                                      v
+---------------------------------------------------------------------------------+
|                           PARVAT NETRA APPLICATION                              |
|                                                                                 |
|   FastAPI Backend + Next.js Frontend                                            |
|   Consumes standard External REST/WebSocket APIs directly:                      |
|   - Weather APIs (IMD, OpenWeatherMap, ECMWF)                                   |
|   - Geospatial & Routing APIs (Mapbox, Google Maps, OpenStreetMap)              |
|   - Satellite Earth Observation (Sentinel Hub, Copernicus)                      |
|   - Sensor Gateways (Rain gauges, piezometers, tiltmeters via MQTT/HTTP)        |
|   - Notification Gateways (Emergency SMS, Email, Slack webhooks)                |
+---------------------------------------------------------------------------------+
```

> **Note:** External application data sources are **NOT** wrapped in pseudo-MCP servers. The FastAPI backend consumes standard REST/HTTP/MQTT endpoints, normalizes records, runs physics/ML models, and populates PostgreSQL/PostGIS.

---

## Active Agent MCP Servers

| Tier | Server Name | Transport / Command | Purpose in Development |
| :--- | :--- | :--- | :--- |
| **Design** | `StitchMCP` | `npx -y mcp-remote https://stitch.googleapis.com/mcp` | UI screen generation and design variant exploration |
| **Design** | `Figma` | `http://127.0.0.1:3845/mcp` (or remote `https://mcp.figma.com/mcp`) | Design system verification, component specs |
| **Design** | `Spline` | Local Spline Desktop binary + AI Bridge | High-altitude 3D terrain and slope visualizations |
| **Engineering** | `github` | `npx -y @modelcontextprotocol/server-github` | Repo interaction without Docker dependency |
| **Engineering** | `mcp-server-neon` | `npx -y mcp-remote https://mcp.neon.tech/sse` | PostGIS migrations, database inspection |
| **Testing** | `chrome-devtools-mcp` | `npx -y chrome-devtools-mcp@latest` | Headless/browser UI auditing, safe-routes verification |
| **Deployment**| `cloudrun` | `npx -y @google-cloud/cloud-run-mcp` | Container deployment to Google Cloud Run |

---

## Authentication & Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Populate required tokens:
   - `GITHUB_PERSONAL_ACCESS_TOKEN` for GitHub MCP
   - `NEON_API_KEY` for Neon database management
   - `FIGMA_PERSONAL_ACCESS_TOKEN` if using remote Figma endpoint
3. Never commit `.env` or hardcode tokens into `mcp_config.json`.
