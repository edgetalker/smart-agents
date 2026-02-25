"""
记忆工具,具体实现由MemeoryManager实现
"""
from ..base import Tool, ToolParameter
from ...memory.base import MemoryConfig
from typing import Any
from datetime import datetime

class MemoryTool(Tool):
    """记忆工具

    为Agent提供记忆功能:
    - 添加记忆
    - 检索相关记忆
    - 获取记忆摘要
    - 管理记忆周期
    """

    def __init__(
        self,
        user_id: str = "default_user",
        memory_config: MemoryConfig = None,
        memory_types: list[str] = None,
        expandable: bool = False
    ):
        super().__init__(
            name="memory",
            description="记忆工具 - 可以存储和检索对话历史、知识和经验"
        )
        
        # 初始化记忆管理器
        self.memory_config = memory_config or MemoryConfig()
        self.memory_types = memory_types or ["working", "episodic", "semantic"]

        self.memory_manager = MemoryManger(
            config=self.memory_config,
            user_id=user_id,
            enable_working="working" in self.memory_types,
            enable_episodic="episodic" in self.memory_types,
            enable_senmatic="semantic" in self.memory_types,
            enable_perceptual="perceptual" in self.memory_types
        )

        # 会话状态
        self.current_session_id = None
        self.conversation_count = 0

    def run(self, parameters: dict[str, Any]) -> str:
        """
        执行工具 - 非展开模式

        Args:
            parameters (dict[str, Any]): 工具参数字典，必须包含action参数

        Returns:
            str: 执行结果字符串
        """
        if not self.validate_parameters(parameters):
            return "❌ 参数验证失败: 缺少必要的参数"
        
        action = parameters.get("action")

        # 根据action调用对应的方法，传入提取的参数
        if action == "add":
            return self._add_memory(
                content = parameters.get("content", ""),
                memory_type = parameters.get("memory_type", "working"),
                importance = parameters.get("importance", 0.5),
                file_path = parameters.get("file_path"),
                modality = parameters.get("modality")
            )
        elif action == "search":
            return self._search_memory(
                query = parameters.get("query"),
                limit=parameters.get("limit", 5),
                memory_type=parameters.get("memory_type"),
                min_importance=parameters.get("min_importance", 0.1)
            )
        elif action == "summary":
            return self._get_summary(limit=parameters.get("limit", 10))
        elif action == "statu":
            return self._get_stats()
        elif action == "update":
            return self._update_memory(
                memory_id=parameters.get("memory_id"),
                content=parameters.get("content"),
                importance=parameters.get("importance")
            )
        elif action == "remove":
            return self._remove_memory(memory_id=parameters.get("memory_id"))
        elif action == "forget":
            return self._forget(
                strategy=parameters.get("strategy", "importance_based"),
                threshold=parameters.get("threshold", 0.1),
                max_age_days=parameters.get("max_age_days", 30)
            )
        elif action == "consolidate":
            return self._consolidate(
                from_type=parameters.get("from_type", "working"),
                to_type=parameters.get("to_type", "episodic"),
                importance_threshold=parameters.get("importance_threshold", 0.7)
            )
        elif action == "clear_all":
            return self._clear_all()
        else:
            return f"❌ 不支持的操作: {action}"
        
    def get_parameters(self) -> list[ToolParameter]:
        """获取工具参数定义"""
        return [
            ToolParameter(
                name="action",
                type="string",
                description=(
                    "要执行的操作："
                    "add(添加记忆), search(搜索记忆), summary(获取摘要), stats(获取统计), "
                    "update(更新记忆), remove(删除记忆), forget(遗忘记忆), consolidate(整合记忆), clear_all(清空所有记忆)"
                ),
                required=True
            ),
            ToolParameter(name="content", type="string", description="记忆内容（add/update时可用；感知记忆可作描述）", required=False),
            ToolParameter(name="query", type="string", description="搜索查询（search时可用）", required=False),
            ToolParameter(name="memory_type", type="string", description="记忆类型：working, episodic, semantic, perceptual（默认：working）", required=False, default="working"),
            ToolParameter(name="importance", type="number", description="重要性分数，0.0-1.0（add/update时可用）", required=False),
            ToolParameter(name="limit", type="integer", description="搜索结果数量限制（默认：5）", required=False, default=5),
            ToolParameter(name="memory_id", type="string", description="目标记忆ID（update/remove时必需）", required=False),
            ToolParameter(name="file_path", type="string", description="感知记忆：本地文件路径（image/audio）", required=False),
            ToolParameter(name="modality", type="string", description="感知记忆模态：text/image/audio（不传则按扩展名推断）", required=False),
            ToolParameter(name="strategy", type="string", description="遗忘策略：importance_based/time_based/capacity_based（forget时可用）", required=False, default="importance_based"),
            ToolParameter(name="threshold", type="number", description="遗忘阈值（forget时可用，默认0.1）", required=False, default=0.1),
            ToolParameter(name="max_age_days", type="integer", description="最大保留天数（forget策略为time_based时可用）", required=False, default=30),
            ToolParameter(name="from_type", type="string", description="整合来源类型（consolidate时可用，默认working）", required=False, default="working"),
            ToolParameter(name="to_type", type="string", description="整合目标类型（consolidate时可用，默认episodic）", required=False, default="episodic"),
            ToolParameter(name="importance_threshold", type="number", description="整合重要性阈值（默认0.7）", required=False, default=0.7),
        ]

    def _add_memory(
            self,
            content: str = "",
            memory_type: str = "working",
            importance: float = 0.5,
            file_path: str = None,
            modality: str = None,
    ) -> str:
        """添加记忆

        Args:
            content (str, optional): 记忆内容
            memory_type (str, optional): 记忆类型
            importance (float, optional): 重要性分数
            file_path (str, optional): 感知记忆： 本地路径文件
            modality (str, optional): 感知记忆模态
        Returns:
            str: 执行结果
        """
        metadata = {}
        try:
            # 确保会话ID存在
            if self.current_session_id is None:
                self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 感知记忆文件支持
            if memory_type == "perceptual" and file_path:
                inferred = modality or self._infer_modality(file_path)
                metadata.setdefault("modality", inferred)
                metadata.setdefault("raw_data", file_path)

            # 添加对话信息到元数据
            metadata.update({
                "session_id": self.current_session_id,
                "timestamp": datetime.now().isoformat()
            })

            memory_id = self.memory_manager.add_memory(
                content = content,
                memory_type = memory_type,
                importance = importance,
                metadata = metadata,
                auto_classify = False 
            )

            return f"✅ 记忆已添加(ID: {memory_id[:8]}...)"
        
        except Exception as e:
            return f"❌ 添加记忆失败 {str(e)}"
        
    def _infer_modality(self, path: str) -> str:
        """根据扩展名推断模态（默认image/audio/text）"""
        try:
            ext = (path.rsplit('.', 1)[-1] or '').lower()
            if ext in {"png", "jpg", "jpeg", "bmp", "gif", "webp"}:
                return "image"
            if ext in {"mp3", "wav", "flac", "m4a", "ogg"}:
                return "audio"
            return "text"
        except Exception:
            return "text"
        
    def _search_memory(
        self,
        query: str,
        limit: int = 5,
        memory_type: str = None,
        min_importance: float = 0.1
    ) -> str:
        """
        搜索记忆

        Args:
            query (str): 搜索查询结果
            limit (int, optional): 搜索结果数量限制
            memory_type (str, optional): 限定记忆类型
            min_importance (float, optional): 最低重要性阈值
        Returns:
            str: 搜索结果
        """
        try:
            # 处理memory_type参数
            memory_type = [memory_type] if memory_type else None

            results = self.memory_manager.retrieve_memories(
                query = query,
                limit = limit,
                memory_type = memory_type,
                min_importance = min_importance
            )

            if not results:
                return f"❌ 未找到与 '{query}' 相关的记忆"
            
            # 格式化结果
            formatted_results = []
            formatted_results.append(f"🔍 找到 {len(results)} 条相关记忆:")

            for i, memory in enumerate(results, 1):
                memory_type_label = {
                    "working": "工作记忆",
                    "episodic": "情景记忆",
                    "semantic": "语义记忆",
                    "perceptual": "感知记忆"
                }.get(memory.memory_type, memory.memory_type)

                content_preview = memory.content[:80] + "..." if len(memory.content) > 80 else memory.content
                formatted_results.append(
                    f"{i}. [{memory_type_label}] {content_preview} (重要性: {memory.importance:.2f})"
                )
            
            return "\n".join(formatted_results)
        
        except Exception as e:
            return f"❌ 搜索记忆失败: {str(e)}"
        
    def _get_summary(self, limit: int = 10) -> str:
        """
        获取记忆摘要

        Args:
            limit (int, optional): 显示重要的记忆数量
        Returns:
            str: 记忆摘要
        """
        try:
            stats = self.memory_manager.get_memory_stats()

            summary_parts = [
                f"📊 记忆系统摘要",
                f"总记忆数: {stats['total_memories']}",
                f"当前会话: {self.current_session_id or '未开始'}",
                f"对话轮次: {self.conversation_count}"
            ]

            # 各类型记忆统计
            if stats['memories_by_type']:
                summary_parts.append("\n📋 记忆类型分布:")
                for memory_type, type_stats in stats['memories_by_type'].items():
                    count = type_stats.get('count', 0)
                    avg_importance = type_stats.get('avg_importance', 0)
                    type_label = {
                        "working": "工作记忆",
                        "episodic": "情景记忆",
                        "semantic": "语义记忆",
                        "perceptual": "感知记忆"
                    }.get(memory_type, memory_type)

                    summary_parts.append(f"  • {type_label}: {count} 条 (平均重要性: {avg_importance:.2f})")
            
            # 获取重要记忆 
            important_memories = self.memory_manager.retrieve_memories(
                query="",
                memory_types=None,  # 从所有类型中检索
                limit=limit * 3,  # 获取更多候选，然后去重
                min_importance=0.5  # 降低阈值以获取更多记忆
            )

            if important_memories:
                # 去重：使用记忆ID和内容双重去重
                seen_ids = set()
                seen_contents = set()
                unique_memories = []
                
                for memory in important_memories:
                    # 使用ID去重
                    if memory.id in seen_ids:
                        continue
                    
                    # 使用内容去重（防止相同内容的不同记忆）
                    content_key = memory.content.strip().lower()
                    if content_key in seen_contents:
                        continue
                    
                    seen_ids.add(memory.id)
                    seen_contents.add(content_key)
                    unique_memories.append(memory)
                
                # 按重要性排序
                unique_memories.sort(key=lambda x: x.importance, reverse=True)
                summary_parts.append(f"\n⭐ 重要记忆 (前{min(limit, len(unique_memories))}条):")

                for i, memory in enumerate(unique_memories[:limit], 1):
                    content_preview = memory.content[:60] + "..." if len(memory.content) > 60 else memory.content
                    summary_parts.append(f"  {i}. {content_preview} (重要性: {memory.importance:.2f})")

            return "\n".join(summary_parts)
        
        except Exception as e:
            return f"❌ 获取摘要失败: {str(e)}"

    def _get_stats(self) -> str:
        """
        获取统计信息

        Returns:
            str: 统计信息
        """
        try:
            stats = self.memory_manager.get_memory_stats()

            stats_info = [
                f"📉 记忆系统统计",
                f"总记忆数: {stats['total_memories']}",
                f"启用的记忆类型: {', '.join(stats['enabled_types'])}",
                f"会话ID: {self.current_session_id or '未开始'}",
                f"对话轮次: {self.conversation_count}"
            ]

            return "\n".join(stats_info)
        
        except Exception as e:
            return f"❌ 获取统计信息失败: {str(e)}"

    def _update_memory(self, memory_id: str, content: str = None, importance: float = None) -> str:
        """更新记忆

        Args:
            memory_id: 要更新的记忆ID
            content: 新的记忆内容
            importance: 新的重要性分数

        Returns:
            执行结果
        """
        try:
            metadata = {}
            success = self.memory_manager.update_memory(
                memory_id=memory_id,
                content=content,
                importance=importance,
                metadata=metadata or None
            )
            return "✅ 记忆已更新" if success else "⚠️ 未找到要更新的记忆"
        except Exception as e:
            return f"❌ 更新记忆失败: {str(e)}"

    def _remove_memory(self, memory_id: str) -> str:
        """删除记忆

        Args:
            memory_id: 要删除的记忆ID

        Returns:
            执行结果
        """
        try:
            success = self.memory_manager.remove_memory(memory_id)
            return "✅ 记忆已删除" if success else "⚠️ 未找到要删除的记忆"
        except Exception as e:
            return f"❌ 删除记忆失败: {str(e)}"
        
    def _forget(self, strategy: str = "importance_based", threshold: float = 0.1, max_age_days: int = 30) -> str:
        """遗忘记忆（支持多种策略）

        Args:
            strategy: 遗忘策略：importance_based(基于重要性)/time_based(基于时间)/capacity_based(基于容量)
            threshold: 遗忘阈值（importance_based时使用）
            max_age_days: 最大保留天数（time_based时使用）

        Returns:
            执行结果
        """
        try:
            count = self.memory_manager.forget_memories(
                strategy=strategy,
                threshold=threshold,
                max_age_days=max_age_days
            )
            return f"🧹 已遗忘 {count} 条记忆（策略: {strategy}）"
        except Exception as e:
            return f"❌ 遗忘记忆失败: {str(e)}"
    
    def _consolidate(self, from_type: str = "working", to_type: str = "episodic", importance_threshold: float = 0.7) -> str:
        """整合记忆（将重要的短期记忆提升为长期记忆）

        Args:
            from_type: 来源记忆类型
            to_type: 目标记忆类型
            importance_threshold: 整合的重要性阈值

        Returns:
            执行结果
        """
        try:
            count = self.memory_manager.consolidate_memories(
                from_type=from_type,
                to_type=to_type,
                importance_threshold=importance_threshold,
            )
            return f"🔄 已整合 {count} 条记忆为长期记忆（{from_type} → {to_type}，阈值={importance_threshold}）"
        except Exception as e:
            return f"❌ 整合记忆失败: {str(e)}"
        
    def _clear_all(self) -> str:
        """清空所有记忆

        Returns:
            执行结果
        """
        try:
            self.memory_manager.clear_all_memories()
            return "🧽 已清空所有记忆"
        except Exception as e:
            return f"❌ 清空记忆失败: {str(e)}"


