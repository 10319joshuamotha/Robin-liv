from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


_HOST = "127.0.0.1"
_PORT = 8765
_lock = threading.Lock()
_tabs: list[dict] = []
_clients: dict[str, list[dict]] = {}
_commands: list[dict] = []
_results: dict[str, dict] = {}
_server = None
_thread = None


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def _json(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        if p.path == "/tabs":
            with _lock:
                merged = []
                for client_tabs in _clients.values():
                    merged.extend(client_tabs)
                _tabs[:] = merged
                return self._json(200, {"tabs": list(_tabs)})
        if p.path == "/poll":
            q = parse_qs(p.query)
            client = q.get("client", [""])[0]
            with _lock:
                for i, cmd in enumerate(_commands):
                    if not cmd.get("client") or cmd.get("client") == client:
                        return self._json(200, _commands.pop(i))
            return self._json(200, {})
        if p.path == "/result":
            q = parse_qs(p.query)
            rid = q.get("id", [""])[0]
            with _lock:
                return self._json(200, _results.get(rid, {}))
        self._json(404, {"error": "not found"})

    def do_POST(self):
        p = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"error": "invalid json"})
        if p.path == "/tabs":
            client = str(data.get("client", "default"))
            with _lock:
                _clients[client] = [t for t in data.get("tabs", []) if not t.get("incognito")]
                merged = []
                for client_tabs in _clients.values():
                    merged.extend(client_tabs)
                _tabs[:] = merged
            return self._json(200, {"ok": True})
        if p.path == "/result":
            rid = str(data.get("id", ""))
            with _lock:
                _results[rid] = data
            return self._json(200, {"ok": True})
        self._json(404, {"error": "not found"})


def start_bridge() -> bool:
    global _server, _thread
    if _server is not None:
        return True
    try:
        _server = ThreadingHTTPServer((_HOST, _PORT), _Handler)
        _thread = threading.Thread(target=_server.serve_forever, daemon=True, name="RobinBrowserBridge")
        _thread.start()
        return True
    except Exception as e:
        print(f"[BrowserBridge] disabled: {e}")
        _server = None
        return False


def _request(method: str, path: str, payload=None, timeout=3):
    import urllib.request
    url = f"http://{_HOST}:{_PORT}{path}"
    if method == "GET":
        req = urllib.request.Request(url, method="GET")
    else:
        raw = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(url, data=raw, method="POST",
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def list_tabs(include_content: bool = False) -> str:
    try:
        data = _request("GET", "/tabs", timeout=2)
        tabs = data.get("tabs", [])
        if not tabs:
            return "No connected normal browser tabs. Install/enable the Robin browser bridge extension."
        lines = []
        for t in tabs:
            lines.append(f"- [{t.get('browser','?')}] {t.get('title','(untitled)')} — {t.get('url','')}")
        return "Open normal browser tabs (incognito excluded):\n" + "\n".join(lines)
    except Exception as e:
        return f"Browser tab bridge unavailable: {e}"


def inspect_tab(tab_id: int, browser: str = "") -> str:
    rid = f"{time.time_ns()}"
    try:
        _request("POST", "/tabs", {"tabs": _tabs}, timeout=1)
        with _lock:
            _commands.append({"id": rid, "client": browser, "action": "inspect", "tabId": int(tab_id)})
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            time.sleep(0.15)
            r = _request("GET", "/result?id="+rid, timeout=2)
            if r.get("id") == rid:
                if r.get("error"):
                    return f"Could not inspect tab: {r['error']}"
                return str(r.get("text", ""))[:12000] or "(page has no readable text)"
        return "Timed out waiting for the browser extension."
    except Exception as e:
        return f"Browser inspection failed: {e}"


def browser_tabs(action: str = "list", tab_id: int = 0, include_content: bool = False,
                  browser: str = "") -> str:
    """Voice-facing browser tab control."""
    action = (action or "list").strip().lower()
    if action in ("list", "tabs", "all"):
        return list_tabs(include_content=include_content)
    if action in ("inspect", "read", "understand") and tab_id:
        return inspect_tab(int(tab_id), browser=browser)
    return "Specify action=list or action=inspect with a tab_id."

TOOL = {
    "name": "browser_tabs",
    "description": (
        "See all connected normal browser tabs, including background tabs, "
        "excluding incognito/private tabs. Use action=list to enumerate tabs; "
        "use action=inspect with tab_id to read the visible page text and understand its contents."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "list or inspect"},
            "tab_id": {"type": "INTEGER", "description": "Tab id returned by list"},
            "include_content": {"type": "BOOLEAN", "description": "Reserved for compatibility; inspect reads page text"},
            "browser": {"type": "STRING", "description": "Optional browser client id"}
        },
        "required": []
    },
    "handler": browser_tabs,
}
