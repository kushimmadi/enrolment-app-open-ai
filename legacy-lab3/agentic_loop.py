import os
import sqlite3
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

# ============================= Agents Env Setup =============================
ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(dotenv_path=ENV_PATH)

PROMPT_DIR = Path(__file__).with_name("prompts")

DATABASE_NAME = Path(__file__).with_name("enrolment.db")

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434/v1"
)

IMPLEMENTATION_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:0.5b"
)

REVIEW_MODEL = os.getenv(
    "OLLAMA_REVIEW_MODEL",
    "llama3.1:8b"
)

# ==================================== Plan ====================================
PLAN = {
    "goal": "Validate Student Enrolment App behavior using a local multi-agent workflow",
    "db_plan": [
        "Check student data quality (10 records, valid required fields)",
        "Check subject-code search returns matching students"
    ],
    "endpoints_plan": [
        "GET /students - get all students",
        "GET /students/by-id - get student by id",
        "GET /students/by-subject - get students by subject code"
    ]
}


# ================================ Observe: Database ================================
def validate_student(student):
    student_id, student_name, subject_code = student

    if not isinstance(student_id, int):
        return False, "student_id must be an integer"

    if not student_name:
        return False, "student_name is required"

    if not subject_code:
        return False, "subject_code is required"

    return True, "ok"


def observe_data_quality():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    students = cursor.execute(
        """
        SELECT
            student_id,
            student_name,
            subject_code
        FROM students
        """
    ).fetchall()

    conn.close()

    if len(students) != 10:
        return False, "Expected 10 students"

    all_ok = True

    for student in students:
        ok, msg = validate_student(student)
        status = "OK" if ok else f"FAIL: {msg}"
        print(f"  Checked student_id={student[0]} -> {status}")

        if not ok:
            all_ok = False

    if not all_ok:
        return False, "One or more student records failed validation"

    return True, "Data validation passed"


def observe_subject_search(subject_code):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    students = cursor.execute(
        """
        SELECT
            student_id,
            student_name,
            subject_code
        FROM students
        WHERE subject_code = ?
        """,
        (subject_code,)
    ).fetchall()

    conn.close()

    if not students:
        print(f"  Checked subject_code={subject_code} -> FAIL: no students found")
        return False, (
            f"No students found for subject code {subject_code}"
        )

    for student in students:
        status = (
            "OK" if student[2] == subject_code
            else f"FAIL: unexpected subject code {student[2]}"
        )
        print(f"  Checked student_id={student[0]} -> {status}")

        if student[2] != subject_code:
            return False, (
                f"Unexpected subject code found: {student[2]}"
            )

    return True, (
        f"Subject search validation passed for {subject_code}"
    )


def get_sample_student():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    row = cursor.execute(
        """
        SELECT student_id, subject_code
        FROM students
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    return row


# ============================= Observe: Live Endpoints ==============================
def observe_live_endpoints(sample_student):
    results = []

    student_id, subject_code = (
        sample_student if sample_student else (None, None)
    )

    def check(label, method, url, **kwargs):
        try:
            response = requests.request(
                method, url, timeout=5, **kwargs
            )
            content_ok = bool(response.text and response.text.strip())
            line = (
                f"{label} -> HTTP {response.status_code}, "
                f"content_ok={content_ok}"
            )
        except Exception as exc:
            line = f"{label} -> error: {exc}"

        print(f"  Checked {line}")
        results.append(line)

    check("/students", "GET", "http://127.0.0.1:5000/students")

    if student_id is not None:
        check(
            "/students/<student_id>",
            "GET",
            f"http://127.0.0.1:5000/students/{student_id}"
        )
        check(
            "/students/by-id",
            "GET",
            f"http://127.0.0.1:5000/students/by-id?student_id={student_id}"
        )
    else:
        skipped_id = "/students/<student_id> -> skipped: no sample student found"
        skipped_by_id = "/students/by-id -> skipped: no sample student found"
        print(f"  Checked {skipped_id}")
        print(f"  Checked {skipped_by_id}")
        results.append(skipped_id)
        results.append(skipped_by_id)

    if subject_code is not None:
        check(
            "/students/by-subject",
            "GET",
            f"http://127.0.0.1:5000/students/by-subject?subject_code={subject_code}"
        )
    else:
        skipped_subject = "/students/by-subject -> skipped: no sample student found"
        print(f"  Checked {skipped_subject}")
        results.append(skipped_subject)

    check(
        "/ask",
        "POST",
        "http://127.0.0.1:5000/ask",
        data={"question": "What does this app do?"}
    )

    return results


# =============================== Model Call Helper ================================
def call_model(model_name, system_prompt, user_prompt, max_tokens=120):
    try:
        client = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama",
            timeout=180.0
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.1
        )

        content = response.choices[0].message.content

        if content and content.strip():
            return content.strip(), None

        return "No response generated.", None

    except Exception as exc:
        return None, (
            f"{model_name} unavailable or timed out ({exc})"
        )


# TASK 2 (COMPLETED): ================= Implementation & Review Agents =================
def load_prompt(filename):
    prompt_path = PROMPT_DIR / filename
    return prompt_path.read_text(encoding="utf-8").strip()


def get_implementation_agent_advice(observe_message):
    system_prompt = load_prompt("implementation_system_prompt.txt")
    task_prompt = load_prompt("implementation_task_prompt.txt")

    task_prompt = task_prompt.replace(
        "{{VALIDATION_EVIDENCE}}", observe_message
    )

    return call_model(
        IMPLEMENTATION_MODEL,
        system_prompt,
        task_prompt,
        max_tokens=120
    )


def get_review_agent_advice(implementation_message, observe_message):
    system_prompt = load_prompt("review_system_prompt.txt")
    task_prompt = load_prompt("review_task_prompt.txt")

    task_prompt = task_prompt.replace(
        "{{IMPLEMENTATION_RECOMMENDATION}}", implementation_message
    )
    task_prompt = task_prompt.replace(
        "{{VALIDATION_EVIDENCE}}", observe_message
    )

    return call_model(
        REVIEW_MODEL,
        system_prompt,
        task_prompt,
        max_tokens=150
    )


# =============================== Human Review & Adapt ================================
def human_review():
    print()
    print("HUMAN REVIEW")
    print("1 - Accept")
    print("2 - Partially Accept")
    print("3 - Reject")

    decision = input("Decision: ").strip()

    if decision == "1":
        return "Accept"

    if decision == "2":
        return "Partially Accept"

    return "Reject"


def adapt(decision):
    print()

    if decision == "Accept":
        print(
            "ADAPT: Apply recommendation and rerun validation."
        )

    elif decision == "Partially Accept":
        print(
            "ADAPT: Apply selected recommendations and "
            "rerun validation."
        )

    else:
        print(
            "ADAPT: Keep current implementation and "
            "document rationale."
        )


# ================================= Main / Loop Entry ================================
def main():
    print("=" * 60)
    print("ASD LAB 03 AGENTIC LOOP")
    print("=" * 60)

    print()
    print("PLAN")
    print(PLAN)

    print()
    print("ACT")
    print("Check local database records")

    print()
    print("OBSERVE: Database Check")
    ok_data, msg_data = observe_data_quality()
    print(msg_data)

    sample_student = get_sample_student()
    sample_subject_code = sample_student[1] if sample_student else "ASD101"

    print()
    print("OBSERVE: Subject Search Check")
    ok_subject, msg_subject = observe_subject_search(
        sample_subject_code
    )
    print(msg_subject)

    print()
    print("OBSERVE: Live Endpoint Check")
    live_results = observe_live_endpoints(sample_student)

    observe_message = (
        f"{msg_data}. "
        f"{msg_subject}. "
        f"Live endpoint checks: " + "; ".join(live_results)
    )

    print()
    print("IMPLEMENTATION AGENT")
    print(f"Model: {IMPLEMENTATION_MODEL}")

    implementation_advice, implementation_error = (
        get_implementation_agent_advice(
            observe_message
        )
    )

    if implementation_advice:
        print()
        print(implementation_advice)
    else:
        print()
        print(implementation_error)
        implementation_advice = (
            "Implementation agent unavailable."
        )

    print()
    print("REVIEW AGENT")
    print(f"Model: {REVIEW_MODEL}")

    review_advice, review_error = (
        get_review_agent_advice(
            implementation_advice,
            observe_message
        )
    )

    if review_advice:
        print()
        print(review_advice)
    else:
        print()
        print(review_error)

    print()
    print("HUMAN DECISION")

    decision = human_review()

    print()
    print(f"Decision: {decision}")

    adapt(decision)

    print()
    print("LOOP COMPLETE")


if __name__ == "__main__":
    main()
