FROM python:3.11-slim

WORKDIR /app

COPY enrolment-service/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY enrolment-service ./enrolment-service
COPY prompts/service ./prompts/service
COPY prompts/lab4 ./prompts/lab4

EXPOSE 5001

CMD ["python", "enrolment-service/app.py"]
