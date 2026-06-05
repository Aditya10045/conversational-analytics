# Conversational Analytics MVP (Open-Source Models + SQL Warehouse)

This project is a full-stack MVP for conversational analytics using a **two-pass Text-to-SQL architecture** with open-source models.

- Pass 1 (SQL generation): coder model (OpenRouter)
- Pass 2 (insight generation): reasoning model (Groq/OpenRouter)
- Backend: FastAPI + SQLAlchemy + sqlglot guardrails
- Frontend: Next.js + Tailwind + Recharts

## What Changed

The stack is now optimized for your open-source model strategy:

- Replaced Claude-only integration with **OpenAI-compatible provider routing**
- Added **separate model/provider config for each pass**
- Added **JSON schema structured output enforcement** (`response_format: json_schema`) with automatic fallback for unsupported routes
- Kept strict SQL validation/security boundary in middleware

## Two-Pass Flow

1. User asks a question in chat UI
2. Backend sends schema + business rules + question to pass-1 model
3. Pass-1 model returns strict JSON: `sql`, `explanation`, `chart_recommendation`
4. Backend validates SQL (`sqlglot`) and executes read-only query
5. Backend sends SQL + result rows + aggregates to pass-2 model
6. Pass-2 model returns structured business insights JSON
7. Frontend renders narrative, SQL, chart, and table

## Security Guardrails

- Read-only DB user (`analytics_ro`)
- Table whitelist (`ALLOWED_TABLES`)
- SQL AST validation with `sqlglot`
- Rejects:
  - comments
  - semicolons
  - multi-statements
  - DDL/DML (INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/...)
  - unknown tables
- Auto-adds `LIMIT` if absent
- Query timeout via `SET LOCAL statement_timeout`

## Model Routing Configuration

Use separate API routes/models per pass:

- **Pass 1 (SQL):** OpenRouter + `qwen/qwen-2.5-coder-32b-instruct` (default)
- **Pass 2 (Insights):** Groq + `openai/gpt-oss-120b` (default)

You can swap models without code changes using env vars.

## Environment Variables

### Root `.env`

```bash
OPENROUTER_API_KEY=your_openrouter_api_key
GROQ_API_KEY=your_groq_api_key
```

### Backend `backend/.env`

Copy from [backend/.env.example](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\backend\.env.example).

Important fields:

- `SQL_LLM_BASE_URL` (default `https://openrouter.ai/api/v1`)
- `SQL_LLM_MODEL`
- `SQL_LLM_API_KEY` (or `OPENROUTER_API_KEY`)
- `INSIGHT_LLM_BASE_URL` (default `https://api.groq.com/openai/v1`)
- `INSIGHT_LLM_MODEL`
- `INSIGHT_LLM_API_KEY` (or `GROQ_API_KEY`)
- `LLM_USE_JSON_SCHEMA=true`
- `DATABASE_URL`
- `ALLOWED_TABLES`

### Frontend `frontend/.env`

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## Run with Docker

1. Copy root env:

```bash
cp .env.example .env
```

2. Add keys to `.env`

3. Start:

```bash
docker compose up --build
```

4. Open:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Sample Questions

- Which regions had highest growth last quarter?
- Show monthly revenue trend by region for the last 6 months.
- Which customer segment has the strongest gross margin?
- Compare quarter-over-quarter margin change by region.

## Key Files

- API dependency wiring: [backend/app/api/dependencies.py](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\backend\app\api\dependencies.py)
- Open-source LLM integration: [backend/app/llm/open_source_service.py](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\backend\app\llm\open_source_service.py)
- SQL guardrails: [backend/app/utils/sql_validator.py](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\backend\app\utils\sql_validator.py)
- Orchestrator: [backend/app/services/orchestrator.py](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\backend\app\services\orchestrator.py)
- Seeded demo schema/data: [sample_data/init.sql](C:\Users\adity\Documents\Codex\2026-05-28\think-like-an-expert-llm-solution\sample_data\init.sql)
