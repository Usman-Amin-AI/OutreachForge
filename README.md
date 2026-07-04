# OutreachForge

OutreachForge is a production-ready multi-agent orchestration framework for outbound sales automation and personalized email outreach. It provides a FastAPI backend, structured task orchestration, async campaign execution, Postgres CRM-style lead storage, observability with OpenTelemetry, and CI/CD-ready testing.

## Architecture

```mermaid
flowchart TB
    subgraph Legacy
        NOTEBOOK[\"Notebook Prototype\"]
    end
    subgraph Platform
        PACKAGE[\"OutreachForge Package\"]
        API[\"FastAPI Backend\"]
        QUEUE[\"Celery / Redis Queue\"]
        DB[\"Postgres Lead Store\"]
        AGENTS[\"Agent Modules\"]
        OBS[\"OpenTelemetry / OTLP Tracing\"]
        WORKER[\"Campaign Worker\"]
    end

    NOTEBOOK --> PACKAGE
    PACKAGE --> API
    PACKAGE --> AGENTS
    API --> QUEUE
    QUEUE --> WORKER
    API --> DB
    AGENTS --> LLM[\"LLM + Search Tools\"]
    AGENTS --> OBS
    API --> OBS
    WORKER --> AGENTS
    DB --> LEADSTORE[\"CRM Deduplicated Lead Store\"]
``` 

## Features

- Modular agent architecture for search, NER, sales profiling, lead outreach, and email writing
- FastAPI production service with both sync and async campaign execution paths
- Celery + Redis task queue for concurrent campaign processing
- Postgres CRM-style lead storage with deduplication by email and lead/company pair
- OpenTelemetry tracing for agent and backend observability
- Built-in email quality evaluation and human-review flagging
- Unit and integration tests with mocked LLM behavior
- GitHub Actions CI for linting, type checking, and tests on PRs

## Getting Started

1. Create a Python environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -e .
   ```
2. Copy `.env.example` to `.env` and populate the required values.
3. Install dev dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. Start supporting infrastructure:
   - Redis: `redis-server`
   - Postgres: create the database and user
   - OTLP collector: run your chosen OTEL backend
5. Run the FastAPI app:
   ```bash
   uvicorn outreachforge.app:app --reload
   ```
6. Start the Celery worker:
   ```bash
   celery -A outreachforge.tasks_async.celery_app worker --loglevel=info
   ```

## API Endpoints

- `POST /run-campaign` - run a campaign synchronously and return a quality report
- `POST /campaigns` - enqueue a campaign for async execution
- `GET /campaigns/{task_id}` - query async campaign status
- `POST /evaluate-email` - evaluate email quality for acceptance or review
- `POST /leads` - create/update CRM lead records with deduplication
- `GET /leads` - retrieve recent leads

## Testing

Run the full suite:
```bash
pytest --cov=outreachforge
```

## CI/CD

The GitHub Actions workflow at `.github/workflows/ci.yml` runs on every pull request and includes:
- `ruff check .` for linting
- `mypy outreachforge tests` for type checking
- `pytest --cov=outreachforge --cov-report=term-missing` for tests

## Observability

OpenTelemetry is configured via `outreachforge/tracing.py` and the app instruments FastAPI requests. Configure OTLP exporter values in `.env`:
- `OTLP_ENDPOINT`
- `OTLP_INSECURE`


## Deployment Steps

1. Set environment variables in `.env`, including `REDIS_URL`, `DATABASE_URL`, and OTLP settings.
2. Deploy the FastAPI app behind a production server.
3. Start Celery workers with access to the same Redis broker.
4. Ensure Postgres is available and reachable.
5. Verify traces in your OTLP-compatible backend.
