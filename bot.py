import os
import feedparser
import requests

from sources import UGV_RSS, EO_IR_RSS
from llm import generate_brief
from telegram import send


# ---------------------------
# 1. DEBUG HELPERS
# ---------------------------
def log(step):
    print(f"[UGV BOT] {step}")


# ---------------------------
# 2. RSS FETCH
# ---------------------------
def fetch_rss(urls, tag):
    log(f"{tag} RSS fetching started")

    news = []

    for url in urls:
        feed = feedparser.parse(url)

        log(f"{tag} parsed: {url} -> {len(feed.entries)} entries")

        for entry in feed.entries[:5]:
            news.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")
            })

    log(f"{tag} total collected: {len(news)}")
    return news


# ---------------------------
# 3. MAIN FLOW
# ---------------------------
def run():
    log("bot started")

    try:
        # RSS COLLECT
        ugv_news = fetch_rss(UGV_RSS, "UGV")
        eo_news = fetch_rss(EO_IR_RSS, "EO/IR")

        all_news = ugv_news + eo_news

        log(f"total news collected: {len(all_news)}")

        if len(all_news) == 0:
            send("⚠️ Bugün veri bulunamadı (RSS boş)")
            return

        log("calling OpenAI analysis")

        # AI ANALYSIS
        report = generate_brief(all_news)

        log("OpenAI response received")

        # TELEGRAM SEND
        send(report)

        log("telegram message sent")

    except Exception as e:
        error_msg = f"❌ BOT ERROR: {str(e)}"
        log(error_msg)

        # fallback telegram error message
        try:
            send(error_msg)
        except:
            pass


# ---------------------------
# 4. ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    run()
