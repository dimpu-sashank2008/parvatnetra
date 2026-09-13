# PARVAT NETRA — MCP Setup & Developer Guide

This guide details how to configure and verify the Model Context Protocol (MCP) tooling ecosystem for **PARVAT NETRA** without unnecessary software bloat.

---

## 1. Prerequisites

- **Python**: 3.10+ (Current system: Python 3.11.0)
- **Node.js**: v18+ with `npx` (Current system: Node v24.19.0, npm/npx 11.17.0)
- **Docker**: **NOT REQUIRED**. GitHub MCP is configured via native Node.js (`npx`) to avoid Docker overhead.
- **MCP Host**: Google Antigravity, Claude Desktop, or VS Code / Cursor.

---

## 2. Fast-Track Setup

### Step 1: Initialize Environment
From the workspace root:
```bash
cp .env.example .env
```
Populate `.env` with your development tokens.

### Step 2: Validate Configuration & Security
Run our automated security and configuration validator:
```bash
python mcp/scripts/validate_config.py
```
This ensures no credentials have been accidentally committed and all JSON schemas are intact.

### Step 3: Run MCP Health Diagnostics
```bash
python mcp/scripts/verify_mcps.py
```

---

## 3. Core MCP Tooling Setup

### 3.1 Design Stack

#### 1. StitchMCP
- **Transport**: `npx -y mcp-remote https://stitch.googleapis.com/mcp`
- **Status**: Live and verified. Used for AI screen generation and UI iteration.

#### 2. Figma
- **Local Dev Mode Option**: Open Figma Desktop App → Preferences / Settings → Enable Developer MCP Server (`http://127.0.0.1:3845/mcp`).
- **Remote Option**: Configure `https://mcp.figma.com/mcp` with `FIGMA_PERSONAL_ACCESS_TOKEN`.

#### 3. Spline
- **Binary**: `C:\Users\dimpu\AppData\Local\Programs\Spline\Spline.exe`
- **Activation**: Open a 3D terrain scene in Spline Desktop and enable the AI Bridge toggle.

---

### 3.2 Engineering Stack

#### 4. GitHub MCP (Zero-Docker Implementation)
Previously, GitHub MCP failed because Docker was missing. We eliminated Docker Desktop dependency by utilizing the official Node.js package:
```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

#### 5. Neon / PostgreSQL PostGIS
- **Transport**: `npx -y mcp-remote https://mcp.neon.tech/sse`
- **Configuration**: Requires `NEON_API_KEY` for branching and database inspection tools.
- **Database Schema**: Pre-configured for PostGIS spatial queries (`mcp/adapters/neon_adapter.py`).

---

### 3.3 Testing & Verification

#### 6. Chrome DevTools MCP
- **Transport**: `npx -y chrome-devtools-mcp@latest`
- **Status**: Verified active and responsive.
- **Capabilities**: Full DOM tree inspection, interaction automation, network sniffing, console telemetry, and Lighthouse audits.

---

### 3.4 Deployment

#### 7. Google Cloud Run
- **Transport**: `npx -y @google-cloud/cloud-run-mcp`
- **Status**: Active. Requires GCP application credentials when triggering deployments (`gcloud auth application-default login`).

---

## 4. MCPs Recommended for Disabling (Noise Reduction)

To avoid context pollution and unnecessary tool calls, the following unrelated MCPs present in global configurations should be disabled:
- `android-management-api`, `dart-mcp-server`, `gopls-mcp-server`
- `google-home-developer`, `stripe`, `sonatype-guide`, `gitlab-orbit`, `netlify`, `atlassian-mcp-server`
- `arize-tracing-assistant`, `windsor`, `mobbin`
- Unused GCP admin servers requiring missing ADC (`bigquery`, `alloydb-postgresql`, `cloud-sql`, `spanner`, etc.)
