# Repository Guidelines

## Project Structure & Module Organization
IncidentLens AI combines FastAPI and React for API checks, incidents, and document search.

- `backend/app/main.py` creates the application and registers routers.
- `backend/app/routers/` defines HTTP endpoints; `schemas/` contains Pydantic request and response models.
- `backend/app/services/` implements API execution, incident analysis, PDF loading, and text chunking.
- `backend/app/crud/` handles persistence operations; `database/` contains SQLAlchemy models and session setup.
- `backend/app/core/` holds configuration and dependencies.
- `tests/` contains pytest tests; `sample.pdf` provides sample text.
- `frontend/src/` contains React screens, styles, an API helper, and UI tests.

## Build, Test, and Development Commands
Run Python commands from the repository root:

- `python -m venv venv` creates a local virtual environment.
- `.\venv\Scripts\Activate.ps1` activates it in PowerShell.
- `python -m uvicorn backend.app.main:app --reload` runs the development API.
- `python -m pytest` runs the full test suite.
- `python -m pytest tests/test_chunker.py tests/test_document_loader.py` runs document-processing tests.

Install Python dependencies with `python -m pip install -r requirements.txt`. In `frontend/`, use `npm ci`, `npm run dev`, `npm test`, and `npm run build` to install, develop, test, and build React. Format with `python -m black backend tests` and frontend `npm run format` (Prettier).

## Coding Style & Naming Conventions
Use four-space indentation, `snake_case` for modules and functions, `PascalCase` for classes, and uppercase configuration names. Add type hints and short docstrings to service functions. Keep HTTP handling in routers, business logic in services, and database operations in CRUD modules. Follow nearby code conventions without unrelated reformatting.

## Testing Guidelines
Name files `test_*.py` and functions `test_<behavior>`. Use pytest parametrization, `tmp_path`, and mocks or `monkeypatch`. Cover success, validation failures, and provider errors. Tests isolate SQLite databases and mock external HTTP/Gemini calls. Embedding tests use the actual local model. Run `python -m pytest --cov=backend/app` for coverage. UI tests use Vitest and Testing Library. No coverage threshold is configured.

## Commit & Pull Request Guidelines
History uses concise Conventional Commit prefixes such as `feat:` and `test:`. Follow that pattern with an imperative summary. PRs should describe behavior changes, link relevant issues, and list validation commands and results. Include request/response examples for API changes and disclose configuration or database changes.

## Security & Configuration
Keep secrets in the ignored `.env`; see `.env.example` for local SQLite settings. `GEMINI_API_KEY` is needed only for AI analysis. Never commit credentials, environments, `.chroma/`, databases, or sensitive incident data. This is a local single-user demo; do not expose it publicly.
