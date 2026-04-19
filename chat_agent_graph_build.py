from typing import Literal, Any

from langchain_core.tools import BaseTool
from langgraph.graph.state import StateGraph
from langgraph.constants import START, END
from langchain_core.messages import AIMessage, SystemMessage

from graph_node import AddQueryFactory, ChatWithModelFactory, ToolCallFactory
from graph_state import GraphState


def add_query_route(state: GraphState) -> Literal['end', 'chat_with_tool']:
    query = state.get('queries')[-1]
    if query.lower() in ['quit', 'exit', 'q']:
        return 'end'
    return 'chat_with_tool'


def chat_with_tool_route(state: GraphState) -> Literal['tool_call', 'add_query', 'chat_with_tool']:
    ai_message = state.get('messages')[-1]
    if not isinstance(ai_message, AIMessage):
        return 'chat_with_tool'

    tool_calls = ai_message.tool_calls
    if tool_calls:
        return 'tool_call'

    print(f'{state.get('chat_model').get_name()}:\n'
          f'{ai_message.text}')
    return 'add_query'


def build_graph(add_query, chat_with_tool, tool_calling):
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node('add_query', add_query)
    graph_builder.add_node('chat_with_tool', chat_with_tool)
    graph_builder.add_node('tool_call', tool_calling)

    graph_builder.add_edge(START, 'add_query')
    graph_builder.add_conditional_edges(
        source='add_query',
        path=add_query_route,
        path_map={
            'end': END,
            'chat_with_tool': 'chat_with_tool',
        }
    )
    graph_builder.add_conditional_edges(
        source='chat_with_tool',
        path=chat_with_tool_route,
        path_map={
            'tool_call': 'tool_call',
            'add_query': 'add_query',
            'chat_with_tool': 'chat_with_tool',
        }
    )
    graph_builder.add_edge('tool_call', 'chat_with_tool')

    return  graph_builder.compile()




class Agent:
    _graph = build_graph(
        add_query=AddQueryFactory.sync_func(),
        chat_with_tool=ChatWithModelFactory.sync_func(),
        tool_calling=ToolCallFactory.sync_func(),
    )
    _agraph = build_graph(
        add_query=AddQueryFactory.async_func(),
        chat_with_tool=ChatWithModelFactory.async_func(),
        tool_calling=ToolCallFactory.async_func(),
    )

    def __init__(
            self,
            llm: Any,
            prompt: SystemMessage,
            tools: list[BaseTool]
    ):
        self._llm = llm
        self._prompt = prompt
        self._tools = {tool.name: tool for tool in tools}

    def run(self) -> None:
        self._graph.invoke({
            'SYSTEM_MSG': self._prompt,
            'chat_model': self._llm,
            'tools': self._tools,
        })

    async def arun(self):
        await self._agraph.ainvoke({
            'SYSTEM_MSG': self._prompt,
            'chat_model': self._llm,
            'tools': self._tools,
        })