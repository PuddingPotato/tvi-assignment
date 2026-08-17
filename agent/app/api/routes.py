from uuid import uuid4

from fastapi import APIRouter, Request
from langchain_core.messages import AnyMessage, HumanMessage

from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()


def extract_text(message: AnyMessage) -> str:
    content = message.content
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return content


def tools_used_this_turn(messages: list[AnyMessage]) -> list[str]:

    start = 0
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            start = i
            break

    names = []
    for message in messages[start:]:
        for call in getattr(message, "tool_calls", None) or []:
            if call["name"] not in names:
                names.append(call["name"])
    return names


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    graph = request.app.state.graph
    thread_id = req.thread_id or str(uuid4())

    result = graph.invoke(
        {
            "messages": [HumanMessage(content=req.message)],
            "employee_id": req.employee_id,
            "llm_calls": 0,
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    return ChatResponse(
        thread_id=thread_id,
        answer=extract_text(result["messages"][-1]),
        tools_used=tools_used_this_turn(result["messages"]),
    )