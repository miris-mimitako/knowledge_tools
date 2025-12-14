from fastapi import APIRouter

router = APIRouter(
    tags=["health"]
)


@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

