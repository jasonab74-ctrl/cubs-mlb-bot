#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, threading, subprocess
from typing import Dict, Any
from flask import Flask, jsonify, render_template, send_from_directory
from feeds import FEEDS, STATIC_LINKS, TEAM_NAME

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "items.json")

app = Flask(__name__, template_folder="templates", static_folder="static")

def load_items()->Dict[str,Any]:
    if not os.path.exists(DATA_FILE): return {"updated":None,"items":[]}
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return {"updated":None,"items":[]}

@app.route("/")
def index():
    data=load_items()
    return render_template("index.html", team_name=TEAM_NAME, updated=data.get("updated"),
                           items=data.get("items",[]), feeds=FEEDS, quick_links=STATIC_LINKS)

@app.route("/items.json")
def items_json(): return jsonify(load_items())

@app.route("/collect-open")
def collect_open():
    # Fire-and-forget build of items.json (handy on free hosts)
    def worker():
        try: subprocess.run(["python3", os.path.join(APP_DIR,"collect.py")], check=False)
        except Exception: pass
    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"ok":True})

@app.route("/health")
def health():
    data=load_items()
    return jsonify({"ok":True,"updated":data.get("updated")})

@app.route("/static/<path:filename>")
def static_files(filename): return send_from_directory(app.static_folder, filename)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT","8080")), debug=True)
