from __future__ import annotations

import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

load_dotenv(Path(__file__).parent / ".env.local", override=True)

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

TABLE_SCHEMA = """
CREATE TABLE employees (
    employee_id        INT PRIMARY KEY,
    first_name         VARCHAR(100) NOT NULL,
    last_name          VARCHAR(100) NOT NULL,
    department         VARCHAR(100) NOT NULL,
    role               VARCHAR(100) NOT NULL,
    employment_status  VARCHAR(20) NOT NULL
        CHECK (employment_status IN ('Active', 'Terminated', 'On Leave')),
    hire_date          DATE NOT NULL,
    leave_type         VARCHAR(100) NULL,
    salary_local       DECIMAL(15,2) NOT NULL,
    salary_usd         DECIMAL(15,2) NOT NULL,
    manager_name       VARCHAR(200) NOT NULL
);
""".strip()


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def execute_sql(sql: str) -> tuple[list[str], list[dict[str, Any]]]:
    """Run a read-only SQL query and return (columns, rows)."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = [dict(row) for row in cur.fetchall()]
        return columns, rows
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# LLM helper – natural language → SQL
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a SQL expert. Given the following PostgreSQL table schema, convert the user's natural language question into a single valid SELECT query.

{TABLE_SCHEMA}

Rules:
- Output ONLY the SQL query — no markdown fences, no explanation.
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any DDL/DML that modifies data.
- Use ILIKE for case-insensitive text matching.
- If the question is ambiguous, make a reasonable assumption and return a query.
- Always qualify column names if needed to avoid ambiguity.
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def nl_to_sql(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    sql = response.choices[0].message.content.strip()
    sql = re.sub(r"^```(?:sql)?\s*", "", sql)
    sql = re.sub(r"\s*```$", "", sql)
    return sql


def validate_sql(sql: str) -> None:
    """Reject anything that isn't a SELECT statement."""
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
    forbidden = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}
    tokens = set(re.findall(r"\b[A-Z]+\b", normalized))
    if tokens & forbidden:
        raise HTTPException(status_code=400, detail="Query contains forbidden SQL keywords.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_db_connection()
    conn.close()
    yield

app = FastAPI(title="Employee Info Search", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    generated_sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


@app.post("/api/query", response_model=QueryResponse)
async def query_employees(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        sql = nl_to_sql(req.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

    validate_sql(sql)

    try:
        columns, rows = execute_sql(sql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {exc}")

    return QueryResponse(
        question=req.question,
        generated_sql=sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
