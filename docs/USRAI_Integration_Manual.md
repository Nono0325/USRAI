# USRAI 整合專案手冊

## 1. 專案目標

USRAI 是整合型 USR 展示與 AI 輔助系統，將水井村風雲客棧網站與智慧養殖 AI 助理整合成同一個 Django 專案。

使用者可透過網站瀏覽活動、課程、故事、USR 成果與 AIoT 技術，也可以使用右下角 AI 助理查詢魚塭水質狀況。

## 2. 系統角色

### 一般訪客

- 瀏覽首頁與導覽頁
- 查看活動與課程
- 報名課程
- 查詢自己的報名紀錄
- 使用 AI 助理查詢魚塭水質
- 送出聯絡表單

### 管理員

- 進入 Django 後台管理內容
- 管理活動、課程、故事、USR 成果
- 查看報名資料
- 匯出簽到表
- 使用 QR Code 報到核銷
- 管理魚塭與水質資料

## 3. 核心功能

### 3.1 風雲客棧網站

- 首頁輪播
- 三生共好服務介紹
- 在地故事
- USR 成果展示
- AIoT 科技導覽
- 活動列表與活動詳情
- 課程列表與課程報名
- 我的報名查詢
- 聯絡我們

### 3.2 AI 聊天助理

右下角固定圖標可開啟 AI 對話框。對話框不會隨頁面捲動移動。

支援模式：

- 水質：查詢指定魚塭最新水質
- 異常：判斷指定魚塭是否有異常
- 平均：查詢指定魚塭平均溶氧
- 魚塭：列出可查詢魚塭

範例問題：

```text
1 號池現在正常嗎？
查詢所有魚塭
2 號池最近 7 天平均溶氧是多少？
3 號池水質有異常嗎？
```

### 3.3 全站互動動畫

- 全站等待 loader
- AI 回覆輸入動畫
- 聊天模式滑動切換動畫
- 卡片 hover 動畫
- 頁面滾動淡入動畫

## 4. 安裝方式

### 4.1 建立虛擬環境

```powershell
python -m venv .venv
```

### 4.2 安裝套件

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4.3 建立環境變數

在專案根目錄新增 `.env`：

```env
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
ALLOWED_HOSTS=*
```

### 4.4 建立資料庫

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 4.5 匯入測試資料

```powershell
.\.venv\Scripts\python.exe manage.py seed_water --reset
.\.venv\Scripts\python.exe create_admin.py
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe seed_events.py
.\.venv\Scripts\python.exe seed_portal.py
.\.venv\Scripts\python.exe create_default_template.py
```

### 4.6 啟動網站

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

開啟：

```text
http://127.0.0.1:8000/
```

## 5. 管理員資訊

```text
後台網址：http://127.0.0.1:8000/admin/Nono/
帳號：cmlin
密碼：12345678
```

正式部署前請更改預設密碼。

## 6. AI 工具資料

AI 助理使用 `chat/tools.py` 中的工具查詢 `water` app 的資料。

目前工具：

- `list_ponds`
- `get_latest_water_quality`
- `get_average_do`
- `get_water_quality_history`
- `check_thresholds`

水質示範資料由以下指令建立：

```powershell
.\.venv\Scripts\python.exe manage.py seed_water --reset
```

## 7. 部署注意事項

正式部署時建議：

- 使用 PostgreSQL
- 設定正式 `SECRET_KEY`
- 設定 `OPENAI_API_KEY`
- 設定 `DEBUG=False`
- 設定正確 `ALLOWED_HOSTS`
- 執行 `collectstatic`
- 不要上傳 `.env`、`.venv/`、`db.sqlite3`

## 8. 常見問題

### AI 顯示缺少 OPENAI_API_KEY

確認 `.env` 中有：

```env
OPENAI_API_KEY=你的 OpenAI API Key
```

修改 `.env` 後需要重新啟動 Django server。

### 頁面沒有圖片

`media/` 預設不建議提交到 GitHub。正式環境需重新上傳媒體檔案，或改用雲端儲存。

### GitHub repo 是空的

空 repo 需要先建立第一個 commit，請參考 `docs/GitHub_Upload_Guide.md`。
