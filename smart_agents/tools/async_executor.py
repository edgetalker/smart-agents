import asyncio
import concurrent.futures
from .registry import ToolRegistry
from typing import Any

class AsyncToolExecutor:
    """异步工具执行器"""

    def __init__(self, registry: ToolRegistry, max_workers: int = 4):
        self.registry = registry
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    async def execute_tool_async(self, tool_name: str, input_data: str) -> str:
        """异步执行单个工具"""
        loop = asyncio.get_event_loop()

        def _execute():
            return self.registry.execute_tool(tool_name, input_data)
        
        try:
            result = await loop.run_in_executor(self.executor, _execute)
            return result
        except Exception as e:
            return f"❌ 工具 '{tool_name}' 异步执行失败：{e}"
    
    async def execute_tools_parallel(self, tasks: list[dict[str, str]]) -> list[dict[str, Any]]:
        """
        并行执行多个工具

        Args:
            tasks (list[dict[str, str]]): 任务列表，每个任务包含 tool_name 和 input_data

        Returns:
            list[dict[str, Any]]: 执行结果列表
        """

        print(f"🚀 开始并行执行 {len(tasks)} 个任务")

        # 创建异步任务
        async_tasks = []
        task_info = []

        for i, task in enumerate(tasks):
            tool_name = task.get("tool_name")
            input_data = task.get("input_data", "")

            if not tool_name:
                print(f"⚠️ 任务 {i+1} 跳过：缺少 tool_name")
                task_info.append(i, task, None)
                continue

            print(f"创建任务 {i+1}: {tool_name}")
            async_task = self.execute_tool_async(tool_name, input_data)
            async_tasks.append(async_task)
            task_info.append((i, task, async_task))

        # 真正的并行执行：同时等待所有有效任务
        if async_tasks:
            print(f"⚡ 正在并行执行 {len(async_tasks)} 个任务...")
            task_results = await asyncio.gather(*async_tasks, return_exceptions=True)
        else:
            task_results = []

        # 构建结果列表，保持原始顺序
        results = []
        result_index = 0
        
        for i, task, async_task in task_info:
            if async_task is None:  # 无效任务
                results.append({
                    "task_id": i,
                    "tool_name": task.get("tool_name", "unknown"),
                    "input_data": task.get("input_data", ""),
                    "result": "❌ 任务无效：缺少 tool_name",
                    "status": "error"
                })
                print(f"❌ 任务 {i+1} 无效: 缺少 tool_name")
            else:
                # 获取对应的执行结果
                result = task_results[result_index]
                result_index += 1
                
                if isinstance(result, Exception):
                    results.append({
                        "task_id": i,
                        "tool_name": task["tool_name"],
                        "input_data": task["input_data"],
                        "result": str(result),
                        "status": "error"
                    })
                    print(f"❌ 任务 {i+1} 失败: {task['tool_name']} - {result}")
                else:
                    results.append({
                        "task_id": i,
                        "tool_name": task["tool_name"],
                        "input_data": task["input_data"],
                        "result": result,
                        "status": "success"
                    })
                    print(f"✅ 任务 {i+1} 完成: {task['tool_name']}")
    
        print(f"🎉 并行执行完成，成功: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
        return results
    

    async def execute_tools_batch(self, tool_name: str, input_list: list[str]) -> list[dict[str, Any]]:
        """
        批量执行同一个工具
        
        Args:
            tool_name: 工具名称
            input_list: 输入数据列表
            
        Returns:
            执行结果列表
        """
        tasks = [
            {"tool_name": tool_name, "input_data": input_data}
            for input_data in input_list
        ]
        return await self.execute_tools_parallel(tasks)

    def close(self):
        """关闭执行器"""
        self.executor.shutdown(wait=True)
        print("🔒 异步工具执行器已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数
async def run_parallel_tools(registry: ToolRegistry, tasks: list[dict[str, str]], max_workers: int = 4) -> list[dict[str, Any]]:
    """
    便捷函数：并行执行多个工具
    
    Args:
        registry: 工具注册表
        tasks: 任务列表
        max_workers: 最大工作线程数
        
    Returns:
        执行结果列表
    """
    async with AsyncToolExecutor(registry, max_workers) as executor:
        return await executor.execute_tools_parallel(tasks)


async def run_batch_tool(registry: ToolRegistry, tool_name: str, input_list: list[str], max_workers: int = 4) -> list[dict[str, Any]]:
    """
    便捷函数：批量执行同一个工具
    
    Args:
        registry: 工具注册表
        tool_name: 工具名称
        input_list: 输入数据列表
        max_workers: 最大工作线程数
        
    Returns:
        执行结果列表
    """
    async with AsyncToolExecutor(registry, max_workers) as executor:
        return await executor.execute_tools_batch(tool_name, input_list)

# 同步包装函数（为了兼容性）
def run_parallel_tools_sync(registry: ToolRegistry, tasks: list[dict[str, str]], max_workers: int = 4) -> list[dict[str, Any]]:
    """同步版本的并行工具执行"""
    return asyncio.run(run_parallel_tools(registry, tasks, max_workers))


def run_batch_tool_sync(registry: ToolRegistry, tool_name: str, input_list: list[str], max_workers: int = 4) -> list[dict[str, Any]]:
    """同步版本的批量工具执行"""
    return asyncio.run(run_batch_tool(registry, tool_name, input_list, max_workers))
