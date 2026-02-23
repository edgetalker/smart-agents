<div align="center">

# 🤖 SmartAgents

*从零实现LLM Agent框架 - 教学级实现与工程化实践*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[🚀 快速开始](#快速开始) • [📖 文档](docs/) • [🎯 示例](examples/) • [🤝 贡献指南](CONTRIBUTING.md)

</div>

---

## ✨ 项目亮点

- 🎓 **低耦合架构**: 清晰的模块组织和渐进式实现，适合学习Agent内部机制
- 🏗️ **工程化实践**: 模块化架构、完整测试、CI/CD流程
- 🔧 **生产可用**: 支持DeepSeek/OpenAI等多Provider，自动检测服务商
- 📚 **功能完整**: 内置多种工具调用、工具链、工具异步调用

## 🎬 快速演示
```python
from smart_agents import SimpleAgent
from smart_agents.llm import SimpleAgentLLM
from smart_agents.tools import ToolRegistry
from smart_agents.tools.bulitin import SearchTool
# 初始化LLM
llm = SmartAgentLLM()

# 初始化工具
tool_registry = ToolRegistry()
searchTool = SearchTool()
tool_registry.register_tool(searchTool)

# 初始化Agent
agent = SimpleAgent(
    name="工具增强助手",
    llm=llm,
    system_prompt="你是一个智能助手，可以使用工具来帮助用户。",
    tool_registry=tool_registry,
    enable_tool_calling=True
)

response = agent.run("2026年小米手机最新款是什么，有什么卖点")
print(f"工具增强助手响应: {response}")
# 2026年小米手机的最新款型有几个比较主要的系列：

# 1. Redmi Note系列：主打千元长续航、耐用抗造，适合长辈、户外、备用机。
# 2. Redmi K系列：主打电竞性能、性价比旗舰，适合学生、游戏玩家。...
```

## 📊 架构设计
```
┌─────────────────────────────────────────┐
│          User Interface (API)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Agent Core (ReAct)             │
│  ┌────────┐ ┌────────┐ ┌──────────┐   │
│  │Planning│ │Executor│ │Reflexion │   │
│  └────────┘ └────────┘ └──────────┘   │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌──▼───┐  ┌──▼─────┐
│Memory │  │Tools │  │LLM Prov│
│System │  │      │  │        │
└───────┘  └──────┘  └────────┘
```

## 🚀 快速开始

### 安装
```bash
# 使用pip安装
pip install smart_agents-py

# 或从源码安装
git clone https://github.com/edgetalker/smart_agents.git
cd hello-agents
```

### 配置
```bash
cp .env.example .env
# 编辑.env文件，填入API密钥
```

## 📖 核心功能

### 1️⃣ ReAct执行循环
```python
# Agent自动进行推理-行动循环
agent.run("帮我查询AAPL股票价格并分析走势")

# 内部执行过程：
# Thought: 需要先获取股票价格
# Action: get_stock_price("AAPL")
# Observation: $178.32
# Thought: 需要分析历史数据
# Action: analyze_trend("AAPL", days=30)
# Observation: 上涨趋势...
# Final Answer: ...
```

### 2️⃣ 向量记忆系统
```python
# 长期记忆存储与检索
agent.memory.store("用户偏好Python开发")
relevant = agent.memory.retrieve("编程语言")
# 自动召回相关上下文
```

### 3️⃣ 自定义工具
```python
from smart_agents-py.tools import Tool

@Tool(
    name="database_query",
    description="查询MySQL数据库"
)
async def query_db(sql: str) -> str:
    # 你的实现
    return results
```

## 🗺️ 开发路线图

- [x] 基础Agent框架 (v0.1.0)
- [x] ReAct执行循环 (v0.2.0)
- [x] 向量记忆系统 (v0.3.0)
- [ ] Reflexion自我反思 (v0.4.0)
- [ ] 多Agent协作 (v0.5.0)
- [ ] 生产优化与部署 (v1.0.0)

## 🤝 贡献

欢迎提交Issue和Pull Request!


## 📄 许可证

[MIT License](LICENSE) © edgetalker

## 🙏 致谢

- DataWhale HelloAgents项目启发
- MIT 6.5940课程的优化技术
- LangChain社区的最佳实践

## 📧 联系方式

- GitHub: [@edgetalker](https://github.com/edgetalker)
- Email: kevinpan998@gmail.com

---

<div align="center">
如果这个项目对你有帮助，请给个⭐️支持一下！
</div>