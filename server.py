#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — News App Server
- Serves index and /items.json
- Reads items.json produced by collect.py
- Picks up your existing static logo/audio filenames if present
"""

import json
import os
import time
from typing import Any, Dict, List
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

ITEMS_FILE = "items.json"

# Try to preserve your current media file names.
CANDIDATE_LOGOS = [
    "cubs-logo.png", "logo.png", "cubs.png", "purdue-logo.png"
]
CANDIDATE_AUDIO = [
    "cubs-win.mp3", "fight-song.mp3", "theme.mp3"
]


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


@app.route("/")
def index():
    data = _read_items()
    logo_path = _first_existing(CANDIDATE_LOGOS)
    audio_path = _first_existing(CANDIDATE_AUDIO)
    return render_template(
        "index.html",
        team=data.get("team", "Chicago Cubs"),
        updated_ts=data.get("updated_ts", time.time()),
        items=data.get("items", []),
        logo_path=logo_path,
        audio_path=audio_path,
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
