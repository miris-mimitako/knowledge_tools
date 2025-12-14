"""テキストファイル読み込みモジュール"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TextFileData(BaseModel):
    """テキストファイルデータのPydanticモデル"""
    file_path: str = Field(..., description="ファイルの絶対パス")
    filename: str = Field(..., description="ファイル名")
    file_type: str = Field(..., description="ファイル拡張子")
    encoding: str = Field(..., description="検出されたエンコーディング")
    content: str = Field(..., description="ファイルの内容")
    line_count: int = Field(..., ge=0, description="行数")
    char_count: int = Field(..., ge=0, description="文字数")
    word_count: int = Field(..., ge=0, description="単語数")
    is_binary: bool = Field(..., description="バイナリファイルかどうか")
    extracted_at: str = Field(..., description="抽出日時（ISO形式）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/file.txt",
                "filename": "file.txt",
                "file_type": ".txt",
                "encoding": "utf-8",
                "content": "Sample text...",
                "line_count": 10,
                "char_count": 100,
                "word_count": 15,
                "is_binary": False,
                "extracted_at": "2024-01-01T00:00:00"
            }
        }


class TextChunkData(BaseModel):
    """テキストチャンクデータのPydanticモデル"""
    chunk_id: int = Field(..., ge=0, description="チャンクID")
    line_start: int = Field(..., ge=0, description="開始行番号")
    line_end: int = Field(..., ge=0, description="終了行番号")
    text: str = Field(..., description="チャンクのテキスト")
    char_count: int = Field(..., ge=0, description="文字数")


def detect_encoding(file_path: str) -> str:
    """
    ファイルのエンコーディングを検出
    
    Args:
        file_path: ファイルパス
        
    Returns:
        検出されたエンコーディング（デフォルト: utf-8）
    """
    try:
        import chardet
    except ImportError:
        # chardetが利用できない場合は、UTF-8とCP932を試す
        return _try_encodings(file_path)
    
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 最初の10KBを読み込んで検出
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            
            # 信頼度が低い場合は、UTF-8とCP932を試す
            if result.get('confidence', 0) < 0.7:
                return _try_encodings(file_path)
            
            return encoding.lower()
    except Exception:
        return _try_encodings(file_path)


def _try_encodings(file_path: str) -> str:
    """
    UTF-8とCP932を試して読み込めるエンコーディングを返す
    
    Args:
        file_path: ファイルパス
        
    Returns:
        読み込めるエンコーディング
    """
    encodings = ['utf-8', 'cp932', 'shift_jis', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    # どれも失敗した場合はUTF-8を返す（エラーは後で発生する）
    return 'utf-8'


def is_text_file(file_path: str) -> bool:
    """
    ファイルがテキストファイルかどうかを判定
    
    Args:
        file_path: ファイルパス
        
    Returns:
        テキストファイルかどうか
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    # テキストファイルの拡張子リスト
    text_extensions = {
        '.txt', '.md', '.markdown', '.rst', '.log',
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
        '.html', '.htm', '.xml', '.css', '.scss', '.sass', '.less',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.sql', '.r', '.m', '.pl', '.pm', '.lua', '.vim', '.vimrc',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
        '.json', '.jsonl', '.csv', '.tsv',
        '.dockerfile', '.gitignore', '.gitattributes', '.env',
        '.makefile', '.cmake', '.gradle', '.properties',
        '.tex', '.bib', '.sty', '.cls'
    }
    
    return ext in text_extensions


def read_text_file(file_path: str, encoding: Optional[str] = None) -> TextFileData:
    """
    テキストファイルを読み込む
    
    Args:
        file_path: テキストファイルのパス
        encoding: エンコーディング（Noneの場合は自動検出）
        
    Returns:
        テキストファイルデータのPydanticモデル
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: テキストファイルとして読み込めない場合
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"ファイルではありません: {file_path}")
    
    # エンコーディングを検出
    if encoding is None:
        detected_encoding = detect_encoding(file_path)
    else:
        detected_encoding = encoding
    
    # バイナリファイルかどうかを判定
    is_binary = not is_text_file(file_path)
    
    # ファイルを読み込む
    try:
        with open(path, 'r', encoding=detected_encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        # 指定されたエンコーディングで読み込めない場合は、再検出を試みる
        if encoding is not None:
            detected_encoding = detect_encoding(file_path)
            with open(path, 'r', encoding=detected_encoding) as f:
                content = f.read()
        else:
            raise ValueError(f"ファイルをテキストとして読み込めません: {file_path}")
    
    # 統計情報を計算
    lines = content.splitlines()
    line_count = len(lines)
    char_count = len(content)
    word_count = len(content.split()) if content else 0
    
    return TextFileData(
        file_path=str(path.absolute()),
        filename=path.name,
        file_type=path.suffix.lower(),
        encoding=detected_encoding,
        content=content,
        line_count=line_count,
        char_count=char_count,
        word_count=word_count,
        is_binary=is_binary,
        extracted_at=datetime.now().isoformat()
    )


def read_text_file_simple(file_path: str, encoding: Optional[str] = None) -> str:
    """
    テキストファイルを読み込んで、シンプルな文字列として返す
    
    Args:
        file_path: テキストファイルのパス
        encoding: エンコーディング（Noneの場合は自動検出）
        
    Returns:
        ファイルの内容
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: テキストファイルとして読み込めない場合
    """
    text_data = read_text_file(file_path, encoding)
    return text_data.content


def read_text_file_lines(file_path: str, encoding: Optional[str] = None) -> List[str]:
    """
    テキストファイルを読み込んで、行のリストとして返す
    
    Args:
        file_path: テキストファイルのパス
        encoding: エンコーディング（Noneの場合は自動検出）
        
    Returns:
        行のリスト
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: テキストファイルとして読み込めない場合
    """
    text_data = read_text_file(file_path, encoding)
    return text_data.content.splitlines()


def extract_text_to_chunks(
    file_path: str, 
    chunk_size: int = 1000,
    encoding: Optional[str] = None
) -> List[TextChunkData]:
    """
    テキストファイルを読み込んで、チャンク単位でテキストを抽出
    
    Args:
        file_path: テキストファイルのパス
        chunk_size: チャンクサイズ（文字数）
        encoding: エンコーディング（Noneの場合は自動検出）
        
    Returns:
        チャンクのリスト
    """
    text_data = read_text_file(file_path, encoding)
    lines = text_data.content.splitlines()
    
    chunks = []
    chunk_id = 0
    current_chunk = ""
    current_chunk_lines = []
    line_start = 0
    
    for line_idx, line in enumerate(lines):
        line_text = line + "\n"  # 改行を含める
        
        if len(current_chunk) + len(line_text) > chunk_size and current_chunk:
            # チャンクを保存
            chunks.append(TextChunkData(
                chunk_id=chunk_id,
                line_start=line_start,
                line_end=line_idx - 1,
                text=current_chunk.rstrip(),
                char_count=len(current_chunk)
            ))
            chunk_id += 1
            current_chunk = ""
            line_start = line_idx
        
        current_chunk += line_text
        current_chunk_lines.append(line_idx)
    
    # 最後のチャンクを保存
    if current_chunk.strip():
        chunks.append(TextChunkData(
            chunk_id=chunk_id,
            line_start=line_start,
            line_end=len(lines) - 1,
            text=current_chunk.rstrip(),
            char_count=len(current_chunk)
        ))
    
    return chunks


def read_text_file_by_lines(
    file_path: str,
    start_line: int = 0,
    end_line: Optional[int] = None,
    encoding: Optional[str] = None
) -> str:
    """
    テキストファイルの指定された行範囲を読み込む
    
    Args:
        file_path: テキストファイルのパス
        start_line: 開始行番号（0から始まる）
        end_line: 終了行番号（Noneの場合は最後まで）
        encoding: エンコーディング（Noneの場合は自動検出）
        
    Returns:
        指定された行範囲のテキスト
        
    Raises:
        FileNotFoundError: ファイルが存在しない場合
        ValueError: テキストファイルとして読み込めない場合
    """
    lines = read_text_file_lines(file_path, encoding)
    
    if end_line is None:
        end_line = len(lines)
    
    # 範囲をチェック
    start_line = max(0, start_line)
    end_line = min(len(lines), end_line)
    
    if start_line >= end_line:
        return ""
    
    selected_lines = lines[start_line:end_line]
    return "\n".join(selected_lines)

