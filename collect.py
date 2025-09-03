#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collects articles from FEEDS (feeds.py), filters for **Chicago Cubs (MLB)**,
normalizes, sorts newest-first, and writes items.json.

- Always excludes other sports (NFL/NBA/NHL/CFB, etc.).
- Trusted Cubs sources bypass strict include checks but STILL honor hard excludes.
- Caps output to the 50 most recent (override with MAX_ITEMS env var).
"""

import os
import json
import time
from datetime import datetime, timezone
from typing import List, Dict, Any

import feedparser
import requests

from feeds import FEEDS  # list of dicts: {"name": ..., "url": ...}

# ---- Settings ----
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "items.json")
TIMEOUT = float(os.environ.get("HTTP_TIMEOUT", "12"))
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "50"))

# Trusted sources (still respect hard excludes)
TRUSTED_SOURCES = {
    "Cubs — Official",
    "Bleed Cubbie Blue",
    "Cubs Insider",
    "Bleacher Nation — Cubs",
    "Reddit — r/CHICubs",
    "ESPN",
    "CBS Sports",
    "Yahoo Sports",
}

# Include signals (team/venue/league)
KEY_INCLUDE = [
    "chicago cubs", "cubs", "north siders", "north siders",
    "wrigley", "wrigley field",
    "mlb", "major league baseball", "national league", "nl central",
]

# Baseball context words
KEY_BASEBALL = [
    "baseball", "mlb", "pitcher", "reliever", "starter", "rotation", "bullpen",
    "inning", "batting", "hitter", "hitting", "home run", "homer", "slugger",
    "triple-a", "iowa cubs", "minor league", "prospect", "lineup",
]

# Hard excludes — these block items even from trusted sources
KEY_EXCLUDE = [
    # other Chicago teams / sports
    "bears", "nfl", "blackhawks", "nhl", "bulls", "nba", "sky", "wnba",
    "fire", "mls", "chicago state", "northwestern", "white sox", "sox",
    # college football/basketball terms
    "purdue", "boilermaker", "boilermakers", "notre dame", "fighting irish",
    "illini", "northwestern wildcats", "badgers", "buckeyes", "spartans",
    "football", "college football", "cfb",
    # obviously not baseball
    "volleyball", "softball", "soccer",
]

# People (recent/typical Cubs references — add more anytime)
PEOPLE = [
    "jed hoyer", "carter hawkins", "craig counsell",
    "dansby swanson", "seiya suzuki", "ian happ", "nicho hoerner", "christopher morel",
    "michael busch", "pete crow-armstrong", "shota imanaga", "justin steele",
    "javier assad", "jordan wicks", "adbert alzolay", "hector neris", "mark leiter jr",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch(url: str) -> bytes:
    r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "cubs-feed-bot/1.0"})
    r.raise_for_status()
    return r.content


def parse_datetime(entry: Dict[str, Any]) -> float:
    ts = None
    for key in ("published_parsed", "updated_parsed"):
        val = entry.get(key)
        if val:
            try:
                ts = time.mktime(val)
                break
            except Exception:
                pass
    if ts is None:
        ts = time.time()
    return float(ts)


def norm(x: Any) -> str:
    return (x or "").strip()


def allow_item(title: str, summary: str, source: str) -> bool:
    """
    Cubs filter:
    - Hard excludes first (block non-baseball/other teams).
    - Trusted sources allowed after excludes.
    - Otherwise require Cubs/venue/league + baseball context OR player/exec names.
    """
    t = f"{title} {summary}".lower()

    if any(ex in t for ex in KEY_EXCLUDE):
        return False

    if source in TRUSTED_SOURCES:
        return True

    inc_hit = any(k in t for k in KEY_INCLUDE) or any(p in t for p in PEOPLE)
    bb_hit  = any(k in t for k in KEY_BASEBALL)

    return inc_hit and bb_hit


def normalize(entry: Dict[str, Any], source: str) -> Dict[str, Any]:
    title = norm(entry.get("title"))
    link = norm(entry.get("link"))
    summary = norm(entry.get("summary") or entry.get("description") or "")
    ts = parse_datetime(entry)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    nice = dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

    return {
        "title": title,
        "link": link,
        "summary": summary,
        "date": nice,
        "ts": ts,
        "source": source,
    }


def collect() -> int:
    items: List[Dict[str, Any]] = []

    for feed in FEEDS:
        name = feed.get("name", "Unknown")
        url = feed.get("url")
        if not url:
            continue
        try:
            raw = fetch(url)
            parsed = feedparser.parse(raw)
            for e in parsed.entries:
                n = normalize(e, name)
                if allow_item(n["title"], n["summary"], name):
                    items.append(n)
        except Exception as e:
            print(f"[collect] feed error: {name}: {e}", flush=True)
            continue

    # Newest-first + cap
    items.sort(key=lambda x: x.get("ts", 0.0), reverse=True)
    if MAX_ITEMS > 0:
        items = items[:MAX_ITEMS]

    data = {
        "items": items,
        "meta": {
            "generated_at": utc_now_iso(),
            "count": len(items),
            "max": MAX_ITEMS,
        },
    }

    tmp = OUTPUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, OUTPUT_PATH)

    print(f"[collect] wrote {len(items)} items (cap={MAX_ITEMS}) → {OUTPUT_PATH}", flush=True)
    return len(items)


if __name__ == "__main__":
    collect()
