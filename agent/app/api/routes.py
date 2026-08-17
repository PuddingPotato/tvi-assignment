import json
from uuid import uuid4
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage

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


@router.post("/chat/stream")
def chat_stream(req: ChatRequest, request: Request):
    graph = request.app.state.graph
    thread_id = req.thread_id or str(uuid4())
    def event_stream():

        yield f"data: {json.dumps({'type': 'start', 'thread_id': thread_id})}\n\n"
        for msg, metadata in graph.stream(
            {
                "messages": [HumanMessage(content=req.message)],
                "employee_id": req.employee_id,
                "llm_calls": 0,
            },
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
        ):
            node = metadata.get("langgraph_node", "")
            if node in ("llm_call", "give_up"):
                if getattr(msg, "tool_calls", None) or getattr(msg, "tool_call_chunks", None):
                    continue
                content = getattr(msg, "content", "")

                if isinstance(content, list):
                    content = "".join(b.get("text", "") for b in content if isinstance(b, dict))

                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
            elif node == "guardrail":

                if isinstance(msg, AIMessage) and not isinstance(msg.content, list) and msg.content.startswith("ขออภัย"):
                    yield f"data: {json.dumps({'type': 'token', 'content': msg.content})}\n\n"
                    
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")