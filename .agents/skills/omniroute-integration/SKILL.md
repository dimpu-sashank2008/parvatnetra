---
name: omniroute-integration
description: "Instructions, best practices, and API references for integrating the local OmniRoute LLM router (http://localhost:20128/v1) into PARVAT NETRA disaster intelligence services."
---

# OmniRoute Integration & Inference Skill

This skill provides step-by-step guidance for invoking, configuring, and monitoring the **OmniRoute** local AI router within **PARVAT NETRA**.

## 1. Overview
- **Gateway Endpoint**: `http://localhost:20128/v1`
- **Health Endpoint**: `http://localhost:20128/api/health`
- **Dashboard UI**: `http://localhost:20128`
- **Protocol**: OpenAI-compatible Chat Completions API (`POST /v1/chat/completions`)

## 2. Using OmniRoute in Python Services
Import the centralized LLM client from `PARVAT_NETRA.llm_client`:

```python
from PARVAT_NETRA.llm_client import (
    is_omniroute_active,
    get_llm_client,
    get_model_id,
    create_chat_completion,
    list_available_models
)

# 1. Check if OmniRoute is running
if is_omniroute_active():
    # 2. Invoke chat completion through OmniRoute
    response = create_chat_completion(
        messages=[
            {"role": "system", "content": "You are PARVAT NETRA Disaster AI."},
            {"role": "user", "content": "Explain geotechnical failure on NH-10 Km 48."}
        ],
        temperature=0.2,
        max_tokens=200
    )
    briefing = response.choices[0].message.content
```

## 3. Environment Configuration
In `.env`:
```env
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=omniroute-local
OMNIROUTE_ENABLED=true
OMNIROUTE_MODEL=default
FLASK_PORT=8080
```
> **Note on Port Separation**: Never set `PORT=8080` in `.env` without setting `FLASK_PORT=8080`, as OmniRoute CLI might otherwise interpret port 8080 as its own control plane.

## 4. Operational Invariants
- **Always implement graceful fallback**: If OmniRoute returns 401, 429, or 500, the system must fall back to deterministic physical models (`services.ai_sitrep.synthesize_executive_sitrep`).
- **Data Provenance**: Label outputs as `[OMNIROUTE / LLM-ENRICHED]` when synthesized by OmniRoute, or `[LIVE / DETERMINISTIC]` on baseline fallback.
