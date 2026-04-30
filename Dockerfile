FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  GRADIO_SERVER_NAME=0.0.0.0 \
  GRADIO_SERVER_PORT=7860 \
  PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
  && apt-get install --yes --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && addgroup --system app \
  && adduser --system --ingroup app app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY --chown=app:app app ./app
COPY --chown=app:app hf_app.py ./hf_app.py
COPY --chown=app:app .env.example ./.env.example
COPY --chown=app:app README.md ./README.md

USER app

EXPOSE 7860

CMD ["python", "hf_app.py"]