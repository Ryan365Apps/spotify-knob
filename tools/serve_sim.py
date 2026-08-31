#!/usr/bin/env python3
"""
Serve design/simulator.html on http://127.0.0.1:8888 so its Live mode can
complete the Spotify PKCE flow using the redirect URI this project already
has registered (http://127.0.0.1:8888/callback — see tools/spotify_auth.py).

Routes:
    /                  -> simulator.html
    /callback          -> simulator.html (the OAuth redirect lands here;
                          the page reads ?code=... itself)
    /api/client_id     -> {"client_id": ...} from spotify_tokens.json, so the
                          page never asks you to paste it. The refresh token
                          is NOT exposed.
    anything else      -> static files from design/

Usage:
    python tools/serve_sim.py
"""

import http.server
import json
import subprocess
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design"
TOKENS = ROOT / "spotify_tokens.json"
PORT = 8888
HOTKEY_LOCK = threading.Lock()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DESIGN), **kwargs)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/callback"):
            self.path = "/simulator.html" + (
                "?" + self.path.split("?", 1)[1] if "?" in self.path else ""
            )
            return super().do_GET()
        if path == "/api/client_id":
            body = b"{}"
            if TOKENS.exists():
                try:
                    cid = json.loads(TOKENS.read_text()).get("client_id")
                    if cid:
                        body = json.dumps({"client_id": cid}).encode()
                except (json.JSONDecodeError, OSError):
                    pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def do_POST(self):
        # Stand-in for the BLE HID keyboard: type the chord Wispr binds to
        # hands-free (Ctrl+Alt+F9) on this PC. Loopback-only, fixed chord.
        # Serialized and blocking: two overlapping sends interleave modifier
        # press/release events and can leave Ctrl or Alt stuck down
        # system-wide (symptom: normal keys start triggering shortcuts).
        if self.path.split("?", 1)[0] == "/api/hotkey":
            ps = ('Add-Type -AssemblyName System.Windows.Forms; '
                  '[System.Windows.Forms.SendKeys]::SendWait("^%{F9}")')
            with HOTKEY_LOCK:
                try:
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                   timeout=10, check=False)
                except subprocess.TimeoutExpired:
                    pass
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet


def main():
    url = f"http://127.0.0.1:{PORT}/simulator.html"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Simulator: {url}")
    print("Live mode uses the registered redirect "
          f"http://127.0.0.1:{PORT}/callback — no dashboard changes needed.")
    print("Ctrl+C to stop.")
    webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
