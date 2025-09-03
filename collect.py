#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, json, time, re, html as _html
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from urllib.parse import urlparse

import requests, feedparser
from feeds import FEEDS

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUTFILE = os.path.join(APP_DIR, "items.json")

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
HTTP_TIMEOUT = 20
MAX_ITEMS = 50   # <-- cap to 50 most recent

# Domains that auto-pass filtering (official/major Cubs sources, keep as-is or extend)
TRUSTED_DOMAINS = {
    "mlb.com", "www.mlb.com",
    "espn.com", "www.espn.com",
    "bleedcubbieblue.com", "www.bleedcubbieblue.com",
    "cubsinsider.com", "www.cubsinsider.com",
    "bleachernation.com", "www.bleachernation.com",
    "sports.yahoo.com", "www.sports.yahoo.com",
    "cbssports.com", "www.cbssports.com",
    "chicagotribune.com", "www.chicagotribune.com",
    "chicago.suntimes.com",
    "reddit.com", "www.reddit.com", "old.reddit.com",
}

def http_get(url: str) -> bytes:
    r = requests.get(
        url, timeout=HTTP_TIMEOUT, allow_redirects=True,
        headers={"User-Agent": USER_AGENT, "Accept":"application/rss+xml,application/xml,*/*;q=0.8"}
    )
    r.raise_for_status()
    return r.content

def clean(s:str)->str:
    s = _html.unescape(s or "")
    s = re.sub(r"<.*?>", "", s)
    return s.replace("\xa0", " ").strip()

def domain_of(u:str)->str:
    try:
        d = urlparse(u).netloc.lower()
        return re.sub(r"^www\.", "", d)
    except Exception:
        return ""

def fmt_clock(dt):
    h = dt.strftime("%I").lstrip("0") or "0"
    return f"{h}:{dt.strftime('%M')} {dt.strftime('%p')}"

def nice_when(ts:int, raw:str)->str:
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts>0 else None
    except Exception:
        dt=None
    if not dt: return raw or ""
    today = datetime.now(timezone.utc).date(); d = dt.date()
    if d==today: p="Today"
    elif (today-d)==timedelta(days=1): p="Yesterday"
    else: p = dt.strftime("%b ")+str(int(dt.strftime("%d")))
    return f"{p} • {fmt_clock(dt)}"

# ---- Cubs filter (loose but targeted) ----
POS_STRONG = [
    "chicago cubs"," cubs","north siders","cubbies","wrigley field","wrigleyville",
    "craig counsell","tom ricketts",
    "dansby swanson","cody bellinger","seiya suzuki","ian happ","nico hoerner",
    "christopher morel","pete crow-armstrong","michael bush",
    "justin steele","shota imanaga","kyle hendricks","javier assad","ben brown",
    "adbert alzolay","jordan wicks","hayden wesneski","julian merriweather",
    "iowa cubs","tennessee smokies","south bend cubs","myrtle beach pelicans",
]
POS_BASEBALL = [
    "mlb","baseball","pitcher","pitching","hitter","batting","lineup","home run",
    "homer","hr","rbi","era","innings","bullpen","rotation","il","injury","rehab",
    "call-up","optioned","waivers","trade","minor league","prospect","double-a",
    "triple-a","aaa","aa","box score","recap","preview"
]
NEG_OTHER = [
    "chicago white sox","white sox","bears","bulls","blackhawks","fire",
    "nfl","nba","nhl","mls","college football","ncaa football","basketball","football"
]

def looks_cubs(title:str, summary:str, link:str)->bool:
    txt = f"{title} {summary} {link}".lower()

    # Trusted domains always pass
    d = urlparse(link).netloc.lower()
    if d in TRUSTED_DOMAINS or re.sub(r"^www\.", "", d) in TRUSTED_DOMAINS:
        return True

    # Hard drops first
    if any(n in txt for n in NEG_OTHER):
        return False

    # Obvious keeps
    if any(p in txt for p in POS_STRONG):
        return True

    # Generic keeps: mention Cubs/Wrigley with baseball context
    if ("cubs" in txt or "wrigley" in txt) and any(b in txt for b in POS_BASEBALL):
        return True

    # Explicit team phrase
    if "chicago cubs" in txt:
        return True

    return False

def normalize(feed_name, feed_url, e)->Dict:
    title = clean(e.get("title") or "")
    link = e.get("link") or e.get("id") or ""
    summary = clean(e.get("summary") or e.get("description") or "")
    pub = e.get("published") or e.get("updated") or ""
    ts = 0
    try:
        if e.get("published_parsed"): ts = time.mktime(e.published_parsed)
        elif e.get("updated_parsed"): ts = time.mktime(e.updated_parsed)
    except Exception:
        ts = 0
    return {
        "source": feed_name, "source_url": feed_url,
        "domain": domain_of(link),
        "title": title, "link": link, "summary": summary[:400],
        "published": pub, "when": nice_when(ts, pub), "_ts": ts
    }

def dedupe(items:List[Dict])->List[Dict]:
    seen, out = set(), []
    for it in items:
        k = it["link"] or (it["title"], it["source"])
        if k in seen: continue
        seen.add(k); out.append(it)
    return out

def main():
    raw=[]
    for f in FEEDS:
        try:
            parsed = feedparser.parse(http_get(f["url"]))
            name = parsed.feed.get("title", f["name"])
            for e in parsed.get("entries", []):
                it = normalize(name, f["url"], e)
                if looks_cubs(it["title"], it["summary"], it["link"]):
                    raw.append(it)
        except Exception:
            continue

    items = dedupe(raw)
    # Sort newest first; _ts may be 0 for some feeds, so include published as tie-breaker
    items.sort(key=lambda x:(x.get("_ts",0), x.get("published","")), reverse=True)
    items = items[:MAX_ITEMS]  # <-- keep only the 50 most recent
    payload = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "items": items
    }
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(items)} items to {OUTFILE}")

if __name__=="__main__":
    main()
