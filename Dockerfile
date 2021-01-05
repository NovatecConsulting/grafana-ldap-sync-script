FROM python:3.9-slim

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ADD LICENSE run.py script/* /

ENTRYPOINT [ "python3", "/run.py" ]
