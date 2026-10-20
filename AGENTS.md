# Repository Guidelines

## Project Structure & Module Organization
IncidentLens AI is a Python FastAPI backend for integration execution, failure detection, incident tracking, and Gemini incident analysis.

- `backend/app/main.py` creates the application and registers routers.
- `backend/app/routers/` defines HTTP endpoints; `schemas/` contains Pydantic request and response models.
- `backend/app/services/` implements API execution, incident analysis, PDF loading, and text chunking.
- `backend/app/crud/` handles persistence operations; `database/` contains SQLAlchemy models and session setup.
- `backend/app/core/` holds configuration and dependencies.
- `tests/` contains pytest tests. Root-level `sample.pdf` is a sample document.

## Build, Test, and Development Commands
Run commands from the repository root with a configured Python environment:

- `python -m venv venv` creates a local virtual environment.
- `.\venv\Scripts\Activate.ps1` activates it in PowerShell.
- `python -m uvicorn backend.app.main:app --reload` runs the development API.
- `python -m pytest` runs the full test suite.
- `python -m pytest tests/test_chunker.py tests/test_document_loader.py` runs document-processing tests.

No dependency manifest, separate build step, or formatter/linter configuration is currently checked in. Dependencies include FastAPI, SQLAlchemy, pydantic-settings, requests, google-genai, pypdf, pytest, and the development server Uvicorn.

## Coding Style & Naming Conventions
Use four-space indentation, `snake_case` for modules and functions, `PascalCase` for classes, and uppercase configuration names. Add type hints and short docstrings to service functions. Keep HTTP handling in routers, business logic in services, and database operations in CRUD modules. Follow nearby code conventions without unrelated reformatting.

## Testing Guidelines
Name files `test_*.py` and functions `test_<behavior>`. Use pytest parametrization for edge cases, `tmp_path` for generated documents, and mocks or `monkeypatch` for database and Gemini interactions. Cover successful results, validation failures, and provider errors. No coverage threshold is configured. The API executor test contacts httpbin; application imports initialize database tables, so use a disposable development database for full-suite runs.

## Commit & Pull Request Guidelines
History uses concise Conventional Commit prefixes such as `feat:` and `test:`. Follow that pattern with an imperative summary. PRs should describe behavior changes, link relevant issues, and list validation commands and results. Include request/response examples for API changes and disclose configuration or database changes.

## Security & Configuration
Keep secrets in the ignored root `.env`. Required settings are `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, and `GEMINI_API_KEY`. Never commit credentials, local environments, or sensitive incident data.
