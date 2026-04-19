from typing import Any
from abc import ABC, abstractmethod

import asyncio
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage, ToolCall
from langchain_core.tools import BaseTool

from graph_state import GraphState
from env_config import load_env_config



ENV_CONFIG = load_env_config()



class BaseGraphNodeFactory(ABC):
    @staticmethod
    @abstractmethod
    def return_dict(content: Any) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def sync_func():
        pass

    @staticmethod
    @abstractmethod
    def async_func():
        pass



class AddQueryFactory(BaseGraphNodeFactory):
    @staticmethod
    def return_dict(content: Any) -> dict:
        return {
            'queries': content,
            'messages': HumanMessage(content=content)
        }


    @staticmethod
    def sync_func():

        def add_query(graph_state: GraphState):
            queries = graph_state.get('queries', [])
            print(f'当前是第{len(queries) + 1}轮对话')
            query = input('user: ')
            while query == '':
                query = input('user: ')
            return AddQueryFactory.return_dict(query)

        return add_query

    @staticmethod
    def async_func():

        async def add_query(graph_state: GraphState):
            queries = graph_state.get('queries', [])
            print(f'当前是第{len(queries) + 1}轮对话')
            query = await asyncio.to_thread(input, 'user: ')
            while query == '':
                query = await asyncio.to_thread(input, 'user: ')
            return AddQueryFactory.return_dict(query)

        return add_query



class ChatWithModelFactory(BaseGraphNodeFactory):
    @staticmethod
    def get_messages(graph_state: GraphState) -> list[BaseMessage]:
        return [graph_state.get('SYSTEM_MSG', '')] + graph_state.get('messages', [])

    @staticmethod
    def get_chat_model(graph_state: GraphState) -> Any:
        chat_model = graph_state.get('chat_model', None)
        if not chat_model:
            raise ValueError('无效的大模型配置')
        tools = [tool for tool in graph_state.get('tools', {}).values()]
        chat_model_with_tools = chat_model.bind_tools(tools)
        return chat_model_with_tools

    @staticmethod
    def return_dict(content: Any) -> dict:
        return {
            'messages': content,
        }


    @staticmethod
    def sync_func():
        def chat_with_tool(graph_state: GraphState):
            messages = ChatWithModelFactory.get_messages(graph_state)
            chat_model_with_tools = ChatWithModelFactory.get_chat_model(graph_state)

            resp = chat_model_with_tools.invoke(messages)

            return ChatWithModelFactory.return_dict(resp)

        return chat_with_tool

    @staticmethod
    def async_func():
        async def achat_with_tool(graph_state: GraphState):
            messages = ChatWithModelFactory.get_messages(graph_state)
            chat_model_with_tools = ChatWithModelFactory.get_chat_model(graph_state)

            resp = await chat_model_with_tools.ainvoke(messages)

            return ChatWithModelFactory.return_dict(resp)

        return achat_with_tool



class ToolCallFactory(BaseGraphNodeFactory):
    @staticmethod
    def get_tool_calls(graph_state: GraphState) -> list[ToolCall]:
        ai_message = graph_state.get('messages')[-1]
        if not isinstance(ai_message, AIMessage):
            raise ValueError(f"期望类型 AIMessage, 实际类型 {type(ai_message)}")

        tool_calls = ai_message.tool_calls
        return tool_calls

    @staticmethod
    def get_tool(graph_state: GraphState, tool_call: ToolCall) -> tuple[BaseTool | None, dict[str, Any], str | None]:
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('args')
        tool_id = tool_call.get('id')

        tool = graph_state.get('tools', {}).get(tool_name, None)

        return tool, tool_args, tool_id



    @staticmethod
    def return_dict(content: Any) -> dict:
        return {
            'messages': content,
        }


    @staticmethod
    def sync_func():
        def tool_calling(graph_state: GraphState):
            tool_calls = ToolCallFactory.get_tool_calls(graph_state)

            if not tool_calls:
                return {}

            tool_messages = []
            for tool_call in tool_calls:
                tool, tool_args, tool_id = ToolCallFactory.get_tool(graph_state, tool_call)
                if not tool:
                    continue

                resp = tool.invoke(tool_args)
                tool_messages.append(
                    ToolMessage(
                        content=resp,
                        tool_call_id=tool_id,
                    )
                )

            return ToolCallFactory.return_dict(tool_messages)

        return tool_calling

    @staticmethod
    def async_func():
        async def tool_calling(graph_state: GraphState):
            tool_calls = ToolCallFactory.get_tool_calls(graph_state)

            if not tool_calls:
                return {}

            semaphore = asyncio.Semaphore(5)

            async def build_tool_calling(tool_call: ToolCall):
                tool, tool_args, tool_id = ToolCallFactory.get_tool(graph_state, tool_call)
                if not tool:
                    return None
                async with semaphore:
                    try:
                        resp = tool.invoke(tool_args)
                    except Exception as e:
                        resp = f'捕获到异常{e}'
                    return ToolMessage(content=resp, tool_call_id=tool_id)

            result = await asyncio.gather(
                *(build_tool_calling(tool) for tool in tool_calls),
            )

            tool_messages = [tool_message for tool_message in result if tool_message]
            return ToolCallFactory.return_dict(tool_messages)

        return tool_calling


