# syntax = docker/dockerfile:1.2
FROM python:3.10.8-slim as backend-base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

RUN apt-get update && \
	apt-get install -y libpq-dev gcc python-dev \
	--no-install-recommends &&\
	rm -rf /var/lib/apt/lists/*

ADD requirements/base.txt .

FROM backend-base as backend-dev
ADD requirements/dev.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r dev.txt
ADD . ./

FROM backend-base as production
ADD requirements/prod.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r prod.txt
ADD . ./
RUN python manage.py collectstatic --noinput

