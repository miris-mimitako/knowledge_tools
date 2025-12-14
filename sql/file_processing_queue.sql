CREATE TABLE file_processing_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,       -- 処理対象のファイルパス（重複登録防止）
    status TEXT NOT NULL DEFAULT 'PENDING', -- 状態管理 (詳細は後述)
    priority INTEGER DEFAULT 0,           -- 優先度 (高い方が先に処理)
    retry_count INTEGER DEFAULT 0,        -- リトライ回数
    error_message TEXT,                   -- エラー時のログ
    file_hash TEXT,                       -- ファイルの内容ハッシュ (変更検知用: オプション)
    metadata TEXT,                        -- JSON形式でその他属性 (ファイルサイズ, MIMEタイプなど)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,                  -- 処理開始時刻
    completed_at DATETIME                 -- 処理完了時刻
);

-- 検索・取り出しを高速化するためのインデックス
CREATE INDEX idx_queue_status_priority ON file_processing_queue (status, priority DESC, created_at ASC);
CREATE INDEX idx_queue_file_path ON file_processing_queue (file_path);