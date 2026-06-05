from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Conversational Analytics API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")

    # Shared optional key fallback for both passes.
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")

    # Pass 1 (SQL generation) model route.
    sql_llm_provider: str = Field(default="openrouter", alias="SQL_LLM_PROVIDER")
    sql_llm_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="SQL_LLM_BASE_URL")
    sql_llm_model: str = Field(default="qwen/qwen-2.5-coder-32b-instruct", alias="SQL_LLM_MODEL")
    sql_llm_api_key: str | None = Field(default=None, alias="SQL_LLM_API_KEY")

    # Pass 2 (insight generation) model route.
    insight_llm_provider: str = Field(default="groq", alias="INSIGHT_LLM_PROVIDER")
    insight_llm_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="INSIGHT_LLM_BASE_URL")
    insight_llm_model: str = Field(default="openai/gpt-oss-120b", alias="INSIGHT_LLM_MODEL")
    insight_llm_api_key: str | None = Field(default=None, alias="INSIGHT_LLM_API_KEY")

    # Provider-scoped fallback keys.
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")

    # Optional OpenRouter attribution headers.
    openrouter_app_url: str | None = Field(default=None, alias="OPENROUTER_APP_URL")
    openrouter_app_name: str | None = Field(default=None, alias="OPENROUTER_APP_NAME")

    llm_use_json_schema: bool = Field(default=True, alias="LLM_USE_JSON_SCHEMA")

    database_url: str = Field(alias="DATABASE_URL")
    warehouse_dialect: str = Field(default="postgres", alias="WAREHOUSE_DIALECT")
    warehouse_schema: str = Field(default="public", alias="WAREHOUSE_SCHEMA")
    allowed_tables_raw: str = Field(alias="ALLOWED_TABLES")

    max_result_rows: int = Field(default=500, alias="MAX_RESULT_ROWS")
    sql_query_timeout_ms: int = Field(default=15000, alias="SQL_QUERY_TIMEOUT_MS")
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    enable_semantic_cache: bool = Field(default=True, alias="ENABLE_SEMANTIC_CACHE")
    semantic_cache_ttl_seconds: int = Field(default=900, alias="SEMANTIC_CACHE_TTL_SECONDS")
    business_rules: str = Field(default="", alias="BUSINESS_RULES")

    sql_generation_max_tokens: int = 700
    insight_generation_max_tokens: int = 1200

    @property
    def resolved_sql_llm_api_key(self) -> str | None:
        return self.sql_llm_api_key or self.openrouter_api_key or self.groq_api_key or self.llm_api_key

    @property
    def resolved_insight_llm_api_key(self) -> str | None:
        return self.insight_llm_api_key or self.groq_api_key or self.openrouter_api_key or self.llm_api_key

    @property
    def allowed_tables(self) -> list[str]:
        return [item.strip() for item in self.allowed_tables_raw.split(",") if item.strip()]

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
