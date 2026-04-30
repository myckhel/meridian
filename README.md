# Meridian FastAPI Scaffold

## Run locally

```bash
uv venv
source .venv/bin/activate
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
```

## Common uv commands

```bash
uv sync
uv run uvicorn app.main:app --reload
uv add <package>
```

## Make targets

```bash
make install
make dev
make run
make lock
```

## Available endpoints

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/chat`

`POST /api/v1/chat` is a scaffold endpoint and currently returns `501 Not Implemented`.