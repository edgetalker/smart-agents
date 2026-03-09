"""简单Agent实现"""
import re
from typing import Optional, TYPE_CHECKING, Iterator
from ..core.message import Message
from ..core.agent import Agent
from ..core.llm import SmartAgentLLM
from ..core.config import Config

if TYPE_CHECKING:
    from ..tools.registry import ToolRegistry

class SimpleAgent(Agent):
    """新增工具调用与消息模版"""

    def __init__(
        self, 
        name: str, 
        llm: SmartAgentLLM, 
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional['ToolRegistry'] = None,
        enable_tool_calling: bool = True
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and self.tool_registry is not None

    def run(self, input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        messages = []
        # 获取系统prompt
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        messages.append({"role": "system","content": enhanced_system_prompt})

        # 获取历史对话信息
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        # 添加当前对话信息
        messages.append({"role": "user", "content": input_text})
        
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(input_text, "user"))
            self.add_message(Message(response, "assistant"))
            print(f"{self.name}调用完成")
            return response
        
        current_iteration = 0
        final_response = ""

        while current_iteration < max_tool_iterations:
            # 调用LLM
            response = self.llm.invoke(messages, **kwargs)
            # 检查是否有工具调用
            tools_calls = self._parse_tool_call(response)

            if tools_calls:
                tool_results = []
                clean_response = response

                for call in tools_calls:
                    result = self._execute_tool_call(call['tool_name'], call['parameters'])
                    tool_results.append(result)
                    clean_response = clean_response.replace(call['original'], "")

                # 构建包含工具结果的消息
                messages.append({"role": "assistant", "content": clean_response})

                # 添加工具结果
                tool_results_text = "\n\n".join(tool_results)
                messages.append({"role": "user", "content": f"工具执行结果: \n{tool_results_text}\n\n请基于这些结果给出完整回答。"})

                current_iteration += 1
                continue

            final_response = response
            break

        # 超过迭代次数，取最后一次调用结果
        if current_iteration >= max_tool_iterations and not final_response:
            final_response = self.llm.invoke(messages, **kwargs)

        # 添加历史信息
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_response, "assistant"))

        return final_response
        
    def _get_enhanced_system_prompt(self) -> str:
        """带有工具调用的系统prompt"""
        base_prompt = self.system_prompt or "你是一个有用的助手"

        if not self.enable_tool_calling or not self.tool_registry:
            return base_prompt
        
        # 获取工具描述
        tools_description = self.tool_registry.get_tools_description()
        if not tools_description or tools_description == "暂无可用工具":
            return base_prompt
        
        tools_section = "\n\n## 可用工具\n"
        tools_section += "你可以使用以下工具来帮助回答问题:\n"
        tools_section += tools_description + '\n'

        tools_section += "\n## 工具调用格式\n"
        tools_section += "当需要调用工具时，请使用以下格式:\n"
        tools_section += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"
        tools_section += "例如:`[TOOL_CALL:search:Python编程]` 或 `[TOOL_CALL:memory:recall=用户信息]`\n\n"
        tools_section += "工具调用结果会自动插入到对话中, 然后你可以基于结果继续回答。\n"

        return base_prompt + tools_section
    
    def _parse_tool_call(self, text: str) -> list:
        """解析文本中的工具调用"""
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)

        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append({
                'tool_name': tool_name.strip(),
                'parameters': parameters.strip(),
                'original': f'[TOOL_CALL:{tool_name}:{parameters}]'
            })
        
        return tool_calls

    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """执行工具调用"""
        if not self.tool_registry:
            return f"❌ 错误: 未配置工具注册表"
        
        try: 
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                return f"❌ 错误: 未找到工具 '{tool_name}' "
            
            # 智能参数解析
            param_dict = self._parse_tool_parameters(tool_name, parameters)

            # 调用工具
            result = tool.run(param_dict)
            print(f"🔧 工具 '{tool_name}' 执行结果: \n{result}")
            return result

        except Exception as e:
            return f"❌ 工具调用失败: {str(e)}"

    def _parse_tool_parameters(self, tool_name: str, parameters: str):
        """智能解析工具调用参数"""  
        param_dict = {}
        
        if "=" in parameters:
            if "," in parameters:
                pairs = parameters.split(",")
                # 多个参数
                for pair in pairs:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        param_dict[key.strip()] = value.strip()
            else:
                # 单个参数
                key, value = parameters.split("=", 1)
                param_dict[key.strip()] = value.strip()
        else:
            # 直接传入参数
            if tool_name == "search":
                param_dict = {"query": parameters}
            elif tool_name == 'memory':
                param_dict = {'action': 'search', 'query': parameters}
            else:
                param_dict = {'input': parameters}
        
        return param_dict

    def add_tool(self, tool) -> None:
        """添加工具到Agent"""
        if not self.tool_registry:
            from ..tools.registry import ToolRegistry
            self.tool_registry = ToolRegistry()
            self.enable_tool_calling = True
        
        self.tool_registry.register_tool(tool)
        print(f"🔧 工具 '{tool.name}' 已添加")

    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        if self.tool_registry:  
            self.tool_registry.unregister(tool_name)
            return True
        return False
    
    def list_tools(self) -> list:
        """列出所有有用工具"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []
    
    def has_tools(self) -> bool:
        """检查是否有可用工具"""
        return self.enable_tool_calling and self.tool_registry is not None
    
    def stream_run(self, input_text: str, **kwargs) -> Iterator[str]:
        """
        流式运行Agent

        Args:
            input_text (str): 用户输入

        Yields:
            Iterator[str]: Agent响应片段
        """
        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": input_text})

        # 流式调用
        full_response = ""
        for chunk in self.llm.stream_invoke(messages, **kwargs):
            full_response += chunk
            yield chunk
        
        # 保存对话历史
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(full_response, "assistant"))

