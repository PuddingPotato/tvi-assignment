import os
import httpx

BASE_URL = os.getenv("MOCK_API_URL", "http://localhost:8080/api")
TOKEN = os.getenv("MOCK_API_TOKEN", "techcorp-mock-token-2025")
TIMEOUT = 5.0

def _get(path: str) -> dict:

    try:
        r = httpx.get(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=TIMEOUT,
        )
    except httpx.RequestError:
        return {"error": "ระบบ HR/IT ไม่ตอบสนอง กรุณาลองใหม่ภายหลัง"}

    if r.status_code == 404:
        return {"error": "ไม่พบข้อมูลที่ค้นหาในระบบ"}
    if r.status_code != 200:
        return {"error": f"ระบบตอบกลับผิดปกติ (HTTP {r.status_code})"}

    return r.json()

def get_leave_balance(employee_id: str) -> dict:
    return _get(f"/employees/{employee_id}/leave-balance")

def get_ticket(ticket_id: str) -> dict:
    return _get(f"/tickets/{ticket_id}")

def get_employee_tickets(employee_id: str) -> dict:
    return _get(f"/employees/{employee_id}/tickets")