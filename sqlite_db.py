"""SQLite3接続管理モジュール"""
import sqlite3
import os
from pathlib import Path

# データベースファイルのパス
DB_FILE = Path("data/knowledge_tools.db")
DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_sqlite_connection():
    """SQLite3接続を取得"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row  # 辞書形式で結果を取得できるようにする
    return conn


def table_exists(table_name: str) -> bool:
    """テーブルが存在するか確認"""
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        result = cursor.fetchone()
        return result is not None
    finally:
        conn.close()


def create_table_from_sql_file(sql_file_path: str):
    """SQLファイルからテーブルを作成"""
    sql_path = Path(sql_file_path)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQLファイルが見つかりません: {sql_file_path}")
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        # SQLスクリプトを実行（複数のステートメントに対応）
        cursor.executescript(sql_script)
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"テーブル作成エラー: {str(e)}")
    finally:
        conn.close()


def ensure_table_exists(table_name: str, sql_file_path: str):
    """テーブルが存在しない場合、SQLファイルから作成"""
    if not table_exists(table_name):
        print(f"テーブル '{table_name}' が存在しません。作成します...")
        create_table_from_sql_file(sql_file_path)
        print(f"テーブル '{table_name}' を作成しました。")
    else:
        print(f"テーブル '{table_name}' は既に存在します。")

