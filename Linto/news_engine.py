import feedparser
import requests
import hashlib
import json
import os

NEWS_CACHE_DIR = "news_cache"

os.makedirs(
    NEWS_CACHE_DIR,
    exist_ok=True
)

RSS_FEEDS = {

    "BTC": [

        "https://www.coindesk.com/arc/outboundfeeds/rss/",

        "https://cointelegraph.com/rss"
    ],

     "GOLD": [

        # Reuters Commodities
        "https://www.reutersagency.com/feed/?best-topics=commodities",

        # Investing.com Commodities
        "https://www.investing.com/rss/news_25.rss",

        # FXStreet Gold
        "https://www.fxstreet.com/rss/news",

        # Kitco News
        "https://www.kitco.com/rss/news",

        # Mining.com Precious Metals
        "https://www.mining.com/feed/",

        # MarketWatch Markets
        "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",

        # Yahoo Finance News
        "https://finance.yahoo.com/news/rssindex",

        # CNBC Markets
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",

        # Federal Reserve News
        "https://www.federalreserve.gov/feeds/press_all.xml",

        # IMF News
        "https://www.imf.org/en/News/RSS"
    ]
}
KEYWORDS = {

    "BTC": [
        "bitcoin",
        "crypto",
        "etf",
        "fed",
        "trump"
    ],

    "GOLD": [
        "gold",
        "fed",
        "treasury",
        "inflation",
        "war",
        "trump",
        "gold",
        "xau",
        "bullion",
        "precious metal",
        "treasury yields",
        "yield",
        "dollar index",
        "dxy",
        "federal reserve",
        "fed",
        "interest rate",
        "inflation",
        "cpi",
        "ppi",
        "middle east",
        "geopolitical",
        "safe haven",
        "central bank"
    ]
}


def cache_key(asset):

    return hashlib.md5(
        asset.encode()
    ).hexdigest()


def cache_file(asset):

    return os.path.join(
        NEWS_CACHE_DIR,
        f"{cache_key(asset)}.json"
    )


def load_cache(asset):

    path = cache_file(asset)

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:

        return json.load(f)


def save_cache(asset, data):

    with open(cache_file(asset), "w") as f:

        json.dump(data, f)


def fetch_news(asset, limit=15):

    feeds = RSS_FEEDS.get(asset, [])

    keywords = KEYWORDS.get(asset, [])

    articles = []
    

    IGNORE_TERMS = [
        "approval of the application",
        "monetary collapse",
        "just getting started",
        "part 1",
        "part 2",
        "what to expect",
        "price action warning"
    ]

    for feed_url in feeds:

        try:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries:

                title = entry.title.lower()

                if any(k in title for k in keywords):
                    
                    if not any(ignore in title for ignore in IGNORE_TERMS):

                        articles.append({

                        "title": entry.title,

                        "link": entry.link,

                        "published": entry.get(
                            "published",
                            ""
                        )
                    })

        except Exception as e:

            print(
                "RSS failed:",
                e
            )

    unique_titles = set()

    filtered = []

    for article in articles:

        title = article["title"]

        if title in unique_titles:

            continue

        unique_titles.add(title)

        filtered.append(article)

    return filtered[:limit]

def summarize_news(articles):

    if not articles:

        return [
            "No major headlines detected."
        ]

    summaries = []

    for article in articles[:5]:

        summaries.append(
            f"• {article['title']}"
        )

    return summaries
