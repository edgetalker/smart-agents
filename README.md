<div align="center">

# 🤖 SmartAgents

*从零实现LLM Agent框架 - 教学级实现与工程化实践*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/PyPI-smartagents--py-orange.svg)](https://pypi.org/project/smartagents-py/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[🚀 快速开始](#快速开始) • [📖 文档](docs/) • [🎯 示例](examples/) • [🤝 贡献指南](CONTRIBUTING.md)

</div>

---

## ✨ 项目亮点

- 🎓 **低耦合架构**：清晰的模块组织，适合学习 Agent 内部机制
- 🧠 **四种 Agent 范式**：SimpleAgent / ReActAgent / ReflectionAgent / PlanAndSolveAgent
- 🔧 **默认优秀**：开箱即用的高质量 Agent，无需配置即可运行
- 🎨 **完全可定制**：支持完全替换各阶段 Prompt 模板，适配专业领域
- ⚡ **工具生态**：内置工具、工具链、并行异步执行一体化
- 🔌 **多 Provider 支持**：兼容 DeepSeek / OpenAI 等，自动检测服务商

---

## 🚀 快速开始

### 安装
```bash
pip install smartagents-py
```

### 配置
```bash
cp .env.example .env
# 填入你的 API Key
```

### 最简示例
```python
from smart_agents import SmartAgentLLM, SimpleAgent
from dotenv import load_dotenv
load_dotenv()

llm = SmartAgentLLM()
agent = SimpleAgent(name="助手", llm=llm, system_prompt="你是一个有用的AI助手。")
print(agent.run("什么是人工智能？"))
```

---

## 🧠 四种 Agent 范式

### 1️⃣ SimpleAgent — 基础对话
```python
from smart_agents import SimpleAgent, SmartAgentLLM

agent = SimpleAgent(
    name="助手",
    llm=SmartAgentLLM(),
    system_prompt="你是一个有用的AI助手，请用中文回答问题。"
)
response = agent.run("请用一句话总结机器学习的核心思想")
```

### 2️⃣ ReActAgent — 推理与行动

内置 Thought → Action → Observation 循环，支持工具调用。
```python
from smart_agents import ReActAgent, ToolRegistry, search, calculate

tool_registry = ToolRegistry()
tool_registry.register_function("search", "网页搜索工具", search)
tool_registry.register_function("calculate", "数学计算工具", calculate)

agent = ReActAgent(
    name="工具助手",
    llm=llm,
    tool_registry=tool_registry,
    max_steps=3
)
response = agent.run("计算 15 * 23 + 45 的结果")
```

**自定义 Prompt（专业角色定制）：**
```python
custom_prompt = """
你是一个专业的研究助手。
可用工具：{tools}

Thought: 分析问题，制定研究策略。
Action:
- `{tool_name}[{tool_input}]`：调用工具
- `Finish[结论]`：输出最终答案

研究问题：{question}
已完成的研究：{history}
"""

research_agent = ReActAgent(
    name="研究助手", llm=llm,
    tool_registry=tool_registry,
    custom_prompt=custom_prompt,
    max_steps=3
)
```

### 3️⃣ ReflectionAgent — 自我反思与迭代优化

生成初稿 → 自我评审 → 迭代精炼，适合需要高质量输出的场景。
```python
from smart_agents import ReflectionAgent

agent = ReflectionAgent(name="反思助手", llm=llm, max_iterations=2)
response = agent.run("解释什么是递归算法，并给出一个简单的例子")
```

**自定义三阶段 Prompt（代码生成专家）：**
```python
code_prompts = {
    "initial":  "你是资深程序员，请根据要求编写代码：\n\n要求: {task}",
    "reflect":  "你是代码评审专家，请审查以下代码质量：\n\n任务: {task}\n代码: {content}",
    "refine":   "请根据评审意见优化代码：\n\n任务: {task}\n上一版: {last_attempt}\n意见: {feedback}"
}

code_agent = ReflectionAgent(
    name="代码专家", llm=llm,
    custom_prompts=code_prompts, max_iterations=2
)
```

### 4️⃣ PlanAndSolveAgent — 分解规划与逐步执行

先生成执行计划，再逐步完成每个子步骤，适合复杂多步骤任务。
```python
from smart_agents import PlanAndSolveAgent

agent = PlanAndSolveAgent(name="规划助手", llm=llm)
response = agent.run("如何学习Python编程？请制定一个详细的学习计划。")
```

**自定义双阶段 Prompt（数学专家）：**
```python
math_prompts = {
    "planner":  "将数学问题分解为计算步骤：\n问题: {question}\n输出格式：```python\n['步骤1', '步骤2', ...]\n```",
    "executor": "严格执行当前计算步骤：\n问题: {question}\n计划: {plan}\n历史: {history}\n当前步骤: {current_step}"
}

math_agent = PlanAndSolveAgent(
    name="数学专家", llm=llm,
    custom_prompts=math_prompts
)
```

---

## 🔧 工具系统

### 内置工具

| 工具 | 说明 |
|------|------|
| `search` | 网页搜索，获取实时信息 |
| `calculate` | 数学计算，支持 sqrt / sin / pi 等 |

### 工具链 — 顺序编排多工具
```python
from smart_agents import ToolChain, ToolChainManager

chain = ToolChain("my_chain", "示例工具链")
chain.add_step("calculate", "2 + 3", "step1")
chain.add_step("calculate", "5 * 2", "step2")

manager = ToolChainManager(registry)
manager.register_chain(chain)
result = manager.execute_chain("my_chain", "开始")
```

### 异步并行执行
```python
from smart_agents import AsyncToolExecutor
import asyncio

async def run():
    executor = AsyncToolExecutor(registry, max_workers=4)
    tasks = [
        {"tool_name": "calculate", "input_data": "10 + 5"},
        {"tool_name": "calculate", "input_data": "20 * 3"},
        {"tool_name": "calculate", "input_data": "100 / 4"},
    ]
    results = await executor.execute_tools_parallel(tasks)
    executor.close()
    return results

asyncio.run(run())
```

---

## 📊 架构设计
```
┌─────────────────────────────────────────────┐
│            User Interface (API)             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              Agent Core                     │
│  ┌───────────┐ ┌──────────┐ ┌───────────┐  │
│  │SimpleAgent│ │ReActAgent│ │Reflection │  │
│  └───────────┘ └──────────┘ │PlanSolve  │  │
│                              └───────────┘  │
└──────────────────┬──────────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
  ┌────▼────┐ ┌───▼─────┐ ┌──▼───────┐
  │  Tools  │ │ToolChain│ │   LLM    │
  │Registry │ │& Async  │ │ Provider │
  └─────────┘ └─────────┘ └──────────┘
```

---

## 🗺️ 开发路线图

- [x] 基础 SimpleAgent 框架 (v0.1.0)
- [x] ReAct 执行循环 + 工具系统 (v0.1.1)
- [x] ReflectionAgent / PlanAndSolveAgent (v0.1.2)
- [x] 工具链 & 异步并行执行 / 自定义 Prompt 支持 (v0.1.3)
- [ ] 向量记忆系统 (v0.2.0)
- [ ] 多 Agent 协作 (v0.3.0)
- [ ] 生产优化与部署 (v1.0.0)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE) © edgetalker

## 🙏 致谢

- DataWhale HelloAgents 项目启发
- MIT 6.5940 EfficientML 课程
- LangChain 社区最佳实践

## 📧 联系方式

- GitHub: [@edgetalker](https://github.com/edgetalker)
- Email: kevinpan998@gmail.com

---

<div align="center">
如果这个项目对你有帮助，请给个 ⭐️ 支持一下！
</div>