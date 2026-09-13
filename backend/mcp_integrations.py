"""
PARVAT NETRA - Model Context Protocol (MCP) Integration & Fallback Dispatcher
Provides programmatic fallbacks and wrappers for Git, Fetch, Docker, and Neon operations.
Ensures zero data loss and automated repository checkpointing across disaster response phases.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_integrations")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def git_status() -> Dict[str, Any]:
    """
    Retrieves current Git status of the repository.
    Returns modified, untracked, staged files, and branch info.
    """
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        
        # Get active branch
        branch_res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        branch = branch_res.stdout.strip() or "HEAD"

        modified = []
        untracked = []
        staged = []

        for line in lines:
            status_code = line[:2]
            filename = line[3:]
            if status_code.startswith("??"):
                untracked.append(filename)
            elif status_code[0] in ("M", "A", "D", "R"):
                staged.append(filename)
            elif status_code[1] in ("M", "D"):
                modified.append(filename)
            else:
                modified.append(filename)

        return {
            "success": True,
            "branch": branch,
            "is_clean": len(lines) == 0,
            "total_changes": len(lines),
            "untracked": untracked,
            "modified": modified,
            "staged": staged,
            "raw_output": lines
        }
    except Exception as e:
        logger.error(f"Error executing git status: {e}")
        return {
            "success": False,
            "error": str(e),
            "is_clean": False,
            "total_changes": 0,
            "untracked": [],
            "modified": [],
            "staged": [],
            "raw_output": []
        }


def git_commit_snapshot(message: str) -> Dict[str, Any]:
    """
    Stages all workspace changes and creates a Git snapshot commit.
    Handles clean working trees gracefully without error.
    """
    try:
        # First check status
        status = git_status()
        if not status.get("success"):
            return {"success": False, "error": status.get("error")}

        if status.get("is_clean"):
            logger.info("Working directory clean, no new snapshot commit needed.")
            return {
                "success": True,
                "committed": False,
                "message": "Working tree clean. Nothing to commit."
            }

        # Stage all changes
        add_res = subprocess.run(
            ["git", "add", "-A"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        if add_res.returncode != 0:
            return {"success": False, "error": f"git add failed: {add_res.stderr}"}

        # Commit
        commit_res = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        if commit_res.returncode != 0:
            # Check if it was because nothing changed
            if "nothing to commit" in commit_res.stdout.lower() or "nothing to commit" in commit_res.stderr.lower():
                return {
                    "success": True,
                    "committed": False,
                    "message": "Working tree clean. Nothing to commit."
                }
            return {"success": False, "error": f"git commit failed: {commit_res.stderr or commit_res.stdout}"}

        # Get the new commit hash
        hash_res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        commit_hash = hash_res.stdout.strip()

        logger.info(f"Successfully committed snapshot {commit_hash[:8]}: {message}")
        return {
            "success": True,
            "committed": True,
            "commit_hash": commit_hash,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error in git_commit_snapshot: {e}")
        return {"success": False, "error": str(e)}


def fetch_external_advisory(url: str, timeout_sec: int = 5) -> Dict[str, Any]:
    """
    Fetches external meteorological, seismic, or NDMA disaster advisories.
    Gracefully handles SSL, DNS, timeout, and offline environments.
    """
    import requests
    try:
        headers = {
            "User-Agent": "PARVAT-NETRA-DisasterIntelligence/1.0 (+https://parvat-netra.gov.in)"
        }
        resp = requests.get(url, headers=headers, timeout=timeout_sec, verify=True)
        return {
            "success": True,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type", ""),
            "content_length": len(resp.content),
            "text": resp.text[:2000] # preview first 2k chars
        }
    except requests.exceptions.SSLError as ssl_err:
        logger.warning(f"SSL error fetching {url}: {ssl_err}")
        return {"success": False, "error": f"SSL Error: {ssl_err}", "category": "SSL"}
    except requests.exceptions.Timeout as to_err:
        logger.warning(f"Timeout fetching {url}: {to_err}")
        return {"success": False, "error": f"Timeout after {timeout_sec}s", "category": "TIMEOUT"}
    except requests.exceptions.ConnectionError as conn_err:
        logger.warning(f"Connection error fetching {url}: {conn_err}")
        return {"success": False, "error": f"Connection Error: {conn_err}", "category": "NETWORK"}
    except Exception as e:
        logger.error(f"Unexpected error fetching advisory from {url}: {e}")
        return {"success": False, "error": str(e), "category": "GENERAL"}


def check_docker_daemon() -> Dict[str, Any]:
    """
    Checks if Docker CLI and the Docker daemon are available and responsive.
    """
    try:
        # Check CLI presence & version
        v_res = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if v_res.returncode != 0:
            return {
                "installed": False,
                "running": False,
                "version": None,
                "details": "Docker CLI not found or returned error."
            }

        docker_version = v_res.stdout.strip()

        # Check daemon responsiveness
        info_res = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_running = (info_res.returncode == 0)

        return {
            "installed": True,
            "running": is_running,
            "version": docker_version,
            "details": "Daemon running" if is_running else "Daemon not responding / stopped"
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {
            "installed": False,
            "running": False,
            "version": None,
            "details": f"Docker check error: {str(e)}"
        }
    except Exception as e:
        return {
            "installed": False,
            "running": False,
            "version": None,
            "details": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    print("--- PARVAT NETRA MCP INTEGRATION HARNESS ---")
    st = git_status()
    print(f"Git status: branch={st.get('branch')}, changes={st.get('total_changes')}")
    dock = check_docker_daemon()
    print(f"Docker status: installed={dock.get('installed')}, running={dock.get('running')}")
    print("--------------------------------------------")
