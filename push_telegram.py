import requests
import os

# 请替换为你在 @BotFather 和 @userinfobot 获取到的实际 Token 和 Chat ID
TELEGRAM_BOT_TOKEN = "8816811327:AAFozbfIqBhUKEkuS9a30if8yISyDEkcEu4"
TELEGRAM_CHAT_ID = "8172433983"

def send_telegram_message(text):
    """通过 Telegram API 发送 Markdown 格式的消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    max_length = 4000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    for chunk in chunks:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                print("✅ Telegram 消息推送成功！")
            else:
                payload.pop("parse_mode")
                requests.post(url, json=payload, timeout=15)
                print("⚠️ Markdown 格式渲染失败，已通过普通文本格式推送成功！")
        except Exception as e:
            print(f"❌ Telegram 推送失败: {e}")

if __name__ == "__main__":
    report_file = "daily_report.txt"
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
        print("🚀 正在将每日精报推送到 Telegram...")
        send_telegram_message(content)
    else:
        print("⚠️ 未找到 daily_report.txt，请先运行 python daily_digest.py 生成报告！")

