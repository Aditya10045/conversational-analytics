from __future__ import annotations

import json
from statistics import mean
from typing import Any

from app.core.config import Settings
from app.models.chat import ChatRequest, ChatResponse, SQLExecutionStats
from app.prompts.insight_generation import build_insight_system_prompt
from app.prompts.sql_generation import build_sql_system_prompt
from app.services.query_executor import QueryExecutor
from app.services.schema_context import SchemaContextBuilder
from app.services.semantic_cache import SemanticCache
from app.services.session_manager import SessionManager, SessionTurn
from app.utils.sql_validator import SQLValidator


class AnalyticsOrchestrator:
    def __init__(
        self,
        *,
        settings: Settings,
        session_manager: SessionManager,
        schema_builder: SchemaContextBuilder,
        query_executor: QueryExecutor,
        llm_service,
        semantic_cache: SemanticCache,
    ) -> None:
        self.settings = settings
        self.session_manager = session_manager
        self.schema_builder = schema_builder
        self.query_executor = query_executor
        self.llm_service = llm_service
        self.semantic_cache = semantic_cache
        self.sql_validator = SQLValidator(
            allowed_tables=settings.allowed_tables,
            dialect=settings.warehouse_dialect,
            max_rows=settings.max_result_rows,
        )

    @staticmethod
    def _numeric_aggregates(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        if not rows:
            return {}

        buckets: dict[str, list[float]] = {}
        for row in rows:
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    buckets.setdefault(key, []).append(float(value))

        aggregates: dict[str, dict[str, float]] = {}
        for key, values in buckets.items():
            if not values:
                continue
            aggregates[key] = {
                "min": min(values),
                "max": max(values),
                "avg": mean(values),
            }
        return aggregates

    def _build_sql_user_prompt(self, *, question: str, history_text: str, schema_prompt: str) -> str:
        return (
            "Use this schema context:\n"
            f"{schema_prompt}\n\n"
            "Conversation history:\n"
            f"{history_text}\n\n"
            "User question:\n"
            f"{question}"
        )

    def _build_sql_repair_user_prompt(
        self,
        *,
        question: str,
        history_text: str,
        schema_prompt: str,
        failed_sql: str,
        error_detail: str,
    ) -> str:
        return (
            "Regenerate the SQL using only existing tables/columns from schema context.\n"
            "Fix the failure and preserve user intent.\n\n"
            "Use this schema context:\n"
            f"{schema_prompt}\n\n"
            "Conversation history:\n"
            f"{history_text}\n\n"
            "User question:\n"
            f"{question}\n\n"
            "Failed SQL:\n"
            f"{failed_sql}\n\n"
            "Execution error:\n"
            f"{error_detail}"
        )

    @staticmethod
    def _is_retryable_sql_error(error_text: str) -> bool:
        lowered = error_text.lower()
        return "does not exist" in lowered and (
            "column" in lowered or "undefinedcolumn" in lowered
        )

    def _build_insight_user_prompt(
        self,
        *,
        question: str,
        sql: str,
        rows: list[dict[str, Any]],
        columns: list[str],
        execution_ms: int,
    ) -> str:
        row_sample = rows[:200]
        payload = {
            "question": question,
            "executed_sql": sql,
            "columns": columns,
            "row_count": len(rows),
            "execution_ms": execution_ms,
            "numeric_aggregates": self._numeric_aggregates(rows),
            "rows_sample": row_sample,
            "rows_truncated_for_prompt": len(rows) > len(row_sample),
        }
        return json.dumps(payload, ensure_ascii=True, indent=2)

    def handle_message(self, payload: ChatRequest) -> ChatResponse:
        session_id = self.session_manager.get_or_create_session(payload.session_id)
        history_text = self.session_manager.format_history_for_prompt(session_id)
        schema_context = self.schema_builder.get_schema_context()

        cache_key = self.semantic_cache.build_key(
            question=payload.message,
            schema_fingerprint=schema_context.prompt,
            history=history_text,
        )
        cached_response = self.semantic_cache.get(cache_key)
        if cached_response:
            response = ChatResponse(**cached_response, session_id=session_id)
            self.session_manager.append_turn(
                session_id,
                SessionTurn(
                    user_message=payload.message,
                    sql=response.sql,
                    assistant_summary=response.executive_summary,
                ),
            )
            return response

        sql_system_prompt = build_sql_system_prompt(
            warehouse_dialect=self.settings.warehouse_dialect,
            allowed_tables=self.settings.allowed_tables,
            max_rows=self.settings.max_result_rows,
            business_rules=self.settings.business_rules,
        )
        sql_user_prompt = self._build_sql_user_prompt(
            question=payload.message,
            history_text=history_text,
            schema_prompt=schema_context.prompt,
        )

        sql_plan = self.llm_service.generate_sql(
            system_prompt=sql_system_prompt,
            user_prompt=sql_user_prompt,
        )

        validation = self.sql_validator.validate_and_rewrite(sql_plan.sql)

        try:
            query_result = self.query_executor.execute(validation.safe_sql)
        except ValueError as exc:
            if not self._is_retryable_sql_error(str(exc)):
                raise

            repair_prompt = self._build_sql_repair_user_prompt(
                question=payload.message,
                history_text=history_text,
                schema_prompt=schema_context.prompt,
                failed_sql=validation.safe_sql,
                error_detail=str(exc),
            )
            repaired_sql_plan = self.llm_service.generate_sql(
                system_prompt=sql_system_prompt,
                user_prompt=repair_prompt,
            )
            validation = self.sql_validator.validate_and_rewrite(repaired_sql_plan.sql)
            query_result = self.query_executor.execute(validation.safe_sql)
            sql_plan = repaired_sql_plan

        insight_system_prompt = build_insight_system_prompt()
        insight_user_prompt = self._build_insight_user_prompt(
            question=payload.message,
            sql=validation.safe_sql,
            rows=query_result.rows,
            columns=query_result.columns,
            execution_ms=query_result.execution_ms,
        )
        insights = self.llm_service.generate_insights(
            system_prompt=insight_system_prompt,
            user_prompt=insight_user_prompt,
        )

        response = ChatResponse(
            session_id=session_id,
            answer=insights.answer,
            executive_summary=insights.executive_summary,
            sql=validation.safe_sql,
            sql_explanation=sql_plan.explanation or "Query generated from user intent and schema context.",
            chart_recommendation=sql_plan.chart_recommendation,
            rows=query_result.rows,
            columns=query_result.columns,
            stats=SQLExecutionStats(
                rows_returned=len(query_result.rows),
                execution_ms=query_result.execution_ms,
                timed_out=query_result.timed_out,
            ),
            key_findings=insights.key_findings,
            trends=insights.trends,
            anomalies=insights.anomalies,
            recommendations=insights.recommendations,
            follow_up_questions=insights.follow_up_questions,
            caveats=insights.caveats,
        )

        self.session_manager.append_turn(
            session_id,
            SessionTurn(
                user_message=payload.message,
                sql=response.sql,
                assistant_summary=response.executive_summary,
            ),
        )

        response_payload = response.model_dump()
        self.semantic_cache.set(cache_key, response_payload)
        return response
