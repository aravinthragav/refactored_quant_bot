from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import datetime as dt
import feedparser
import pandas as pd
import yfinance as yf
from forecast_engine import get_forecast_payload
import math
import socket
import os

# Set socket timeout to 3 seconds to prevent RSS feeds from hanging
socket.setdefaulttimeout(3.0)

app = FastAPI(title="AI Gold Forecast API")

# Ensure charts directory exists
os.makedirs("charts", exist_ok=True)
app.mount("/charts", StaticFiles(directory="charts"), name="charts")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

news_cache = {}

def is_blacklisted(title):
    title_lower = title.lower()
    blacklist = [
        "website", "newsletter", "subscribe", "subscription", "sign up", "follow us",
        "advertisement", "goldseek.com", "kitco.com", "cookie", "privacy policy",
        "launch new", "feedback", "terms of use", "disclaimer", "rss feed", "advertise",
        "sponsor", "sponsorship"
    ]
    return any(b in title_lower for b in blacklist)

def is_news_relevant(title, asset_name):
    title_lower = title.lower()
    if asset_name == "BTC":
        keywords = [
            "btc", "bitcoin", "crypto", "ether", "eth", "solana", "sol", "blockchain",
            "cryptocurrency", "sec", "binance", "coinbase", "etf", "ledger",
            "satoshi", "halving", "digital asset", "fed", "inflation", "macro"
        ]
    else:
        keywords = [
            "gold", "silver", "platinum", "palladium", "metal", "metals", "bullion", "xau", 
            "mining", "miner", "miners", "commodity", "commodities", "fed", "fomc", "inflation", "cpi", 
            "yield", "yields", "rates", "interest rate", "interest rates", "central bank", "central banks", "dollar", "usd", 
            "greenback", "macro", "monetary", "powell", "treasury", "safe-haven", "safe haven", "bond", "bonds", 
            "economic", "gdp", "recession", "rate cut", "rate cuts", "rate hike", "rate hikes", "hike", "cut", 
            "reserve", "reserves", "spot price", "precious"
        ]
    return any(k in title_lower for k in keywords)

def get_news_headlines(asset_name):
    # Check memory cache
    now = dt.datetime.now()
    if asset_name in news_cache:
        cache_time, cached_headlines = news_cache[asset_name]
        # Cache for 15 minutes to reduce API latency
        if (now - cache_time).total_seconds() < 900:
            return cached_headlines

    feeds = []
    if asset_name == "BTC":
        feeds = [
            {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "filter": False},
            {"url": "https://cointelegraph.com/rss", "filter": False}
        ]
    else:
        feeds = [
            {"url": "https://www.kitco.com/rss/news", "filter": False},
            {"url": "https://news.goldseek.com/newsRSS.xml", "filter": False},
            {"url": "https://www.mining.com/feed/", "filter": False},
            {"url": "https://www.federalreserve.gov/feeds/press_all.xml", "filter": False},
            {"url": "https://www.imf.org/en/News/RSS", "filter": False},
            {"url": "https://www.reutersagency.com/feed/?best-topics=commodities", "filter": True},
            {"url": "https://www.fxstreet.com/rss/news", "filter": True}
        ]

    headlines = []
    for feed_info in feeds:
        url = feed_info["url"]
        should_filter = feed_info["filter"]
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.title.replace("&amp;", "&")
                # Skip blacklisted/self-promotional headlines
                if is_blacklisted(title):
                    continue
                # Filter general feeds for relevance
                if not should_filter or is_news_relevant(title, asset_name):
                    headlines.append(title)
        except Exception:
            pass

    headlines = list(dict.fromkeys(headlines))
    if not headlines:
        headlines = [
            "Markets monitoring Fed commentary",
            "Gold traders watching bond yields",
            "Macro uncertainty driving safe-haven flows"
        ]
    
    result = headlines[:10]
    news_cache[asset_name] = (now, result)
    return result

def get_sr_levels(ticker, current_price):
    levels = []
    timeframes = [
        ("15m", "15m", "7d"),
        ("30m", "30m", "14d"),
        ("1H", "60m", "30d"),
        ("4H", "4h", "90d"),
        ("D", "1d", "180d"),
        ("W", "1wk", "2y"),
        ("M", "1mo", "5y")
    ]
    for label, interval, period in timeframes:
        try:
            htf = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=False)
            if htf.empty: continue
            if isinstance(htf.columns, pd.MultiIndex):
                htf.columns = [c[0] for c in htf.columns]
            
            recent_high = htf['High'].tail(20).max()
            recent_low = htf['Low'].tail(20).min()
            
            levels.append({"tf": label, "type": "R", "price": float(recent_high)})
            levels.append({"tf": label, "type": "S", "price": float(recent_low)})
        except Exception:
            pass

    filtered = []
    for lvl in levels:
        if math.isnan(lvl["price"]): continue
        distance_pct = abs(lvl["price"] - current_price) / current_price * 100
        if distance_pct <= 6.0:
            filtered.append(lvl)

    # Group and merge S/R levels that are within 0.15% of each other
    levels_R = sorted([l for l in filtered if l["type"] == "R"], key=lambda x: x["price"])
    levels_S = sorted([l for l in filtered if l["type"] == "S"], key=lambda x: x["price"])

    def merge_levels(lvl_list):
        if not lvl_list:
            return []
        merged = []
        current = lvl_list[0]
        for next_lvl in lvl_list[1:]:
            if abs(next_lvl["price"] - current["price"]) / current["price"] * 100 <= 0.15:
                # Merge: combine timeframes
                tfs = current["tf"].split("/") + next_lvl["tf"].split("/")
                order_map = {"15m": 0, "30m": 1, "1H": 2, "4H": 3, "D": 4, "W": 5, "M": 6}
                unique_tfs = sorted(list(set(tfs)), key=lambda x: order_map.get(x, 99))
                current["tf"] = "/".join(unique_tfs)
                # Set price to average
                current["price"] = (current["price"] + next_lvl["price"]) / 2
            else:
                merged.append(current)
                current = next_lvl
        merged.append(current)
        return merged

    merged_R = merge_levels(levels_R)
    merged_S = merge_levels(levels_S)
    return merged_R + merged_S

@app.get("/api/forecast")
def get_forecast(ticker: str = "GC=F", asset_name: str = "GOLD", lookback: int = 256, pred_len: int = 12):
    # Try reading from cache file first to save CPU
    try:
        import os
        import json
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent
        cache_path = BASE_DIR / "cache" / f"{asset_name.lower()}_forecast.json"
        if cache_path.exists():
            # Ensure the cache file is relatively fresh (max 15 minutes)
            import time
            mtime = os.path.getmtime(cache_path)
            age_sec = time.time() - mtime
            is_weekend = dt.datetime.now().weekday() in [5, 6]
            if age_sec < 900 or is_weekend:
                with open(cache_path, "r") as f:
                    data = json.load(f)
                # Overwrite weekend check dynamically
                data["market_closed"] = is_weekend if asset_name == "GOLD" else False
                return data
    except Exception as e:
        print(f"Error reading forecast cache: {e}")

    try:
        config = {
            "ticker": ticker,
            "interval": "5m",
            "lookback": lookback,
            "pred_len": pred_len
        }
        payload = get_forecast_payload(config)
        
        # Format DataFrames for JSON response
        x_timestamp = payload["x_timestamp"]
        x_df = payload["x_df"]
        pred_df = payload["pred_df"]
        y_timestamp = payload["y_timestamp"]
        df = payload["df"]
        
        hist_data = []
        for i in range(len(x_df)):
            hist_data.append({
                "time": int(x_timestamp.iloc[i].timestamp()),
                "open": float(x_df['open'].iloc[i]),
                "high": float(x_df['high'].iloc[i]),
                "low": float(x_df['low'].iloc[i]),
                "close": float(x_df['close'].iloc[i])
            })
            
        forecast_data = []
        # Connect to last hist candle
        forecast_data.append({
            "time": int(x_timestamp.iloc[-1].timestamp()),
            "value": float(x_df['close'].iloc[-1])
        })
        for i in range(len(pred_df)):
            forecast_data.append({
                "time": int(y_timestamp.iloc[i].timestamp()),
                "value": float(pred_df['close'].iloc[i])
            })
            
        ema20_data = []
        ema20_series = df['ema20'].tail(lookback)
        for i in range(len(ema20_series)):
            val = ema20_series.iloc[i]
            if not math.isnan(val):
                ema20_data.append({
                    "time": int(x_timestamp.iloc[i].timestamp()),
                    "value": float(val)
                })
                
        ema89_data = []
        ema89_series = df['ema89_median'].tail(lookback)
        for i in range(len(ema89_series)):
            val = ema89_series.iloc[i]
            if not math.isnan(val):
                ema89_data.append({
                    "time": int(x_timestamp.iloc[i].timestamp()),
                    "value": float(val)
                })

        sr_levels = get_sr_levels(ticker, payload["current_price"])

        # Calculate MAE if possible
        mae = None
        try:
            actual = df['close'].tail(pred_len).values
            predicted = pred_df['close'].values[:len(actual)]
            mae = float(sum(abs(actual - predicted)) / len(actual))
        except:
            pass

        is_weekend = dt.datetime.now().weekday() in [5, 6]

        return {
            "success": True,
            "asset_name": asset_name,
            "current_price": float(payload["current_price"]),
            "forecast_price": float(payload["forecast_price"]),
            "move_pct": float(payload["move_pct"]),
            "direction": payload["direction"],
            "hist_data": hist_data,
            "forecast_data": forecast_data,
            "ema20_data": ema20_data,
            "ema89_data": ema89_data,
            "sr_levels": sr_levels,
            "mae": mae,
            "market_closed": is_weekend if asset_name == "GOLD" else False
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/active-signal")
def get_active_signal(symbol: str = "GC=F"):
    try:
        from db.signal_storage import get_open_signals
        signals = get_open_signals()
        symbol_signals = [s for s in signals if s["symbol"] == symbol]
        if symbol_signals:
            latest = sorted(symbol_signals, key=lambda x: x["id"])[-1]
            
            # Check if stale (> 60 minutes)
            try:
                from datetime import datetime, timezone
                created_at = datetime.fromisoformat(latest["created_at"])
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                elapsed_minutes = (now_utc - created_at).total_seconds() / 60
                if elapsed_minutes > 60:
                    return {
                        "success": True,
                        "has_signal": False,
                        "signal": None
                    }
            except Exception as e:
                print("Error verifying signal freshness:", e)

            return {
                "success": True,
                "has_signal": True,
                "signal": {
                    "id": latest["id"],
                    "symbol": latest["symbol"],
                    "direction": latest["direction"],
                    "entry_price": latest["entry_price"],
                    "tp_price": latest["tp_price"],
                    "sl_price": latest["sl_price"],
                    "forecast_price": latest["forecast_price"],
                    "move_pct": latest["move_pct"],
                    "confidence": latest["confidence"],
                    "created_at": latest["created_at"]
                }
            }
        return {
            "success": True,
            "has_signal": False,
            "signal": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news")
def get_news(asset_name: str = "GOLD"):
    return {"success": True, "headlines": get_news_headlines(asset_name)}

# =========================================================
# BLOG ENGINE ENDPOINTS
# =========================================================

@app.get("/api/blog")
def get_blog_posts():
    try:
        from db.blog_storage import get_all_posts
        posts = get_all_posts()
        return {"success": True, "posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blog/{slug}")
def get_blog_post(slug: str):
    try:
        from db.blog_storage import get_post_by_slug
        post = get_post_by_slug(slug)
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        return {"success": True, "post": post}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# TWITTER/X POSTING HELPER
# =========================================================

def post_to_twitter(text: str):
    import os
    import requests
    
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        try:
            print(f"Twitter keys missing. Logging tweet to file: {text}")
        except UnicodeEncodeError:
            print(f"Twitter keys missing. Logging tweet to file: {text.encode('ascii', 'replace').decode('ascii')}")
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tweets.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{dt.datetime.now().isoformat()}] {text}\n")
        return True, "Twitter API keys not set. Draft tweet logged to tweets.log locally."
        
    try:
        from requests_oauthlib import OAuth1Session
        twitter = OAuth1Session(api_key, client_secret=api_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret)
        response = twitter.post("https://api.twitter.com/2/tweets", json={"text": text})
        if response.status_code == 201:
            return True, "Successfully posted to Twitter!"
        else:
            return False, f"Twitter API error ({response.status_code}): {response.text}"
    except Exception as e:
        return False, f"Twitter post exception: {str(e)}"

# =========================================================
# TELEGRAM AND GITHUB WEBHOOKS
# =========================================================

@app.post("/api/telegram-webhook")
async def telegram_webhook(update: dict):
    import requests
    import os
    
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "8704963574:AAGOZoYjiqSPkF-FQIuuvTsUYTPgF0fPmsk")
    
    if "callback_query" in update:
        cq = update["callback_query"]
        data = cq["data"]
        msg = cq.get("message", {})
        chat_id = msg.get("chat", {}).get("id")
        message_id = msg.get("message_id")
        
        # Acknowledge the callback query to Telegram
        try:
            requests.post(f"https://api.telegram.org/bot{token}/answerCallbackQuery", json={"callback_query_id": cq["id"]}, timeout=5)
        except:
            pass
            
        if data.startswith("approve_x:"):
            post_id = int(data.replace("approve_x:", ""))
            from db.blog_storage import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT x_draft, x_status FROM blog_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            
            if row:
                x_draft, x_status = row[0], row[1]
                if x_status == 'APPROVED':
                    new_text = f"Already approved and posted to X! ✅\n\n```\n{x_draft}\n```"
                else:
                    success, message = post_to_twitter(x_draft)
                    if success:
                        cursor.execute("UPDATE blog_posts SET x_status = 'APPROVED' WHERE id = ?", (post_id,))
                        new_text = f"Approved and posted to X! ✅\n\n```\n{x_draft}\n```\n\n_{message}_"
                    else:
                        new_text = f"Failed to post to X! ❌\nError: {message}\n\n```\n{x_draft}\n```"
            else:
                new_text = "Draft post not found in database."
                
            conn.commit()
            conn.close()
            
            # Update the original Telegram message in-place
            try:
                requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": new_text,
                    "parse_mode": "Markdown"
                }, timeout=5)
            except Exception as e:
                print("Telegram edit failed:", e)
                
        elif data.startswith("reject_x:"):
            post_id = int(data.replace("reject_x:", ""))
            from db.blog_storage import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT x_draft FROM blog_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            x_draft = row[0] if row else ""
            cursor.execute("UPDATE blog_posts SET x_status = 'REJECTED' WHERE id = ?", (post_id,))
            conn.commit()
            conn.close()
            
            new_text = f"Post rejected! ❌\n\n```\n{x_draft}\n```"
            try:
                requests.post(f"https://api.telegram.org/bot{token}/editMessageText", json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": new_text,
                    "parse_mode": "Markdown"
                }, timeout=5)
            except Exception as e:
                print("Telegram edit failed:", e)
                
    return {"ok": True}

@app.post("/api/github-webhook")
async def github_webhook():
    import subprocess
    import os
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", "deploy.sh")
    if not os.path.exists(script_path):
        script_path = "/home/ubuntu/refactored_quant_bot/Linto/scripts/deploy.sh"
        
    print(f"Executing GitHub Webhook Auto-Deploy: {script_path}")
    try:
        if os.path.exists(script_path):
            # Run asynchronously
            subprocess.Popen(["bash", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {"success": True, "message": "GitHub deployment triggered successfully."}
        else:
            return {"success": False, "message": "Auto-deploy script (deploy.sh) not found."}
    except Exception as e:
        return {"success": False, "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
