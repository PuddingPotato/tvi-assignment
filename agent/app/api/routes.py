from uuid import uuid4
from fastapi import APIRouter, Request

from app.api.schemas import ChatRequest, ChatResponse

from langchain_core.messages import HumanMessage

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):

    graph = request.app.state.graph
    thread_id = req.thread_id or str(uuid4())
    result = graph.invoke({
        "messages": [HumanMessage(content=req.message)],
        "employee_id": req.employee_id,
        "llm_calls": 0
    }, config={"configurable": {"thread_id": thread_id}})

    msg = result["messages"][-1]
    content = msg.content
    if isinstance(content, list):
        content = "".join(b.get("text", "") for b in content if isinstance(b, dict))

    return ChatResponse(answer=content, thread_id=thread_id)