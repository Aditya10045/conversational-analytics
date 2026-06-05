from fastapi import APIRouter, Depends

from app.api.dependencies import get_schema_builder
from app.services.schema_context import SchemaContextBuilder

router = APIRouter()


@router.get("/schema")
def get_schema(schema_builder: SchemaContextBuilder = Depends(get_schema_builder)) -> dict:
    context = schema_builder.get_schema_context()
    return context.model_dump()
