#!/usr/bin/env python3
"""
Lists every Spotify device your account can currently see, and whether each one
will accept volume commands from the Web API.

Run this to find out which of your playback devices could support the volume
dial. Devices only appear if Spotify has seen them recently - open the Spotify
app on anything you want tested (phone, desktop, speaker) before running.

Usage:
    python tools/check_devices.py            # uses spotify_tokens.json
    python tools/check_devices.py --client-id X --refresh-token Y
"""

import argparse
import json
import os

import requests

TOKEN_URL = "https://accounts.spotify.com/api/token"
API = "https://api.spotify.com/v1"


def get_access_token(client_id, refresh_token):
    r = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }, timeout=20)
    r.raise_for_status()
    body = r.json()
    if body.get("refresh_token") and body["refresh_token"] != refresh_token:
        print("NOTE: Spotify issued a new refresh token. Updating spotify_tokens.json.")
        if os.path.exists("spotify_tokens.json"):
            with open("spotify_tokens.json") as f:
                data = json.load(f)
            data["refresh_token"] = body["refresh_token"]
            with open("spotify_tokens.json", "w") as f:
                json.dump(data, f, indent=2)
    return body["access_token"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-id")
    ap.add_argument("--refresh-token")
    args = ap.parse_args()

    client_id, refresh_token = args.client_id, args.refresh_token
    if not (client_id and refresh_token):
        if not os.path.exists("spotify_tokens.json"):
            raise SystemExit("No spotify_tokens.json found. Pass --client-id and --refresh-token.")
        with open("spotify_tokens.json") as f:
            data = json.load(f)
        client_id = client_id or data["client_id"]
        refresh_token = refresh_token or data["refresh_token"]

    token = get_access_token(client_id, refresh_token)
    h = {"Authorization": "Bearer " + token}

    r = requests.get(API + "/me/player/devices", headers=h, timeout=20)
    r.raise_for_status()
    devices = r.json().get("devices", [])

    if not devices:
        print("No devices visible. Open the Spotify app on the things you want tested.")
        return

    print("\n%-28s %-14s %-8s %s" % ("DEVICE", "TYPE", "ACTIVE", "VOLUME DIAL"))
    print("-" * 72)
    usable = []
    for d in devices:
        sv = d.get("supports_volume")
        verdict = "YES" if sv else "no"
        if sv:
            usable.append(d["name"])
        print("%-28s %-14s %-8s %s" % (
            (d.get("name") or "?")[:27],
            (d.get("type") or "?")[:13],
            "yes" if d.get("is_active") else "-",
            verdict))
    print("-" * 72)

    if usable:
        print("\nVolume control is available on: %s" % ", ".join(usable))
        print("Building a volume mode is worthwhile - it will work on these devices")
        print("and gracefully fall back on the others.")
    else:
        print("\nNo visible device supports volume control.")
        print("If none of your listening devices ever will, replace the volume mode")
        print("with track seek (see BUILD.md, requirement R5).")


if __name__ == "__main__":
    main()
