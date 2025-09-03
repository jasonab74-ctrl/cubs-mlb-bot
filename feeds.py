# feeds.py — Chicago Cubs sources (used by collect.py)
# FEEDS drives the Sources dropdown. STATIC_LINKS drives the top buttons.

FEEDS = [
    # ===== Broad Cubs aggregators
    {"name": "Google News — Chicago Cubs",
     "url": "https://news.google.com/rss/search?q=%22Chicago+Cubs%22+OR+Cubs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Chicago Cubs",
     "url": "https://www.bing.com/news/search?q=%22Chicago+Cubs%22&format=RSS"},

    # ===== Major outlets (Cubs filters via Google News site: searches)
    {"name": "Google — MLB.com (Cubs)",
     "url": "https://news.google.com/rss/search?q=site:mlb.com/cubs+OR+site:mlb.com/news+Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google — ESPN (Cubs)",
     "url": "https://news.google.com/rss/search?q=site:espn.com+Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google — Yahoo Sports (Cubs)",
     "url": "https://news.google.com/rss/search?q=site:sports.yahoo.com+Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google — CBS Sports (Cubs)",
     "url": "https://news.google.com/rss/search?q=site:cbssports.com+Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google — The Athletic (Cubs)",
     "url": "https://news.google.com/rss/search?q=site:theathletic.com+Chicago+Cubs&hl=en-US&gl=US&ceid=US:en"},

    # ===== Team blogs / insiders
    {"name": "Cubs Insider (RSS)",
     "url": "https://www.cubsinsider.com/feed/"},
    {"name": "Bleacher Nation — Cubs",
     "url": "https://www.bleachernation.com/cubs-rumors/feed/"},
    {"name": "Bleed Cubbie Blue",
     "url": "https://www.bleedcubbieblue.com/rss/index.xml"},

    # ===== Reddit
    {"name": "Reddit — r/CHICubs",
     "url": "https://www.reddit.com/r/CHICubs/.rss"},
]

# Quick links (top buttons). Order & labels to match your UI.
STATIC_LINKS = [
    {"label": "Cubs — Official",      "url": "https://www.mlb.com/cubs"},
    {"label": "Schedule",             "url": "https://www.mlb.com/cubs/schedule"},
    {"label": "Roster",               "url": "https://www.mlb.com/cubs/roster"},
    {"label": "Standings",            "url": "https://www.mlb.com/standings"},
    {"label": "ESPN",                 "url": "https://www.espn.com/mlb/team/_/name/chc/chicago-cubs"},
    {"label": "CBS Sports",           "url": "https://www.cbssports.com/mlb/teams/CHC/chicago-cubs/"},
    {"label": "Yahoo Sports",         "url": "https://sports.yahoo.com/mlb/teams/chicago/"},
    {"label": "Bleed Cubbie Blue",    "url": "https://www.bleedcubbieblue.com/"},
    {"label": "Cubs Insider",         "url": "https://www.cubsinsider.com/"},
    {"label": "Bleacher Nation — Cubs","url": "https://www.bleachernation.com/chicago-cubs/"},
    {"label": "Reddit — r/CHICubs",   "url": "https://www.reddit.com/r/CHICubs/"},
]
