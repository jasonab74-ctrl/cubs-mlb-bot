#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — Feeds + Fan-Friendly Quick Links
"""

FEEDS = [
    # Team/league outlets
    "https://www.mlb.com/cubs/feeds/news/rss.xml",
    "https://www.espn.com/espn/rss/mlb/team?team=chc",
    "https://www.nbcsportschicago.com/rss/teams/chicago-cubs",
    "https://www.cbssports.com/feeds/team/mlb/chc",
    "https://sports.yahoo.com/mlb/teams/chc/rss/",
    # Cubs-focused sites
    "https://www.bleachernation.com/cubs/feed/",
    "https://www.bleedcubbieblue.com/rss/index.xml",
    "https://www.yardbarker.com/rss/team/56",
    # Local media
    "https://www.chicagotribune.com/arcio/rss/category/sports/cubs/?query=display_date:[* TO NOW]",
    "https://chicago.suntimes.com/cubs/rss",
    # Aggregator (broad but useful)
    "https://news.google.com/rss/search?q=%22Chicago%20Cubs%22%20OR%20Cubs%20-%22Iowa%20Cubs%22&hl=en-US&gl=US&ceid=US:en",
    # Community / video
    "https://www.reddit.com/r/CHICubs/.rss",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyerV8C6ip3zjYB4Z1cdqgw",
]

# Fan-facing quick links (pills at top) — trimmed & useful
STATIC_LINKS = [
    {"name": "Bleacher Nation",   "url": "https://www.bleachernation.com/chicago-cubs/"},
    {"name": "Bleed Cubbie Blue", "url": "https://www.bleedcubbieblue.com/"},
    {"name": "Reddit /r/CHICubs", "url": "https://www.reddit.com/r/CHICubs/"},
    {"name": "ESPN Cubs",         "url": "https://www.espn.com/mlb/team/_/name/chc/chicago-cubs"},
    {"name": "MLB.com Cubs",      "url": "https://www.mlb.com/cubs"},
    {"name": "NBC Sports Chicago","url": "https://www.nbcsportschicago.com/teams/chicago-cubs"},
    {"name": "Chicago Tribune",   "url": "https://www.chicagotribune.com/sports/cubs/"},
    {"name": "Sun-Times Cubs",    "url": "https://chicago.suntimes.com/cubs"},
    {"name": "CBS Sports Cubs",   "url": "https://www.cbssports.com/mlb/teams/CHC/chicago-cubs/"},
    {"name": "Yahoo Cubs",        "url": "https://sports.yahoo.com/mlb/teams/chc/"},
    # a few utility/fan staples
    {"name": "Schedule",          "url": "https://www.mlb.com/cubs/schedule"},
    {"name": "Box Scores",        "url": "https://www.espn.com/mlb/team/schedule/_/name/chc"},
]
