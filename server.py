#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — MLB Feed (Flask server with protected /collect-open)

Security:
- Set env COLLECT_TOKEN="some-long-random-string"
- /collect-open requires header: Authorization: Bearer <COLLECT_TOKEN>
- If COLLECT_TOKEN is UNSET, /collect-open is OPEN (not recommended)

Endpoints:
- GET /               -> renders templates/index.html with items.json content
- GET /items.json     -> returns the cached items (collector output)
- GET /collect-open   -> kicks collect.py in a background thread (requires token if set)
- GET /health         -> { ok: true, updated: "...", count: N }
- GET /static/<file>  -> serves static assets (style.css, logo.png, etc.)
"""

import os
import json
import threading
import subprocess
from typing import Dict, Any
from flask import Flask, jsonify, render_template, send_from_directory, request, abort

# Import feed definitions and team name
from feeds import FEEDS, STATIC_LINKS, TEAM_NAME

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "items.json")
COLLECT_SCRIPT = os.path.join(APP_DIR, "collect.py")

app = Flask(__name__, template_folder="templates", static_folder="static")

# -------- helpers --------

def load_items() -> Dict[str, Any]:
    """Load items.json produced by collect.py; tolerate missing/invalid file."""
    if not os.path.exists(DATA_FILE):
        return {"updated": None, "items": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"updated": None, "items": []}
            data.setdefault("items", [])
            return data
    except Exception:
        return {"updated": None, "items": []}

def start_collect_async() -> None:
    """Fire-and-forget run of collect.py in a background thread."""
    def worker():
        try:
            subprocess.run(
                ["python3", COLLECT_SCRIPT],
                cwd=APP_DIR,
                check=False
            )
        except Exception:
            # Swallow errors; /health + logs are where you’d check status
            pass
    threading.Thread(target=worker, daemon=True).start()

def require_collect_auth() -> None:
    """Enforce Bearer token on /collect-open if COLLECT_TOKEN is set."""
    token = os.environ.get("COLLECT_TOKEN", "").strip()
    if not token:
        # No token configured -> endpoint is open (for simple setups)
        return
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        abort(401)
    supplied = auth.split(" ", 1)[1].strip()
    if supplied != token:
        abort(403)

# -------- routes --------

@app.route("/")
def index():
    data = load_items()
    return render_template(
        "index.html",
        team_name=TEAM_NAME,
        updated=data.get("updated"),
        items=data.get("items", []),
        feeds=FEEDS,
        quick_links=STATIC_LINKS,
    )

@app.route("/items.json")
def items_json():
    return jsonify(load_items())

@app.route("/collect-open", methods=["GET", "POST"])
def collect_open():
    require_collect_auth()
    start_collect_async()
    return jsonify({"ok": True})

@app.route("/health")
def health():
    data = load_items()
    return jsonify({
        "ok": True,
        "updated": data.get("updated"),
        "count": len(data.get("items", []))
    })

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Optional: simple version endpoint using Railway/Git env vars
@app.route("/version")
def version():
    sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA") or os.environ.get("GIT_COMMIT") or ""
    return jsonify({"commit": sha[:12] if sha else None})

if __name__ == "__main__":
    # Local dev fallback (Railway sets PORT in production)
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
