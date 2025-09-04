#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chicago Cubs — Feed list and quick links
Edit FEEDS to add/remove sources. Prefer team-specific pages when possible.
"""

FEEDS = [
    # MLB.com Cubs
    "https://www.mlb.com/cubs/feeds/news/rss.xml",
    # ESPN team page
    "https://www.espn.com/espn/rss/mlb/team?team=chc",
    # NBC Sports Chicago (Cubs)
    "https://www.nbcsportschicago.com/rss/teams/chicago-cubs",
    # Bleacher Nation (Cubs)
    "https://www.bleachernation.com/cubs/feed/",
    # SB Nation (Bleed Cubbie Blue)
    "https://www.bleedcubbieblue.com/rss/index.xml",
    # Chicago Tribune Cubs
    "https://www.chicagotribune.com/arcio/rss/category/sports/cubs/?query=display_date:[* TO NOW]",
    # Sun-Times Cubs
    "https://chicago.suntimes.com/cubs/rss",
    # Reddit r/CHICubs (can be noisy, but useful)
    "https://www.reddit.com/r/CHICubs/.rss",
    # YouTube – Chicago Cubs channel uploads (if present; YouTube RSS works via /feeds)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyerV8C6ip3zjYB4Z1cdqgw",
]

# Optional: buttons on top of the page (names/URLs)
STATIC_LINKS = [
    {"name": "Schedule", "url": "https://www.mlb.com/cubs/schedule"},
    {"name": "Roster", "url": "https://www.mlb.com/cubs/roster"},
    {"name": "Standings", "url": "https://www.mlb.com/standings"},
    {"name": "Tickets", "url": "https://www.mlb.com/cubs/tickets"},
    {"name": "Box Scores", "url": "https://www.espn.com/mlb/team/schedule/_/name/chc"},
]
