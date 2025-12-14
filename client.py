from nicegui import ui
import httpx
import asyncio

# FastAPIサーバーのURL
API_URL = "http://localhost:8000"

# グローバル変数で結果を保持
result_text = None
status_label = None


async def call_api(endpoint: str = "/"):
    """FastAPIエンドポイントを呼び出す"""
    global result_text, status_label
    
    try:
        status_label.text = "リクエスト送信中..."
        status_label.classes("text-blue-500")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_URL}{endpoint}")
            response.raise_for_status()
            data = response.json()
            
            # 結果を表示
            result_text.text = f"レスポンス:\n{data}"
            status_label.text = f"成功 (ステータス: {response.status_code})"
            status_label.classes("text-green-500")
            
    except httpx.ConnectError:
        result_text.text = "エラー: FastAPIサーバーに接続できません。\nサーバーが起動しているか確認してください。"
        status_label.text = "接続エラー"
        status_label.classes("text-red-500")
    except httpx.HTTPStatusError as e:
        result_text.text = f"HTTPエラー: {e.response.status_code}\n{e.response.text}"
        status_label.text = f"HTTPエラー ({e.response.status_code})"
        status_label.classes("text-red-500")
    except Exception as e:
        result_text.text = f"エラー: {str(e)}"
        status_label.text = "エラー"
        status_label.classes("text-red-500")


def send_request(endpoint: str = "/"):
    """非同期リクエストを実行"""
    asyncio.create_task(call_api(endpoint))


def create_navigation():
    """ナビゲーションバーを作成"""
    with ui.row().classes("w-full bg-blue-600 text-white p-4 gap-4 shadow-lg"):
        ui.link("ホーム", "/").classes("text-white hover:text-blue-200 px-4 py-2 rounded")
        ui.link("API テスト", "/api-test").classes("text-white hover:text-blue-200 px-4 py-2 rounded")
        ui.link("AI モデル", "/ai-models").classes("text-white hover:text-blue-200 px-4 py-2 rounded")
        ui.link("アイテム管理", "/items").classes("text-white hover:text-blue-200 px-4 py-2 rounded")


@ui.page("/")
def main_page():
    """メインページ"""
    ui.page_title("ホーム - FastAPI クライアント")
    
    create_navigation()
    
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-4"):
        ui.label("FastAPI クライアント").classes("text-4xl font-bold mb-4")
        ui.label("FastAPIサーバーに接続してAPIをテストできます").classes("text-lg text-gray-600 mb-6")
        
        with ui.row().classes("gap-4 w-full"):
            with ui.card().classes("p-6 flex-1"):
                ui.label("API テスト").classes("text-2xl font-bold mb-2")
                ui.label("FastAPIのエンドポイントをテストします").classes("text-gray-600 mb-4")
                ui.link("ページを開く", "/api-test").classes("bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded")
            
            with ui.card().classes("p-6 flex-1"):
                ui.label("AI モデル").classes("text-2xl font-bold mb-2")
                ui.label("利用可能なAIモデル一覧を表示します").classes("text-gray-600 mb-4")
                ui.link("ページを開く", "/ai-models").classes("bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded")
            
            with ui.card().classes("p-6 flex-1"):
                ui.label("アイテム管理").classes("text-2xl font-bold mb-2")
                ui.label("アイテムのCRUD操作を行います").classes("text-gray-600 mb-4")
                ui.link("ページを開く", "/items").classes("bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded")


@ui.page("/api-test")
def api_test_page():
    """APIテストページ"""
    global result_text, status_label
    
    ui.page_title("API テスト - FastAPI クライアント")
    
    create_navigation()
    
    with ui.column().classes("w-full max-w-2xl mx-auto p-8 gap-4"):
        ui.label("API テスト").classes("text-3xl font-bold mb-4")
        
        ui.label("FastAPIサーバーに問い合わせます").classes("text-lg text-gray-600 mb-6")
        
        # ステータス表示
        status_label = ui.label("待機中").classes("text-lg font-semibold")
        
        # ボタン群
        with ui.row().classes("gap-4 mb-4"):
            ui.button("Hello World (/)", on_click=lambda: send_request("/")).classes("bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded")
            ui.button("Health Check (/health)", on_click=lambda: send_request("/health")).classes("bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded")
        
        # カスタムエンドポイント入力
        with ui.row().classes("w-full gap-2 mb-4"):
            custom_endpoint = ui.input("エンドポイント", placeholder="/api/items/1").classes("flex-1")
            ui.button("送信", on_click=lambda: send_request(custom_endpoint.value or "/")).classes("bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded")
        
        # 結果表示エリア
        ui.label("結果:").classes("text-lg font-semibold mt-4")
        result_text = ui.label("ここに結果が表示されます").classes("bg-gray-100 p-4 rounded border min-h-[100px] whitespace-pre-wrap")
        
        # サーバーURL表示
        ui.label(f"接続先: {API_URL}").classes("text-sm text-gray-500 mt-4")


@ui.page("/ai-models")
def ai_models_page():
    """AIモデル一覧ページ"""
    ui.page_title("AI モデル - FastAPI クライアント")
    
    create_navigation()
    
    models_result = ui.label("読み込み中...").classes("bg-gray-100 p-4 rounded border")
    
    async def load_models():
        """AIモデル一覧を読み込む"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{API_URL}/ai/models")
                response.raise_for_status()
                data = response.json()
                
                models_result.text = ""
                with models_result:
                    models_result.text = ""
                    with ui.column().classes("gap-2"):
                        for model in data.get("models", []):
                            with ui.card().classes("p-4"):
                                ui.label(model.get("name", "Unknown")).classes("text-xl font-bold")
                                ui.label(model.get("description", "")).classes("text-gray-600")
                                ui.label(f"ID: {model.get('id', '')}").classes("text-sm text-gray-500")
        except Exception as e:
            models_result.text = f"エラー: {str(e)}"
    
    asyncio.create_task(load_models())
    
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-4"):
        ui.label("AI モデル一覧").classes("text-3xl font-bold mb-4")
        ui.button("再読み込み", on_click=lambda: asyncio.create_task(load_models())).classes("bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded mb-4")
        models_result


@ui.page("/items")
def items_page():
    """アイテム管理ページ"""
    ui.page_title("アイテム管理 - FastAPI クライアント")
    
    create_navigation()
    
    items_result = ui.label("").classes("bg-gray-100 p-4 rounded border")
    
    async def load_items():
        """アイテム一覧を読み込む"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{API_URL}/api/items/")
                response.raise_for_status()
                data = response.json()
                
                items_result.text = ""
                with items_result:
                    items_result.text = ""
                    ui.label(f"アイテム数: {data.get('total', 0)}").classes("text-lg font-semibold mb-2")
                    if data.get("items"):
                        with ui.column().classes("gap-2"):
                            for item in data.get("items", []):
                                with ui.card().classes("p-4"):
                                    ui.label(f"ID: {item.get('id', 'N/A')}").classes("font-bold")
                    else:
                        ui.label("アイテムがありません").classes("text-gray-500")
        except Exception as e:
            items_result.text = f"エラー: {str(e)}"
    
    asyncio.create_task(load_items())
    
    with ui.column().classes("w-full max-w-4xl mx-auto p-8 gap-4"):
        ui.label("アイテム管理").classes("text-3xl font-bold mb-4")
        ui.button("再読み込み", on_click=lambda: asyncio.create_task(load_items())).classes("bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded mb-4")
        items_result


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="FastAPI HelloWorld クライアント", port=8080)

