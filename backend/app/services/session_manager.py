from dataclasses import dataclass
from threading import Lock
from uuid import uuid4


@dataclass
class SessionTurn:
    user_message: str
    sql: str
    assistant_summary: str


class SessionManager:
    def __init__(self, *, max_turns: int = 20) -> None:
        self.max_turns = max_turns
        self._sessions: dict[str, list[SessionTurn]] = {}
        self._lock = Lock()

    def get_or_create_session(self, session_id: str | None) -> str:
        with self._lock:
            resolved = session_id or str(uuid4())
            self._sessions.setdefault(resolved, [])
            return resolved

    def get_turns(self, session_id: str) -> list[SessionTurn]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append_turn(self, session_id: str, turn: SessionTurn) -> None:
        with self._lock:
            history = self._sessions.setdefault(session_id, [])
            history.append(turn)
            if len(history) > self.max_turns:
                self._sessions[session_id] = history[-self.max_turns :]

    def format_history_for_prompt(self, session_id: str, *, max_items: int = 6) -> str:
        turns = self.get_turns(session_id)[-max_items:]
        if not turns:
            return "No prior context."

        lines: list[str] = []
        for idx, turn in enumerate(turns, start=1):
            lines.append(f"Turn {idx} - User: {turn.user_message}")
            lines.append(f"Turn {idx} - SQL: {turn.sql}")
            lines.append(f"Turn {idx} - Assistant: {turn.assistant_summary}")
        return "\n".join(lines)
