import json
from datetime import datetime
from fetcher import collect_all_intelligence

def generate_daily_20_report():
    print("⚙️ 正在执行情报降噪与 20 条每日精报渲染...\n")
    raw_data = collect_all_intelligence()
    
    top_hits = raw_data.get("top_hits", [])[:10]
    tools = raw_data.get("tools_github", [])[:6]
    papers = raw_data.get("research", [])[:4]
    
    date_str = datetime.now().strftime("%Y年%m月%d日")
    
    report = []
    report.append(f"🤖 **【AI 前沿每日情报精报 - {date_str}】**\n")
    report.append("==================================================\n")
    
    # 1. 每日必读 · 全球 AI 焦点 (10 条)
    report.append("🔥 **一、 每日必读 · 全球 AI 焦点 (Top 10)**\n")
    for i, item in enumerate(top_hits, 1):
        report.append(f"{i}. **[{item['source']}]** {item['title']}")
        report.append(f"   💡 *{item['metrics']}* | 摘要: {item['summary'][:100]}...")
        report.append(f"   🔗 {item['url']}\n")
        
    # 2. 趋势工具与热门项目 (6 条)
    report.append("🛠️ **二、 趋势工具与热门项目 (Top 6)**\n")
    for i, item in enumerate(tools, 1):
        report.append(f"{i}. **[{item['source']}]** {item['title']}")
        report.append(f"   ✨ *{item['metrics']}* | 简介: {item['summary']}")
        report.append(f"   🔗 {item['url']}\n")
        
    # 3. 前沿学术与论文速递 (4 条)
    report.append("📄 **三、 前沿学术与论文速递 (Top 4)**\n")
    for i, item in enumerate(papers, 1):
        report.append(f"{i}. **[{item['source']}]** {item['title']}")
        report.append(f"   🔬 *{item['metrics']}* | 突破点: {item['summary']}")
        report.append(f"   🔗 {item['url']}\n")
        
    report.append("==================================================")
    report.append("✨ *由 AI Intelligence Agent 自动过滤与渲染生成*")
    
    final_output = "\n".join(report)
    
    # 将结果写入本地 daily_report.txt 文件，方便直接预览或后续推送 API 提取
    with open("daily_report.txt", "w", encoding="utf-8") as f:
        f.write(final_output)
        
    print(final_output)
    print("\n✅ 每日精报生成成功！已同时存入本地 daily_report.txt 文件。")

if __name__ == "__main__":
    generate_daily_20_report()
