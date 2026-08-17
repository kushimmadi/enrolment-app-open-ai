def format_students_html(students):
    if not students:
        return "<p>No students found.</p>"

    html = "<ul>"
    for student in students:
        html += (
            f"<li>{student['student_id']} - "
            f"{student['student_name']} - {student['subject_code']}</li>"
        )
    html += "</ul>"
    return html


def format_student_html(student):
    return (
        f"<p>ID: {student['student_id']}<br>"
        f"Name: {student['student_name']}<br>"
        f"Subject: {student['subject_code']}</p>"
    )
