FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.10 /uv /uvx /bin/

WORKDIR /app
ENV UV_NO_DEV=1

# deps only (cached until pyproject.toml and uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project


# copy source, then install project itself
COPY . .
RUN uv sync --locked

CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
