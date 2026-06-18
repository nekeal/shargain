# Justfile for shargain

set positional-arguments := true

COMMIT_SHA := `git rev-parse HEAD`
BRANCH_NAME := `git rev-parse --abbrev-ref HEAD`
MANAGE := "uv run python manage.py"
DOCKER_REGISTRY := "shargain"

# Show help
default: help

help:
    @just --list

# --- Cleanup ---

# Remove all build, test, coverage and Python artifacts
clean: clean-pyc clean-test

# Remove Python file artifacts
clean-pyc:
    find . -name '*.pyc' -delete
    find . -name '*.pyo' -delete
    find . -name '*~' -delete
    find . -name '__pycache__' -type d -exec rm -rf {} +

# Remove test and coverage artifacts
clean-test:
    rm -rf .tox/ .coverage coverage.xml htmlcov/ .pytest_cache

# --- Development Setup ---

# Bootstrap project (sync + migrate + fixtures)
bootstrap:
    uv sync
    {{ MANAGE }} migrate
    {{ MANAGE }} loaddata fixtures/*

# Install pre-commit hooks
install-pre-commit:
    uv run pre-commit install --install-hooks
    uv run pre-commit install -t commit-msg

# Recreate database with fixtures
rebuild-db:
    #!/usr/bin/env bash
    set -euo pipefail
    echo yes | {{ MANAGE }} reset_db
    {{ MANAGE }} migrate
    [ -d fixtures ] && {{ MANAGE }} loaddata fixtures/* || true

# Bootstrap project in Docker
bootstrap-docker:
    docker compose up --build -d
    docker compose exec web python manage.py migrate
    docker compose exec web python manage.py loaddata fixtures/*.yaml

# --- Testing & Quality ---

# Run backend tests
test:
    pytest shargain

# Run tests on every Python version with tox
test-tox:
    tox

# Run coverage report
coverage:
    uv run pytest --cov=shargain shargain
    coverage report -m
    coverage html

# Run quality checks (ruff + mypy)
quality-check: autoformatters
    uv run ruff check shargain
    uv run ruff format --check shargain
    uv run mypy shargain

# Run autoformatters
autoformatters:
    uv run ruff format shargain
    uv run ruff check --fix shargain

# --- Frontend ---

# Start frontend dev server
frontend-dev:
    npm --prefix frontend run dev

# Run frontend tests
frontend-test:
    npm --prefix frontend run test

# Lint frontend
frontend-lint:
    npm --prefix frontend run lint

# Fix frontend lint issues
frontend-lint-fix:
    npm --prefix frontend run lint:fix

# Build frontend for production
frontend-build:
    npm --prefix frontend run build

# Generate API client from OpenAPI spec
frontend-generate-api-client:
    npm --prefix frontend run generate:api-client

# --- Docker ---

# Show docker tags for current build
docker-show-tags:
    @echo -t {{ DOCKER_REGISTRY }}:{{ COMMIT_SHA }} -t {{ DOCKER_REGISTRY }}:{{ BRANCH_NAME }}

# Build docker image
docker-build:
    docker build -t {{ DOCKER_REGISTRY }}:{{ COMMIT_SHA }} -t {{ DOCKER_REGISTRY }}:{{ BRANCH_NAME }} .

# Push docker image
docker-push:
    docker push {{ DOCKER_REGISTRY }}:{{ COMMIT_SHA }}
    docker push {{ DOCKER_REGISTRY }}:{{ BRANCH_NAME }}

# --- CI/CD ---

# Show current pipeline status
pipeline-status:
    @gh run list -c `git rev-parse HEAD`

# Run backend and frontend dev servers in parallel
run:
    #!/usr/bin/env -S parallel --shebang --ungroup --jobs 2
    {{ MANAGE }} runserver
    npm --prefix frontend run dev

# --- Combined Commands ---

# Run all tests (backend + frontend)
test-all:
    pytest shargain
    npm --prefix frontend run test

# Run all quality checks (backend + frontend)
check-all: quality-check
    npm --prefix frontend run lint

# Full CI pipeline
ci: check-all test-all
