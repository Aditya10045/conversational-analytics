from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from time import perf_counter
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class QueryExecutionResult:
    rows: list[dict[str, Any]]
    columns: list[str]
    execution_ms: int
    timed_out: bool


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class QueryExecutor:
    def __init__(self, *, engine: Engine, dialect: str, timeout_ms: int) -> None:
        self.engine = engine
        self.dialect = dialect
        self.timeout_ms = timeout_ms

    def execute(self, sql: str) -> QueryExecutionResult:
        started = perf_counter()
        timed_out = False

        try:
            with self.engine.begin() as conn:
                if self.dialect.startswith("postgres"):
                 conn.execute(text(f"SET LOCAL statement_timeout = {self.timeout_ms}"))

                result = conn.execute(text(sql))
                rows = [dict(row) for row in result.mappings().all()]
                columns = list(result.keys())
        except SQLAlchemyError as exc:
            message = str(exc).lower()
            if "statement timeout" in message or "canceling statement due to statement timeout" in message:
                timed_out = True
                raise ValueError("Query timed out. Try narrowing scope or adding filters.") from exc
            raise ValueError(f"SQL execution failed: {exc}") from exc

        execution_ms = int((perf_counter() - started) * 1000)
        normalized_rows = [{key: _to_jsonable(value) for key, value in row.items()} for row in rows]

        return QueryExecutionResult(
            rows=normalized_rows,
            columns=columns,
            execution_ms=execution_ms,
            timed_out=timed_out,
        )
