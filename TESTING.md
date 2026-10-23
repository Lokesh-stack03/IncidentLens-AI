# Verification results

Verified locally on 21 October 2026 using Python 3.14 and Node.js 24.

| Check | Result |
| --- | --- |
| Backend pytest suite | 50 passed |
| Backend statement coverage | 98% |
| React and API-helper tests | 11 passed |
| Chrome workflow test | 1 passed |
| React production build | Passed |
| npm dependency audit | 0 reported vulnerabilities at installation |
| Python compilation and Git whitespace check | Passed |

## What was exercised

- Integration creation, listing, lookup, editing, deletion, URL validation, and inactive execution rejection.
- Successful API requests, HTTP failures, timeouts, connection failures, and automatic incident creation.
- Manual incident reporting, status changes, filtering, lookup, deletion, and invalid integration/status handling.
- Gemini response parsing, provider failures, invalid responses, and missing-key feedback.
- PDF source/page extraction, chunk overlap, encrypted/blank/invalid/oversized files, uploads, listing, storage, retrieval, and deletion.
- Actual local embedding generation and semantic retrieval from the included sample PDF.
- React navigation, forms, error feedback, document search, keyboard dialog dismissal, and focus restoration.
- A real Chrome workflow connecting React to FastAPI: create/edit/check an integration, resolve an incident, report/filter/delete a manual incident, upload/search/delete a PDF, delete records, and check the mobile viewport.

## Limits

Live Gemini calls were not made; provider responses were mocked. Real browser tests verified the missing-key message. API execution was tested against the local test server; external API availability is outside these checks. PostgreSQL was not tested; database tests used disposable SQLite databases. Dependency deprecation warnings remain, especially with Python 3.14. This is a local learning application, not a tested public deployment.

Run the commands in [README.md](README.md) to reproduce these checks. Chrome screenshots are written to ignored `frontend/test-results/` files by `npm run test:e2e`.
