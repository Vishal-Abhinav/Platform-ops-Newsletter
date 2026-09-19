#!/usr/bin/env python3
"""Mark authenticated knowledge routes as private before sitemap generation."""
import os
import pathlib
import re

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
PREMIUM_SLUGS = [
    "networking",
    "cloud",
    "gitops",
    "devops",
    "containers",
    "kubernetes",
    "openshift",
    "observability",
    "sre",
    "security",
    "platform-engineering",
]
PREMIUM = [ROOT / "categories" / slug / "index.html" for slug in PREMIUM_SLUGS]

for page in PREMIUM:
    if not page.exists():
        raise SystemExit(f"premium page missing: {page}")
    source = page.read_text(encoding="utf-8")
    robots = '<meta name="robots" content="noindex,nofollow">'
    if re.search(r'<meta\s+name=["\']robots["\'][^>]*>', source, re.I):
        source = re.sub(r'<meta\s+name=["\']robots["\'][^>]*>', robots, source, count=1, flags=re.I)
    else:
        source = source.replace("</head>", robots + "\n</head>", 1)
    page.write_text(source, encoding="utf-8")

print(f"  premium -> {len(PREMIUM)} authenticated route")
