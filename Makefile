.PHONY: install dev run lock docker-build docker-run

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload

run:
	uv run uvicorn app.main:app

lock:
	uv lock

docker-build:
	docker build -t meridian-api .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env meridian-api