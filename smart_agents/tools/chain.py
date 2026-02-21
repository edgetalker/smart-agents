from .registry import ToolRegistry
from typing import Any, Optional

class ToolChain:
    """工具链 - 支持多个工具的顺序调用"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: list[dict[str, any]] = []

    def add_step(self, tool_name: str, input_template: str, output_key: str = None):
        """
        添加工具执行步骤

        Args:
            tool_name (str): 工具名称
            input_template (str): 输入模版，支持变量替换
            output_key (str, optional): 输出结果的键名，用于后续步骤的引用
        """

        step = {
            "tool_name": tool_name,
            "input_template": input_template,
            "output_key": output_key or f"step_{len(self.steps)}_result"
        }
        self.steps.append(step)
        print(f"✅ 工具链 '{self.name}' 添加步骤：{tool_name}")

    def execute(self, registry: ToolRegistry, input_data: str, context: dict[str, Any] = None) -> str:
        """
        执行工具链

        Args:
            registry (ToolRegistry): 工具注册表
            input_data (str): 初始输入数据
            context (dict[str, Any], optional): 执行上下文.

        Returns:
            str: 最终执行结果
        """
        if not self.steps:
            return "❌ 工具链为空，无法执行"
        
        print(f"🚀 开始执行工具链: {self.name}")

        # 初始化上下文
        if context is None:
            context = {}
        context['input'] = input_data

        final_result = input_data

        for i, step in enumerate(self.steps):
            tool_name = step["tool_name"]
            input_template = step["input_template"]
            output_key = step["output_key"]

            print(f" 执行步骤{i+1}/{len(self.steps)}: {tool_name}")

            # 替换模版中的变量
            try:
                actual_input = input_template.format(**context)
            except KeyError as e:
                return f"❌ 模版变量替换失败: {e}"
            
            # 执行工具
            try:
                result  = registry.execute_tool(tool_name, actual_input)
                context[output_key] = result
                final_result = result
                print(f"✅ 步骤 {i+1}完成")
            except Exception as e:
                return f"❌ 工具 '{tool_name}' 执行失败: {e}"
            
        print(f"🎉 工具链 '{self.name}' 执行完成")
        return final_result
    
class ToolChainManager:
    """工具链管理器"""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.chains: dict[str, ToolChain] = {}
    
    def register_chain(self, chain: ToolChain):
        """注册工具链"""
        self.chains[chain.name] = chain
        print(f"✅ 工具链 '{chain.name}' 已注册")
    
    def execute_chain(self, chain_name: str, input_data: str, context: dict[str, Any] = None) -> str:
        """指定工具链"""
        if chain_name not in self.chains:
            print(f"❌ 工具链{self.name} 不存在")
        
        chain = self.chains[chain_name]
        return chain.execute(self.registry, input_data, context)

    def list_chains(self) -> list[str]:
        """列出所有工具链"""
        return list(self.chains.keys())

    def get_chain_info(self, chain_name: str) -> Optional[dict[str, Any]]:
        """获取工具链信息"""
        if chain_name not in self.chains:
            return None
        
        chain = self.chains[chain_name]
        return {
            "name": chain.name,
            "description": chain.description,
            "steps": len(chain.steps),
            "step_details": [
                {
                    "tool_name": step["tool_name"],
                    "input_template": step["input_template"],
                    "output_key": step["output_key"]
                }
                for step in chain.steps
            ]
        }