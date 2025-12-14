from fastapi import APIRouter
from pydantic_core.core_schema import ModelSchema

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

MODELS = [
    {
        "id": "qwen/qwen3-embedding-8b",
        "name": "qwen/qwen3-embedding-8b",
        "description": "Embedding model for qwen/qwen3-embedding-8b"
    },
    {
        "id": "openai/gpt-5.2",
        "name": "openai/gpt-5.2",
        "description": "openai/gpt-5.2 Text model"
    },
    {
        "id": "google/gemini-3-pro-preview",
        "name": "google/gemini-3-pro-preview",
        "description": "google/gemini-3-pro-preview Text model"
    },
    {
        "id": "openai/gpt-oss-120b",
        "name": "openai/gpt-oss-120b",
        "description": "openai/gpt-oss-120b Text model"
    }
]

@router.get("/models")
async def get_models():
    """AIモデル一覧を取得"""
    return {"models": MODELS}


