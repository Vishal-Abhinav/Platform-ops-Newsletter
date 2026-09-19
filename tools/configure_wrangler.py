#!/usr/bin/env python3
"""Write a deploy-only Wrangler config with the production D1 database ID."""
import os
import pathlib
import re
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: configure_wrangler.py INPUT OUTPUT")

database_id = os.environ.get("D1_DATABASE_ID", "").strip()
if not re.fullmatch(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", database_id):
    raise SystemExit("D1_DATABASE_ID must be a UUID")

source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
placeholder = "00000000-0000-0000-0000-000000000000"
if source.count(placeholder) != 1:
    raise SystemExit("expected exactly one D1 database placeholder")
pathlib.Path(sys.argv[2]).write_text(source.replace(placeholder, database_id), encoding="utf-8")
