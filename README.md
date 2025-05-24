# Shargain

[![CI](https://github.com/nekeal/shargain/actions/workflows/backend.yml/badge.svg)](https://github.com/nekeal/shargain/actions)

Django app which stores scrapped data.

# Prerequisites

## Native way with virtualenv
- [Python3.10](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/)

## Docker way
- [Docker](https://docs.docker.com/engine/install/)  
- [Docker Compose](https://docs.docker.com/compose/install/)

## Local Development

## Native way with uv

First create postgresql database:

```sql
create user shargain with createdb;
alter user shargain password 'shargain';
create database shargain owner shargain;
```
Now you can setup virtualenv and django:
```bash
uv sync
make bootstrap
```

## Docker way

Start the dev server for local development:
```bash
docker compose up
```

Run a command inside the docker container:

```bash
docker compose run --rm web [command]
```


## Pre-commit hooks

To install pre-commit hooks run:

```bash
pre-commit install
```
