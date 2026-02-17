from ..core.agent import Agent
from ..core.llm import SmartAgentLLM

class SimpleAgent(Agent):
    def __init__(self, name: str, llm: SmartAgentLLM, system_prompt: str):
        super().__init__(name, llm, system_prompt)

    def run(self, input_text: str) -> str:
        messages = []
        messages.append({"role": "system","content": self.system_prompt})
        messages.append({"role": "user", "content": input_text})
        
        response = self.llm.think(messages)

        return response

if __name__ == '__main__':
    llm = SmartAgentLLM()
    agent = SimpleAgent(
        name="AI助手",
        llm=llm,
        system_prompt="你是一个有用的AI助手"
    )
    response = agent.run("介绍一下你自己")
    print(response)