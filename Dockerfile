FROM python:3.10.5-slim-buster

WORKDIR /src

COPY /src .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "probe.py"]