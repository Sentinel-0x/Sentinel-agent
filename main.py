import os
from dotenv import load_dotenv
from openai import OpenAI
from job_agent import ReActJobAgent

# 加载环境变量
load_dotenv()

# 初始化 SiliconFlow 客户端（兼容 OpenAI 接口规范）
client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# 实例化确定性路由智能体
agent = ReActJobAgent(client=client, model_name="Qwen/Qwen2.5-7B-Instruct")

# 注册真实工具函数
def search_salary_benchmark(role: str, city: str) -> str:
    print(f"    └─ 🛠️ [Tool Executed] 正在查询城市 [{city}] 职位 [{role}] 的薪资基准...")
    return f"Global Remote Benchmark for {role}: Median rate $40k-$80k/year (Project-based / Part-time flexible)."

def fetch_github_trending(language: str) -> str:
    print(f"    └─ 🛠️ [Tool Executed] 正在抓取 {language} 的 GitHub Trending...")
    return f"Top {language} Trending: AgenticFlow, OpenClaw, Multi-Agent Orchestration frameworks."

agent.register_tool(
    name="search_salary_benchmark",
    description="查询全球远程或特定城市的薪资和市场基准",
    parameters={"role": "string", "city": "string"},
    func=search_salary_benchmark
)

agent.register_tool(
    name="fetch_github_trending",
    description="获取 GitHub 上的热门开源项目",
    parameters={"language": "string"},
    func=fetch_github_trending
)

if __name__ == "__main__":
    print("[Agent Workflow] 启动全球远程多赛道动态路由与市场情报分析智能体...\n")
    
    # 模拟你关心的全球远程多元求职目标（可以随时修改这里的关键词测试不同赛道）
    test_goal = "我需要一份关于 Crypto 研究与 AI 商业化 GTM 方向的全球远程兼职市场分析报告，顺便看看 Python 相关的开源项目。"
    
    report = agent.run(test_goal)
    print("\n✅ [Agent 综合情报分析完成]:")
    print(report)