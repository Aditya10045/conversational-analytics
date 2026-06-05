from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_orchestrator
from app.models.chat import ChatRequest, ChatResponse
from app.services.orchestrator import AnalyticsOrchestrator

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    orchestrator: AnalyticsOrchestrator = Depends(get_orchestrator),
) -> ChatResponse:
    try:
        return orchestrator.handle_message(payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}") from exc
