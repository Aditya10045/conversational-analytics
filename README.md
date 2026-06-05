# Conversational Analytics

AI-powered conversational analytics platform that converts natural language questions into SQL, generates business insights, and visualizes data through interactive dashboards.

## Overview

Conversational Analytics enables users to explore business data using natural language instead of writing SQL manually.

The application uses a two-pass LLM architecture:

1. **Pass 1 – SQL Generation**

   * Converts user questions into SQL queries.
   * Produces explanations and chart recommendations.

2. **Pass 2 – Insight Generation**

   * Analyzes query results.
   * Generates business insights and summaries.

The platform includes SQL validation guardrails, read-only database access, interactive charts, and a modern chat-based user interface.

---

## Features

* Natural Language → SQL conversion
* AI-generated business insights
* Interactive data visualizations
* SQL query transparency
* Read-only database architecture
* Table-level access controls
* SQL validation using sqlglot
* Semantic caching support
* OpenRouter and Groq model integration
* Responsive Next.js frontend
* FastAPI backend

---

## Architecture

User Question

↓

LLM Pass 1 (Text-to-SQL)

↓

SQL Validation & Guardrails

↓

PostgreSQL Database

↓

LLM Pass 2 (Insight Generation)

↓

Charts + Insights + Results

---

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Recharts

### Backend

* FastAPI
* SQLAlchemy
* Pydantic
* Psycopg
* sqlglot

### AI Layer

* OpenRouter
* Groq
* DeepSeek Models
* Qwen Models

### Database

* PostgreSQL

---

## Project Structure

```text
conversational-analytics/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── analytics.db
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
│
├── sample_data/
│   └── init.sql
│
├── .env.example
└── README.md
```

---

## Environment Setup

### Backend

Create a `.env` file inside `backend/`.

Example:

```env
OPENROUTER_API_KEY=your_api_key

SQL_LLM_MODEL=deepseek/deepseek-chat-v3

INSIGHT_LLM_MODEL=deepseek/deepseek-chat-v3

INSIGHT_LLM_PROVIDER=openrouter
INSIGHT_LLM_BASE_URL=https://openrouter.ai/api/v1

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/analytics

ALLOWED_TABLES=sales_summary,orders,customers,revenue_by_region
```

### Frontend

Create a `.env` file inside `frontend/`.

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Local Installation

### Backend

```bash
cd backend

python -m venv .venv

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```text
http://localhost:3000
```

---

## Sample Questions

* Which region generated the highest revenue?
* Show monthly revenue trends for the last six months.
* Compare customer segments by sales performance.
* Which products contributed most to revenue growth?
* Show revenue distribution by region.

---

## Security Guardrails

The platform implements multiple protections:

* Read-only database access
* Table whitelist enforcement
* SQL AST validation
* Blocked DDL/DML operations
* Query timeout limits
* Automatic row limits
* Restricted schema access

Unsupported operations include:

* INSERT
* UPDATE
* DELETE
* DROP
* ALTER
* TRUNCATE

---

## Demo Data

This repository includes a sample analytics database populated with fictional business data for demonstration and development purposes.

No real customer or production data is included.

---

## Future Improvements

* Authentication and role-based access control
* Dashboard sharing
* Query history
* Export to CSV and Excel
* Multi-database support
* Advanced chart recommendations
* RAG-based business knowledge integration

---

## Author

Aditya S

Built as part of an AI-powered analytics and business intelligence learning project demonstrating LLM-based Text-to-SQL workflows, insight generation, and interactive data visualization.
