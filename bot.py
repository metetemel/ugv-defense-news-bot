import feedparser
import os

from sources import UGV_RSS, EO_IR_RSS
from telegram import send


# ----------------------------
# KEYWORD INTELLIGENCE ENGINE
# ----------------------------
UGV_KEYWORDS = [
    "ugv", "unmanned ground", "ground vehicle",
    "autonomous vehicle", "robotic vehicle"
]

CAMERA_KEYWORDS = [
    "eo/ir", "infrared", "thermal", "tactical camera",
    "electro-optical", "sensor", "surveillance"
]

MILITARY_KEYWORDS = [
    "military", "defense", "army", "combat", "tactical"
]


# ----------------------------
# SCORING SYSTEM
# ----------------------------
def score_item(text):
    text = text.lower()

    score = 0

    for k in UGV_KEYWORDS:
        if k in text:
            score += 3

    for k in CAMERA_KEYWORDS:
        if k in text:
            score += 2

    for k in MILITARY_KEYWORDS:
        if k in text:
            score += 1

    return score


# ----------------------------
# FETCH RSS
# ----------------------------
def fetch(urls):
    items = []

    for url in urls:
        feed = feedparser.parse(url)

        for e in feed.entries[:10]:
            text = (e.title + " " + getattr(e, "summary", "")).lower()

            items.append({
                "title": e.title,
                "link": e.link,
                "score": score_item(text)
            })

    return items


# ----------------------------
# BUILD REPORT
# ----------------------------
def build_report(items):
    items = sorted(items, key=lambda x: x["score"], reverse=True)

    report = "🛡️ GÜNLÜK UGV & TAKTİK SİSTEM BÜLTENİ\n\n"

    count = 0

    for item in items:
        if item["score"] < 3:
            continue

        count += 1

        report += f"🔹 {item['title']}\n"
        report += f"📊 Önem Skoru: {item['score']}\n"
        report += f"🔗 {item['link']}\n\n"

        if count >= 10:
            break

    if count == 0:
        report += "Bugün yüksek öncelikli UGV / sensör haberi bulunamadı.\n"

    return report


# ----------------------------
# MAIN
# ----------------------------
def run():
    print("bot started")

    ugv = fetch(UGV_RSS)
    eo = fetch(EO_IR_RSS)

    all_items = ugv + eo

    print(f"items collected: {len(all_items)}")

    report = build_report(all_items)

    send(report)

    print("sent to telegram")


if __name__ == "__main__":
    run()
