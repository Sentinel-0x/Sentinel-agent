import os
import json
from openai import OpenAI
from tool_registry import registry, read_file, write_file
from agent_memory import AgentMemoryStore

class ReActAgent:
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-V3"):
        self.client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
        self.model_name = model_name
        self.registry = registry

    def run(self, user_goal: str, max_steps: int = 5):
        """
        ReAct 核心循环引擎：
        维护对话历史，让大模型自主交替进行 Thought -> Action -> Observation
        """
        tools_desc = json.dumps(self.registry.tool_schemas, ensure_ascii=False, indent=2)
        system_prompt = (
            "你是一个具备自主决策能力的 ReAct Agent。\n"
            "你有权使用以下工具来完成用户的目标：\n"
            f"{tools_desc}\n\n"
            "请严格按照以下格式和逻辑运转：\n"
            "当你需要调用工具时，使用标准的 OpenAI tool_calls 机制。\n"
            "当你认为任务已经彻底完成时，直接向用户输出最终的文字总结（无需再调用工具）。\n"
            "切记：不要陷入死循环，每次行动前仔细观察上一步工具返回的 Observation。"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal}
        ]

        print(f"\n[ReAct Agent 启动] 目标: {user_goal}")

        for step in range(1, max_steps + 1):
            print(f"\n--- [ReAct 循环步数: {step}/{max_steps}] ---")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.registry.tool_schemas if self.registry.tool_schemas else None,
                tool_choice="auto",
                temperature=0.1
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.tool_calls:
                print("[Thought & Action] 模型决定调用工具:")
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    print(f" -> 工具名称: {tool_name}")
                    print(f" -> 传入参数: {tool_args}")
                    
                    observation = self.registry.execute(tool_name, tool_args)
                    print(f" [Observation 结果]: {str(observation)[:300]}...")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(observation)
                    })
            else:
                final_answer = response_message.content
                print("\n[ReAct 任务达成] 最终结论:")
                print(final_answer)
                return final_answer

        print("\n[ReAct 警告] 达到最大步数限制，任务被迫终止。")
        return "达到最大步数限制，未完全收敛。"


# ==================== 新增：具备长程记忆持久化能力的 Agent 扩展类 ====================
class PersistentReActAgent(ReActAgent):
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-V3", db_path: str = "agent_state.db"):
        super().__init__(model_name)
        self.memory = AgentMemoryStore(db_path)

    def run_with_memory(self, task_id: str, user_goal: str, max_steps: int = 5):
        # 检查是否存在历史记忆（支持断点恢复）
        existing_state = self.memory.load_task_state(task_id)
        if existing_state and existing_state["status"] == "COMPLETED":
            print(f"[Memory] 发现任务 '{task_id}' 已有成功历史记录，直接跳过执行。")
            return existing_state["final_answer"]

        tools_desc = json.dumps(self.registry.tool_schemas, ensure_ascii=False, indent=2)
        system_prompt = (
            "你是一个具备自主决策能力的 ReAct Agent。\n"
            "你有权使用以下工具来完成用户的目标：\n"
            f"{tools_desc}\n\n"
            "请严格按照 ReAct 规范运转，并在任务达成时输出最终结论。"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_goal}
        ]

        print(f"\n[Persistent ReAct Agent 启动] 任务ID: {task_id} | 目标: {user_goal}")

        for step in range(1, max_steps + 1):
            print(f"\n--- [ReAct 循环步数: {step}/{max_steps}] ---")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.registry.tool_schemas if self.registry.tool_schemas else None,
                tool_choice="auto",
                temperature=0.1
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}
                    
                    print(f" -> 调用工具: {tool_name} | 参数: {tool_args}")
                    observation = self.registry.execute(tool_name, tool_args)
                    print(f" [Observation 结果]: {str(observation)[:200]}...")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(observation)
                    })
                
                # 每执行完一步，立刻将状态持久化到 SQLite
                self.memory.save_task_state(task_id, user_goal, "RUNNING", messages)
            else:
                final_answer = response_message.content
                print("\n[ReAct 任务达成] 最终结论:")
                print(final_answer)
                
                # 持久化最终成功状态
                self.memory.save_task_state(task_id, user_goal, "COMPLETED", messages, final_answer)
                return final_answer

        self.memory.save_task_state(task_id, user_goal, "FAILED", messages, "达到最大步数限制")
        return "达到最大步数限制。"


if __name__ == "__main__":
    # 使用带记忆持久化的 Agent 进行沙箱自愈任务测试
    agent = PersistentReActAgent()
    
    goal = (
        "请帮我编写一个名为 bug_demo.py 的文件，故意在里面写一段有语法错误或者运行时错误的 Python 代码。"
        "然后，请你自主调用 Docker 沙箱工具去运行它，获取报错的 Observation 后，自主修改并重写这个文件，"
        "重复这个过程直到它在沙箱中成功运行并正常输出。"
    )
    
    # 赋予一个固定的 task_id，以便支持 SQLite 状态持久化和断点恢复
    agent.run_with_memory(task_id="sandbox_repair_task_001", user_goal=goal)