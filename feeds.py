#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — Feed list and quick links
Add/remove as you like. Prefer team-specific feeds when available.
"""

FEEDS = [
    # Team/league outlets
    "https://www.mlb.com/cubs/feeds/news/rss.xml",
    "https://www.espn.com/espn/rss/mlb/team?team=chc",
    "https://www.nbcsportschicago.com/rss/teams/chicago-cubs",
    "https://www.cbssports.com/feeds/team/mlb/chc",  # CBS Sports team feed
    "https://sports.yahoo.com/mlb/teams/chc/rss/",   # Yahoo team

    # Cubs-focused sites
    "https://www.bleachernation.com/cubs/feed/",
    "https://www.bleedcubbieblue.com/rss/index.xml",
    "https://www.yardbarker.com/rss/team/56",  # Cubs team ID on Yardbarker

    # Local media
    "https://www.chicagotribune.com/arcio/rss/category/sports/cubs/?query=display_date:[* TO NOW]",
    "https://chicago.suntimes.com/cubs/rss",

    # Aggregators
    "https://news.google.com/rss/search?q=%22Chicago%20Cubs%22%20OR%20Cubs%20-%22Iowa%20Cubs%22&hl=en-US&gl=US&ceid=US:en",

    # Community / video (can be noisy but useful)
    "https://www.reddit.com/r/CHICubs/.rss",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyerV8C6ip3zjYB4Z1cdqgw",
]

# Buttons row (edit freely)
STATIC_LINKS = [
    {"name": "Schedule", "url": "https://www.mlb.com/cubs/schedule"},
    {"name": "Roster", "url": "https://www.mlb.com/cubs/roster"},
    {"name": "Standings", "url": "https://www.mlb.com/standings"},
    {"name": "Tickets", "url": "https://www.mlb.com/cubs/tickets"},
    {"name": "Box Scores", "url": "https://www.espn.com/mlb/team/schedule/_/name/chc"},
    {"name": "Stats", "url": "https://www.mlb.com/cubs/stats"},
    {"name": "Depth Chart", "url": "https://www.mlb.com/cubs/roster/depth-chart"},
    {"name": "Transactions", "url": "https://www.mlb.com/cubs/roster/transactions"},
    {"name": "Prospects", "url": "https://www.mlb.com/prospects/cubs"},
    {"name": "Shop", "url": "https://www.mlbshop.com/chicago-cubs/o-2409+t-92200540+z-9931-154294832"},
]
