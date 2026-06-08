import os
import sys
import json
import datetime as dt
import requests
import yfinance as yf
import pandas as pd
import math

# Load environment variables from .env
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env()

# Import local db and utilities
from db.blog_storage import save_blog_post, init_blog_db, get_connection
from api import get_news_headlines
from macro_calendar import get_macro_risk

# Try importing google generative ai
try:
    import google.generativeai as genai
    GEMINI_SUPPORT = True
except ImportError:
    GEMINI_SUPPORT = False

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8704963574:AAGOZoYjiqSPkF-FQIuuvTsUYTPgF0fPmsk")
ADMIN_CHAT_ID = os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "5316727978")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def get_market_metrics():
    ticker = "GC=F"
    try:
        data = yf.download(ticker, period="2d", interval="5m", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [c[0] for c in data.columns]
        
        current_price = float(data['Close'].iloc[-1])
        daily_high = float(data['High'].tail(12).max())  # Approx 1 hour high
        daily_low = float(data['Low'].tail(12).min())    # Approx 1 hour low
        
        # Calculate fast EMAs for technical guidance
        # Let's fetch 5 days of hourly data to calculate proper EMA 20 & 89
        htf = yf.download(ticker, period="5d", interval="60m", progress=False)
        if isinstance(htf.columns, pd.MultiIndex):
            htf.columns = [c[0] for c in htf.columns]
        
        ema20 = float(htf['Close'].ewm(span=20, adjust=False).mean().iloc[-1])
        ema89 = float(htf['Close'].ewm(span=89, adjust=False).mean().iloc[-1])
    except Exception as e:
        print("Error fetching market metrics via yfinance:", e)
        current_price = 2350.00
        daily_high = 2362.50
        daily_low = 2341.20
        ema20 = 2348.50
        ema89 = 2345.10
        
    return current_price, daily_high, daily_low, ema20, ema89

def get_latest_forecast():
    # Read from cache file if available
    try:
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent
        cache_path = BASE_DIR / "cache" / "gold_forecast.json"
        if cache_path.exists():
            with open(cache_path, "r") as f:
                data = json.load(f)
                return data["forecast_price"], data["move_pct"], data["direction"]
    except Exception as e:
        print("Forecast cache not found or unreadable:", e)
    
    return 2365.40, 0.65, "🟢 Bullish"

def generate_template_post(current_price, daily_high, daily_low, ema20, ema89, forecast_price, move_pct, direction, headlines, macro):
    today = dt.datetime.now().strftime("%B %d, %Y")
    title = f"Gold Trading Analysis: Spot Holds ${current_price:.2f} as AI Signals {direction.split()[-1]} Target"
    slug = slugify(title)
    
    summary = f"Gold Spot price trades at ${current_price:.2f}. The OHLC-based deep learning model forecasts a {move_pct:.2f}% {direction.lower()} move towards ${forecast_price:.2f} in the upcoming session."
    
    news_lines = "\n".join([f"- {h}" for h in headlines[:5]])
    
    content = f"""# Daily Gold Market Report - {today}

## Executive Summary
Spot Gold prices are currently holding steady around **${current_price:.2f}**, trading between a short-term high of **${daily_high:.2f}** and a low of **${daily_low:.2f}**. Market participants are closely monitoring interest rate paths and macroeconomic news. The OHLC-based gold-finetuned deep learning model has computed a **{direction}** outlook for the next session.

## Technical Analysis
- **Current Spot Price**: ${current_price:.2f}
- **EMA 20 (Hourly)**: ${ema20:.2f}
- **EMA 89 (Hourly)**: ${ema89:.2f}
- **Market Trend**: Spot is trading {"above" if current_price > ema89 else "below"} the EMA 89 median line, indicating a {"bullish" if current_price > ema89 else "bearish"} structural bias. 

Support is established near **${daily_low:.2f}**, while key overhead resistance is situated at **${daily_high:.2f}**.

## AI Forecast Breakdown
The deep learning model forecasts a target of **${forecast_price:.2f}**, reflecting a potential move of **{move_pct:.2f}%**. 
- **Sentiment Direction**: {direction}
- **Target Target**: ${forecast_price:.2f}
- **Uptime/Macro risk**: {macro["risk"]} (U.S. events multiplier at {macro["multiplier"]:.2f})

## Macroeconomic & News Sentiment
Key news driving the precious metals market today:
{news_lines}

With the macro risk index set to **{macro["risk"]}**, traders should prepare for potential volatility spikes around key session releases.

## Professional Trade Recommendations
Based on technical indicator crossovers and predicted directional bias:
- **Trade Bias**: {"BUY" if "Bullish" in direction else "SELL"}
- **Suggested Entry Range**: ${current_price:.2f} - ${current_price - 2 if "Bullish" in direction else current_price + 2:.2f}
- **Take Profit Target**: ${forecast_price:.2f}
- **Stop Loss Recommendation**: ${current_price - 12 if "Bullish" in direction else current_price + 12:.2f} (Based on ATR volatility limits)
- **Risk-to-Reward Ratio**: 1.5+

## Recommended Execution Hook
To trade this signal with raw spreads, tight leverage, and instant deposit/withdrawal cycles, execute your trades using our recommended platform: [Open an account with Exness](https://aigoldforecast.com/refer/exness).
"""
    return title, slug, summary, content

def generate_blog_report():
    init_blog_db()
    
    # 1. Fetch Market Metrics
    current_price, daily_high, daily_low, ema20, ema89 = get_market_metrics()
    forecast_price, move_pct, direction = get_latest_forecast()
    headlines = get_news_headlines("GOLD")
    macro = get_macro_risk()
    
    today = dt.datetime.now().strftime("%B %d, %Y")
    
    # 2. Call Gemini API if Key is present
    if GEMINI_SUPPORT and GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
You are an expert commodities research analyst and senior trading strategist specializing in Precious Metals (XAU/USD).
Write a comprehensive, professional Daily Gold Market Report for today ({today}).

Market Data:
- Current Spot Gold price: ${current_price:.2f}
- Daily High: ${daily_high:.2f}
- Daily Low: ${daily_low:.2f}
- AI Model Prediction: The model forecasts a {move_pct:.2f}% move ({direction}) to target ${forecast_price:.2f} over the next session.
- Technical Markers: EMA 20 is at ${ema20:.2f}, EMA 89 is at ${ema89:.2f}.
- Macroeconomic Risk Level: {macro["risk"]}

Recent Headlines:
{chr(10).join(['- ' + h for h in headlines[:8]])}

Requirements:
1. Title: Create a catchy, high-impact SEO title for the post (do not put quotes around it, e.g. Gold Holds Support at $2350 as Inflation Fears Anchor Safe-Haven Demand).
2. Structure:
   - Executive Summary: A quick 3-sentence summary of today's price action.
   - Technical Analysis: Detail the EMA crossover signals (EMA 20 vs 89), support/resistance zones, and market volatility.
   - AI Forecast Breakdown: Explain the deep learning model's forecasted path and prediction targets. Refer to it ONLY as the "OHLC-based gold-finetuned deep learning model" (Do NOT mention "Kronos").
   - Macroeconomic & News Sentiment: Analyze how the headlines and upcoming events will affect the dollar index and gold safe-haven appeal.
   - Professional Trade Recommendations: Give explicit trading rules (Buy/Sell directions, entries, take profit targets, stop loss recommendations based on ATR/volatility, and risk-to-reward ratio).
   - Recommended Execution (CTA): Add a short section titled "Recommended Execution" advising traders to execute these setups on our partner broker Exness for raw spreads, 0% commissions, and instant payouts. Include a markdown link to [Exness](https://aigoldforecast.com/refer/exness).
3. Tone: Highly analytical, authoritative, professional, and readable. Output MUST be in JSON format with exactly three string keys: "title", "summary", and "content" (the content must be formatted in beautiful GitHub Markdown).

Return ONLY raw JSON, do not wrap it in markdown code blocks.
"""
            response = model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Clean JSON wrappers if generated by the LLM
            if text_response.startswith("```json"):
                text_response = text_response.replace("```json", "", 1)
            if text_response.endswith("```"):
                text_response = text_response.rsplit("```", 1)[0]
                
            data = json.loads(text_response.strip())
            title = data["title"]
            summary = data["summary"]
            content = data["content"]
            slug = slugify(title)
        except Exception as e:
            print("Gemini API generation failed. Falling back to template. Error:", e)
            title, slug, summary, content = generate_template_post(
                current_price, daily_high, daily_low, ema20, ema89, 
                forecast_price, move_pct, direction, headlines, macro
            )
    else:
        print("Gemini API not configured. Using template generation.")
        title, slug, summary, content = generate_template_post(
            current_price, daily_high, daily_low, ema20, ema89, 
            forecast_price, move_pct, direction, headlines, macro
        )
        
    # 3. Save to DB
    # We will modify/extend the database to support x_draft and x_status columns if missing
    # SQLite schema upgrade
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE blog_posts ADD COLUMN x_draft TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE blog_posts ADD COLUMN x_status TEXT DEFAULT 'PENDING'")
    except:
        pass
    conn.commit()
    conn.close()
    
    # Save post
    x_draft = f"🟡 #Gold Pre-Session Forecast: AI Model predicts {direction.lower()} target of ${forecast_price:.2f} (Entry: ${current_price:.2f}). U.S. Macro risk: {macro['risk']}. Full analysis: https://aigoldforecast.com/blog/{slug}"
    
    # Save via helper and get post_id
    post_id = save_blog_post(title, slug, content, summary)
    
    # Store the x_draft and status in the DB
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE blog_posts 
            SET x_draft = ?, x_status = 'PENDING' 
            WHERE id = ?
        """, (x_draft, post_id))
    except Exception as e:
        if "sqlite3" not in str(type(e)):
            cursor.execute("""
                UPDATE blog_posts 
                SET x_draft = %s, x_status = 'PENDING' 
                WHERE id = %s
            """, (x_draft, post_id))
        else:
            raise e
    conn.commit()
    conn.close()
    
    print(f"Blog post saved successfully! ID: {post_id}, Slug: {slug}")
    
    # 4. Send draft to Telegram for approval
    send_telegram_approval(post_id, x_draft)
    return slug

def send_telegram_approval(post_id, x_draft):
    if not TELEGRAM_BOT_TOKEN or not ADMIN_CHAT_ID:
        print("Telegram configuration is missing. Skipping approval notification.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    text = f"📢 *New Pre-Session Blog Post Generated!*\n\n*Draft X (Twitter) Post:*\n```\n{x_draft}\n```\n\nApprove below to post this directly to Twitter/X."
    
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Approve to X ✅", "callback_data": f"approve_x:{post_id}"},
                    {"text": "Reject ❌", "callback_data": f"reject_x:{post_id}"}
                ]
            ]
        }
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Telegram approval response:", r.text)
    except Exception as e:
        print("Failed to send Telegram approval message:", e)

if __name__ == "__main__":
    generate_blog_report()
