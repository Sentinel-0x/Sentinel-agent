import os
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential

TELEGRAM_BOT_TOKEN = "8816811327:AAFozbfIqBhUKEkuS9a30i..." # 保持你原来的配置
TELEGRAM_CHAT_ID = "8172433983"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def send_telegram_message(text):
    """通过 Telegram API 发送 Markdown 格式的消息（带指数退避自动重试）"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    max_length = 4000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        res = requests.post(url, json=payload, timeout=15)
        res.raise_for_status()  # 触发 HTTP 状态码异常，供 @retry 捕获并重试