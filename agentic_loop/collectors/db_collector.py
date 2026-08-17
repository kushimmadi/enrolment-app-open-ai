import sqlite3
from pathlib import Path


DATABASE_NAME = "enrolment.db"


def _validate_student(student: tuple[int, str, str]) -> tuple[bool, str]:
    student_id, student_name, subject_code = student
    if not isinstance(student_id, int):
        return False, "student_id must be integer"
    if not student_name:
        return False, "student_name required"
    if not subject_code:
        return False, "subject_code required"
    return True, "ok"


def collect(app_dir: Path, repo_root: Path) -> tuple[bool, str]:
    db_path = app_dir / "legacy-lab3" / DATABASE_NAME
    if not db_path.exists():
        return False, f"Missing local database file: {db_path.name}"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    students = cursor.execute(
        """
        SELECT student_id, student_name, subject_code
        FROM students
        """
    ).fetchall()
    count_asd101 = cursor.execute(
        "SELECT COUNT(*) FROM students WHERE subject_code = ?",
        ("ASD101",),
    ).fetchone()[0]
    conn.close()

    if len(students) != 10:
        return False, f"Expected 10 students, found {len(students)}"

    for student in students:
        ok, msg = _validate_student(student)
        if not ok:
            return False, msg

    return True, (
        "Database evidence: students table has 10 valid rows; "
        f"ASD101 rows count is {count_asd101}; fields are student_id, student_name, subject_code."
    )
