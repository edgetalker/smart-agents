from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel
from datetime import datetime

class MemoryItem(BaseModel):
    """记忆项数据结构"""
    id: str
    content: str
    memory_type: str
    user_id: str
    timestamp: datetime
    importance: float = 0.5
    metadata: dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True

class MemoryConfig(BaseModel):
    """记忆系统配置"""
    # 存储路径
    storage_path: str = "./memory_data"

    # 统计显示用的基础配置
    max_capacity: int = 100
    importance_threshold: float = 0.1
    decay_factor: float = 0.95

    # 工作记忆配置
    working_memory_capacity: int = 10
    working_memory_tokens: int = 2000
    working_memory_ttl_minutes: int = 120

    # 感知记忆特定配置
    perceptual_memory_modaities: list[str] = ["text", "image", "audio", "video"]

class BaseMemory(ABC):
    def __init__(self, config: MemoryConfig, storage_backend=None):
        self.config = config
        self.storage = storage_backend
        self.memory_type = self.__class__.__name__.lower().replace("memory", "")

    @abstractmethod
    def add(self, memory_item: MemoryItem) -> str:
        """
        添加记忆项

        Args:
            memory_item (MemoryItem): 记忆项对象

        Returns:
            str: 记忆ID
        """
        pass
    
    @abstractmethod
    def retrieve(self, query: str, limit: int = 5, **kwargs) -> list[MemoryItem]:
        """
        检索相关记忆

        Args:
            query (str): 查询内容
            limit (int, optional): 返回数量限制

        Returns:
            list[MemoryItem]: 相关记忆列表
        """
        pass
    
    @abstractmethod
    def update(self, memory_id: str, content: str = None,
               importance: float = None, metadata: dict[str, Any] = None) -> bool:
        """更新记忆

        Args:
            memory_id (str): 记忆ID
            content (str, optional): 新内容
            importance (float, optional): 新重要性
            metadata (dict[str, Any], optional): 新元数据

        Returns:
            bool: 是否更新成功
        """
        pass

    @abstractmethod
    def remove(self, memory_id: str) -> bool:
        """删除记忆

        Args:
            memory_id (str): 记忆ID

        Returns:
            bool: 是否成功删除
        """
        pass
    
    @abstractmethod
    def has_memory(self, memory_id: str) -> bool:
        """检查记忆是否存在"""
        pass

    @abstractmethod
    def clear(self):
        """清空所有记忆"""
        pass
    
    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """获取记忆统计信息"""
        pass

    def _generate_id(self) -> str:
        """生成记忆ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _calculate_importance(self, content: str, base_importance: float = 0.5) -> str:
        """计算记忆重要性"""

        importance = base_importance

        if len(content) > 100:
            importance += 0.1
        
        importance_keywords = ["重要", "关键", "必须", "注意", "警告", "错误"]
        if any(keyword in content for keyword in importance_keywords):
            importance += 0.2
        
        return max(0.0, min(1.0, importance))
    
    def __str__(self) -> str:
        stats = self.get_stats()
        return f"{self.__class__.__name__}(count={stats.get('count', 0)})"

    def __repr__(self) -> str:
        return self.__str__()
