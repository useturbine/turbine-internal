FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .
