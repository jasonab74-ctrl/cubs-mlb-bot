#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — News App Server
- Serves index and /items.json
- Reads items.json produced by collect.py
- Shows Quick Link pills (from feeds.STATIC_LINKS)
- Shows "News Sources" dropdown built from feeds.FEEDS
- Preserves your existing static logo/audio filenames if present
"""

import json
import os
import time
from urllib.parse import urlparse
from typing import Any, Dict, List
from flask import Flask, jsonify, render_template

from feeds import FEEDS, STATIC_LINKS  # <-- wire in

app = Flask(__name__, template_folder="templates", static_folder="static")

ITEMS_FILE = "items.json"

# Try to preserve your current media file names.
CANDIDATE_LOGOS = [
    "cubs-logo.png", "logo.png", "cubs.png", "purdue-logo.png"
]
CANDIDATE_AUDIO = [
    "cubs-win.mp3", "fight-song.mp3", "theme.mp3"
]

# Optional friendly names for some sources (fallback = domain)
FRIENDLY_SOURCE_NAMES = {
    "www.mlb.com": "MLB.com",
    "mlb.com": "MLB.com",
    "www.espn.com": "ESPN",
    "espn.com": "ESPN",
    "www.nbcsportschicago.com": "NBC Sports Chicago",
    "nbcsportschicago.com": "NBC Sports Chicago",
    "www.bleachernation.com": "Bleacher Nation",
    "bleachernation.com": "Bleacher Nation",
    "www.bleedcubbieblue.com": "Bleed Cubbie Blue",
    "bleedcubbieblue.com": "Bleed Cubbie Blue",
    "www.chicagotribune.com": "Chicago Tribune",
    "chicagotribune.com": "Chicago Tribune",
    "chicago.suntimes.com": "Chicago Sun-Times",
    "www.reddit.com": "Reddit /r/CHICubs",
    "reddit.com": "Reddit /r/CHICubs",
    "www.youtube.com": "YouTube",
    "youtube.com": "YouTube",
}

def _first_existing(static_rel_paths: List[str]) -> str:
    for rel in static_rel_paths:
        full = os.path.join(app.static_folder, rel)
        if os.path.exists(full):
            return rel
    # Fallback to nothing; template will hide if missing
    return ""

def _read_items() -> Dict[str, Any]:
    if not os.path.exists(ITEMS_FILE):
        return {"team": "Chicago Cubs", "updated_ts": time.time(), "items": []}
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"team": "Chicago Cubs", "updated_ts": time.time(), "items": []}

def _build_sources() -> List[Dict[str, str]]:
    """Turn FEEDS into [{name, url}] using friendly names where possible."""
    out: List[Dict[str, str]] = []
    seen = set()
    for u in FEEDS:
        try:
            host = urlparse(u).netloc.lower()
            name = FRIENDLY_SOURCE_NAMES.get(host) or host.replace("www.", "")
            key = (name, u)
            if key in seen:
                continue
            seen.add(key)
            out.append({"name": name, "url": u})
        except Exception:
            continue
    # de-dupe by name, keep first URL
    dedup: Dict[str, Dict[str, str]] = {}
    for s in out:
        if s["name"] not in dedup:
            dedup[s["name"]] = s
    return sorted(dedup.values(), key=lambda d: d["name"].lower())

@app.route("/")
def index():
    data = _read_items()
    logo_path = _first_existing(CANDIDATE_LOGOS)
    audio_path = _first_existing(CANDIDATE_AUDIO)
    sources = _build_sources()
    return render_template(
        "index.html",
        team=data.get("team", "Chicago Cubs"),
        updated_ts=data.get("updated_ts", time.time()),
        items=data.get("items", []),
        logo_path=logo_path,
        audio_path=audio_path,
        quick_links=STATIC_LINKS,  # pills row
        sources=sources,           # news sources dropdown
    )

@app.route("/items.json")
def items_json():
    # Serve the latest cache directly
    return jsonify(_read_items())

@app.route("/health")
def health():
    return jsonify({"ok": True, "time": time.time()})

if __name__ == "__main__":
    # For local debug use: python3 server.py
    app.run(host="0.0.0.0", port=5000, debug=False)
