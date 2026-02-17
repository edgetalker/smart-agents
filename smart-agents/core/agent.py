from abc import ABC, abstractmethod
from typing import List, Dict
from .llm import SmartAgentLLM

# Agent基类
class Agent(ABC):
    def __init__(self, name: str, llm: SmartAgentLLM, system_prompt: str):
        name = name
        self.llm = llm
        self.system_prompt = system_prompt
        
    @abstractmethod
    def run(self, input_text: str) -> str:
        """运行Agent"""
        pass


        
