#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — News App Server (safe startup)
- Cubs-themed Purdue UI
- Fan-friendly quick links (feeds.STATIC_LINKS)
- Clean collapsible "News Sources" (from feeds.FEEDS)
- /collect-open   : run collector in a background thread
- /debug-collect  : run collector synchronously and return result
- /health         : collector status + last error
- SAFE AUTO-COLLECT: on the first normal page request only, if items.json is empty
  (no cron; non-blocking; guarded so it runs once per process)
"""

import json
import os
import time
import threading
from urllib.parse import urlparse
from typing import Any, Dict, List
from flask import Flask, jsonify, render_template

from feeds import FEEDS, STATIC_LINKS

app = Flask(__name__, template_folder="templates", static_folder="static")

ITEMS_FILE = "items.json"

# Media autodetect (keeps your filenames intact)
CANDIDATE_LOGOS = ["cubs-logo.png", "logo.png", "cubs.png", "purdue-logo.png"]
CANDIDATE_AUDIO = ["cubs-win.mp3", "fight-song.mp3", "theme.mp3"]

# Friendly names for source list
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

# ------------------------ Helpers ------------------------

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

# ---------------- Collector control & state ----------------

_collect_lock = threading.Lock()
_collect_state: Dict[str, Any] = {
    "running": False,
    "last_start": None,
    "last_end": None,
    "last_count": 0,
    "last_error": None,
}

# Guard to ensure we only try the auto-collect once per process
_startup_check_done = False
_startup_check_lock = threading.Lock()

def _run_collect_background():
    """Run the collector safely in a background thread and update items.json."""
    from collect import collect as _collector_collect  # local import avoids circular deps
    try:
        items = _collector_collect()
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

def _start_background_collect_if_idle() -> bool:
    """Start background collect if not already running. Returns True if started."""
    if _collect_state["running"]:
        return False
    acquired = _collect_lock.acquire(blocking=False)
    if not acquired:
        _collect_state["running"] = True
        return False
    _collect_state["running"] = True
    _collect_state["last_start"] = time.time()
    _collect_state["last_end"] = None
    threading.Thread(target=_run_collect_background, daemon=True).start()
    return True

def _items_empty() -> bool:
    try:
        data = _read_items()
        return not data.get("items")
    except Exception:
        return True

def _maybe_auto_collect_once():
    """
    Safe, lightweight auto-collect:
    - Runs at the first normal page request only (per worker)
    - Does nothing if DISABLE_STARTUP_COLLECT=1
    - Does nothing if items.json already has content
    - Non-blocking (background thread)
    """
    global _startup_check_done
    if os.environ.get("DISABLE_STARTUP_COLLECT") == "1":
        return
    if _startup_check_done:
        return
    with _startup_check_lock:
        if _startup_check_done:
            return
        _startup_check_done = True
        if _items_empty():
            _start_background_collect_if_idle()

# --------------------------- Routes ---------------------------

@app.route("/")
def index():
    # Kick off a one-time background collect if empty (safe, non-blocking)
    _maybe_auto_collect_once()

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
    """Kick off a background collect (non-blocking)."""
    started = _start_background_collect_if_idle()
    status = "started" if started else "already-running"
    return jsonify({
        "ok": True,
        "status": status,
        "last_count": _collect_state["last_count"],
        "last_error": _collect_state["last_error"],
    })

@app.route("/debug-collect")
def debug_collect():
    """
    Run collector synchronously and return a summary.
    Use this if you want an immediate refresh and to see any error surfaced.
    """
    from collect import collect as _collector_collect
    started = time.time()
    try:
        items = _collector_collect()
        _write_items(items)
        _collect_state.update({
            "running": False,
            "last_start": started,
            "last_end": time.time(),
            "last_count": len(items),
            "last_error": None,
        })
        return jsonify({"ok": True, "count": len(items), "duration_s": round(time.time() - started, 2)})
    except Exception as e:
        _collect_state.update({
            "running": False,
            "last_start": started,
            "last_end": time.time(),
            "last_error": repr(e),
        })
        return jsonify({"ok": False, "error": repr(e)}), 500

@app.route("/health")
def health():
    return jsonify({
        "ok": True,
        "time": time.time(),
        "collector": _collect_state
    })

# --------------------------- Main ---------------------------

if __name__ == "__main__":
    # For local debug: python3 server.py
    app.run(host="0.0.0.0", port=5000, debug=False)
