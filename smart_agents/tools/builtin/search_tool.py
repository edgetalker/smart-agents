# Tavily 搜索API库 - 返回格式化搜索内容
# SERPAPI 通用SERP数据抓取

import os 
from dotenv import load_dotenv
from typing import Any
from ..base import Tool

load_dotenv()

class SearchTool(Tool):
    """内置搜索工具"""
    def __init__(self):
        super().__init__(
            name="my_advanced_search_tool",
            description="多源搜索工具"
        )
        self.search_tools = []
        self._setup_search_resources()
    
    def run(self, parameters: dict[str, Any]) -> str:
        """执行智能搜索"""
        print(f"🔍 开始执行搜索")
        input = parameters.get("input")

        for tool in self.search_tools:
            try:
                if tool == 'tavily':
                    result = self._search_with_tavily(input)
                    if result and "未找到" not in result:
                        return f"Tavily 搜索结果: \n\n{result}"
                    
                elif tool == 'serpapi':
                    result = self._search_with_serpapi(input)
                    if result and "未找到" not in result:
                        return f"SerpApi Google搜索结果: \n\n{result}"
            except Exception as e:
                print(f"⚠️ {tool} 搜索失败: {e}")
                continue

        return "❌ 所有搜索源都失败了，请检查网络连接和API密钥配置"
        
    def get_parameters(self):
        """获取工作参数定义"""
        from ..base import ToolParameter
        return [
            ToolParameter(
                name = "input",
                type = "string",
                description = "需要查询的信息",
                required = True
            )
        ]

    def _setup_search_resources(self):
        """初始化搜索源"""
        if os.getenv("TAVILY_API_KEY"):
            try:
                from tavily import TavilyClient
                self.tavily_client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
                self.search_tools.append("tavily")
                print(f"✅ 已启用travily搜索源")
            except ImportError:
                print(f"⚠️ tavily 库未安装")

        if os.getenv("SERPAPI_API_KEY"):
            try:
                import serpapi    
                self.search_tools.append("serpapi")
                print(f"✅ 已启用serpapi搜索源")
            except ImportError:
                print(f"⚠️ serpapi 库未安装")

        if self.search_tools:
            print(f"🔧 可用搜索源：{', '.join(self.search_tools)}")
        else:
            print("⚠️ 没有可用的搜索源，请配置API密钥")

    def _search_with_tavily(self, query: str) -> str:
        """使用Tavily搜索"""
        response = self.tavily_client.search(query=query, max_results=3)

        if response.get('answer'):
            result = f"💡 AI直接答案:{response['answer']}\n\n"
        else:
            result = ""

        result += "🔗 相关结果:\n"
        for i, item in enumerate(response.get('results', [])[:3], 1):
            result += f"[{i}] {item.get('title', '')}\n"
            result += f"    {item.get('content', '')[:150]}...\n\n"

        return result

    def _search_with_serpapi(self, query: str) -> str:
        """使用SerpApi搜索"""
        from serpapi import GoogleSearch

        search = GoogleSearch({
            "q": query,
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "num": 3
        })

        results = search.get_dict()

        result = "🔗 Google搜索结果:\n"
        if "organic_results" in results:
            for i, res in enumerate(results["organic_results"][:3], 1):
                result += f"[{i}] {res.get('title', '')}\n"
                result += f"    {res.get('snippet', '')}\n\n"

        return result


# 便携函数
def search(query: str) -> str:
    tool = SearchTool()
    return tool.run({"input": query, "backend": backend})  # type: ignore[return-value]
