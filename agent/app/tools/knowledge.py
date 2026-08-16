from app.rag.retriever import search
from langchain_core.tools import tool

ALLOWED_LEAVE_FIELDS = {"employee_id", "leave_balance", "upcoming_leaves"}

@tool
def knowledge_search(query: str) -> str:
    """ค้นหาข้อมูลจากคู่มือพนักงาน TechCorp — นโยบายการลา, การเบิกค่าใช้จ่าย,
    IT security (password/VPN/AI tools), onboarding, สิ่งอำนวยความสะดวกในออฟฟิศ"""

    docs = search(query)

    if not docs:
        return "ไม่พบข้อมูลที่เกี่ยวข้องในคู่มือพนักงาน"

    return "\n\n---\n\n".join(f"[{d.metadata['source']}] {d.page_content}" for d in docs)