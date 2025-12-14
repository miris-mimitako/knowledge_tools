import queue
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from routers import items, health, ai, db, queue
from sqlite_db import ensure_table_exists

app = FastAPI(
    title="Knowledge Tools API",
    description="FastAPI初期プロジェクト",
    version="1.0.0"
)

# SQLite3テーブルの存在確認と作成
ensure_table_exists("file_processing_queue", "sql/file_processing_queue.sql")

# ルーターを登録
app.include_router(items.router)
app.include_router(health.router)
app.include_router(ai.router)
app.include_router(db.router)
app.include_router(queue.router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Hello World"}

