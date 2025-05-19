FROM python:3.10.17-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"
WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

FROM builder AS development

COPY . /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

FROM development AS ci

FROM python:3.10.17-slim-bookworm AS production

ARG VERSION
ENV PYTHONUNBUFFERED=1 SENTRY_RELEASE=${VERSION} PATH="/app/.venv/bin:$PATH" VIRTUAL_ENV="/app/.venv"
WORKDIR /app/

RUN apt-get update && \
	apt-get install -y libpq-dev \
	--no-install-recommends &&\
	rm -rf /var/lib/apt/lists/*

COPY manage.py /app
COPY shargain /app/shargain
COPY --from=builder --chown=app:app /app/.venv /app/.venv