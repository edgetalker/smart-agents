from abc import ABC, abstractmethod
from typing import Any, Callable
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
      
class Tool(ABC):
    """工具基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, parameters: dict[str, Any]) -> str:
        """执行工具"""
        pass

    @abstractmethod
    def get_parameters(self) -> list[ToolParameter]:
        """获取参数定义"""
        pass

    def to_openai_schema(self) -> dict[str, Any]:
        """转换为OpenAI function calling scheme 格式
        用于 FunctionCallAgent，使工具能被OpenAI原生 function calling 使用
        """
        pass

class ToolRegistry:
    """工具注册表
    Tool对象注册： 复杂工具定义
    函数直接注册：简单工具
    """
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """注册Tool对象"""
        if tool.name in self._tools:
            print(f"⚠️ 工具 '{tool.name}' 已经存在，将被覆盖")  
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已经注册")

    def registry_function(self, name: str, description: str, func: Callable[[str], str]):
        """直接注册函数作为工具（简便方式）"""
        if name in self._functions:
            print(f"⚠️ 工具 '{name}' 已经存在，将被覆盖")
        
        self._functions[name] = {
            "description": description,
            "func": func
        }
        print(f"✅ 工具 '{name}' 已经注册")

    def unregister(self, name: str):
        """注销工具"""
        if name in self._tools:
            del self.tools[name]
            print(f"🗑️ 工具 '{name}' 已注销")
        elif name in self._functions:
            del self._functions[name]

    def get_tool(self, name: str) -> Tool:
        """获取工具对象"""
        return self._tools[name]

    def get_tools_description(self) -> str:
        """获取所有工具的格式化描述字符串"""
        descriptions = []
        
        # Tool工具描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"
    
    def list_tools(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys()) + list(self._functions.keys())
    
    def get_all_tools(self) -> list[Tool]:
        """获取所有Tool对象"""
        return list(self._tools.values())
    
    def clear(self):
        self._tools.clear()
        self._functions.clear()
        print(f"🧹 所有工具已清空")