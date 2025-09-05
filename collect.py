#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — Feed Collector (robust)
- Fetches FEEDS (requests with timeout, then feedparser)
- Light-but-accurate Cubs filter (trusted hosts bypass)
- Writes items.json (newest first, cap 50)
"""

import json
import time
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, List, Any, Optional

import requests
import feedparser

from feeds import FEEDS

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
    "+cubs-news-bot"
)

OUTPUT = "items.json"
MAX_ITEMS = 50
HTTP_TIMEOUT = 12  # seconds

# --- Filtering ----------------------------------------------------------------

ALLOW_PATTERNS = [
    r"\bChicago Cubs\b",
    r"\bCubs\b",
    r"\bWrigley\b",
    r"\bNorth Siders?\b",
    r"\bClark and Addison\b",
]

CUBS_NAMES = [
    # coaches/front office
    "Craig Counsell", "Jed Hoyer", "Carter Hawkins", "David Ross",
    # notable players (current/common)
    "Nico Hoerner", "Dansby Swanson", "Seiya Suzuki", "Ian Happ",
    "Christopher Morel", "Shota Imanaga", "Justin Steele", "Kyle Hendricks",
    "Cody Bellinger", "Pete Crow-Armstrong", "Miguel Amaya", "Jameson Taillon",
    "Ben Brown", "Jordan Wicks", "Keegan Thompson", "Adbert Alzolay",
]

EXCLUDE_PATTERNS = [
    r"\bWhite Sox\b", r"\bBears\b", r"\bBlackhawks\b", r"\bBulls\b",
    r"\bNotre Dame\b", r"\bNorthwestern\b",
]

TRUSTED_HOST_HINTS = [
    "mlb.com/cubs",
    "espn.com/mlb/team/_/name/chc",
    "nbcsportschicago.com",
    "bleachernation.com",
    "bleedcubbieblue.com",
    "yardbarker.com",
    "sports.yahoo.com/mlb/teams/chc",
    "cbssports.com/feeds/team/mlb/chc",
    "chicagotribune.com",
    "chicago.suntimes.com",
    "news.google.com",
    "reddit.com/r/CHICubs",
    "youtube.com/feeds/videos.xml",
]

def is_trusted(url: str) -> bool:
    u = url.lower()
    return any(h in u for h in TRUSTED_HOST_HINTS)

def strip_html(text: Optional[str]) -> str:
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

    # Google News type headlines
    if re.search(r"\bChicago\b", hay, flags=re.I) and re.search(r"\bMLB\b|\bbaseball\b", hay, flags=re.I):
        return True

    return False

def normalize_time(entry: Dict[str, Any]) -> float:
    # RFC822 strings
    for k in ("published", "updated", "pubDate"):
        if entry.get(k):
            try:
                dt = parsedate_to_datetime(entry[k])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.timestamp()
            except Exception:
                pass
    # struct_time
    for k in ("published_parsed", "updated_parsed"):
        if entry.get(k):
            try:
                return time.mktime(entry[k])  # type: ignore[arg-type]
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
    """
    Try requests first (handles some TLS/redirect quirks), then feedparser on bytes.
    Fall back to feedparser.parse(url) if requests fails.
    """
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=HTTP_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
        return feedparser.parse(resp.content)
    except Exception:
        return feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})

def collect() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for url in FEEDS:
        try:
            parsed = fetch_feed(url)
            feed_title = (parsed.feed.get("title") or "Source").strip()
            for entry in parsed.entries:
                try:
                    if allow_item(entry, url):
                        items.append(to_item(entry, feed_title))
                except Exception:
                    continue
        except Exception:
            continue

    # newest first + cap
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
