# 🛡️ Safe & Self-Healing ReAct Agent Core

一个具备 **Docker 沙箱安全隔离**、**AST 静态防御**、**自主闭环纠错** 以及 **SQLite 长程状态持久化** 的生产级轻量化 ReAct Agent 架构引擎。

---

## 🚀 核心架构亮点 (Key Highlights)

- **多层安全防线（Guardrailed Autonomy）**：在执行动态代码前，通过 AST 静态分析拦截低级语法风险；实际运行则完全隔离在受控的 Docker 沙箱中，限制内存与 CPU，杜绝恶意逃逸。
- **自主纠错闭环（Self-Healing ReAct Loop）**：不只是“代码生成器”。Agent 能够自主读取运行报错（Observation），进行逻辑反思，并实时重写代码，直到在沙箱中成功通过并输出预期结果。
- **长程状态持久化（Long-term State Persistence）**：基于 SQLite 构建的轻量级状态管理器，将对话历史与 ReAct 轨迹（Trajectory）结构化存储，支持任务中断后的无损断点恢复。

---

## 🏗️ 系统架构设计 (Architecture)
