def format_telegram_markdown(intelligence_data):
    """
    将 LLM 分析后的结构化 JSON 渲染为 Telegram Markdown 消息
    """
    if not intelligence_data:
        return "⚠️ 今日未检测到满足标准的高价值 AI 前沿情报。"

    header = "🤖 *【AI 全网前沿高价值精报】*\n"
    header += "=============================\n\n"

    body_items = []
    sorted_data = sorted(intelligence_data, key=lambda x: x.get('score', 0), reverse=True)

    for idx, item in enumerate(sorted_data, 1):
        score = item.get('score', 7)
        score_stars = "🔥" * (score - 6) if score >= 7 else "⚡"
        category = item.get('category', '通用')
        title = item.get('title_zh', '无标题')
        summary = item.get('summary', '无摘要')
        url = item.get('url', '#')

        item_str = (
            f"{idx}. *[{category}]* {score_stars} *{score}分*\n"
            f"📌 *{title}*\n"
            f"💡 {summary}\n"
            f"🔗 [查看原文/讨论]({url})"
        )
        body_items.append(item_str)

    footer = "\n=============================\n💡 *提示*：本情报由智能 Agent 自动过滤全网源生成。"
    return header + "\n\n-----------------------------\n\n".join(body_items) + footer
