import json
import logging
from typing import Dict, Any, Optional, Callable, List
from openai import OpenAI
from metrics import JOBS_PROCESSED

logger = logging.getLogger("job_agent")

# ==================== 1. 全局配置常量化 ====================
DEFAULT_WORK_TYPE = "Remote"
DEFAULT_LOCATION = "Worldwide"
DEFAULT_ROLE = "AI GTM & Ecosystem Partner"

# 赛道关键词映射表（用于动态分流）
TRACK_MAPPINGS = {
    "crypto": {"role": "Crypto Research Analyst", "focus": "Web3 / Crypto Research & Tokenomics"},
    "web3": {"role": "Web3 Community & Operations", "focus": "Web3 Ecosystem & Operations"},
    "gtm": {"role": "AI GTM & Commercialization Specialist", "focus": "AI SaaS Commercialization & GTM"},
    "商业化": {"role": "AI Commercialization Lead", "focus": "AI Commercialization & Enterprise SaaS"},
    "生态": {"role": "AI Ecosystem Partnership Manager", "focus": "AI Ecosystem & Strategic Partnerships"},
    "实施": {"role": "AI Solutions Delivery & Implementation Consultant", "focus": "AI Solutions & Client Success"},
    "research": {"role": "AI Research Ops Specialist", "focus": "AI Research Operations & Evaluation"}
}

class ReActJobAgent:
    """
    确定性多工具路由智能体：全球远程多元赛道精准匹配与终态合成
    """
    def __init__(self, client: OpenAI, model_name: str, max_steps: int = 3):
        self.client = client
        self.model_name = model_name
        self.max_steps = max_steps
        self.tools: Dict[str, Callable[..., str]] = {}
        self.tool_descriptions: Dict[str, str] = {}

    def register_tool(self, name: str, description: str, parameters: dict, func: Callable[..., str]):
        """注册工具及其业务描述"""
        self.tools[name] = func
        self.tool_descriptions[name] = description

    def _resolve_dynamic_track(self, goal: str) -> Dict[str, str]:
        """根据用户输入通过关键词动态分流到对应的垂直赛道"""
        lower_goal = goal.lower()
        for keyword, config in TRACK_MAPPINGS.items():
            if keyword in lower_goal:
                return config
        # 默认兜底：全球远程生态与商业化方向
        return {"role": DEFAULT_ROLE, "focus": "AI Global Remote Ecosystem & Commercialization"}

    def run(self, goal: str) -> Optional[str]:
        """
        确定性执行闭环：意图解析 -> 动态分流 -> 异常收敛的安全工具调用 -> 文本合成与防呆
        """
        logger.info(f"[Agent Target] 收到全球远程业务目标: {goal}")
        
        # 提取动态分流赛道
        track_config = self._resolve_dynamic_track(goal)
        logger.info(f"[Dynamic Router] 动态匹配垂直赛道: {track_config['focus']} | 目标岗位: {track_config['role']}")
        
        execution_logs = []
        
        # ==================== 4. 异常捕获边界收敛 (工具层安全隔离) ====================
        try:
            if "薪资" in goal or "salary" in goal.lower() or "基准" in goal:
                if "search_salary_benchmark" in self.tools:
                    logger.info("[Deterministic Router] 语义命中工具 -> search_salary_benchmark")
                    res1 = self.tools["search_salary_benchmark"](role=track_config["role"], city=DEFAULT_LOCATION)
                    execution_logs.append(f"【全球远程薪资/市场基准】: {res1}")

            if "github" in goal.lower() or "开源" in goal or "项目" in goal:
                if "fetch_github_trending" in self.tools:
                    logger.info("[Deterministic Router] 语义命中工具 -> fetch_github_trending")
                    lang = "python" if "python" in goal.lower() else "typescript"
                    res2 = self.tools["fetch_github_trending"](language=lang)
                    execution_logs.append(f"【GitHub 开源/项目对标】: {res2}")
        except Exception as e:
            logger.error(f"[Tool Execution Error] 工具执行阶段发生异常已被边界拦截: {str(e)}")
            execution_logs.append(f"【系统警告】部分工具执行受阻，已启用降级容错: {str(e)}")

        if not execution_logs:
            # 基础降级路由：直接把动态分流识别出的赛道作为基础情报产出
            execution_logs.append(f"【赛道定向分析】目标赛道：{track_config['focus']}，面向全球远程（Remote）项目制/兼职机会。")

        # 让大模型基于真实拿到的工具数据进行最终的综合报告合成
        synthesis_prompt = (
            f"用户原始目标：{goal}\n"
            f"当前定位赛道：{track_config['focus']} (Global Remote)\n"
            f"已通过确定性工具获取到以下结构化数据：\n" + "\n".join(execution_logs) + "\n\n"
            "请基于以上真实数据，为用户整理出一份结构清晰、专业美观的全球远程市场分析报告。"
        )

        logger.info("[Agent Synthesis] 正在交由大模型合成最终综合报告...")
        
        # ==================== 异常边界收敛：API 调用与降级熔断 ====================
        response_content = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional global remote business analyst and career strategist."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.3,
                extra_body={
                    "repetition_penalty": 1.15  # 压制 7B 模型死循环重复生成相同字符的顽疾
                }
            )
            response_content = response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"[API Error Boundary] 大模型合成接口调用遭遇异常已被安全捕获: {str(e)}")
            # 优雅降级：当大模型挂掉时，直接利用已有的工具日志拼装基础情报，保证核心数据不丢失
            response_content = (
                f"### 【系统降级提示】大模型在线合成接口暂不可用（错误: {str(e)}）\n\n"
                f"但已成功为您捕获并提取以下底层确定性情报：\n" + 
                "\n".join([f"- {log}" for log in execution_logs]) + 
                "\n\n建议您稍后重新运行程序。"
            )
        
        # 防呆拦截：检查是否有无限重复的退化字符
        if len(response_content) > 20 and len(set(response_content)) < 3:
            logger.error("[Guardrail Triggered] 检测到大模型输出发生严重的重复退化现象。")
            return "Error: Model output degraded into infinite repetition loop."
            
        return response_content