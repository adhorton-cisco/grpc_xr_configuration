FROM python:3.10.5-slim-buster

COPY /src /src

COPY requirements.txt /src

COPY /config/config.yaml /config/config.yaml

WORKDIR /src

RUN pip install -r requirements.txt

CMD ["python3", "probe.py"]