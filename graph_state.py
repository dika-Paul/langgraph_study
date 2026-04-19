from typing import TypedDict, Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph.message import add_messages


def add_tools(old: dict[str, BaseTool], new: BaseTool | dict[str, BaseTool]) -> dict[str, BaseTool]:
    if not isinstance(new, dict):
        new = {new.name: new}
    for name, tool in new.items():
        if name in old.keys():
            continue
        old[name] = tool
    return old


def add_queries(old: Any, new: Any) -> Any:
    if old is None:
        old = []
    if new is None:
        new = []
    if not isinstance(old, list):
        old = [old]
    if not isinstance(new, list):
        new = [new]
    return old + new


class GraphState(TypedDict):
    SYSTEM_MSG: SystemMessage
    messages: Annotated[list[BaseMessage], add_messages]
    chat_model: BaseChatModel
    tools: Annotated[dict[str, BaseTool], add_tools]
    queries: Annotated[list[str], add_queries]