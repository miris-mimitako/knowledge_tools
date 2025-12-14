from fastapi import APIRouter, HTTPException
from database import get_db_connection, DB_DIR
import lancedb
from lancedb.pydantic import LanceModel, Vector
from datetime import datetime

router = APIRouter(
    prefix="/db",
    tags=["db"]
)
# ベクトルの次元数 (例: OpenAI text-embedding-3-small)
VECTOR_DIM = 4096
class File(LanceModel):
    file_id: str            # ファイルの一意なID (UUIDなど)
    filename: str           # ファイル名 (例: "contract_2024.pdf")
    file_path: str          # ファイルの場所 (S3パスやURL)
    file_type: str          # 拡張子
    created_at: datetime    # ファイル作成日
    active: bool = True     # チャンクがアクティブかどうか
    file_size: int = 0      # ファイルサイズ
    file_hash: str = ""     # ファイルのハッシュ
    file_last_modified: datetime = datetime.now() # ファイルの最終更新日
    file_owner: str = ""    # ファイルの所有者
    file_revision: str = "" # ファイルのリビジョン
    file_tags: list[str] = [] # ファイルのタグ
    file_pages: list[int] = [] # ファイルのページ
    category: str = "general" # ファイルのカテゴリ


class DocChunk(LanceModel):
    # ---------------------------------------------------------
    # 1. ベクトルデータ (Vector Data)
    # ---------------------------------------------------------
    # 検索の主役となるフィールド
    vector: Vector(VECTOR_DIM)

    # ---------------------------------------------------------
    # 2. テキストデータ & チャンクデータ (Text & Chunk Data)
    # ---------------------------------------------------------
    # チャンクごとのテキスト内容
    text: str
    
    # チャンク自身のメタデータ
    chunk_id: int           # ファイル内での連番 (0, 1, 2...)
    char_start: int         # 元ファイル内での開始文字位置
    char_end: int           # 元ファイル内での終了文字位置
    token_count: int        # (任意) トークン数

    # ---------------------------------------------------------
    # 3. ファイルのメタデータ (File Metadata)
    # ---------------------------------------------------------
    # ※検索フィルタリング用に、各チャンクにファイルの情報を付与します
    file_id: str            # ファイルの一意なID (UUIDなど)
    filename: str           # ファイル名 (例: "contract_2024.pdf")
    file_path: str          # ファイルの場所 (S3パスやURL)
    file_type: str          # 拡張子
    created_at: datetime    # ファイル作成日
    active: bool = True     # チャンクがアクティブかどうか
    file_size: int = 0      # ファイルサイズ
    file_hash: str = ""     # ファイルのハッシュ
    file_last_modified: datetime = datetime.now() # ファイルの最終更新日
    file_owner: str = ""    # ファイルの所有者
    file_revision: str = "" # ファイルのリビジョン
    file_tags: list[str] = [] # ファイルのタグ
    file_pages: list[int] = [] # ファイルのページ


    
    # 必要に応じてカテゴリやタグを追加
    category: str = "general"




# ---------------------------------------------------------
# テーブル作成用コード
# ---------------------------------------------------------
def create_flat_table():
    """フラットなスキーマでテーブルを作成"""
    # database.pyで定義した接続管理を使用
    db = get_db_connection()
    
    # テーブル名 'raw_texts' で作成
    table = db.create_table(
        "raw_texts",
        schema=DocChunk,
        mode="overwrite"  # 本番環境では "create" または "exist_ok=True"
    )
    
    print(f"Table '{table.name}' created successfully with flat schema.")
    return table

@router.get("/connect")
async def connect_db(uri: str = None):
    """LanceDBに接続"""
    try:
        db = get_db_connection(uri)
        
        # テーブル一覧を取得
        table_names = db.table_names()
        
        return {
            "status": "connected",
            "uri": str(DB_DIR.absolute()) if uri is None else uri,
            "tables": table_names,
            "table_count": len(table_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"接続エラー: {str(e)}")


@router.get("/tables")
async def list_tables():
    """テーブル一覧を取得"""
    try:
        db = get_db_connection()
        table_names = db.table_names()
        
        return {
            "tables": table_names,
            "count": len(table_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラー: {str(e)}")


@router.get("/status")
async def db_status():
    """データベースの状態を取得"""
    try:
        db = get_db_connection()
        table_names = db.table_names()
        
        return {
            "connected": True,
            "uri": str(DB_DIR.absolute()),
            "table_count": len(table_names),
            "tables": table_names
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }

