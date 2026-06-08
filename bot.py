from fetch import fetch_rss
from llm import generate_brief
from telegram import send
from sources import UGV_RSS, EO_IR_RSS

def run():
    news_ugv = fetch_rss(UGV_RSS)
    news_eo = fetch_rss(EO_IR_RSS)

    all_news = news_ugv + news_eo

    report = generate_brief(all_news)
    send(report)

if __name__ == "__main__":
    run()
