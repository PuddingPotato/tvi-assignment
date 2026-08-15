import json
from typing import Literal

from app.llm import TOOLS_BY_NAME, get_model_with_tools
from app.graph.state import AgentState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, ToolMessage

def llm_call(state: AgentState):

    return {
        "messages": [
            get_model_with_tools().invoke(
                [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
        "total_llm_calls": 1
    }

def tool_node(state: AgentState):

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = TOOLS_BY_NAME[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=json.dumps(observation, ensure_ascii=False), tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: AgentState) -> Literal["tool_node", END]:

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"
    else:
        return END


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)

    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue)
    builder.add_edge("tool_node", "llm_call")

    return builder.compile(checkpointer=MemorySaver())