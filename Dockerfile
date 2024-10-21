FROM python:3.13-slim AS installer
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY script ./script
COPY setup.py .
RUN pip install .

FROM python:3.13-slim AS runtime
COPY --from=installer /opt/venv /opt/venv

WORKDIR /data
COPY config.yml .
COPY example.csv /data/bind.csv

WORKDIR /app
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY run.py .

VOLUME [ "/data" ]

CMD [ "python", "run.py", "--config=/data/config.yml", "--bind=/data/bind.csv" ]
