from langchain_core.tools import tool

ALLOWED_LEAVE_FIELDS = {"leave_balance", "upcoming_leaves"}

@tool
def knowledge_search(query: str) -> str:
    """ค้นหาข้อมูลจากคู่มือพนักงาน TechCorp — นโยบายการลา, การเบิกค่าใช้จ่าย,
    IT security (password/VPN/AI tools), onboarding, สิ่งอำนวยความสะดวกในออฟฟิศ"""

    return "ลาพักร้อนตั้งแต่ 3 วันขึ้นไปติดต่อกัน ต้องได้รับอนุมัติจาก Director ขึ้นไป"

@tool
def get_leave_balance() -> dict:
    """ดูวันลาคงเหลือของพนักงานที่กำลังสนทนาอยู่ (ลาพักร้อน/ลาป่วย/ลากิจ)"""

    data = {
        "employee_id": "EMP-1234",
        "employee_name": "สมชาย วงศ์สวัสดิ์",
        "department": "Engineering",
        "position": "Senior Software Engineer",
        "leave_balance": {
            "annual_leave": {"total_entitlement": 12, "used": 4, "remaining": 8, "pending_approval": 1},
            "sick_leave": {"total_entitlement": 30, "used": 2, "remaining": 28},
        },
    }
    
    return {k: v for k, v in data.items() if k in ALLOWED_LEAVE_FIELDS}