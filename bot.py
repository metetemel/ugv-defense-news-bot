import feedparser
import hashlib

from sources import UGV_RSS, EO_IR_RSS, TR_DEFENSE_RSS, UAS_UGV_CROSSOVER_RSS
from telegram import send


# =========================
# KEYWORDS (INTELLIGENCE MODEL)
# =========================

UGV_KEYWORDS = [
    "ugv", "ground vehicle", "unmanned ground",
    "autonomous vehicle", "robotic vehicle", "land robot"
]

EOIR_KEYWORDS = [
    "eo/ir", "electro-optical", "infrared", "thermal",
    "camera", "sensor", "surveillance", "imaging"
]

STRATEGIC_KEYWORDS = [
    "combat", "military", "army", "defense",
    "tactical", "battlefield"
]

HIGH_VALUE_ENTITIES = [
    "rheinmetall", "aselsan", "qinetiq",
    "bae systems", "knds", "general dynamics"
]


# =========================
# NORMALIZE TITLE
# =========================
def normalize(text):
    return " ".join(text.lower().split())


# =========================
# DEDUP KEY (HASH BASED)
# =========================
def make_hash(title):
    return hashlib.md5(title.encode("utf-8")).hexdigest()


# =========================
# SCORING v2
# =========================
def score(text):
    text = text.lower()

    s = 0

    # UGV relevance
    for k in UGV_KEYWORDS:
        if k in text:
            s += 4

    # EO/IR relevance
    for k in EOIR_KEYWORDS:
        if k in text:
            s += 3

    # Military context
    for k in STRATEGIC_KEYWORDS:
        if k in text:
            s += 2

    # High-value companies boost
    for k in HIGH_VALUE_ENTITIES:
        if k in text:
            s += 5

    return s


# =========================
# FETCH RSS
# =========================
def fetch(urls, source_name):
    items = []

    for url in urls:
        feed = feedparser.parse(url)

        for e in feed.entries[:15]:
            title = normalize(e.title)
            summary = normalize(getattr(e, "summary", ""))

            full_text = title + " " + summary

            items.append({
                "id": make_hash(title),
                "title": e.title,
                "link": e.link,
                "score": score(full_text),
                "source": source_name
            })

    return items


# =========================
# DEDUPLICATION ENGINE
# =========================
def deduplicate(items):
    seen = {}
    merged = {}

    for item in items:
        _id = item["id"]

        if _id not in seen:
            seen[_id] = True
            merged[_id] = item
        else:
            # duplicate found → boost score
            merged[_id]["score"] += 2

    return list(merged.values())


# =========================
# REPORT BUILDER
# =========================
def build_report(items):
    items = sorted(items, key=lambda x: x["score"], reverse=True)

    report = "🛡️ UGV INTELLIGENCE REPORT v2\n\n"

    count = 0

    for i in items:
        if i["score"] < 5:
            continue

        count += 1

        report += f"🔹 {i['title']}\n"
        report += f"📊 Intelligence Score: {i['score']}\n"
        report += f"🌐 Source: {i['source']}\n"
        report += f"🔗 {i['link']}\n\n"

        if count >= 12:
            break

    if count == 0:
        report += "No high-value intelligence signals today.\n"

    return report


# =========================
# MAIN PIPELINE
# =========================
def run():
    print("UGV INTEL v2 starting...")

    all_items = []

    all_items += fetch(UGV_RSS, "UGV")
    all_items += fetch(EO_IR_RSS, "EOIR")
    all_items += fetch(TR_DEFENSE_RSS, "TR")
    all_items += fetch(UAS_UGV_CROSSOVER_RSS, "UAS")

    print(f"raw items: {len(all_items)}")

    # DEDUP STEP
    clean_items = deduplicate(all_items)

    print(f"after dedup: {len(clean_items)}")

    # REPORT
    report = build_report(clean_items)

    send(report)

    print("sent to telegram")


if __name__ == "__main__":
    run()
