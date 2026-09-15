# -*- coding: utf-8 -*-
"""
scripts/audit_phase11j_assets_and_hosts.py
Audits static asset existence and localhost references across templates and static js.
"""
import os
import re
import json

templates_dir = "templates"
static_dir = "static"

missing_assets = []
hardcoded_dev_urls = []

url_for_pattern = re.compile(r"url_for\(['\"]static['\"],\s*filename=['\"]([^'\"]+)['\"]\)")
src_href_pattern = re.compile(r"(?:src|href)=['\"](/static/[^'\"]+)['\"]")
localhost_pattern = re.compile(r"(http://(?:localhost|127\.0\.0\.1):(?!20128)[0-9]+[^\s'\"<>]*)")

for root, _, files in os.walk(templates_dir):
    for f in files:
        if f.endswith(".html"):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
                
                for match in url_for_pattern.finditer(content):
                    rel = match.group(1).split("?")[0]
                    target = os.path.join(static_dir, rel.replace("/", os.sep))
                    if not os.path.exists(target):
                        missing_assets.append({"template": filepath, "rel": rel, "target": target})
                        
                for match in src_href_pattern.finditer(content):
                    rel = match.group(1).replace("/static/", "").split("?")[0]
                    target = os.path.join(static_dir, rel.replace("/", os.sep))
                    if not os.path.exists(target):
                        missing_assets.append({"template": filepath, "rel": rel, "target": target})
                        
                for match in localhost_pattern.finditer(content):
                    hardcoded_dev_urls.append({"file": filepath, "url": match.group(1)})

# Also check static JS for localhost URLs
for root, _, files in os.walk(static_dir):
    for f in files:
        if f.endswith(".js"):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
                for match in localhost_pattern.finditer(content):
                    hardcoded_dev_urls.append({"file": filepath, "url": match.group(1)})

report = {
    "missing_assets_count": len(missing_assets),
    "missing_assets": missing_assets,
    "hardcoded_dev_urls_count": len(hardcoded_dev_urls),
    "hardcoded_dev_urls": hardcoded_dev_urls
}

os.makedirs("reports", exist_ok=True)
with open("reports/PHASE11J_STATIC_AND_HOST_AUDIT.json", "w", encoding="utf-8") as out:
    json.dump(report, out, indent=2)

print(f"[AUDIT] Missing assets: {len(missing_assets)}")
for m in missing_assets:
    print(f"  MISSING: {m['rel']} in {m['template']}")

print(f"[AUDIT] Hardcoded dev URLs: {len(hardcoded_dev_urls)}")
for u in hardcoded_dev_urls:
    print(f"  URL: {u['url']} in {u['file']}")
