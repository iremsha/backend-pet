FROM python:3.12-slim

USER root
WORKDIR /app

RUN pip install poetry

COPY backend_pet backend_pet
COPY --chown=user scripts/* .

COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

RUN chmod u+x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["backend-pet", "run"]
