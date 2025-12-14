from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter(
    prefix="/api/items",
    tags=["items"]
)


@router.get("/")
async def list_items(skip: int = 0, limit: int = 10):
    """アイテム一覧を取得"""
    return {
        "items": [],
        "skip": skip,
        "limit": limit,
        "total": 0
    }


@router.get("/{item_id}")
async def read_item(item_id: int, q: Optional[str] = Query(None)):
    """アイテムを取得する"""
    return {"item_id": item_id, "q": q}


@router.post("/")
async def create_item(name: str, description: Optional[str] = None):
    """新しいアイテムを作成"""
    return {
        "id": 1,
        "name": name,
        "description": description
    }


@router.put("/{item_id}")
async def update_item(item_id: int, name: str, description: Optional[str] = None):
    """アイテムを更新"""
    return {
        "id": item_id,
        "name": name,
        "description": description
    }


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """アイテムを削除"""
    return {"message": f"Item {item_id} deleted"}

