from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from .config import Config
from .message import Message
from .llm import SmartAgentLLM

# Agent基类
class Agent(ABC):
    def __init__(
            self, 
            name: str, 
            llm: SmartAgentLLM, 
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None
            ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: List[Message] = []

        
    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        pass

    def add_message(self, message: Message):
        self._history.append(message)

    def clear_message(self):
        self._history.clear()

    def get_history(self) -> List[Message]:
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider})"
    
    def __repr__(self) -> str:
        return self.__str__()



        
