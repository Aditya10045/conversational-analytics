from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ChartRecommendation(BaseModel):
    type: Literal["bar", "line", "pie", "table"] = "table"
    x_axis: str | None = None
    y_axis: str | None = None


class SQLGenerationOutput(BaseModel):
    sql: str
    explanation: str = ""
    chart_recommendation: ChartRecommendation = Field(default_factory=ChartRecommendation)


class InsightOutput(BaseModel):
    answer: str
    executive_summary: str
    key_findings: list[str] = Field(default_factory=list)
    trends: list[str] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=2, max_length=5000)
    user_id: str | None = None


class SQLExecutionStats(BaseModel):
    rows_returned: int
    execution_ms: int
    timed_out: bool = False


class ChatResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    answer: str
    executive_summary: str
    sql: str
    sql_explanation: str
    chart_recommendation: ChartRecommendation
    rows: list[dict[str, Any]]
    columns: list[str]
    stats: SQLExecutionStats
    key_findings: list[str] = Field(default_factory=list)
    trends: list[str] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
