#!/bin/bash

# FastAPIサーバーのベースURL
BASE_URL="http://localhost:8000"

echo "=== キュー一覧を取得 ==="
curl -X GET "${BASE_URL}/queue/queue_list" -H "Content-Type: application/json"
echo -e "\n"

echo "=== キューにファイルを追加（優先度1） ==="
curl -X POST "${BASE_URL}/queue/enqueue" -H "Content-Type: application/json" -d '{"file_path": "/path/to/file.txt", "priority": 1}'
echo -e "\n"

echo "=== キューにファイルを追加（優先度0、デフォルト） ==="
curl -X POST "${BASE_URL}/queue/enqueue" -H "Content-Type: application/json" -d '{"file_path": "C:/Users/example/document.pdf", "priority": 0}'
echo -e "\n"

echo "=== キューにファイルを追加（dequeueエンドポイント） ==="
curl -X POST "${BASE_URL}/queue/dequeue" -H "Content-Type: application/json" -d '{"file_path": "/data/files/example.xlsx"}'
echo -e "\n"

echo "=== キュー一覧を再取得（確認用） ==="
curl -X GET "${BASE_URL}/queue/queue_list" -H "Content-Type: application/json"
echo -e "\n"

