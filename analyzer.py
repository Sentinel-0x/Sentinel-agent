import json

def analyze_raw_items(raw_data):
    if not raw_data:
        return "🤖 Agent 报告：本次运行未抓取到最新的 AI 动态数据。"

    formatted_text = "🤖 **今日 AI 前沿情报精选**\n\n"
    formatted_text += f"📊 *已为你自动筛选并提炼 {len(raw_data)} 条高价值动态*\n"
    formatted_text += "━━━━━━━━━━━━━━━━━━━\n\n"

    for idx, item in enumerate(raw_data, 1):
        if isinstance(item, dict):
            title = item.get("title_zh") or item.get("title") or "无标题"
            summary = item.get("summary") or item.get("content") or "暂无详细摘要"
            category = item.get("category", "前沿资讯")
            url = item.get("url", "#")
            score = item.get("score", "N/A")

            formatted_text += f"**{idx}. [{category}] {title}**\n"
            formatted_text += f"💡 **核心摘要**：{summary}\n"
            if score != "N/A":
                formatted_text += f"🔥 **推荐指数**：{score}/10\n"
            formatted_text += f"🔗 [阅读原文]({url})\n\n"
        else:
            formatted_text += f"• {str(item)}\n\n"

    formatted_text += "━━━━━━━━━━━━━━━━━━━\n"
    formatted_text += "✨ *推送完成，祝你今天工作愉快！*"
    
    return formatted_text
