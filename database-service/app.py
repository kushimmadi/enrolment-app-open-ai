from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE_NAME = "/app/data/enrolment.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def health():
    return jsonify({"service": "database-service", "status": "running"})

@app.get("/students")
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in students])

@app.get("/students/<int:student_id>")
def get_student(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))

@app.get("/students/by-subject")
def get_students_by_subject():
    subject_code = request.args.get("subject_code", "").strip().upper()

    if not subject_code:
        return jsonify({"error": "subject_code required"}), 400

    conn = get_db_connection()
    students = conn.execute(
        "SELECT student_id, student_name, subject_code FROM students WHERE subject_code = ?",
        (subject_code,),
    ).fetchall()
    conn.close()

    if not students:
        return jsonify({"error": "No students found"}), 404

    return jsonify([dict(row) for row in students])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
