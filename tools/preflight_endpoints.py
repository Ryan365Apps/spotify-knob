#!/usr/bin/env python3
"""
Endpoint pre-flight for Radial.

Spotify changed Development Mode on 11 February 2026. Client IDs created after
that date are restricted to "a smaller set of supported endpoints", and the
restriction was postponed only for integrations that already existed.

This app was created on 2026-08-31, so it is in the new class. Every endpoint
Waves 3-6 depend on therefore needs proving before the firmware assumes it.
Finding a 403 here costs a minute; finding it in Wave 6 costs an evening with
the board on the desk.

Usage:
    python tools/preflight_endpoints.py                  # safe checks only
    python tools/preflight_endpoints.py --disruptive     # also test skip

Start playback on any device first.
"""

import argparse
import json
import os
import sys
import time

import requests

TOKEN_URL = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"

OK = "\033[32mPASS\033[0m"
NO = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"


def access_token():
    if not os.path.exists("spotify_tokens.json"):
        raise SystemExit("Run this from the repo root — spotify_tokens.json not found.")
    with open("spotify_tokens.json") as f:
        data = json.load(f)
    r = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": data["refresh_token"],
        "client_id": data["client_id"],
    }, timeout=20)
    if r.status_code != 200:
        raise SystemExit("Token refresh failed (%s). If this is 400 invalid_grant, "
                         "the refresh token has expired — re-run spotify_auth.py."
                         % r.status_code)
    body = r.json()
    if body.get("refresh_token") and body["refresh_token"] != data["refresh_token"]:
        data["refresh_token"] = body["refresh_token"]
        with open("spotify_tokens.json", "w") as f:
            json.dump(data, f, indent=2)
        print("NOTE: Spotify rotated the refresh token; spotify_tokens.json updated.\n")
    return body["access_token"]


results = []


def check(label, wave, method, path, headers, params=None, expect=(200, 202, 204), json_body=None):
    try:
        r = requests.request(method, API + path, headers=headers, params=params,
                             json=json_body, timeout=20)
    except Exception as e:
        results.append((label, wave, "ERR", str(e)[:60]))
        print("%s  %-34s %s" % (NO, label, e))
        return None
    good = r.status_code in expect
    detail = ""
    if not good:
        try:
            detail = r.json().get("error", {}).get("reason") or r.json().get("error", {}).get("message", "")
        except Exception:
            detail = r.text[:80]
    results.append((label, wave, r.status_code, detail))
    print("%s  %-34s HTTP %s %s" % (OK if good else NO, label, r.status_code, detail))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disruptive", action="store_true",
                    help="also test next/previous — this WILL change the playing track")
    args = ap.parse_args()

    h = {"Authorization": "Bearer " + access_token()}

    print("Start playback on any device, then press Enter.")
    input()

    print("\n--- READ ---")
    r = check("GET /me/player", "3-7", "GET", "/me/player", h, expect=(200, 204))
    if r is None or r.status_code == 204:
        raise SystemExit("\nNothing is playing — Spotify returns 204 and the rest cannot be tested.")
    state = r.json()
    dev = state.get("device") or {}
    pos = state.get("progress_ms") or 0
    was_playing = state.get("is_playing")
    print("     device: %s (%s)  supports_volume=%s"
          % (dev.get("name"), dev.get("type"), dev.get("supports_volume")))

    check("GET /me/player/devices", "R8", "GET", "/me/player/devices", h, expect=(200,))

    print("\n--- WRITE, non-destructive ---")
    if dev.get("volume_percent") is not None:
        check("PUT /me/player/volume", "6/R5", "PUT", "/me/player/volume", h,
              {"volume_percent": dev["volume_percent"]})
    else:
        results.append(("PUT /me/player/volume", "6/R5", "SKIP", "device reports no volume"))
        print("%s  %-34s device reports no volume" % (SKIP, "PUT /me/player/volume"))

    check("PUT /me/player/seek", "6/R5", "PUT", "/me/player/seek", h, {"position_ms": pos})
    dev_id = dev.get("id")
    if dev_id:
        # transfer to the device it is already on - a no-op that still proves the call
        check("PUT /me/player (transfer)", "6/R8", "PUT", "/me/player", h,
              json_body={"device_ids": [dev_id], "play": bool(was_playing)})
    else:
        results.append(("PUT /me/player (transfer)", "6/R8", "SKIP", "no device id returned"))
        print("%s  %-34s no device id returned" % (SKIP, "PUT /me/player (transfer)"))

    print("\n--- WRITE, restores itself ---")
    check("PUT /me/player/pause", "6/R4", "PUT", "/me/player/pause", h)
    time.sleep(1)
    if was_playing:
        check("PUT /me/player/play", "6/R4", "PUT", "/me/player/play", h)

    print("\n--- WRITE, destructive ---")
    if args.disruptive:
        check("POST /me/player/next", "6/R3", "POST", "/me/player/next", h)
        time.sleep(1)
        check("POST /me/player/previous", "6/R3", "POST", "/me/player/previous", h)
        print("     (your playing track has changed — this is expected)")
    else:
        for lbl in ("POST /me/player/next", "POST /me/player/previous"):
            results.append((lbl, "6/R3", "SKIP", "run with --disruptive"))
            print("%s  %-34s run with --disruptive to test" % (SKIP, lbl))

    print("\n" + "=" * 68)
    bad = [r for r in results if isinstance(r[2], int) and r[2] >= 400]
    if bad:
        print("BLOCKED ENDPOINTS — these invalidate the requirements listed:\n")
        for lbl, wave, code, detail in bad:
            print("  %-34s HTTP %s  (Wave/req %s)  %s" % (lbl, code, wave, detail))
        print("\nRecord these in BUILD.md section 1 under Verified constraints,")
        print("and re-scope the affected requirement before building it.")
        sys.exit(1)
    print("All tested endpoints permitted. Record the date in BUILD.md section 1.")


if __name__ == "__main__":
    main()
