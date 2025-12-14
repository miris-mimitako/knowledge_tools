from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlite_db import get_sqlite_connection
import sqlite3


router = APIRouter(
    prefix="/queue",
    tags=["queue"]
)


class EnqueueRequest(BaseModel):
    """キュー登録リクエストモデル"""
    file_path: str = Body(..., description="登録するファイルパス")
    priority: int = Body(0, description="優先度（高い方が先に処理）")


def process_file(file_path: str):
    """ファイルを処理"""
    print(f"ファイルを処理: {file_path}")
    pass


@router.get("/queue_list")
async def get_queue_list():
    """キュー一覧を取得"""
    try:
        conn = get_sqlite_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, file_path, status, priority, retry_count, 
                       created_at, updated_at, started_at, completed_at
                FROM file_processing_queue
                ORDER BY priority DESC, created_at ASC
            """)
            rows = cursor.fetchall()
            
            queue_list = []
            for row in rows:
                queue_list.append({
                    "id": row["id"],
                    "file_path": row["file_path"],
                    "status": row["status"],
                    "priority": row["priority"],
                    "retry_count": row["retry_count"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"]
                })
            
            return {"queue_list": queue_list, "count": len(queue_list)}
        finally:
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"キュー一覧取得エラー: {str(e)}")


@router.post("/enqueue")
async def enqueue(request: EnqueueRequest):
    """キューにファイルを追加"""
    try:
        conn = get_sqlite_connection()
        try:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO file_processing_queue 
                (file_path, status, priority, retry_count, error_message, 
                 file_hash, metadata, created_at, updated_at, started_at, completed_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.file_path, "PENDING", request.priority, 0, None, 
                None, None, now, now, None, None
            ))
            
            conn.commit()
            queue_id = cursor.lastrowid
            
            return {
                "message": "キューに登録されました",
                "queue_id": queue_id,
                "file_path": request.file_path,
                "status": "PENDING",
                "priority": request.priority
            }
        finally:
            conn.close()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"ファイルは既にキューに登録されています: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"キュー登録エラー: {str(e)}")


@router.post("/dequeue")
async def dequeue(request: EnqueueRequest):
    """キューへ登録（互換性のためのエイリアス）"""
    # priorityを0に設定してenqueueを呼び出す
    request.priority = 0
    return await enqueue(request)