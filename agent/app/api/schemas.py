from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    employee_id: str = "EMP-1234"
    thread_id: str | None = None

class ChatResponse(BaseModel):
    thread_id: str
    answer: str