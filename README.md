# S.H.I.P: Self-Healing Infrastructure Pipeline

An experimental pipeline that intercepts a server error, asks Gemini to diagnose it, asks a second Gemini agent to write a patch, and applies the patch to an allowlisted file.

> **Status: experimental.** This is a learning project and a working demo, not a production tool. Do not point it at systems you care about. See [Known limitations](#known-limitations).

---

## What it does

1. A crashing service sends its stack trace and source file to `POST /api/v1/intercept-log`.
2. **Agent 1 (Root Cause Analyst)** reads the stack trace and writes a diagnosis. It does not write code.
3. **Agent 2 (Patching Compiler)** takes the diagnosis and the broken file and produces a replacement file.
4. The patch is stored in the database as an incident.
5. A token-authenticated call to `POST /api/v1/deploy-patch/{incident_id}` writes the patch to the target file.
6. A WebSocket dashboard shows incidents as they happen.

Separating diagnosis from code generation keeps each prompt single-purpose. Whether that improves accuracy over a single prompt has **not** been measured yet (see the roadmap).

## Demo scenarios

Each demo resets a broken fixture, crashes it for real, sends the crash to the engine, and deploys the patch.

| Script | Fixture | Bug |
|---|---|---|
| `run_live_demo.py` | `payment_gateway.broken.py` | `ZeroDivisionError` on an empty cart, unbound `discount` variable |
| `run_local_simulation.py` | `app_target_demo.broken.py` | `TypeError` from concatenating a string with an int |
| `run_billing_demo.py` | `billing_engine.broken.py` | `ZeroDivisionError` on an empty order |

Before/after examples of generated patches are in [`examples/`](examples/). Gemini is not deterministic, so a run may produce different code.

## Quick start

Requires Python 3.10+ (developed on 3.13) and a [Gemini API key](https://aistudio.google.com/app/apikey).

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # Windows: copy .env.example .env
```

Edit `.env`:

```
GEMINI_API_KEY=your-gemini-key
SHIP_ADMIN_TOKEN=<generate one, see below>
SAFE_SANDBOX_DIR=<absolute path of this project folder>
```

Generate a token:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Run the server and, in a second terminal, a demo:

```bash
uvicorn app:app
python run_live_demo.py
python app_target_demo.py     # after run_local_simulation.py, to see the healed result
```

The demos call Gemini, so they use your API quota.

```bash
pytest                        # unit tests for server_math.py
python verify_security.py     # checks the API rejects bad requests (server must be running)
```

## API

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/v1/intercept-log` | `X-Ship-Token` | Body: `error_log`, `broken_code`, `target_file`. Runs both agents, stores the incident. |
| `POST /api/v1/deploy-patch/{incident_id}` | `X-Ship-Token` | Writes the stored patch to the incident's target file. |
| `GET /metrics` | none | Prometheus metrics. |
| `WS /ws/telemetry` | none | Live incident events for the dashboard. |

Send `X-Trace-ID` to correlate a request across logs.

## Security controls

Verified by `verify_security.py` (all expected to pass):

- A request without a token is rejected (`422`), a wrong token is rejected (`403`).
- `target_file` must be on an allowlist (`ALLOWED_TARGET_FILES` in `app.py`). `app.py`, `config.py`, and `../app.py` are rejected (`422`).
- Oversized `error_log` input is rejected (`422`).

Also in the code, not covered by a dedicated test: a sandbox boundary check at deploy time, and a `pip-audit` dependency scan at startup.

## Observability

`structlog` JSON logs carrying the trace ID, `X-Trace-ID` propagation, a Prometheus `/metrics` endpoint, and a real-time dashboard (Jinja2, Tailwind CSS, Chart.js).

## Known limitations

These are real, not hypothetical. Read them before using this on anything.

| Limitation | Consequence |
|---|---|
| Patches overwrite the target file directly, with no backup and no rollback | A bad patch cannot be undone from within the tool |
| The output "sanitizer" only strips markdown code fences. It does not validate the code | A patch can be syntactically valid yet wrong, or unsafe |
| Tests do not gate deployment | A patch that fixes one failure can break other behavior |
| No check that the file changed between crash and deploy | Two patches for the same file can overwrite each other |
| The sandbox directory is the whole project folder, protected only by the allowlist | The sandbox is not a real isolation boundary |
| One shared admin token, no per-user access control, no rate limit | Not suitable for multiple users |
| The WebSocket endpoint is not authenticated | Incident data can be read by anyone who can reach the server |
| No evaluation of success rate or latency | There is no honest figure for how often it fixes a bug |
| Uses the deprecated `google-generativeai` package | Migration to `google-genai` is planned |
| Diagnosis comes from an LLM and can be wrong | A wrong diagnosis produces a wrong patch |
| The patch replaces the whole file | The model can change code outside the bug (observed once: it added extra calls to a demo block) |

## Roadmap

Planned, in this order:

1. Move to the `google-genai` SDK.
2. **Safety loop:** AST validation of patches, run the tests in a temporary copy before deploying, backup and rollback, file-hash check to reject stale patches, optional human approval.
3. Docker, `docker-compose`, and CI (tests plus `verify_security.py` on every push).
4. Deliver patches as pull requests instead of overwriting files.
5. Per-project API keys, rate limiting, Postgres, a job queue.
6. An evaluation benchmark: a set of bug types, with success rate, time, and token cost per incident.
7. A public playground using fixed scenarios, so no visitor-supplied code runs on the server.

Completed so far: async FastAPI core and SQLite storage, two-agent chain, token authentication and path restrictions, WebSocket dashboard, tracing, structured logging, Prometheus metrics, demo fixtures, security verification script.

## Tech stack

Python, FastAPI, SQLAlchemy (async) with SQLite (`aiosqlite`), Pydantic Settings, Google Gemini (`gemini-2.5-flash`), structlog, `prometheus-fastapi-instrumentator`, Pytest, `pip-audit`, Jinja2, Tailwind CSS, Chart.js.