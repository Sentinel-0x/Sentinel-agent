import time
import json
import os
import requests
import feedparser

# ---------------- 配置区 ----------------
TELEGRAM_BOT_TOKEN = "8816811327:AAFozbfIqBhUKEkuS9a30if8yISyDEkcEu4"
TELEGRAM_CHAT_ID = "8172433983"

SEEN_CACHE_FILE = "seen_items.json"

# 1. Twitter KOL 监测列表 (通过 Nitter / RSS 节点)
TWITTER_HANDLES = [
    "karpathy", "YannLeCun", "DrJimFan", "sama", "DarioAmodei",
    "gerganov", "hwchase17", "jerryjliu0", "swyx", "chiphuyen",
    "eladgil", "benthompson", "OpenAI", "AnthropicAI", "GoogleDeepMind"
]

# 2. 社区热榜 & 论文 RSS 源
RSS_FEEDS = {
    "Reddit LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day",
    "Hacker News AI": "https://hnrss.org/newest?q=AI",
    "Hugging Face Papers": "https://huggingface.co/papers/rss"
}

def load_seen_items():
    if os.path.exists(SEEN_CACHE_FILE):
        try:
            with open(SEEN_CACHE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_items(seen_set):
    recent_items = list(seen_set)[-2000:]
    with open(SEEN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(recent_items, f, ensure_ascii=False, indent=2)

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code != 200:
            payload.pop("parse_mode")
            requests.post(url, json=payload, timeout=15)
        print("✅ Telegram 精报推送成功！")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

def run_daily_digest():
    seen_items = load_seen_items()
    report_sections = []

    # --- A. Twitter 大 V 动态 ---
    twitter_items = []
    for handle in TWITTER_HANDLES:
        rss_url = f"https://nitter.net/{handle}/rss"
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:2]: # 取最新 2 条
                item_id = entry.link
                if item_id not in seen_items:
                    seen_items.add(item_id)
                    title = entry.title if hasattr(entry, 'title') else "新推文"
                    twitter_items.append(f"• *@*{handle}: {title}\n  🔗 [查看原文]({entry.link})")
        except Exception as e:
            print(f"抓取 Twitter @{handle} 失败: {e}")

    if twitter_items:
        report_sections.append("🐦 *【Twitter KOL 前沿动态】*\n" + "\n\n".join(twitter_items[:8]))

    # --- B. 社区热门与学术前沿 ---
    community_items = []
    for name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                item_id = entry.link
                if item_id not in seen_items:
                    seen_items.add(item_id)
                    community_items.append(f"• *[{name}]* {entry.title}\n  🔗 [链接]({entry.link})")
        except Exception as e:
            print(f"抓取 {name} 失败: {e}")

    if community_items:
        report_sections.append("🔥 *【社区热议与前沿学术】*\n" + "\n\n".join(community_items[:8]))

    save_seen_items(seen_items)

    # --- C. 汇总组装并发送 ---
    if report_sections:
        full_report = "🤖 *【AI 全网前沿每日精报】*\n=============================\n\n" + "\n\n-----------------------------\n\n".join(report_sections)
        send_telegram_msg(full_report)
    else:
        print("今日暂无未推送的新内容。")

if __name__ == "__main__":
    run_daily_digest()
