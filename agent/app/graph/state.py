import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    employee_id: str
    route: Literal["helpdesk", "reject"]
    llm_calls: int
    total_llm_calls: Annotated[int, operator.add]
