# PARVAT NETRA — MCP Integration Hub

This directory contains utility adapters, diagnostic scripts, and JSON validation schemas for the Model Context Protocol (MCP) tooling ecosystem used by Antigravity during the development and maintenance of **PARVAT NETRA**.

---

## Directory Structure

```
mcp/
├── README.md               # Overview of MCP tools and operational practices
├── adapters/               # Bridge scripts and wrappers for MCP servers
│   ├── github_adapter.py   # Node-based GitHub runner (bypassing Docker)
│   └── neon_adapter.py     # Neon PostgreSQL / PostGIS connection validator
├── schemas/                # Contract schemas for MCP configuration & evidence
│   ├── mcp_config.schema.json      # Schema for .agents/mcp_config.json
│   └── evidence_payload.schema.json# Multimodal evidence input data contract
└── scripts/                # Diagnostic and verification tooling
    ├── verify_mcps.py      # Automated health check for active MCP servers
    └── validate_config.py  # Validation of environment templates and configs
```

---

## Core Guidelines

1. **Keep Secrets Out of VCS**: All MCP tokens (`GITHUB_PERSONAL_ACCESS_TOKEN`, `NEON_API_KEY`, etc.) are read from environment variables or `.env`.
2. **Zero Fake MCPs**: Real application data feeds (IMD weather, Mapbox routing, IoT sensors) belong in the FastAPI backend ingestion pipeline, not in developer MCP servers.
3. **No Docker Dependency for GitHub**: Use the native Node.js package `@modelcontextprotocol/server-github` via `npx` so developers and agents do not need Docker Desktop.
