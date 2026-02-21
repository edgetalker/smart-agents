# Tavily 搜索API库 - 返回格式化搜索内容
# SERPAPI 通用SERP数据抓取

import os 
from dotenv import load_dotenv

from ..tools.base import ToolRegistry

load_dotenv()

class SearchTool:
    """搜索工具"""

    def __init__(self):
        self.name = "my_advanced_search_tool"
        self.search_tools = []
        self._setup_search_resources()

    def _setup_search_resources(self):
        """初始化搜索源"""
        if os.getenv("TAVILY_API_KEY"):
            try:
                from tavily import tavilyClient
                self.travily_client = tavilyClient(api_key = os.getenv("TAVILY_API_KEY"))
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
    
    def search(self, query: str) -> str:
        """执行智能搜索"""
        print(f"🔍 开始执行搜索")

        for tool in self.search_tools:
            try:
                if tool == 'tavily':
                    result = self._search_with_tavily(query)
                    if result and "未找到" not in result:
                        return f"Tavily 搜索结果: \n\n{result}"
                    
                elif tool == 'serpapi':
                    result = self._search_with_serpapi(query)
                    if result and "未找到" not in result:
                        return f"SerpApi Google搜索结果: \n\n{result}"
            except Exception as e:
                print(f"⚠️ {tool} 搜索失败: {e}")
                continue
            return "❌ 所有搜索源都失败了，请检查网络连接和API密钥配置"

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
        import serpapi

        search = serpapi.GoogleSearch({
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

def create_advanced_search_registry():
    """创建包含高级搜索工具的注册表"""
    registry = ToolRegistry()

    # 创建搜索工具实例
    search_tool = SearchTool()

    # 注册搜索工具的方法作为函数
    registry.register_function(
        name="advanced_search",
        description="高级搜索工具，整合Tavily和SerpAPI多个搜索源，提供更全面的搜索结果",
        func=search_tool.search
    )

    return registry
