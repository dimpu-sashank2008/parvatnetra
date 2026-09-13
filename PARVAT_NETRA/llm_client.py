"""
PARVAT NETRA - OmniRoute & LLM Gateway Client
Routes OpenAI-compatible Chat Completions API calls through OmniRoute
(http://localhost:20128/v1) with fallback to Experiential Labs.
"""

import os
import logging
from typing import Any, Dict, List, Optional
import time
import requests
from openai import OpenAI

logger = logging.getLogger("PARVAT_NETRA_OMNIROUTE")

OMNIROUTE_BASE_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNIROUTE_API_KEY = os.environ.get("OMNIROUTE_API_KEY", "omniroute-local")
EXPERIENTIAL_BASE_URL = os.environ.get("EXPLABS_BASE_URL", "https://api.experientiallabs.ai/v1")
DEFAULT_MODEL = os.environ.get("OMNIROUTE_MODEL", os.environ.get("MODEL_ID", "gpt-4o"))

_last_health_check = 0.0
_is_active = False


def is_omniroute_active(timeout: float = 1.0) -> bool:
    """Checks if the local OmniRoute router is alive and responding (cached for 10s)."""
    global _last_health_check, _is_active
    now = time.time()
    if now - _last_health_check < 10.0:
        return _is_active
    _last_health_check = now
    try:
        base = OMNIROUTE_BASE_URL.replace("/v1", "")
        res = requests.get(f"{base}/api/health", timeout=timeout)
        _is_active = (res.status_code == 200)
    except Exception:
        _is_active = False
    return _is_active


def get_llm_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> OpenAI:
    """
    Builds and returns an OpenAI client configured for OmniRoute or upstream gateway.
    Prioritizes local OmniRoute router if available.
    """
    # 1. Check OmniRoute
    if base_url is None:
        if is_omniroute_active():
            base_url = OMNIROUTE_BASE_URL
            api_key = api_key or OMNIROUTE_API_KEY
        else:
            base_url = EXPERIENTIAL_BASE_URL
            api_key = api_key or os.environ.get("EXPLABS_API_KEY", "dummy-key")

    key = api_key or "omniroute-local"
    return OpenAI(base_url=base_url, api_key=key)


def get_model_id() -> str:
    """Returns the configured model id."""
    return DEFAULT_MODEL


def list_available_models() -> List[str]:
    """Retrieves models from the active OmniRoute gateway."""
    try:
        client = get_llm_client()
        models = client.models.list()
        return [m.id for m in models.data]
    except Exception as e:
        logger.debug(f"Could not list OmniRoute models: {e}")
        return [DEFAULT_MODEL]


def create_chat_completion(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    stream: bool = False,
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[Any] = None,
    **kwargs: Any,
):
    """
    Execute chat completions through OmniRoute with standard OpenAI interface.
    """
    client = get_llm_client()
    target_model = model or get_model_id()
    call_kwargs: Dict[str, Any] = {
        "model": target_model,
        "messages": messages,
        "stream": stream,
        **kwargs,
    }
    if tools is not None:
        call_kwargs["tools"] = tools
    if tool_choice is not None:
        call_kwargs["tool_choice"] = tool_choice

    return client.chat.completions.create(**call_kwargs)
