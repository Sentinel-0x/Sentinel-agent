import json
import feedparser
import requests
from analyzer import analyze_raw_items
from formatter import format_telegram_markdown

def fetch_ai_intelligence(source_type="all"):
    """
    抓取最新的 AI 社交媒体动态与社区热点。
    """
    raw_items = []
    
    if source_type in ["twitter", "all"]:
        twitter_handles = ["karpathy", "YannLeCun", "DrJimFan", "sama", "gerganov", "swyx"]
        for handle in twitter_handles:
            try:
                feed = feedparser.parse(f"https://nitter.net/{handle}/rss")
                for entry in feed.entries[:2]:
                    raw_items.append({
                        "source": f"Twitter @{handle}",
                        "title": entry.title if hasattr(entry, 'title') else "新推文",
                        "content": entry.summary if hasattr(entry, 'summary') else "",
                        "url": entry.link
                    })
            except Exception as e:
                print(f"抓取 Twitter @{handle} 失败: {e}")

    if source_type in ["community", "all"]:
        rss_feeds = {
            "Reddit LocalLLaMA": "https://www.reddit.com/r/LocalLLaMA/top/.rss?t=day",
            "Hugging Face Papers": "https://huggingface.co/papers/rss"
        }
        for name, feed_url in rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    raw_items.append({
                        "source": name,
                        "title": entry.title,
                        "content": entry.summary if hasattr(entry, 'summary') else "",
                        "url": entry.link
                    })
            except Exception as e:
                print(f"抓取 {name} 失败: {e}")

    return raw_items

def push_to_telegram(formatted_text, bot_token, chat_id):
    """
    将排版好的文本推送到 Telegram 机器人。
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": formatted_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        if res.status_code != 200:
            payload.pop("parse_mode")
            requests.post(url, json=payload, timeout=15)
        return "✅ 成功推送到 Telegram！"
    except Exception as e:
        return f"❌ 推送失败: {e}"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "fetch_ai_intelligence",
            "description": "抓取全网最新 24 小时的 AI 动态（包含 Twitter 大 V 推文、Reddit 热榜与论文）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_type": {
                        "type": "string",
                        "enum": ["twitter", "community", "all"],
                        "description": "要抓取的数据源类型，默认为 'all'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "push_to_telegram",
            "description": "将整理好的高质量 AI 简报推送到用户的 Telegram 账户。",
            "parameters": {
                "type": "object",
                "properties": {
                    "formatted_text": {
                        "type": "string",
                        "description": "最终经过 Markdown 排版的美化文字内容"
                    }
                },
                "required": ["formatted_text"]
            }
        }
    }
]
