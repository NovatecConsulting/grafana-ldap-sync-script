FROM python:3.9-slim

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt && mkdir /app

WORKDIR /app

COPY LICENSE run.py /app/
COPY script /app/script

ENTRYPOINT [ "python3", "./run.py" ]
