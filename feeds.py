# -*- coding: utf-8 -*-

TEAM_NAME = "Chicago Cubs — MLB Feed"

# Quick link buttons (left-to-right)
STATIC_LINKS = [
    ("Cubs — Official", "https://www.mlb.com/cubs"),
    ("Schedule", "https://www.mlb.com/cubs/schedule"),
    ("Roster", "https://www.mlb.com/cubs/roster"),
    ("Standings", "https://www.mlb.com/standings"),
    ("ESPN", "https://www.espn.com/mlb/team/_/name/chc/chicago-cubs"),
    ("CBS Sports", "https://www.cbssports.com/mlb/teams/CHC/chicago-cubs/"),
    ("Yahoo Sports", "https://sports.yahoo.com/mlb/teams/chicago/"),
    ("Bleed Cubbie Blue", "https://www.bleedcubbieblue.com/"),
    ("Cubs Insider", "https://www.cubsinsider.com/"),
    ("Bleacher Nation — Cubs", "https://www.bleachernation.com/chicago-cubs-news-rumors/"),
    ("Reddit — r/CHICubs", "https://www.reddit.com/r/CHICubs/"),
]

# News/feeds shown in Sources dropdown and used by collect.py
FEEDS = [
    # Broad news
    {"name":"Google News — Chicago Cubs","url":"https://news.google.com/rss/search?q=%22Chicago+Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Bing News — Chicago Cubs","url":"https://www.bing.com/news/search?q=%22Chicago+Cubs%22&format=rss"},

    # Targeted site queries (reliable via Google News)
    {"name":"Google — MLB.com (Cubs)","url":"https://news.google.com/rss/search?q=site:mlb.com%2Fcubs+%22Chicago+Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — ESPN (Cubs)","url":"https://news.google.com/rss/search?q=site:espn.com+%22Chicago+Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Yahoo Sports (Cubs)","url":"https://news.google.com/rss/search?q=site:sports.yahoo.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — CBS Sports (Cubs)","url":"https://news.google.com/rss/search?q=site:cbssports.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — The Athletic (Cubs)","url":"https://news.google.com/rss/search?q=site:theathletic.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Chicago Tribune (Cubs)","url":"https://news.google.com/rss/search?q=site:chicagotribune.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Sun-Times (Cubs)","url":"https://news.google.com/rss/search?q=site:chicago.suntimes.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Bleacher Nation (Cubs)","url":"https://news.google.com/rss/search?q=site:bleachernation.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Cubs Insider","url":"https://news.google.com/rss/search?q=site:cubsinsider.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},
    {"name":"Google — Bleed Cubbie Blue","url":"https://news.google.com/rss/search?q=site:bleedcubbieblue.com+%22Cubs%22&hl=en-US&gl=US&ceid=US:en"},

    # Direct RSS where available
    {"name":"Bleed Cubbie Blue (RSS)","url":"https://www.bleedcubbieblue.com/rss/index.xml"},
    {"name":"Cubs Insider (RSS)","url":"https://www.cubsinsider.com/feed/"},
    {"name":"Reddit — r/CHICubs (RSS)","url":"https://www.reddit.com/r/CHICubs/.rss"},

    # League-wide (helps fill slow news days)
    {"name":"MLB — League News","url":"https://www.mlb.com/feeds/news/rss.xml"},
]
