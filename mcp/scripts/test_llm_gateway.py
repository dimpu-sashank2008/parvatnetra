"""
Test script for Experiential Labs Gateway integration with 'gpt-6-astra'.
"""

import sys
import os

# Add root and PARVAT_NETRA to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from PARVAT_NETRA.llm_client import get_llm_client, get_model_id


def run_test():
    print("[1] Building LLM client...")
    client = get_llm_client()
    model = get_model_id()
    print(f"    Base URL: {client.base_url}")
    print(f"    Model ID: {model}")

    print("\n[2] Dispatching test chat completion...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello! Confirm connection."}],
        )
        print("\n[SUCCESS] Test Call Response:")
        print(f"Reply: {response.choices[0].message.content}")
        print(f"Usage: {response.usage}")
        return response
    except Exception as exc:
        print(f"\n[API ERROR] Call failed: {exc}")
        return None


if __name__ == "__main__":
    run_test()
