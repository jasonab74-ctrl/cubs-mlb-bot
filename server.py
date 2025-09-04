#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — News App Server
- Purdue-style UI with Cubs branding
- Fan-friendly quick links (from feeds.STATIC_LINKS)
- Clean collapsible "News Sources" (from feeds.FEEDS)
- NEW: /collect-open endpoint to refresh items.json on-demand (no cron needed)
"""

import json
import os
import time
import threading
from urllib.parse import urlparse
from typing import Any, Dict, List
from flask import Flask, jsonify, render_template

from feeds import FEEDS, STATIC_LINKS

# ------- App & paths ----------------------------------------------------------

app = Flask(__name__, template_folder="templates", static_folder="static")
ITEMS_FILE = "items.json"

# Media auto-detection (keeps your filenames intact if present)
CANDIDATE_LOGOS = ["cubs-logo.png", "logo.png", "cubs.png", "purdue-logo.png"]
CANDIDATE_AUDIO = ["cubs-win.mp3", "fight-song.mp3", "theme.mp3"]

# Human names for sources (fallback to host)
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

# ------- Helpers --------------------------------------------------------------

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

def _write_items(items: List[Dict[str, Any]]) -> None:
    data = {"team": "Chicago Cubs", "updated_ts": time.time(), "items": items}
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# ------- On-demand collector (no cron) ---------------------------------------

_collect_lock = threading.Lock()
_collect_state: Dict[str, Any] = {
    "running": False,
    "last_start": None,
    "last_end": None,
    "last_count": 0,
    "last_error": None,
}

def _run_collect_background():
    """Run the collector safely in a background thread and update items.json."""
    from collect import collect as _collector_collect  # local import avoids circulars
    try:
        items = _collector_collect()  # returns list of items (already sorted & capped)
        _write_items(items)
        _collect_state["last_count"] = len(items)
        _collect_state["last_error"] = None
    except Exception as e:
        _collect_state["last_error"] = repr(e)
    finally:
        _collect_state["last_end"] = time.time()
        _collect_state["running"] = False
        try:
            _collect_lock.release()
        except Exception:
            pass

# ------- Routes ---------------------------------------------------------------

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

@app.route("/collect-open")
def collect_open():
    """
    Start a background collection run if one isn't already running.
    Returns immediate status JSON. Hit this URL whenever you want a manual refresh.
    """
    if _collect_state["running"]:
        return jsonify({
            "ok": True,
            "status": "already-running",
            "last_start": _collect_state["last_start"],
            "last_end": _collect_state["last_end"],
            "last_count": _collect_state["last_count"],
            "last_error": _collect_state["last_error"],
        })

    acquired = _collect_lock.acquire(blocking=False)
    if not acquired:
        # Another request won the race; report running.
        _collect_state["running"] = True
        return jsonify({"ok": True, "status": "already-running"})

    _collect_state["running"] = True
    _collect_state["last_start"] = time.time()
    _collect_state["last_end"] = None

    t = threading.Thread(target=_run_collect_background, daemon=True)
    t.start()

    return jsonify({"ok": True, "status": "started"})

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "time": time.time(),
        "collector": {
            "running": _collect_state["running"],
            "last_start": _collect_state["last_start"],
            "last_end": _collect_state["last_end"],
            "last_count": _collect_state["last_count"],
            "last_error": _collect_state["last_error"],
        }
    })

# ------- Main -----------------------------------------------------------------

if __name__ == "__main__":
    # For local debug: python3 server.py
    app.run(host="0.0.0.0", port=5000, debug=False)
