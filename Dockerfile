FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /uvx /bin/

WORKDIR /app
ENV UV_NO_DEV=1

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

COPY . .

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
