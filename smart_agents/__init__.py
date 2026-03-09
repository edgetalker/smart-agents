"""SmartAgents - A lightweight agent framework based on LLM"""

__version__ = "0.1.3"

# 核心组件
from smart_agents.core.config import Config
from smart_agents.core.llm import SmartAgentLLM
from smart_agents.core.message import Message

# Agent实现
from smart_agents.agents.simple_agent import SimpleAgent
from smart_agents.agents.react_agent import ReActAgent
from smart_agents.agents.reflection_agent import ReflectionAgent
from smart_agents.agents.plan_solve_agent import PlanAndSolveAgent

# 工具实现
from .tools.registry import ToolRegistry, global_registry
from .tools.builtin.search_tool import SearchTool, search
from .tools.builtin.calculator import CalculatorTool, calculate
from .tools.chain import ToolChain, ToolChainManager
from .tools.async_executor import AsyncToolExecutor

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("qdrant_client").setLevel(logging.WARNING)

__all__ = [
    # 核心组件
    "Config",
    "SmartAgentLLM",
    "Message",

    # Agent 范式
    "SimpleAgent",
    "ReActAgent",
    "ReflectionAgent",
    "PlanAndSolveAgent",

    # 工具系统
    "ToolRegistry",
    "global_registry",
    "SearchTool",
    "search",
    "CalculatorTool",
    "calculate",
    "ToolChain",
    "ToolChainManager",
    "AsyncToolExecutor",
]