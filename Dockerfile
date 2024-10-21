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

WORKDIR /app
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY run.py .

RUN mkdir -p config
COPY config.yml example.csv config/
COPY example.csv config/bind.csv

VOLUME [ "/app/config" ]

CMD [ "python", "run.py", "--config=config/config.yml", "--bind=config/bind.csv" ]
