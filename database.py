"""LanceDB接続管理モジュール"""
import lancedb
import os
from pathlib import Path

# データベースディレクトリ
DB_DIR = Path("data/lancedb")
DB_DIR.mkdir(parents=True, exist_ok=True)

# グローバル接続インスタンス
_db_connection = None


def get_db_connection(uri: str = None):
    """LanceDB接続を取得（シングルトン）"""
    global _db_connection
    
    if _db_connection is None:
        if uri is None:
            # デフォルトはローカルディレクトリ
            uri = str(DB_DIR.absolute())
        
        _db_connection = lancedb.connect(uri)
    
    return _db_connection


def reset_connection():
    """接続をリセット（テスト用）"""
    global _db_connection
    _db_connection = None

