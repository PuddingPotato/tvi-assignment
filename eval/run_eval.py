import os
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from questions import QUESTIONS, Question  # noqa: E402

AGENT_URL = os.getenv("AGENT_URL", "http://localhost:8000")
EMPLOYEE_ID = "EMP-1234"
TIMEOUT = 120.0
RESULTS_PATH = Path(__file__).parent / "results.md"

# Prevent the model's rate limit
PAUSE_SECONDS = float(os.getenv("EVAL_PAUSE", "16"))
RETRY_SECONDS = 65.0

# ideally a different model from the one being tested
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-3.5-flash")
JUDGE_PROVIDER = os.getenv("LLM_PROVIDER", "google_genai")

JUDGE_PROMPT = """คุณคือผู้ตรวจคำตอบของระบบ Helpdesk

ตัดสินว่าคำตอบจริงให้ข้อมูลตรงกับคำตอบที่ควรได้หรือไม่

เกณฑ์
- ดูที่ข้อเท็จจริงและตัวเลข ไม่ต้องสนใจสำนวนหรือการจัดรูปแบบ
- ถ้าคำตอบจริงมีข้อมูลครบตามที่ควรได้ ให้ผ่าน แม้จะใช้คำต่างกันหรือมีรายละเอียดเพิ่ม
- ถ้าตัวเลขผิด ชื่อผู้อนุมัติผิด หรือขาดข้อมูลสำคัญที่ระบุไว้ ให้ไม่ผ่าน
- ถ้าคำตอบที่ควรได้บอกให้ปฏิเสธ ต้องปฏิเสธจริงจึงจะผ่าน

คำถาม: {query}

คำตอบที่ควรได้: {expected}

คำตอบจริง:
{answer}"""


class Verdict(BaseModel):
    passed: bool = Field(description="คำตอบจริงตรงกับคำตอบที่ควรได้หรือไม่")
    reason: str = Field(description="เหตุผลสั้น ๆ ไม่เกิน 2 ประโยค")


def ask(query: str) -> tuple[str, list[str]]:
    """POST /chat with a fresh thread_id, retry once past the rate limit."""
    payload = {
        "message": query,
        "employee_id": EMPLOYEE_ID,
        "thread_id": f"eval-{uuid4()}",
    }
    for attempt in (1, 2):
        r = httpx.post(f"{AGENT_URL}/chat", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            return data["answer"], data.get("tools_used", [])
        if attempt == 1:
            print(f"    ได้ {r.status_code} รอ {RETRY_SECONDS:.0f} วินาทีแล้วลองใหม่")
            time.sleep(RETRY_SECONDS)
    r.raise_for_status()
    raise RuntimeError("unreachable")


def check_structural(question: Question, answer: str, tools_used: list[str]) -> tuple[bool, str]:
    """Layer 1: behaviour, not wording."""
    missing = [t for t in question["must_call"] if t not in tools_used]
    if missing:
        return False, f"ไม่ได้เรียก tool ที่ต้องเรียก: {', '.join(missing)}"

    group = question["any_of_call"]
    if group and not any(t in tools_used for t in group):
        return False, f"ไม่ได้เรียก tool ใดเลยจาก: {', '.join(group)}"

    leaked = [w for w in question["must_not_contain"] if w.lower() in answer.lower()]
    if leaked:
        return False, f"ข้อมูลที่ห้ามเปิดเผยหลุดออกมา: {', '.join(leaked)}"

    return True, ""


def make_judge():
    model = init_chat_model(model=JUDGE_MODEL, model_provider=JUDGE_PROVIDER)
    return model.with_structured_output(Verdict)


def judge_answer(judge, question: Question, answer: str) -> Verdict:
    """Layer 2: free-text content."""
    prompt = JUDGE_PROMPT.format(
        query=question["query"],
        expected=question["expected"],
        answer=answer.strip(),
    )
    for attempt in (1, 2):
        try:
            return judge.invoke(prompt)
        except Exception:  # 429
            if attempt == 2:
                raise
            print(f"    judge พลาด รอ {RETRY_SECONDS:.0f} วินาทีแล้วลองใหม่")
            time.sleep(RETRY_SECONDS)
    raise RuntimeError("unreachable")


def one_line(text: str, limit: int = 110) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[:limit] + "…"


def main() -> int:
    try:
        httpx.get(f"{AGENT_URL}/docs", timeout=5.0)
    except httpx.RequestError:
        print(f"ต่อ {AGENT_URL} ไม่ได้ — รัน docker compose up ก่อน")
        return 2

    judge = make_judge()
    rows = []

    for index, question in enumerate(QUESTIONS):
        if index:
            time.sleep(PAUSE_SECONDS)

        print(f"[{question['id']}] {question['query']}")
        answer, tools_used = ask(question["query"])

        structural_ok, structural_reason = check_structural(question, answer, tools_used)
        verdict = judge_answer(judge, question, answer)
        passed = structural_ok and verdict.passed
        agrees = ("pass" if passed else "fail") == question["human_verdict"]

        rows.append(
            {
                "question": question,
                "answer": answer,
                "tools_used": tools_used,
                "structural_ok": structural_ok,
                "judge": verdict,
                "passed": passed,
                "reason": structural_reason or verdict.reason,
                "agrees_with_human": agrees,
            }
        )

        mark = "PASS" if passed else "FAIL"
        flag = "" if agrees else "   <-- ต่างจากที่คนตัดสิน"
        print(f"    {mark}  tools={tools_used or '[]'}{flag}")
        print(f"    {one_line(answer)}")
        if not passed:
            print(f"    เหตุผล: {rows[-1]['reason']}")
        print()

    write_results(rows)

    total = len(rows)
    passed_count = sum(1 for r in rows if r["passed"])
    agree_count = sum(1 for r in rows if r["agrees_with_human"])

    print(f"ผ่าน {passed_count}/{total}")
    print(f"judge ตัดสินตรงกับคน {agree_count}/{total}")
    print(f"เขียนผลลงที่ {RESULTS_PATH}")

    return 0 if agree_count == total else 1


def write_results(rows) -> None:
    total = len(rows)
    passed_count = sum(1 for r in rows if r["passed"])
    agree_count = sum(1 for r in rows if r["agrees_with_human"])

    lines = [
        "# ผลการประเมิน (รันอัตโนมัติ)",
        "",
        f"ยิงผ่าน `{AGENT_URL}/chat` ในนามพนักงาน `{EMPLOYEE_ID}`",
        "",
        "ตัดสิน 2 ชั้น — structural (เรียก tool ถูกตัวไหม / ข้อมูลรั่วไหม) "
        f"และ LLM judge (`{JUDGE_MODEL}`) ต้องผ่านทั้งคู่จึงนับว่าผ่าน",
        "",
        "| # | คำถาม | คำตอบที่ควรได้ | คำตอบจริง | tool ที่เรียก | ผล |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        q = row["question"]
        tools = ", ".join(f"`{t}`" for t in row["tools_used"]) or "—"
        mark = "ผ่าน" if row["passed"] else "ไม่ผ่าน"
        if not row["agrees_with_human"]:
            mark += " **(ต่างจากที่คนตัดสิน)**"
        lines.append(
            f"| {q['id']} | {q['query']} | {q['expected']} | "
            f"{one_line(row['answer'], 120)} | {tools} | {mark} |"
        )

    lines += [
        "",
        f"**สรุป: ผ่าน {passed_count}/{total}**",
        "",
        "## judge เชื่อได้แค่ไหน",
        "",
        f"เทียบคำตัดสินของ judge กับคำตัดสินที่คนตรวจไว้ก่อนหน้า — **ตรงกัน {agree_count}/{total}**",
        "",
        "ลำดับคือคนตรวจคำตอบทั้งหมดด้วยตาก่อน แล้วจึงเอาผลนั้นมาวัดว่า judge ตัดสินเหมือนคนไหม "
        "ไม่ได้ปล่อยให้ judge ตัดสินโดยไม่มีอะไรมาเทียบ",
        "",
        "## รายละเอียดแต่ละข้อ",
        "",
    ]
    for row in rows:
        q = row["question"]
        lines += [
            f"### {q['id']} — {q['query']}",
            "",
            f"- **ที่มา:** {q['source']}",
            f"- **tool ที่เรียก:** {row['tools_used'] or 'ไม่เรียกเลย'}",
            f"- **ชั้น structural:** {'ผ่าน' if row['structural_ok'] else 'ไม่ผ่าน'}",
            f"- **ชั้น judge:** {'ผ่าน' if row['judge'].passed else 'ไม่ผ่าน'} — {row['judge'].reason}",
            f"- **คนตัดสินไว้ว่า:** {q['human_verdict']}",
            "",
            "```",
            row["answer"].strip(),
            "```",
            "",
        ]

    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
