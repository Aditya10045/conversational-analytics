import hashlib
import json
from typing import Any

from cachetools import TTLCache


class SemanticCache:
    def __init__(self, *, enabled: bool, ttl_seconds: int, maxsize: int = 500) -> None:
        self.enabled = enabled
        self.cache: TTLCache[str, dict[str, Any]] = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def build_key(self, *, question: str, schema_fingerprint: str, history: str) -> str:
        payload = {
            "question": question.strip().lower(),
            "schema_fingerprint": schema_fingerprint,
            "history": history[-1200:],  # keep key compact while preserving recent context
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return digest

    def get(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        return self.cache.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.cache[key] = value
