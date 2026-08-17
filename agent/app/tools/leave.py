from typing import Annotated

from app.clients import mock_api
from langchain_core.tools import tool, InjectedToolArg

ALLOWED_LEAVE_FIELDS = {"employee_id", "leave_balance", "upcoming_leaves"}

@tool
def get_leave_balance(employee_id: Annotated[str, InjectedToolArg]) -> dict:
    """ดูวันลาคงเหลือของพนักงานที่กำลังสนทนาอยู่ (ลาพักร้อน/ลาป่วย/ลากิจ)"""

    data = mock_api.get_leave_balance(employee_id)
    if "error" in data:
        return data

    return {k: v for k, v in data.items() if k in ALLOWED_LEAVE_FIELDS}

@tool
def get_ticket_status(
    ticket_id: str,                                   # LLM ใส่
    employee_id: Annotated[str, InjectedToolArg],     # โค้ดใส่
) -> dict:
    """เช็คสถานะ IT ticket จากหมายเลข (เช่น IT-2025-0042)"""

    data = mock_api.get_ticket(ticket_id)
    if "error" in data:
        return data

    if data["created_by"]["employee_id"] != employee_id:
        return {
            "error": (
                f"ticket {ticket_id} ไม่ใช่ ticket ที่ผู้ถามเป็นผู้แจ้ง "
                "ให้ปฏิเสธโดยระบุชัดเจนว่า ticket นี้ไม่ใช่ของเขา ไม่ต้องใช้คำว่า 'หาก'"
            )
        }

    return data

@tool
def get_my_tickets(employee_id: Annotated[str, InjectedToolArg]) -> dict:
    """ดูรายการ IT ticket ทั้งหมดที่พนักงานคนนี้เป็นผู้แจ้ง"""

    return mock_api.get_employee_tickets(employee_id)