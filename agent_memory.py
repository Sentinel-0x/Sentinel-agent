import sqlite3
import json
import os
from datetime import datetime

class AgentMemoryStore:
    def __init__(self, db_path: str = "agent_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化轻量级 SQLite 状态存储表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_tasks (
                task_id TEXT PRIMARY KEY,
                goal TEXT,
                status TEXT,
                trajectory TEXT,
                final_answer TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_task_state(self, task_id: str, goal: str, status: str, messages: list, final_answer: str = ""):
        """持久化保存当前任务的执行状态与对话历史轨迹"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将复杂的消息对象序列化为 JSON 字符串存储
        serialized_messages = []
        for msg in messages:
            # 处理 OpenAI 消息对象的兼容转换
            if hasattr(msg, "role"):
                msg_dict = {"role": msg.role, "content": msg.content}
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in msg.tool_calls
                    ]
                serialized_messages.append(msg_dict)
            elif isinstance(msg, dict):
                serialized_messages.append(msg)

        trajectory_json = json.dumps(serialized_messages, ensure_ascii=False)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT OR REPLACE INTO agent_tasks (task_id, goal, status, trajectory, final_answer, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, goal, status, trajectory_json, final_answer, created_at))
        
        conn.commit()
        conn.close()

    def load_task_state(self, task_id: str) -> dict:
        """根据任务 ID 读取历史记忆状态，用于断点恢复"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT task_id, goal, status, trajectory, final_answer FROM agent_tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "task_id": row[0],
                "goal": row[1],
                "status": row[2],
                "trajectory": json.loads(row[3]),
                "final_answer": row[4]
            }
        return None