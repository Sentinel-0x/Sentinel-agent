import os
import time
import requests
import logging

def send_telegram_message(message: str, max_retries: int = 3):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not token or not chat_id:
        error_msg = "❌ TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未配置"
        logging.error(error_msg)
        return error_msg
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    # 自动重试机制
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"🚀 尝试发送 Telegram 消息 (第 {attempt}/{max_retries} 次)...")
            response = requests.post(url, json=payload, timeout=10)
            res_data = response.json()
            
            if res_data.get("ok"):
                logging.info("✅ Telegram 消息推送成功！")
                return "推送成功"
            else:
                err_desc = f"❌ Telegram API 返回错误: {res_data.get('description')}"
                logging.warning(err_desc)
                
        except Exception as e:
            logging.warning(f"⚠️ 第 {attempt} 次请求失败 (网络/超时异常): {e}")
        
        # 如果未达到最大次数，等待后重试
        if attempt < max_retries:
            sleep_time = attempt * 2  # 第一次等2秒，第二次等4秒
            logging.info(f"⏱️ {sleep_time} 秒后重试...")
            time.sleep(sleep_time)

    final_error = f"❌ 推送失败：已连续重试 {max_retries} 次均未成功。"
    logging.error(final_error)
    return final_error
import os
import time
import requests
import logging

def send_telegram_message(message: str, max_retries: int = 3):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    
    if not token or not chat_id:
        error_msg = "❌ TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 未配置"
        logging.error(error_msg)
        return error_msg
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    # 自动重试机制
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"🚀 尝试发送 Telegram 消息 (第 {attempt}/{max_retries} 次)...")
            response = requests.post(url, json=payload, timeout=10)
            res_data = response.json()
            
            if res_data.get("ok"):
                logging.info("✅ Telegram 消息推送成功！")
                return "推送成功"
            else:
                err_desc = f"❌ Telegram API 返回错误: {res_data.get('description')}"
                logging.warning(err_desc)
                
        except Exception as e:
            logging.warning(f"⚠️ 第 {attempt} 次请求失败 (网络/超时异常): {e}")
        
        # 如果未达到最大次数，等待后重试
        if attempt < max_retries:
            sleep_time = attempt * 2  # 第一次等2秒，第二次等4秒
            logging.info(f"⏱️ {sleep_time} 秒后重试...")
            time.sleep(sleep_time)

    final_error = f"❌ 推送失败：已连续重试 {max_retries} 次均未成功。"
    logging.error(final_error)
    return final_error
