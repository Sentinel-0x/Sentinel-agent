import os
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 1. 读取中转站配置并初始化客户端
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

MODEL_NAME = "gpt-4o-mini" # 中转站通常支持 gpt-4o, gpt-4o-mini 等标准模型名

# 2. 定义可供 Agent 调用的真实工具函数
def fetch_github_trending():
    """抓取 GitHub 今日热门开源项目"""
    print("  └── 🛠️ [Tool Executed] 正在抓取 GitHub Trending 数据...")
    url = "https://github.com/trending/python?since=daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200: return "Error: 网页响应状态码异常"
        soup = BeautifulSoup(resp.text, 'html.parser')
        repos = soup.find_all('article', class_='Box-row')
        results = []
        for repo in repos[:3]:
            title_tag = repo.find('h2')
            if title_tag:
                repo_name = title_tag.text.strip().replace(" ", "").replace("\n", "")
                desc_tag = repo.find('p')
                desc = desc_tag.text.strip() if desc_tag else "无详细描述"
                results.append({"name": repo_name, "desc": desc, "url": f"https://github.com/{repo_name}"})
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return f"Error: 抓取失败 - {str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_github_trending",
            "description": "抓取 GitHub 今日热门 Python/AI 开源项目列表",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

# 3. 带自愈与熔断的 Agent 主循环
def run_self_healing_agent(prompt, max_turns=5):
    messages = [
        {"role": "system", "content": "你是一个智能情报分析 Agent。请调用工具获取数据并提炼价值。格式严格要求为 JSON。"},
        {"role": "user", "content": prompt}
    ]
    
    consecutive_errors = 0
    
    for turn in range(max_turns):
        print(f"\n🔄 [Turn {turn + 1}/{max_turns}] Agent 正在思考...")
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    fn_name = tool_call.function.name
                    print(f"👉 AI 决定调用工具: {fn_name}")
                    
                    if fn_name == "fetch_github_trending":
                        tool_result = fetch_github_trending()
                        
                        if tool_result.startswith("Error:"):
                            consecutive_errors += 1
                            print(f"⚠️ [工具报错自愈中] 报错回传 AI ({consecutive_errors}/2)...")
                        else:
                            consecutive_errors = 0
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })

            elif response_message.content:
                print("\n✅ [Agent 决策完成，成功输出最终结果]:")
                print(response_message.content)
                return

        except Exception as e:
            consecutive_errors += 1
            print(f"❌ [API 通信层异常]: {e}")
            messages.append({"role": "user", "content": f"系统运行报错: {str(e)}，请调整策略重新尝试。"})

        if consecutive_errors >= 2:
            print("\n🛑 [熔断机制触发]: 连续报错次数过多，已自动强制终止程序！")
            break

    print("\n⚠️ 达到最大交互轮次上限，Agent 安全退出。")

if __name__ == "__main__":
    print("[Agent Workflow] 启动基于 OpenAI 兼容中转接口的自愈式智能体...")
    run_self_healing_agent("请帮我抓取今天的 GitHub AI 热门项目，并分析出最有价值的 1 个项目。")
