"""
Security & Configuration Validator for PARVAT NETRA
Ensures:
1. No API keys, passwords, or tokens are committed in .agents/mcp_config.json or .env.example
2. .gitignore properly covers all secret and sensitive patterns
3. JSON syntax validity across schemas and configurations
"""

import re
import sys
import json
from pathlib import Path

SECRET_PATTERNS = [
    r"ghp_[A-Za-z0-9_]{30,}",         # GitHub Personal Access Token
    r"sk_test_[A-Za-z0-9_]{20,}",       # Stripe test key
    r"sk_live_[A-Za-z0-9_]{20,}",       # Stripe live key
    r"AIzaSy[A-Za-z0-9_-]{33}",         # Google API Key
    r"postgres(?:ql)?://(?!<[^>]+>)[a-zA-Z0-9_\-\.]+:(?!<[^>]+>)[^@\s]+@" # Actual credentials in postgres URI
]


def scan_for_secrets(file_path: Path) -> list:
    """Scan file content for known secret patterns."""
    findings = []
    if not file_path.exists():
        return findings

    content = file_path.read_text(encoding="utf-8")
    for pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        for m in matches:
            # Mask the secret for safe logging
            masked = m[:6] + "..." + m[-4:] if len(m) > 10 else "***"
            findings.append((file_path.name, masked))
    return findings


def validate_gitignore(gitignore_path: Path) -> bool:
    """Ensure sensitive patterns are covered in .gitignore."""
    required_patterns = [".env", "*.key", "*.pem", "*service-account*.json"]
    if not gitignore_path.exists():
        print("[FAIL] .gitignore is missing!")
        return False

    content = gitignore_path.read_text(encoding="utf-8")
    missing = []
    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)

    if missing:
        print(f"[FAIL] .gitignore is missing required ignore patterns: {missing}")
        return False

    print("[PASS] .gitignore includes all essential secret protection patterns.")
    return True


def validate_json_files(root: Path) -> bool:
    """Ensure all JSON files under .agents and mcp/schemas are valid."""
    all_valid = True
    json_targets = list((root / ".agents").glob("*.json")) + list((root / "mcp" / "schemas").glob("*.json"))
    for target in json_targets:
        try:
            with open(target, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"[PASS] JSON syntax valid: {target.relative_to(root)}")
        except Exception as e:
            print(f"[FAIL] JSON syntax error in {target.relative_to(root)}: {e}")
            all_valid = False
    return all_valid


def main():
    root = Path(__file__).resolve().parent.parent.parent
    print("==================================================================")
    print("      PARVAT NETRA — Security & Secret Leak Validator")
    print("==================================================================")

    # 1. Check for secret leaks
    files_to_scan = [
        root / ".env.example",
        root / ".agents" / "mcp_config.json",
        root / "docs" / "MCP_SETUP.md"
    ]

    all_clean = True
    for f in files_to_scan:
        leaks = scan_for_secrets(f)
        if leaks:
            all_clean = False
            for fname, secret in leaks:
                print(f"[DANGER] Hardcoded secret pattern detected in {fname}: {secret}")
        else:
            if f.exists():
                print(f"[PASS] No hardcoded credentials detected in {f.name}.")

    # 2. Check .gitignore
    gitignore_valid = validate_gitignore(root / ".gitignore")

    # 3. Check JSON validity
    json_valid = validate_json_files(root)

    print("\n------------------------------------------------------------------")
    if all_clean and gitignore_valid and json_valid:
        print("RESULT: ALL SECURITY AND CONFIGURATION CHECKS PASSED.")
        sys.exit(0)
    else:
        print("RESULT: FAILURES DETECTED IN CONFIGURATION OR SECURITY AUDIT.")
        sys.exit(1)


if __name__ == "__main__":
    main()
