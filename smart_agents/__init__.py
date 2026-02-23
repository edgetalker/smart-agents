"""SmartAgents - A lightweight agent framework based on LLM"""

__version__ = "0.1.2"

from smart_agents.agents.simple_agent import SimpleAgent
from smart_agents.agents.react_agent import ReActAgent
from smart_agents.core.config import Config
from smart_agents.core.llm import SmartAgentLLM
from smart_agents.core.message import Message

from .tools.registry import ToolRegistry, global_registry
from .tools.builtin.search import SearchTool 
from .tools.builtin.calculator import CalculatorTool
from .tools.chain import ToolChain, ToolChainManager
from .tools.async_executor import AsyncToolExecutor

__all__ = [
    # 核心组件
    "Config",
    "SmartAgentLLM",
    "Message",

    # Agent 范式
    "SimpleAgent",
    "ReActAgent",

    # 工具系统
    "ToolRegistry",
    "global_registry",
    "SearchTool",
    "CalculatorTool",
    "ToolChain",
    "ToolChainManager",
    "AsyncToolExecutor",
]