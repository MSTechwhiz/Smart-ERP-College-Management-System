from __future__ import annotations

import json
import re
from pathlib import Path


ROUTE_RE = re.compile(r'^@api_router\.(get|post|put|delete)\("([^"]+)"', re.MULTILINE)
WS_RE = re.compile(r'^@app\.websocket\("([^"]+)"', re.MULTILINE)


def build_inventory(server_py: str) -> dict:
    api_routes = [{"method": m.upper(), "path": p} for m, p in ROUTE_RE.findall(server_py)]
    ws_routes = [{"path": p} for p in WS_RE.findall(server_py)]
    return {"api_prefix": "/api", "routes": api_routes, "websockets": ws_routes}


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[2]  # backend/
    server_path = backend_dir / "server.py"
    text = server_path.read_text(encoding="utf-8")
    inv = build_inventory(text)
    print(json.dumps(inv, indent=2))


if __name__ == "__main__":
    main()

