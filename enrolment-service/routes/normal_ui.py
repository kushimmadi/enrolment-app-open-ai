from flask import Blueprint, request
import requests

from services.database_api import get_student_by_id_response, get_students, get_students_by_subject_response
from views.html_formatters import format_student_html, format_students_html


normal_ui_bp = Blueprint("normal_ui", __name__)


@normal_ui_bp.get("/")
def health():
    return "<p>enrolment-service running</p>", 200


@normal_ui_bp.get("/students")
def get_students_route():
    try:
        return format_students_html(get_students()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve students from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


@normal_ui_bp.get("/students/by-id")
def get_student_by_id():
    student_id = request.args.get("student_id", "").strip()

    if not student_id:
        return "<p>Student ID is required.</p>", 400

    try:
        response = get_student_by_id_response(student_id)

        if response.status_code == 404:
            return "<p>Student not found.</p>", 404
        if response.status_code == 400:
            return "<p>Student ID must be valid.</p>", 400

        response.raise_for_status()
        return format_student_html(response.json()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve student from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )


@normal_ui_bp.get("/students/by-subject")
def get_students_by_subject():
    subject_code = request.args.get("subject_code", "").strip().upper()

    if not subject_code:
        return "<p>Subject code is required.</p>", 400

    try:
        response = get_students_by_subject_response(subject_code)

        if response.status_code == 404:
            return f"<p>No students found for {subject_code}.</p>", 404

        response.raise_for_status()
        return format_students_html(response.json()), 200
    except requests.RequestException as exc:
        return (
            "<p>Failed to retrieve subject results from database-service.</p>"
            f"<pre>{exc}</pre>",
            503,
        )
