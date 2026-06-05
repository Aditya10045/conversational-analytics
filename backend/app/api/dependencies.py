from functools import lru_cache

from fastapi import HTTPException

from app.core.config import get_settings
from app.db.session import get_engine
from app.llm.open_source_service import OpenSourceLLMService
from app.services.orchestrator import AnalyticsOrchestrator
from app.services.query_executor import QueryExecutor
from app.services.schema_context import SchemaContextBuilder
from app.services.semantic_cache import SemanticCache
from app.services.session_manager import SessionManager


@lru_cache(maxsize=1)
def get_session_manager() -> SessionManager:
    return SessionManager(max_turns=20)


@lru_cache(maxsize=1)
def get_schema_builder() -> SchemaContextBuilder:
    settings = get_settings()
    return SchemaContextBuilder(
        engine=get_engine(),
        warehouse_schema=settings.warehouse_schema,
        allowed_tables=settings.allowed_tables,
    )


@lru_cache(maxsize=1)
def get_query_executor() -> QueryExecutor:
    settings = get_settings()
    return QueryExecutor(
        engine=get_engine(),
        dialect=settings.warehouse_dialect,
        timeout_ms=settings.sql_query_timeout_ms,
    )


@lru_cache(maxsize=1)
def get_llm_service() -> OpenSourceLLMService:
    settings = get_settings()
    try:
        return OpenSourceLLMService(
            sql_api_key=settings.resolved_sql_llm_api_key,
            sql_base_url=settings.sql_llm_base_url,
            sql_model=settings.sql_llm_model,
            sql_provider=settings.sql_llm_provider,
            insight_api_key=settings.resolved_insight_llm_api_key,
            insight_base_url=settings.insight_llm_base_url,
            insight_model=settings.insight_llm_model,
            insight_provider=settings.insight_llm_provider,
            sql_max_tokens=settings.sql_generation_max_tokens,
            insight_max_tokens=settings.insight_generation_max_tokens,
            use_json_schema=settings.llm_use_json_schema,
            openrouter_app_url=settings.openrouter_app_url,
            openrouter_app_name=settings.openrouter_app_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@lru_cache(maxsize=1)
def get_semantic_cache() -> SemanticCache:
    settings = get_settings()
    return SemanticCache(enabled=settings.enable_semantic_cache, ttl_seconds=settings.semantic_cache_ttl_seconds)


@lru_cache(maxsize=1)
def get_orchestrator() -> AnalyticsOrchestrator:
    settings = get_settings()
    return AnalyticsOrchestrator(
        settings=settings,
        session_manager=get_session_manager(),
        schema_builder=get_schema_builder(),
        query_executor=get_query_executor(),
        llm_service=get_llm_service(),
        semantic_cache=get_semantic_cache(),
    )
