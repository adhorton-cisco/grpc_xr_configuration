FROM python:3.10.5-slim-buster

WORKDIR /app

COPY /src /config/schema.json requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "monitor.py"]