### 1.实现openai格式接口
### 2.兼容其他格式
import os
from typing import Optional, List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SmartAgentLLM:
    def __init__(self, model: Optional[str] = None, apiKey: Optional[str] = None, baseUrl: Optional[str] = None, timeout: Optional[int] = None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl, timeout]):
            raise ValueError("模型参数未在.env文件中定义")
        
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl,timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float= 0) -> str:
        try:
            # 开启流式输出
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            full_response = ""
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            return full_response
        
        except Exception as e:
            print(f"调用LLM发生错误{e}")

if __name__ == '__main__':
    llm = SmartAgentLLM()
    messages = [{"role": "user" , "content": "介绍一下你自己"}]
    llm.think(messages=messages)