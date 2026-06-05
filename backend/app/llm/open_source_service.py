from __future__ import annotations

from typing import Any

from openai import BadRequestError, OpenAI

from app.models.chat import InsightOutput, SQLGenerationOutput
from app.utils.json_parser import extract_json_object


SQL_OUTPUT_SCHEMA: dict[str, Any] = {
    "name": "sql_generation_output",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "sql": {"type": "string"},
            "explanation": {"type": "string"},
            "chart_recommendation": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["bar", "line", "pie", "table"]},
                    "x_axis": {"type": "string"},
                    "y_axis": {"type": "string"},
                },
                "required": ["type", "x_axis", "y_axis"],
                "additionalProperties": False,
            },
        },
        "required": ["sql", "explanation", "chart_recommendation"],
        "additionalProperties": False,
    },
}


INSIGHT_OUTPUT_SCHEMA: dict[str, Any] = {
    "name": "insight_generation_output",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "executive_summary": {"type": "string"},
            "key_findings": {"type": "array", "items": {"type": "string"}},
            "trends": {"type": "array", "items": {"type": "string"}},
            "anomalies": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
            "follow_up_questions": {"type": "array", "items": {"type": "string"}},
            "caveats": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "answer",
            "executive_summary",
            "key_findings",
            "trends",
            "anomalies",
            "recommendations",
            "follow_up_questions",
            "caveats",
        ],
        "additionalProperties": False,
    },
}


class OpenSourceLLMService:
    """
    OpenAI-compatible LLM integration with separate model routes for:
    - pass 1 SQL generation
    - pass 2 insight generation

    Supports providers like OpenRouter and Groq through base_url + API key.
    """

    def __init__(
        self,
        *,
        sql_api_key: str | None,
        sql_base_url: str,
        sql_model: str,
        sql_provider: str,
        insight_api_key: str | None,
        insight_base_url: str,
        insight_model: str,
        insight_provider: str,
        sql_max_tokens: int,
        insight_max_tokens: int,
        use_json_schema: bool,
        openrouter_app_url: str | None = None,
        openrouter_app_name: str | None = None,
    ) -> None:
        if not sql_api_key:
            raise ValueError("Missing SQL model API key. Set SQL_LLM_API_KEY or OPENROUTER_API_KEY.")
        if not insight_api_key:
            raise ValueError("Missing insight model API key. Set INSIGHT_LLM_API_KEY or GROQ_API_KEY.")

        self.sql_model = sql_model
        self.sql_provider = sql_provider
        self.sql_max_tokens = sql_max_tokens

        self.insight_model = insight_model
        self.insight_provider = insight_provider
        self.insight_max_tokens = insight_max_tokens
        self.use_json_schema = use_json_schema

        self.sql_client = self._build_client(
            api_key=sql_api_key,
            base_url=sql_base_url,
            openrouter_app_url=openrouter_app_url,
            openrouter_app_name=openrouter_app_name,
        )
        self.insight_client = self._build_client(
            api_key=insight_api_key,
            base_url=insight_base_url,
            openrouter_app_url=openrouter_app_url,
            openrouter_app_name=openrouter_app_name,
        )

    @staticmethod
    def _build_client(
        *,
        api_key: str,
        base_url: str,
        openrouter_app_url: str | None,
        openrouter_app_name: str | None,
    ) -> OpenAI:
        base = base_url.rstrip("/")
        headers: dict[str, str] = {}

        if "openrouter.ai" in base:
            if openrouter_app_url:
                headers["HTTP-Referer"] = openrouter_app_url
            if openrouter_app_name:
                headers["X-OpenRouter-Title"] = openrouter_app_name

        return OpenAI(api_key=api_key, base_url=base, default_headers=headers or None)

    @staticmethod
    def _extract_text(response: Any) -> str:
        choices = getattr(response, "choices", None)
        if not choices:
            raise ValueError("LLM response did not include choices.")

        message = choices[0].message
        content = getattr(message, "content", None)

        if isinstance(content, str):
            text = content.strip()
            if text:
                return text

        if isinstance(content, list):
            chunks: list[str] = []
            for part in content:
                if isinstance(part, str):
                    chunks.append(part)
                    continue
                if isinstance(part, dict):
                    part_text = part.get("text") or part.get("content")
                    if isinstance(part_text, str):
                        chunks.append(part_text)
            joined = "\n".join(chunks).strip()
            if joined:
                return joined

        raise ValueError("LLM returned empty content.")

    def _chat_completion(
        self,
        *,
        client: OpenAI,
        model: str,
        max_tokens: int,
        temperature: float,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
    ) -> str:
        request_payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if self.use_json_schema:
            request_payload["response_format"] = {
                "type": "json_schema",
                "json_schema": schema,
            }

        try:
            response = client.chat.completions.create(**request_payload)
        except BadRequestError as exc:
            error_text = str(exc).lower()
            schema_related = any(
                token in error_text
                for token in ["response_format", "json_schema", "structured output", "unsupported"]
            )
            if not self.use_json_schema or not schema_related:
                raise

            # Fallback for model/provider routes that do not support json_schema.
            request_payload.pop("response_format", None)
            response = client.chat.completions.create(**request_payload)

        return self._extract_text(response)

    def generate_sql(self, *, system_prompt: str, user_prompt: str) -> SQLGenerationOutput:
        text = self._chat_completion(
            client=self.sql_client,
            model=self.sql_model,
            max_tokens=self.sql_max_tokens,
            temperature=0.01,  # near deterministic; Groq does not accept exact zero for some models
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=SQL_OUTPUT_SCHEMA,
        )
        parsed = extract_json_object(text)
        return SQLGenerationOutput.model_validate(parsed)

    def generate_insights(self, *, system_prompt: str, user_prompt: str) -> InsightOutput:
        text = self._chat_completion(
            client=self.insight_client,
            model=self.insight_model,
            max_tokens=self.insight_max_tokens,
            temperature=0.2,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=INSIGHT_OUTPUT_SCHEMA,
        )
        parsed = extract_json_object(text)
        return InsightOutput.model_validate(parsed)
