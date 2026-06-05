from __future__ import annotations

from time import time

from pydantic import BaseModel, Field
from sqlalchemy import inspect
from sqlalchemy.engine import Engine


class ColumnInfo(BaseModel):
    name: str
    type: str
    description: str | None = None


class TableInfo(BaseModel):
    schema_name: str
    name: str
    description: str | None = None
    columns: list[ColumnInfo] = Field(default_factory=list)


class SchemaContext(BaseModel):
    warehouse_schema: str
    allowed_tables: list[str]
    tables: list[TableInfo]
    missing_tables: list[str]
    prompt: str


class SchemaContextBuilder:
    def __init__(self, *, engine: Engine, warehouse_schema: str, allowed_tables: list[str]) -> None:
        self.engine = engine
        self.warehouse_schema = warehouse_schema
        self.allowed_tables = allowed_tables
        self._cached_context: SchemaContext | None = None
        self._cached_at: float = 0
        self._cache_seconds = 300

    @staticmethod
    def _split_table_identifier(table_identifier: str, default_schema: str) -> tuple[str, str]:
        if "." not in table_identifier:
            return default_schema, table_identifier
        schema, table = table_identifier.split(".", 1)
        return schema, table

    def _build_prompt(self, tables: list[TableInfo], missing_tables: list[str]) -> str:
        sections: list[str] = []
        for table in tables:
            columns = ", ".join(f"{col.name} ({col.type})" for col in table.columns)
            table_title = f"{table.schema_name}.{table.name}"
            table_description = table.description or "No table description available."
            sections.append(f"- {table_title}: {table_description}\n  Columns: {columns}")

        missing = ", ".join(missing_tables) if missing_tables else "None"
        return (
            "Warehouse schema context:\n"
            f"Missing tables from whitelist: {missing}\n"
            + "\n".join(sections)
        )

    def get_schema_context(self, *, force_refresh: bool = False) -> SchemaContext:
        if (
            not force_refresh
            and self._cached_context is not None
            and (time() - self._cached_at) < self._cache_seconds
        ):
            return self._cached_context

        inspector = inspect(self.engine)

        tables: list[TableInfo] = []
        missing_tables: list[str] = []
        table_cache_by_schema: dict[str, set[str]] = {}
        view_cache_by_schema: dict[str, set[str]] = {}

        for raw_table in self.allowed_tables:
            schema, table_name = self._split_table_identifier(raw_table, self.warehouse_schema)

            if schema not in table_cache_by_schema:
                table_cache_by_schema[schema] = set(inspector.get_table_names(schema=schema))
                view_cache_by_schema[schema] = set(inspector.get_view_names(schema=schema))

            available_tables = table_cache_by_schema[schema] | view_cache_by_schema[schema]
            if table_name not in available_tables:
                missing_tables.append(raw_table)
                continue

            columns_meta = inspector.get_columns(table_name, schema=schema)

            try:
                table_description = inspector.get_table_comment(table_name, schema=schema).get("text")
            except Exception:
                table_description = None

            columns = [
                ColumnInfo(
                    name=col.get("name", ""),
                    type=str(col.get("type", "unknown")),
                    description=col.get("comment"),
                )
                for col in columns_meta
            ]

            tables.append(TableInfo(schema_name=schema, name=table_name, description=table_description, columns=columns))

        prompt = self._build_prompt(tables=tables, missing_tables=missing_tables)
        context = SchemaContext(
            warehouse_schema=self.warehouse_schema,
            allowed_tables=self.allowed_tables,
            tables=tables,
            missing_tables=missing_tables,
            prompt=prompt,
        )

        self._cached_context = context
        self._cached_at = time()
        return context
