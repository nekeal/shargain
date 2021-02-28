# syntax = docker/dockerfile:1.2
FROM python:3.8.7-slim as backend-base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
ADD . ./
CMD ["./entrypoint.sh"]

FROM backend-base as backend-dev
ADD requirements/dev.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r dev.txt

FROM backend-base as production
ADD requirements/prod.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r prod.txt
RUN python manage.py collectstatic --noinput

