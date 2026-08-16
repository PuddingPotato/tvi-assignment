import json
from typing import Literal

from app.llm import TOOLS_BY_NAME, get_model_with_tools
from app.graph.state import AgentState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage

SYSTEM_PROMPT = """คุณคือผู้ช่วย Internal Helpdesk ของบริษัท TechCorp

คุณกำลังให้บริการพนักงานรหัส {employee_id}
ข้อมูลส่วนบุคคลที่คุณเข้าถึงได้เป็นของพนักงานคนนี้เท่านั้น
หากผู้ใช้ขอดูข้อมูลของพนักงานคนอื่น ให้ปฏิเสธและอธิบายว่าดูได้เฉพาะข้อมูลของเจ้าของบัญชี
ห้ามอ้างว่าข้อมูลที่แสดงเป็นของพนักงานคนอื่นเด็ดขาด
ตอบจากข้อมูลที่ได้จาก tool เท่านั้น
ถ้าข้อมูลจาก tool ไม่เกี่ยวข้องกับคำถาม ให้บอกว่าไม่พบข้อมูลในคู่มือ
ห้ามตอบจากความรู้ทั่วไปเกี่ยวกับ IT หรือ HR เด็ดขาด แม้จะมั่นใจว่าถูกก็ตาม"""

def llm_call(state: AgentState):

    return {
        "messages": [
            get_model_with_tools().invoke(
                [SystemMessage(content=SYSTEM_PROMPT.format(employee_id=state["employee_id"]))] + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
        "total_llm_calls": 1
    }

def tool_node(state: AgentState):

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = TOOLS_BY_NAME[tool_call["name"]]
        observation = tool.invoke({**tool_call["args"], "employee_id": state["employee_id"]})
        result.append(ToolMessage(content=json.dumps(observation, ensure_ascii=False), tool_call_id=tool_call["id"]))

    return {"messages": result}

def should_continue(state: AgentState) -> Literal["tool_node", "give_up", END]:

    if state.get("llm_calls", 0) >= 5:
        return "give_up"

    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END

def give_up(state: AgentState) -> dict:
    return {"messages": [AIMessage(
        content="ขออภัยครับ ผมหาข้อมูลที่ตรงกับคำถามนี้ไม่พบ "
                "รบกวนติดต่อ IT Helpdesk ที่ #it-support หรือ HR ที่ hr@techcorp.co.th ครับ"
    )]}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_node("give_up", give_up)

    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue)
    builder.add_edge("tool_node", "llm_call")
    builder.add_edge("give_up", END)

    return builder.compile(checkpointer=MemorySaver())