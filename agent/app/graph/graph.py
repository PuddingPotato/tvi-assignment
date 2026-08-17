import json
import re
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

# Patterns that indicate prompt injection attempts.
# Deliberately kept simple and fast — no LLM call needed.
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)", re.I),
    re.compile(r"forget\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?|rules?)", re.I),
    re.compile(r"(reveal|show|print|tell\s+me|repeat|output)\s+(your\s+)?(system\s+prompt|instructions?|rules?)", re.I),
    re.compile(r"you\s+are\s+now\s+", re.I),
    re.compile(r"(act|pretend|behave)\s+as\s+(if\s+you\s+(are|were)|a\s+)", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above|your)", re.I),
    re.compile(r"(dump|export|list)\s+(all\s+)?(employee|staff|user)\s+(data|records?|info)", re.I),
]

_INJECTION_REFUSAL = (
    "ขออภัยครับ ผมไม่สามารถดำเนินการตามคำขอนี้ได้ "
    "ผมเป็นผู้ช่วย Internal Helpdesk ของ TechCorp ช่วยได้เฉพาะเรื่อง "
    "นโยบาย HR, IT support, และการเบิกค่าใช้จ่ายครับ"
)


def _is_injection(text: str) -> bool:
    """Return True if the message matches any known injection pattern."""
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def guardrail(state: AgentState) -> dict:
    """Fast pre-LLM check: reject obvious injection attempts without calling the LLM."""
    last_human = next(
        (m for m in reversed(state["messages"]) if getattr(m, "type", None) == "human"),
        None,
    )
    if last_human and _is_injection(last_human.content):
        return {"messages": [AIMessage(content=_INJECTION_REFUSAL)], "route": "reject"}
    return {"route": "helpdesk"}


def route_after_guardrail(state: AgentState) -> Literal["llm_call", END]:
    if state.get("route") == "reject":
        return END
    return "llm_call"


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
    builder.add_node("guardrail", guardrail)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_node("give_up", give_up)

    builder.add_edge(START, "guardrail")
    builder.add_conditional_edges("guardrail", route_after_guardrail)
    builder.add_conditional_edges("llm_call", should_continue)
    builder.add_edge("tool_node", "llm_call")
    builder.add_edge("give_up", END)

    return builder.compile(checkpointer=MemorySaver())