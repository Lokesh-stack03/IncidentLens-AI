# IncidentLens AI

A student-friendly application for checking APIs, recording failures, investigating incidents with Gemini, and finding context in PDF runbooks. React provides the interface; FastAPI provides the backend.

## Run locally

Use Python 3.11+ (3.11 or 3.12 is recommended for machine-learning packages) and Node.js 22.12+.

From the repository root in PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Only copy if you do not already have a .env file:
Copy-Item .env.example .env
python -m uvicorn backend.app.main:app --reload
```

Keep this terminal open. In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:5173**. API docs are at **http://127.0.0.1:8000/docs**. Vite forwards `/api` requests to port 8000.

SQLite works without a database server. An existing `.env` takes precedence over defaults: set `DATABASE_URL=sqlite:///./incidentlens.db` to use SQLite. For PostgreSQL, install `psycopg2-binary` and start the database server. If your shell sets `DEBUG=release`, remove that variable or set it to `false` before starting FastAPI.

Set `GEMINI_API_KEY` in `.env` to enable analysis; other features work without it. Gemini receives incident text and may incur provider charges. Change `GEMINI_MODEL` if the provider rejects the configured model. Embeddings run locally: the first upload or search downloads `all-MiniLM-L6-v2` and requires internet access.

## Demonstrate the features

1. Add an integration with an API URL you are allowed to test. Run check sends a real request using its configured method.
2. Success shows a notification. Failure automatically creates an incident.
3. Open an incident and change its status: **OPEN → INVESTIGATING → RESOLVED**. Request Gemini investigation suggestions or report an incident manually.
4. Upload a text-based PDF in Knowledge base. Scanned or encrypted PDFs are unsupported; uploads are limited to 10 MB.
5. Search a question to retrieve passages with source, page, and vector distance. Incident details include a shortcut to search the error. Document search and Gemini analysis are separate actions; retrieved passages are not automatically sent to Gemini.
6. Edit or delete integrations. Delete their incidents first. Document deletion removes all chunks with the selected filename. Re-uploading a filename adds chunks; delete the old document first to replace it.

## Explain the code

```text
React form → api.js fetch → FastAPI router → service → database
PDF → document_loader → text_chunker → embedding → ChromaDB
Question → embedding → ChromaDB query → passages with sources
API failure → incident_service → SQLAlchemy Incident → React list
Incident → gemini_service → structured investigation → React dialog
```

- `frontend/src/App.jsx`: state, navigation, and user actions. `useState` remembers values; `useEffect` loads data. Handlers call the API and refresh the screen.
- `frontend/src/components/`: one component per page, forms, incident details, and a keyboard-accessible dialog. Props pass data and event handlers from `App` to each screen.
- `frontend/src/api.js`: a reusable fetch function with readable errors.
- `frontend/src/styles.css`: responsive layout and component styles.
- `backend/app/routers/`: HTTP endpoints and validation.
- `backend/app/services/`: functions for execution, failure detection, documents, search, and AI.
- `backend/app/crud/`: database create, read, update, and delete operations.
- `backend/app/schemas/`: input/output shapes; `database/models.py` defines stored records.
- `tests/`: backend tests. `conftest.py` supplies isolated SQLite databases. React tests live beside the UI code.

Local data lives in `incidentlens.db` and `.chroma/`. Keep these files and `.env` out of Git. The empty `or_store.py` is unused; the implemented service is `vector_store.py`.

## Test and build

```powershell
python -m pytest -q --cov=backend/app --cov-report=term-missing
cd frontend
npm test
npm run build
npm audit
```

For the real-browser workflow, install Google Chrome and run `npm run test:e2e` in `frontend/`. It starts its own API on port 8010 and UI on port 5174 with temporary SQLite and Chroma data and an empty Gemini key. Keep these ports available. Screenshots are saved under `frontend/test-results/`. Set `HF_HUB_OFFLINE=1` before the command if the embedding model is already cached and network checks are slow.

Use `python -m black backend tests` and `npm run format` (inside `frontend/`) to format code consistently.

Tests mock outgoing API execution and Gemini calls. Embedding and semantic search tests use the actual local model, which must be cached for offline tests. Database and collection tests are isolated from application data.

This is a local, single-user learning project with no login, background monitoring, or deployment setup. Do not expose it publicly: API execution can reach URLs accessible from your computer. An active integration can be run manually; it is not continuously monitored. Verify AI suggestions against real evidence.
