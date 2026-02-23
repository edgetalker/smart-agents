"""
定义框架内统一的消息格式，确保Agent与模型之间消息传递的标准化
"""
from typing import Literal, Optional, Any
from datetime import datetime
from pydantic import BaseModel

MessageRole = Literal["system", "user", "assistant", "tool"]

class Message(BaseModel):
    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[dict[str, Any]] = None

    def __init__(self, content: str, role: MessageRole, **kwargs):
        super().__init__(
            content=content,
            role=role,
            timestamp=kwargs.get('timestamp', datetime.now()),
            metadata=kwargs.get('metadata', {})
        )
    
    def to_dict(self) -> dict[str: Any]:
        """转换为OpenAI格式"""
        return {
            "role": self.role,
            "content": self.content
        }
    
    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"