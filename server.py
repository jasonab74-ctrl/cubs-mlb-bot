#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — News App Server
Purdue-style UI with Cubs branding, quick links, and a clean "News Sources" section.
"""

import json
import os
import time
from urllib.parse import urlparse
from typing import Any, Dict, List
from flask import Flask, jsonify, render_template

from feeds import FEEDS, STATIC_LINKS

app = Flask(__name__, template_folder="templates", static_folder="static")

ITEMS_FILE = "items.json"

CANDIDATE_LOGOS = ["cubs-logo.png", "logo.png", "cubs.png", "purdue-logo.png"]
CANDIDATE_AUDIO = ["cubs-win.mp3", "fight-song.mp3", "theme.mp3"]

FRIENDLY_SOURCE_NAMES = {
    "mlb.com": "MLB.com",
    "espn.com": "ESPN",
    "nbcsportschicago.com": "NBC Sports Chicago",
    "bleachernation.com": "Bleacher Nation",
    "bleedcubbieblue.com": "Bleed Cubbie Blue",
    "chicagotribune.com": "Chicago Tribune",
    "chicago.suntimes.com": "Chicago Sun-Times",
    "cbssports.com": "CBS Sports",
    "sports.yahoo.com": "Yahoo Sports",
    "yardbarker.com": "Yardbarker",
    "reddit.com": "Reddit /r/CHICubs",
    "youtube.com": "YouTube",
    "news.google.com": "Google News",
}

def _first_existing(options: List[str]) -> str:
    for rel in options:
        full = os.path.join(app.static_folder, rel)
        if os.path.exists(full):
            return rel
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
    out: List[Dict[str, str]] = []
    seen = set()
    for u in FEEDS:
        try:
            host = urlparse(u).netloc.replace("www.", "").lower()
            name = FRIENDLY_SOURCE_NAMES.get(host, host)
            if name not in seen:
                seen.add(name)
                out.append({"name": name, "url": u})
        except Exception:
            continue
    return sorted(out, key=lambda d: d["name"].lower())

@app.route("/")
def index():
    data = _read_items()
    return render_template(
        "index.html",
        team=data.get("team", "Chicago Cubs"),
        updated_ts=data.get("updated_ts", time.time()),
        items=data.get("items", []),
        logo_path=_first_existing(CANDIDATE_LOGOS),
        audio_path=_first_existing(CANDIDATE_AUDIO),
        quick_links=STATIC_LINKS,
        sources=_build_sources(),
    )

@app.route("/items.json")
def items_json():
    return jsonify(_read_items())

@app.route("/health")
def health():
    return jsonify({"ok": True, "time": time.time()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
