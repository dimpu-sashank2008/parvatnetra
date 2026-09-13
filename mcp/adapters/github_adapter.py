"""
GitHub MCP Adapter & Diagnostic Helper for PARVAT NETRA
Validates connection to GitHub using either local npx package or remote endpoint,
completely eliminating the local Docker Desktop dependency.
"""

import os
import sys
import json
import urllib.request
import urllib.error


def verify_github_token() -> bool:
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
    if not token:
        print("[WARN] GITHUB_PERSONAL_ACCESS_TOKEN is not set in environment or .env.")
        print("       Set GITHUB_PERSONAL_ACCESS_TOKEN to enable GitHub MCP repository management.")
        return False

    # Verify token validity against GitHub REST API
    req = urllib.request.Request("https://api.github.com/user")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "Parvat-Netra-MCP-Adapter")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                print(f"[OK] GitHub authentication verified for user: {data.get('login')}")
                return True
    except urllib.error.HTTPError as e:
        print(f"[ERROR] GitHub authentication failed: HTTP {e.code} ({e.reason})")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to reach GitHub API: {e}")
        return False


def get_recommended_mcp_config() -> dict:
    """Returns the Node/npx-based GitHub MCP configuration."""
    return {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
        }
    }


if __name__ == "__main__":
    print("--- PARVAT NETRA: GitHub MCP Configuration Check ---")
    verified = verify_github_token()
    print("Recommended MCP Server Config (No Docker required):")
    print(json.dumps(get_recommended_mcp_config(), indent=2))
    sys.exit(0 if verified else 1)
