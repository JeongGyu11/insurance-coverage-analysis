"""Validate source hashes and syntax without importing or running analysis code."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", help="Node executable for optional JavaScript syntax checking")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "docs/source-index.json").read_text(encoding="utf-8"))
    errors = []
    counts = {"python": 0, "javascript": 0}
    for item in manifest["files"]:
        path = root / item["file"]
        if not path.is_file():
            errors.append(f"Missing: {item['file']}")
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            errors.append(f"Hash mismatch: {item['file']}")
        if path.suffix == ".py":
            try:
                ast.parse(data.decode("utf-8-sig"), filename=str(path))
                counts["python"] += 1
            except SyntaxError as exc:
                errors.append(f"Python syntax: {item['file']}: {exc}")
        elif args.node:
            result = subprocess.run([args.node, "--check", str(path)], capture_output=True, text=True)
            if result.returncode:
                errors.append(f"JS syntax: {item['file']}: {result.stderr}")
            else:
                counts["javascript"] += 1
    print(json.dumps({"scripts": manifest["count"], "checked": counts, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
