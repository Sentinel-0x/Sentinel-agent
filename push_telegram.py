import os
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential
from logger import logger  # 1. 导入刚才第一步创建的 logger 模块

TELEGRAM_BOT_TOKEN = "8816811327:AAFozbfIqBhUKEkuS9a30i..." # 保持你原来的配置
TELEGRAM_CHAT_ID = "8172433983"

@retry(
    wait=wait_random_exponential(min=1, max=60), 
    stop=stop_after_attempt(5),
    # 2. 发生重试时，记录 WARNING 级别的警告日志
    before_sleep=lambda retry_state: logger.warning(f"Telegram API 接口超时/报错，即将开始第 {retry_state.attempt_number} 次重试...")
)
def send_telegram_message(text):
    """通过 Telegram API 发送 Markdown 格式的消息（带自动重试与生产级日志记录）"""
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
        res.raise_for_status()
        
        # 3. 成功时，记录 INFO 级别的日志（不再使用 print）
        logger.info(f"成功推送 1 篇文本分块 (块大小: {len(chunk)} 字符)")