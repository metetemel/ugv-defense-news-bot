import feedparser
import hashlib

from sources import UGV_RSS, EO_IR_RSS, TR_DEFENSE_RSS, UAS_UGV_CROSSOVER_RSS
from telegram import send
from entities import extract_company, extract_country, classify_system


# =========================
# KEYWORDS
# =========================
UGV_KEYWORDS = ["ugv", "ground vehicle", "robotic vehicle"]
EOIR_KEYWORDS = ["eo/ir", "thermal", "infrared", "camera"]
MIL_KEYWORDS = ["military", "defense", "army", "combat"]


# -------------------------
def score(text):
    t = text.lower()
    s = 0

    for k in UGV_KEYWORDS:
        if k in t:
            s += 4

    for k in EOIR_KEYWORDS:
        if k in t:
            s += 3

    for k in MIL_KEYWORDS:
        if k in t:
            s += 2

    company, _ = extract_company(t)
    if company:
        s += 5

    return s


# -------------------------
def hash_id(text):
    return hashlib.md5(text.encode()).hexdigest()


# -------------------------
def fetch(urls, source):
    items = []

    for url in urls:
        feed = feedparser.parse(url)

        for e in feed.entries[:15]:
            text = e.title + " " + getattr(e, "summary", "")

            items.append({
                "id": hash_id(e.title),
                "title": e.title,
                "link": e.link,
                "text": text,
                "source": source,
                "score": score(text)
            })

    return items


# -------------------------
def dedup(items):
    seen = {}
    out = []

    for i in items:
        if i["id"] not in seen:
            seen[i["id"]] = i
            out.append(i)
        else:
            seen[i["id"]]["score"] += 2

    return out


# -------------------------
def enrich(item):
    text = item["text"]

    company, country = extract_company(text)
    sys_type = classify_system(text)

    item["company"] = company
    item["country"] = country
    item["system"] = sys_type

    return item


# -------------------------
def build_report(items):
    items = sorted(items, key=lambda x: x["score"], reverse=True)

    report = "🧠 UGV INTELLIGENCE REPORT v3\n\n"

    for i in items[:12]:

        i = enrich(i)

        if i["score"] < 5:
            continue

        report += f"🔹 {i['title']}\n"
        report += f"📊 Score: {i['score']}\n"
        report += f"🤖 System: {i['system']}\n"

        if i["company"]:
            report += f"🏭 Company: {i['company']}\n"

        report += f"🌍 Country: {i['country']}\n"
        report += f"🔗 {i['link']}\n\n"

    return report


# -------------------------
def run():
    print("INTEL v3 starting...")

    all_items = []

    all_items += fetch(UGV_RSS, "UGV")
    all_items += fetch(EO_IR_RSS, "EOIR")
    all_items += fetch(TR_DEFENSE_RSS, "TR")
    all_items += fetch(UAS_UGV_CROSSOVER_RSS, "UAS")

    print("raw:", len(all_items))

    clean = dedup(all_items)

    print("dedup:", len(clean))

    report = build_report(clean)

    send(report)

    print("done")


if __name__ == "__main__":
    run()
