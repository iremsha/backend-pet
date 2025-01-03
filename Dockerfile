FROM python:3.12-slim as builder

USER root
WORKDIR /app

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

FROM builder as dev

WORKDIR /app

COPY backend_pet backend_pet
COPY --chown=user scripts/* .

RUN chmod u+x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]