import sqlite3

DATABASE_NAME = "enrolment.db"

students = [
    (1, "John Smith", "ASD101"),
    (2, "Sarah Jones", "ASD101"),
    (3, "Michael Lee", "WEB201"),
    (4, "Emma Brown", "WEB201"),
    (5, "James Wilson", "DBS101"),
    (6, "Olivia White", "DBS101"),
    (7, "Daniel Green", "NET201"),
    (8, "Sophia Hall", "NET201"),
    (9, "Liam King", "SEC301"),
    (10, "Chloe Young", "SEC301")
]

conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    student_name TEXT NOT NULL,
    subject_code TEXT NOT NULL
)
""")

cursor.execute("DELETE FROM students")

cursor.executemany(
    "INSERT INTO students (student_id, student_name, subject_code) VALUES (?, ?, ?)",
    students
)

conn.commit()
conn.close()

print("Database initialized with 10 students.")
