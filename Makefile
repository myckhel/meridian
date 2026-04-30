.PHONY: install dev run lock

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload

run:
	uv run uvicorn app.main:app

lock:
	uv lock