import re
from dataclasses import dataclass

import sqlglot
from sqlglot import exp


FORBIDDEN_NODE_NAMES = {
    "Insert",
    "Update",
    "Delete",
    "Drop",
    "Alter",
    "Create",
    "Truncate",
    "TruncateTable",
    "Command",
    "Grant",
    "Revoke",
    "Merge",
    "Copy",
    "Transaction",
}


@dataclass
class SQLValidationResult:
    safe_sql: str
    referenced_tables: list[str]


class SQLValidator:
    def __init__(self, *, allowed_tables: list[str], dialect: str, max_rows: int) -> None:
        self.dialect = dialect
        self.max_rows = max_rows
        self.allowed_normalized = self._normalize_allowed_tables(allowed_tables)

    @staticmethod
    def _normalize_identifier(name: str) -> str:
        return name.replace('"', "").replace("`", "").strip().lower()

    def _normalize_allowed_tables(self, tables: list[str]) -> set[str]:
        normalized: set[str] = set()
        for table in tables:
            clean = self._normalize_identifier(table)
            if not clean:
                continue
            normalized.add(clean)
            if "." in clean:
                normalized.add(clean.split(".")[-1])
        return normalized

    def _reject_unsafe_tokens(self, sql: str) -> None:
        if ";" in sql:
            sql = sql.strip().rstrip(";")
        if re.search(r"--|/\*|\*/", sql):
            raise ValueError("SQL comments are not allowed.")

    def validate_and_rewrite(self, sql: str) -> SQLValidationResult:
        sql = sql.strip()
        if not sql:
            raise ValueError("Generated SQL was empty.")

        self._reject_unsafe_tokens(sql)

        try:
            parsed_statements = sqlglot.parse(sql, read=self.dialect)
        except Exception as exc:
            raise ValueError(f"SQL parse error: {exc}") from exc

        if len(parsed_statements) != 1 or parsed_statements[0] is None:
            raise ValueError("Only one SQL statement is allowed.")

        parsed = parsed_statements[0]

        for node in parsed.walk():
            if node.__class__.__name__ in FORBIDDEN_NODE_NAMES:
                raise ValueError(f"Forbidden SQL operation detected: {node.__class__.__name__}")

        if parsed.find(exp.Select) is None:
            raise ValueError("Only SELECT queries are allowed.")

        cte_names = {cte.alias_or_name.lower() for cte in parsed.find_all(exp.CTE) if cte.alias_or_name}
        referenced_tables: list[str] = []

        for table in parsed.find_all(exp.Table):
            leaf = self._normalize_identifier(table.name or "")
            full = self._normalize_identifier(".".join(part.name for part in table.parts if getattr(part, "name", None)))

            if leaf in cte_names:
                continue

            if leaf not in self.allowed_normalized and full not in self.allowed_normalized:
                raise ValueError(f"Table not allowed: {full or leaf}")

            if full:
                referenced_tables.append(full)
            elif leaf:
                referenced_tables.append(leaf)

        if parsed.args.get("limit") is None:
            parsed = parsed.limit(self.max_rows, copy=False)

        safe_sql = parsed.sql(dialect=self.dialect, comments=False).strip()

        self._reject_unsafe_tokens(safe_sql)
        return SQLValidationResult(safe_sql=safe_sql, referenced_tables=sorted(set(referenced_tables)))
