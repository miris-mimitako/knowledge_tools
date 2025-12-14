"""ファイル読み込みとメタ情報取得モジュール"""
import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any, List
import json
from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """ファイルメタ情報のPydanticモデル"""
    file_id: str = Field(..., description="ファイルの一意なID")
    filename: str = Field(..., description="ファイル名")
    file_path: str = Field(..., description="ファイルの絶対パス")
    file_type: str = Field(..., description="ファイル拡張子")
    file_size: int = Field(..., ge=0, description="ファイルサイズ（バイト）")
    file_hash: str = Field(..., description="ファイルのハッシュ値")
    mime_type: str = Field(..., description="MIMEタイプ")
    created_at: str = Field(..., description="作成日時（ISO形式）")
    file_last_modified: str = Field(..., description="最終更新日時（ISO形式）")
    file_owner: str = Field(default="", description="ファイルの所有者")
    file_revision: str = Field(default="", description="ファイルのリビジョン")
    file_tags: List[str] = Field(default_factory=list, description="ファイルのタグ")
    file_pages: List[int] = Field(default_factory=list, description="ファイルのページ番号リスト")
    category: str = Field(default="general", description="ファイルのカテゴリ")
    active: bool = Field(default=True, description="ファイルがアクティブかどうか")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "/path/to/file.txt",
                "filename": "file.txt",
                "file_path": "/path/to/file.txt",
                "file_type": ".txt",
                "file_size": 1024,
                "file_hash": "5d41402abc4b2a76b9719d911017c592",
                "mime_type": "text/plain",
                "created_at": "2024-01-01T00:00:00",
                "file_last_modified": "2024-01-01T00:00:00",
                "file_owner": "user",
                "file_revision": "",
                "file_tags": [],
                "file_pages": [],
                "category": "general",
                "active": True
            }
        }


def get_file_metadata(file_path: str) -> FileMetadata:
    """
    ファイルのメタ情報を取得
    
    Args:
        file_path: ファイルパス
        
    Returns:
        メタ情報のPydanticモデル
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        OSError: ファイルアクセスエラー
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"ファイルではありません: {file_path}")
    
    # 基本情報
    stat = path.stat()
    
    # ファイルハッシュ（MD5）
    file_hash = calculate_file_hash(file_path)
    
    # MIMEタイプ
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # 拡張子
    file_ext = path.suffix.lower()
    
    # メタ情報を構築してPydanticモデルとして返す
    return FileMetadata(
        file_id=str(path.absolute()),  # 一意なIDとして絶対パスを使用（実際はUUID推奨）
        filename=path.name,
        file_path=str(path.absolute()),
        file_type=file_ext,
        file_size=stat.st_size,
        file_hash=file_hash,
        mime_type=mime_type or "application/octet-stream",
        created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
        file_last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        file_owner=get_file_owner(file_path),
        file_revision="",  # バージョン管理システムから取得する場合は実装
        file_tags=[],  # タグは別途管理
        file_pages=[],  # PDFなどのページ情報は別途取得
        category="general",
        active=True
    )


def calculate_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    ファイルのハッシュ値を計算
    
    Args:
        file_path: ファイルパス
        algorithm: ハッシュアルゴリズム（md5, sha1, sha256）
        
    Returns:
        ハッシュ値（16進数文字列）
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        # 大きなファイルでもメモリ効率的に処理
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_file_owner(file_path: str) -> str:
    """
    ファイルの所有者を取得（Windows対応）
    
    Args:
        file_path: ファイルパス
        
    Returns:
        所有者名（取得できない場合は空文字列）
    """
    try:
        import win32security
        import win32api
        
        # ファイルのセキュリティ情報を取得
        sd = win32security.GetFileSecurity(
            file_path,
            win32security.OWNER_SECURITY_INFORMATION
        )
        owner_sid = sd.GetSecurityDescriptorOwner()
        owner_name, _, _ = win32security.LookupAccountSid(None, owner_sid)
        return owner_name
    except ImportError:
        # win32securityが利用できない場合は、環境変数から取得
        return os.environ.get("USERNAME", os.environ.get("USER", ""))
    except Exception:
        # エラーが発生した場合は空文字列を返す
        return ""


def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """
    テキストファイルの内容を読み込む
    
    Args:
        file_path: ファイルパス
        encoding: 文字エンコーディング（デフォルト: utf-8）
        
    Returns:
        ファイルの内容
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        UnicodeDecodeError: デコードエラー
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # UTF-8でデコードできない場合は、バイナリとして扱う
        raise ValueError(f"テキストファイルとして読み込めません: {file_path}")


def read_file_binary(file_path: str) -> bytes:
    """
    ファイルをバイナリとして読み込む
    
    Args:
        file_path: ファイルパス
        
    Returns:
        ファイルのバイナリデータ
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    with open(path, 'rb') as f:
        return f.read()


def get_file_info_summary(file_path: str) -> Dict[str, Any]:
    """
    ファイル情報のサマリーを取得（軽量版）
    
    Args:
        file_path: ファイルパス
        
    Returns:
        ファイル情報のサマリー
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "exists": False,
                "error": "ファイルが見つかりません"
            }
        
        stat = path.stat()
        
        return {
            "exists": True,
            "filename": path.name,
            "file_size": stat.st_size,
            "file_type": path.suffix.lower(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": path.is_file(),
            "is_directory": path.is_dir()
        }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }

