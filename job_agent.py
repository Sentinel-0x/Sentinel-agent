import os
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("SILICONFLOW_API_KEY")
MODEL_NAME = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct")

CONFIG = {
    "restricted_locations": ["usa", "(usa)", "us only", "usa only", "uk only", "canada only", "eu only", "based in us", "latin america"],
    "unwanted_roles": [
        "designer", "ui/ux", "architect", "engineer", "developer", "backend", "frontend",
        "director", "principal", "vice president", "vp", "head of",
        "business development", "sales"
    ]
}

def get_robust_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

session = get_robust_session()

def quick_filter(job: dict) -> tuple[bool, str]:
    title = str(job.get('title', '')).lower()
    location = str(job.get('location', '')).lower()

    for res in CONFIG["restricted_locations"]:
        if res in location:
            return False, f"限制地区: {res}"

    for role in CONFIG["unwanted_roles"]:
        if role in title:
            return False, f"非目标岗位/职级: {role}"

    return True, "通过粗筛"

def send_telegram_msg(msg: str):
    if not TELEGRAM_BOT_TOKEN or "your_telegram" in TELEGRAM_BOT_TOKEN:
        logging.warning("⚠️ 未检测到有效 Telegram Token，跳过推送")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        # 去掉 parse_mode="Markdown" 避免符号解析报错导致发送失败
        res = session.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
        if res.status_code == 200:
            logging.info("📤 已成功推送至 Telegram！")
        else:
            logging.error(f"❌ Telegram 推送拒绝 ({res.status_code}): {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram 网络请求失败: {e}")

def evaluate_job_via_cloud_gpu(job: dict) -> str:
    if not API_KEY or "你的真实Key" in API_KEY:
        return "错误: 未在 .env 中配置有效的 SILICONFLOW_API_KEY"

    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""岗位名称：{job['title']}
地区设置：{job['location']}
岗位描述：{job['desc'][:300]}

评估要求：
1. 优先推荐：AI 解决方案/运营/Prompt/社区/Web3/远程文员类岗位。
2. 明确排除：高管、工程师、设计师、限定单国家的岗位。

回答格式：
结论：推荐 或 不推荐
原因：一句话说明原因"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严格的求职筛选助手。仅输出结论和一句话原因。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }

    try:
        response = session.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"API 返回异常 ({response.status_code}): {response.text}"
    except Exception as e:
        return f"请求云端失败: {e}"

if __name__ == "__main__":
    if not os.path.exists("jobs_data.json"):
        logging.error("❌ 未找到 jobs_data.json 文件！请先运行 python fetch_jobs.py")
        exit(1)

    with open("jobs_data.json", "r", encoding="utf-8") as f:
        raw_jobs = json.load(f)

    valid_jobs = []
    dropped_count = 0
    for j in raw_jobs:
        passed, reason = quick_filter(j)
        if passed:
            valid_jobs.append(j)
        else:
            dropped_count += 1

    logging.info(f"📊 原始数据 {len(raw_jobs)} 条 -> 粗筛拦截 {dropped_count} 条 -> 送交云端 GPU 精筛 {len(valid_jobs)} 条")

    recommended_jobs = []

    for idx, job in enumerate(valid_jobs, 1):
        print(f"\n================ [{idx}/{len(valid_jobs)}] ================")
        print(f"📌 岗位: {job['title']} @ {job['company']} ({job['location']})")
        
        result = evaluate_job_via_cloud_gpu(job)
        print(f"🤖 云端评估结果:\n{result}")

        # 放宽触发条件：只要包含“推荐”且不显式包含“不推荐”，即执行推送
        if "推荐" in result and "不推荐" not in result:
            job["ai_evaluation"] = result
            recommended_jobs.append(job)
            card = f"🎯 发现匹配岗位！\n\n职位: {job['title']}\n公司: {job['company']}\n地区: {job['location']}\n链接: {job['url']}\n\nAI 评估报告:\n{result}"
            send_telegram_msg(card)

    with open("evaluated_jobs.json", "w", encoding="utf-8") as f:
        json.dump(recommended_jobs, f, ensure_ascii=False, indent=2)
    logging.info(f"💾 评估完成！已将 {len(recommended_jobs)} 条精选岗位保存至 evaluated_jobs.json")
