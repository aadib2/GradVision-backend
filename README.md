# GradVision
Backend for the COMPE561 Full Stack Web Development course, built with FastAPI.

## Getting Started

Setup virtual environment / dependencies (uv makes this easy!):

```bash
uv sync
```

Navigate to the src/ directory:

```bash
cd src
```

Startup the fastapi app (this will automatically detect the entrypoint - see `[tool.fastapi]` in `pyproject.toml`):

```bash
uv run fastapi dev
```

or you can alternatively do:

```bash
uv run uvicorn app.main:app --reload
```

Alternatively if you don't want to switch directories, you can also just run:

```bash
uv run uvicorn app.main:app --reload --app-dir src
```

## Repository Structure
Placeholder until features are built out


## Running Tests

Run all tests from the repo root:

```
JWT_SECRET_KEY="test-secret-key" PYTHONPATH=src uv run pytest -v
```