# FastAPIサーバーのベースURL
$BASE_URL = "http://localhost:8000"

Write-Host "=== キュー一覧を取得 ===" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$BASE_URL/queue/queue_list" -Method Get -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "=== キューにファイルを追加（優先度1） ===" -ForegroundColor Cyan
$body = @{
    file_path = "/path/to/file.txt"
    priority = 1
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BASE_URL/queue/enqueue" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "=== キューにファイルを追加（優先度0、デフォルト） ===" -ForegroundColor Cyan
$body = @{
    file_path = "C:/Users/example/document.pdf"
    priority = 0
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BASE_URL/queue/enqueue" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "=== キューにファイルを追加（dequeueエンドポイント） ===" -ForegroundColor Cyan
$body = @{
    file_path = "/data/files/example.xlsx"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BASE_URL/queue/dequeue" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host ""

Write-Host "=== キュー一覧を再取得（確認用） ===" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "$BASE_URL/queue/queue_list" -Method Get -ContentType "application/json"
$response | ConvertTo-Json -Depth 10
Write-Host ""

