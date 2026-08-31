#!/usr/bin/env python3
"""
Spotify auth + pre-flight diagnostic for the Waveshare knob project.

Does three things:
  1. Runs the Authorization Code + PKCE flow (no client secret needed, so the
     ESP32 never has to hold one).
  2. Prints the refresh token you will flash onto the device.
  3. Runs a diagnostic against your CURRENT playback device to check whether the
     things the knob needs to do are actually permitted on it.

Usage:
    pip install requests
    python spotify_auth.py --client-id YOUR_CLIENT_ID

Prereq: in the Spotify developer dashboard, create an app and add
        http://127.0.0.1:8888/callback   as a Redirect URI.
"""

import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import threading
import urllib.parse
import webbrowser

import requests

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-playback-state user-modify-playback-state"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"

_code_holder = {}


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        _code_holder.update({k: v[0] for k, v in params.items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Done. Close this tab and return to the terminal.</h2>")

    def log_message(self, *args):
        pass


def pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(64)).decode().rstrip("=")
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge


def authorize(client_id):
    verifier, challenge = pkce_pair()
    state = secrets.token_urlsafe(16)
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "state": state,
    })

    server = http.server.HTTPServer(("127.0.0.1", 8888), _CallbackHandler)
    t = threading.Thread(target=server.handle_request, daemon=True)
    t.start()

    print("\nOpening browser for Spotify authorisation...")
    print("If it does not open, paste this into your browser:\n\n" + url + "\n")
    webbrowser.open(url)
    t.join(timeout=300)

    if _code_holder.get("state") != state:
        raise SystemExit("State mismatch or timeout - aborting.")
    if "error" in _code_holder:
        raise SystemExit("Spotify returned an error: " + _code_holder["error"])

    r = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": _code_holder["code"],
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "code_verifier": verifier,
    }, timeout=20)
    r.raise_for_status()
    return r.json()


def diagnose(access_token):
    h = {"Authorization": "Bearer " + access_token}
    print("\n--- PRE-FLIGHT DIAGNOSTIC -------------------------------------")
    print("Start playing something on the device you actually use (phone,")
    print("speaker, whatever), then press Enter.")
    input()

    r = requests.get(API + "/me/player", headers=h, timeout=20)
    if r.status_code == 204:
        print("FAIL: 204 No Content - Spotify sees no active playback device.")
        print("      The knob cannot show or control anything in this state.")
        return
    r.raise_for_status()
    s = r.json()

    dev = s.get("device") or {}
    item = s.get("item") or {}
    album = item.get("album") or {}
    images = album.get("images") or []

    print("\nDevice          : %s (%s)" % (dev.get("name"), dev.get("type")))
    print("supports_volume : %s   <-- must be true for the volume dial" % dev.get("supports_volume"))
    print("volume_percent  : %s" % dev.get("volume_percent"))
    print("is_playing      : %s" % s.get("is_playing"))
    print("playing type    : %s" % s.get("currently_playing_type"))
    print("Track           : %s - %s" % (
        ", ".join(a.get("name", "") for a in item.get("artists", [])),
        item.get("name")))
    print("Album art sizes : %s" % ", ".join(
        "%sx%s" % (i.get("width"), i.get("height")) for i in images))
    if images:
        print("Largest art URL : %s" % images[0].get("url"))

    dis = (s.get("actions") or {}).get("disallows") or {}
    print("\nDisallowed actions on this device: %s" % (list(dis.keys()) or "none"))

    print("\nTesting volume control (sets volume to current value, no audible change)...")
    vol = dev.get("volume_percent")
    if vol is None:
        print("SKIP: device reports no volume.")
    else:
        rv = requests.put(API + "/me/player/volume",
                          headers=h, params={"volume_percent": vol}, timeout=20)
        if rv.status_code in (200, 202, 204):
            print("PASS: volume control accepted (HTTP %s)." % rv.status_code)
        else:
            print("FAIL: HTTP %s - %s" % (rv.status_code, rv.text[:300]))
            print("      Volume-by-dial will not work against this device.")
    print("---------------------------------------------------------------")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id", required=True)
    ap.add_argument("--skip-diagnostic", action="store_true")
    args = ap.parse_args()

    tok = authorize(args.client_id)

    print("\n=== FLASH THESE ONTO THE DEVICE ===============================")
    print("SPOTIFY_CLIENT_ID     = %s" % args.client_id)
    print("SPOTIFY_REFRESH_TOKEN = %s" % tok.get("refresh_token"))
    print("===============================================================")
    print("Refresh token is valid for 6 months from now. Re-run this script")
    print("to mint a new one when it expires.")

    with open("spotify_tokens.json", "w") as f:
        json.dump({"client_id": args.client_id,
                   "refresh_token": tok.get("refresh_token")}, f, indent=2)
    print("Also written to spotify_tokens.json (keep it out of git).")

    if not args.skip_diagnostic:
        diagnose(tok["access_token"])


if __name__ == "__main__":
    main()
