from fastapi import FastAPI, Depends, HTTPException

from app.auth import verify_token
from app.seed import EMPLOYEES, TICKETS

app = FastAPI(title="TechCorp Mock API")

@app.get("/api/tickets/{ticket_id}", dependencies=[Depends(verify_token)])
def get_ticket(ticket_id: str):

    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Not Found", "message": f"Ticket with ID '{ticket_id}' not found"},
        )
    return ticket

@app.get("/api/employees/{employee_id}/tickets", dependencies=[Depends(verify_token)])
def get_employee_tickets(employee_id: str):

    employee = EMPLOYEES.get(employee_id)
    if employee is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Not Found", "message": f"Employee with ID '{employee_id}' not found"},
        )

    tickets = []

    for ticket in TICKETS.values():
        if ticket["created_by"]["employee_id"] == employee_id:
            tickets.append({
                "ticket_id": ticket["ticket_id"],
                "title": ticket["title"],
                "status": ticket["status"],
                "priority": ticket["priority"],
                "created_at": ticket["created_at"],
                "updated_at": ticket["updated_at"],
            })

    return {"employee_id": employee_id, "tickets": tickets, "total": len(tickets)}


SICK_TOTAL = 30
PERSONAL_TOTAL = 5
PERSONAL_PAID = 3


def annual_entitlement(years: int) -> int:
    if years >= 7:
        return 18
    if years >= 4:
        return 14
    if years >= 2:
        return 10
    return 6


@app.get("/api/employees/{employee_id}/leave-balance", dependencies=[Depends(verify_token)])
def get_employee_leave_balance(employee_id: str):
    employee = EMPLOYEES.get(employee_id)
    if employee is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Not Found", "message": f"Employee with ID '{employee_id}' not found"},
        )

    annual_total = annual_entitlement(employee["years_of_service"]) + employee["carried_over"]
    personal_used = employee["personal_used"]

    return {
        "employee_id": employee_id,
        "employee_name": employee["employee_name"],
        "department": employee["department"],
        "position": employee["position"],
        "years_of_service": employee["years_of_service"],
        "leave_balance": {
            "annual_leave": {
                "total_entitlement": annual_total,
                "used": employee["annual_used"],
                "remaining": annual_total - employee["annual_used"],
                "carried_over_from_last_year": employee["carried_over"],
                "pending_approval": employee["pending_approval"],
            },
            "sick_leave": {
                "total_entitlement": SICK_TOTAL,
                "used": employee["sick_used"],
                "remaining": SICK_TOTAL - employee["sick_used"],
            },
            "personal_leave": {
                "total_entitlement": PERSONAL_TOTAL,
                "used": personal_used,
                "remaining": PERSONAL_TOTAL - personal_used,
                "paid_remaining": max(0, PERSONAL_PAID - personal_used),
                "unpaid_remaining": PERSONAL_TOTAL - PERSONAL_PAID - max(0, personal_used - PERSONAL_PAID),
            },
        },
        "upcoming_leaves": employee["upcoming_leaves"],
        "last_updated": "2025-07-10T09:00:00+07:00",
    }

