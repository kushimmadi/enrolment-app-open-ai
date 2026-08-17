import os

import requests


DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://database-service:5002")


def get_students():
    response = requests.get(f"{DATABASE_SERVICE_URL}/students", timeout=5)
    response.raise_for_status()
    return response.json()


def get_student_by_id_response(student_id):
    return requests.get(f"{DATABASE_SERVICE_URL}/students/{student_id}", timeout=5)


def get_students_by_subject_response(subject_code):
    return requests.get(
        f"{DATABASE_SERVICE_URL}/students/by-subject",
        params={"subject_code": subject_code},
        timeout=5,
    )
