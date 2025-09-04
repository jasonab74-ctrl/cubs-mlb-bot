#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — Feed Collector
- Pulls FEEDS, filters for Cubs content, writes items.json
- Caps at 50 newest items
"""

import json
import time
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List, Any

import feedparser

from feeds import FEEDS

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36 (+sports-app-collector)"
)

OUTPUT = "items.json"
MAX_ITEMS = 50

# ----- Filtering --------------------------------------------------------------

# Strong allow cues
ALLOW_PATTERNS = [
    r"\bChicago Cubs\b",
    r"\bCubs\b",
    r"\bWrigley\b",
    r"\bNorth Siders?\b",
    r"\bClark and Addison\b",
]

# Names to catch box scores/features that skip team names
CUBS_NAMES = [
    "Craig Counsell", "Jed Hoyer", "David Ross",
    "Nico Hoerner", "Dansby Swanson", "Seiya Suzuki", "Ian Happ",
    "Christopher Morel", "Shota Imanaga", "Justin Steele", "Kyle Hendricks",
    "Cody Bellinger", "Pete Crow-Armstrong", "Miguel Amaya", "Jameson Taillon",
]

# Light exclusions (don’t block obvious neighboring teams’ news unless necessary)
EXCLUDE_PATTERNS = [
    r"\bWhite Sox\b",
    r"\bBears\b", r"\bBlackhawks\b", r"\bBulls\b",
    r"\bNotre Dame\b", r"\bNorthwestern\b",
]

# Hosts that are already Cubs-specific; we trust them and allow broadly
TRUSTED_HOST_HINTS = [
    "mlb.com/cubs",
    "espn.com/mlb/team/_/name/chc",
    "nbcsportschicago.com",
    "bleachernation.com",
    "bleedcubbieblue.com",
    "yardbarker.com",
    "yahoo.com/mlb/teams/chc",
    "cbssports.com/feeds/team/mlb/chc",
]

def is_trusted(url: str) -> bool:
    url_lower = url.lower()
    return any(h in url_lower for h in TRUSTED_HOST_HINTS)

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")

def allow_item(entry: Dict[str, Any], source_url: str) -> bool:
    title = (entry.get("title") or "").strip()
    summary = strip_html(entry.get("summary") or entry.get("description") or "")
    hay = f"{title}\n{summary}"

    if any(re.search(p, hay, flags=re.I) for p in EXCLUDE_PATTERNS):
        return False

    if is_trusted(source_url):
        return True

    if any(re.search(p, hay, flags=re.I) for p in ALLOW_PATTERNS):
        return True

    if any(name.lower() in hay.lower() for name in CUBS_NAMES):
        return True

    # Google News sometimes puts team in 'source' only; be permissive if title mentions MLB and Chicago
    if re.search(r"\bChicago\b", hay, flags=re.I) and re.search(r"\bMLB\b|\bbaseball\b", hay, flags=re.I):
        return True

    return False

def normalize_time(entry: Dict[str, Any]) -> float:
    for k in ("published", "updated", "pubDate"):
        if entry.get(k):
            try:
                dt = parsedate_to_datetime(entry[k])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.timestamp()
            except Exception:
                pass
    for k in ("published_parsed", "updated_parsed"):
        if entry.get(k):
            try:
                return time.mktime(entry[k])
            except Exception:
                pass
    return time.time()

def to_item(entry: Dict[str, Any], feed_title: str) -> Dict[str, Any]:
    link = entry.get("link") or ""
    title = (entry.get("title") or "").strip()
    author = (entry.get("author") or "").strip()
    summary = strip_html(entry.get("summary") or entry.get("description") or "").strip()
    ts = normalize_time(entry)
    iso = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return {
        "title": title,
        "link": link,
        "by": author or feed_title,
        "source": feed_title,
        "published_ts": ts,
        "published_iso": iso,
        "summary": summary[:5000],
    }

def fetch_feed(url: str):
    return feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})

def collect() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for url in FEEDS:
        try:
            parsed = fetch_feed(url)
            feed_title = (parsed.feed.get("title") or "Source").strip()
            for entry in parsed.entries:
                if allow_item(entry, url):
                    items.append(to_item(entry, feed_title))
        except Exception:
            continue

    items.sort(key=lambda x: x["published_ts"], reverse=True)
    return items[:MAX_ITEMS]

def main() -> None:
    data = {
        "team": "Chicago Cubs",
        "updated_ts": time.time(),
        "items": collect(),
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
