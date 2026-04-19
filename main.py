from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from agent_tool import IPLocationByGaoDe, SearchQueryByBoCha
from env_config import load_env_config
from chat_agent_graph_build import Agent



ENV_CONFIG = load_env_config()



def main():
    chat_model = init_chat_model(
        model='deepseek-v3.2',
        model_provider='openai',
        temperature=0.1,
        api_key=ENV_CONFIG['openai_api_key'],
        base_url=ENV_CONFIG['openai_base_url'],
        configurable_fields=['model', 'temperature']
    )
    prompt = SystemMessage(
        '''
        你是一个可以调用工具的智能 Agent。
    
        你的目标是优先正确解决用户问题，并在必要时使用工具补充能力。
    
        你必须严格遵守以下规则：
        - 优先判断是否真的需要调用工具
        - 当问题涉及实时信息、外部检索、IP 地理位置查询等内容时，优先调用工具
        - 当你已经可以直接回答用户问题时，不要额外调用工具
        - 只能调用系统已经绑定的工具，每次只调用一个
        - 调用工具时，参数必须严格符合工具定义，不要遗漏或编造字段
        - 不要伪造工具调用结果
        - 如果工具返回的信息不足以支撑结论，要明确说明
        - 最终回复必须基于已知事实或工具结果，保持简洁、准确、可执行
        
        你要使用的是 tool calling 模式：
        - 需要工具时，直接发起工具调用
        - 不需要工具时，直接输出最终答案
        - 不要把工具调用意图伪装成 JSON 文本返回给用户
        '''
    )
    tools = [IPLocationByGaoDe(), SearchQueryByBoCha()]

    agent = Agent(llm=chat_model, tools=tools, prompt=prompt)
    agent.run()


if __name__ == '__main__':
    main()