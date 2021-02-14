# syntax = docker/dockerfile:1.2
FROM python:3.8.7-slim as backend-base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT=8000
WORKDIR /app

ADD requirements/base.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r base.txt
ADD . ./
CMD ["./entrypoint.sh"]

FROM backend-base as backend-dev
ADD requirements/dev.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r dev.txt

FROM backend-base as backend-production
ADD requirements/prod.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r prod.txt
RUN python manage.py collectstatic --noinput

