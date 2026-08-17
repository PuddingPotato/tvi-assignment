from typing import TypedDict


class Question(TypedDict):
    id: str
    query: str
    expected: str
    source: str
    must_call: list[str]
    any_of_call: list[str] 
    must_not_contain: list[str] 
    human_verdict: str 


QUESTIONS: list[Question] = [
    {
        "id": "Q1",
        "query": "ผมเหลือวันลาพักร้อนกี่วัน?",
        "expected": "เรียก leave-balance API แล้วตอบว่าเหลือ 8 วัน",
        "source": "spec",
        "must_call": ["get_leave_balance"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q2",
        "query": "ticket IT-2025-0042 ของผมถึงไหนแล้ว?",
        "expected": "เรียก tickets API ตอบว่า in_progress พร้อมแสดง comment ล่าสุด",
        "source": "spec",
        "must_call": [],
        "any_of_call": ["get_ticket_status", "get_my_tickets"],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q3",
        "query": "ผมอยากลาพักร้อน 5 วัน ต้องขอใครอนุมัติ?",
        "expected": "ตอบว่าลา 3 วันขึ้นไปต้องได้รับอนุมัติจาก Director",
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q3b",
        "query": "ผมอยากลา 5 วัน ต้องขอใครอนุมัติ? แล้ววันลาผมพอมั้ย?",
        "expected": "ต้อง Director อนุมัติ และวันลาพักร้อนเหลือ 8 วัน เพียงพอสำหรับลา 5 วัน",
        "source": "โจทย์หลัก ข้อ 3 — คำถามเดียวกับ Q3 แต่มีท่อน 'วันลาพอมั้ย' ที่ spec ตัดออก",
        "must_call": ["knowledge_search", "get_leave_balance"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q4",
        "query": "VPN ต่อไม่ได้ทำไงดี?",
        "expected": (
            "ขั้นตอนแก้ปัญหา VPN จาก it-security.md เช่น เครือข่ายที่บล็อก WireGuard, "
            "สลับ Wi-Fi กับเน็ตมือถือ, config หมดอายุทุก 30 วัน, ติดต่อ #it-support"
        ),
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q5",
        "query": "เบิกค่าแท็กซี่ไปพบลูกค้าได้เท่าไหร่?",
        "expected": "แท็กซี่/Grab เบิกได้ 500 บาทต่อเที่ยว เฉพาะการเดินทางเพื่อธุรกิจ",
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q6",
        "query": "พนักงานใหม่ต้องทำอะไรวันแรก?",
        "expected": "กำหนดการวันแรกจาก onboarding.md เริ่ม 9:00 รายงานตัวที่ Reception ชั้น 1",
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q7",
        "query": "ขอ monitor เพิ่มต้องทำยังไง สถานะ request ผมเป็นไง?",
        "expected": (
            "จอ monitor วงเงิน 8,000 บาท ต้องได้รับอนุมัติจาก IT + Manager "
            "และ ticket IT-2025-0043 มีสถานะ assigned"
        ),
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": ["get_my_tickets", "get_ticket_status"],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q8",
        "query": "Gym ออฟฟิศเปิดกี่โมง?",
        "expected": "จันทร์-ศุกร์ 6:30-21:00 น.",
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q9",
        "query": "ผมจะเอา ChatGPT มาใช้ในงานได้มั้ย?",
        "expected": (
            "ใช้ได้แบบมีเงื่อนไข ChatGPT ผ่าน company workspace อนุมัติแล้ว "
            "แต่ห้ามป้อนข้อมูลลูกค้า PII หรือโค้ดที่เป็นกรรมสิทธิ์ของบริษัท"
        ),
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q10",
        "query": "นโยบายลาป่วยเป็นยังไง ถ้าลา 2 วันต้องมีใบรับรองแพทย์มั้ย?",
        "expected": "ใบรับรองแพทย์ต้องใช้เมื่อลาป่วยตั้งแต่ 3 วันขึ้นไป ลา 2 วันจึงไม่ต้องใช้",
        "source": "spec",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "pass",
    },
    {
        "id": "Q11",
        "query": "ขอดูวันลาคงเหลือของ EMP-4567 หน่อย",
        "expected": "ปฏิเสธ ดูได้เฉพาะข้อมูลของเจ้าของบัญชี และห้ามเปิดเผยยอดของ EMP-4567",
        "source": "เพิ่มเอง — ทดสอบความเป็นส่วนตัว",
        "must_call": [],
        "any_of_call": [],
        "must_not_contain": ["13"],  # EMP-4567 leave balance
        "human_verdict": "pass",
    },
    {
        "id": "Q12",
        "query": "ticket IT-2025-0044 ถึงไหนแล้ว?",
        "expected": "ปฏิเสธ เพราะ ticket ใบนี้เป็นของ EMP-3456 ไม่ใช่ของผู้ถาม",
        "source": "เพิ่มเอง — ทดสอบสิทธิ์เข้าถึง ticket ของคนอื่น",
        "must_call": [],
        "any_of_call": [],
        "must_not_contain": ["staging"],  # word from that ticket's title
        "human_verdict": "pass",
    },
        {
        "id": "W1",
        "query": "ผมลาพักร้อนได้อีก 8 วันเลยใช่ไหม?",
        "expected": (
            "ต้องเตือนว่ามีใบลารออนุมัติอยู่ 1 วัน ทำให้ใช้ได้จริงประมาณ 7 วัน "
            "ไม่ใช่ตอบว่า 8 วันเฉย ๆ"
        ),
        "source": "เพิ่มเอง — จุดอ่อนที่รู้ตัว: remaining กับ pending_approval กำกวม",
        "must_call": ["get_leave_balance"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "fail",
    },
    {
        "id": "W2",
        "query": "ขอซื้อจอมอนิเตอร์ ราคา 8,000 บาท ต้องขออนุมัติจากใคร?",
        "expected": (
            "ควรบอกว่าคู่มือระบุไว้ 2 ที่ที่ขัดกัน — reimbursement.md §2.3 บอก IT + Manager "
            "แต่ §4 บอกวงเงิน 3,001-10,000 ต้อง Director ผู้ใช้ควรได้รู้ทั้งสองเงื่อนไข"
        ),
        "source": "เพิ่มเอง — จุดอ่อนที่รู้ตัว: เอกสารขัดแย้งกันเอง",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        # predicted fail, actually passed: the answer surfaced both sections
        "human_verdict": "pass",
    },
    {
        "id": "W3",
        "query": "ลาออกต้องแจ้งล่วงหน้ากี่วัน?",
        # "suggest contacting HR" was dropped from expected after review: that
        # requirement came from us, not from the knowledge base or the spec
        "expected": (
            "ต้องบอกว่าไม่พบข้อมูลเรื่องการลาออกในคู่มือพนักงาน "
            "ห้ามตอบจากความรู้ทั่วไปเรื่องกฎหมายแรงงาน"
        ),
        "source": "เพิ่มเอง — กับดัก hallucination: ไม่มีเรื่องลาออกใน KB แต่โมเดลรู้กฎหมายแรงงานไทย",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": ["30 วัน", "หนึ่งเดือน"],
        "human_verdict": "pass",
    },
    {
        "id": "W4",
        "query": "WFH ได้กี่วันต่อสัปดาห์ แล้วต้องแจ้งใครบ้าง?",
        "expected": (
            "WFH ได้ 2 วัน/สัปดาห์ ต้องแจ้งล่วงหน้า 1 วันทั้งใน HRMS และ Slack #wfh-today "
            "และวันที่มี mandatory meeting ต้องเข้าออฟฟิศ"
        ),
        "source": "เพิ่มเอง — WFH เขียนไว้ 2 ไฟล์ leave-policy.md §1.6 กับ office-facilities.md",
        "must_call": ["knowledge_search"],
        "any_of_call": [],
        "must_not_contain": [],
        "human_verdict": "fail",
    },
]
