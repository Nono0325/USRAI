# USRAI - 水井村風雲客棧 AI 整合專案

本專案整合「水井村風雲客棧」入口網站與「水井 USR 智慧養殖 AI 專家系統」。

系統包含活動報名、在地故事、USR 成果展示、AIoT 科技導覽、後台管理、QR Code 報到，以及右下角固定式 AI 助理。AI 助理可查詢魚塭水質、平均溶氧、異常狀態與魚塭清單。

## 主要功能

- Django 5.2 網站平台
- Bootstrap 5 前端介面
- 全站美化與滾動淡入動畫
- 全站等待載入動畫
- 右下角固定 AI 聊天助理
- AI 回覆輸入動畫
- 聊天模式切換：水質、異常、平均、魚塭
- OpenAI Function Calling 水質查詢
- 活動、課程、故事、USR 成果與聯絡表單
- 後台管理與活動報名資料管理
- QR Code 報到與簽到表匯出

## 專案結構

```text
USRAI/
├── chat/                  # AI 聊天 API 與 OpenAI tool calling
├── water/                 # 魚塭與水質感測資料
├── inn_app/               # 風雲客棧主網站功能
├── fengyun/               # Django project settings / urls
├── templates/             # 全站與頁面模板
├── static/                # 靜態資源
├── docs/                  # 新增專案手冊
├── manage.py
├── requirements.txt
└── README.md
```

## 快速啟動

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_water --reset
.\.venv\Scripts\python.exe create_admin.py
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe seed_events.py
.\.venv\Scripts\python.exe seed_portal.py
.\.venv\Scripts\python.exe create_default_template.py
.\.venv\Scripts\python.exe manage.py runserver
```

啟動後開啟：

```text
http://127.0.0.1:8000/
```

## AI 設定

建立 `.env`：

```env
OPENAI_API_KEY=你的 OpenAI API Key
OPENAI_MODEL=gpt-4o-mini
DEBUG=True
ALLOWED_HOSTS=*
```

如果沒有設定 `OPENAI_API_KEY`，網站仍可瀏覽，但 AI 聊天回覆會顯示缺少金鑰的錯誤。

## 後台帳號

```text
後台網址：http://127.0.0.1:8000/admin/Nono/
帳號：cmlin
密碼：12345678
```

## 手冊

完整操作與部署說明請看：

- [USRAI 整合專案手冊](docs/USRAI_Integration_Manual.md)
- [GitHub 上傳指南](docs/GitHub_Upload_Guide.md)

## GitHub 目標 Repo

目標儲存庫：

```text
https://github.com/Nono0325/USRAI.git
```

目前環境沒有安裝 `git` 或 `gh`，也沒有 GitHub 寫入權杖，因此我已先整理好專案與手冊。若要直接推送，請在有 Git 的環境執行：

```bash
git init
git branch -M main
git add .
git commit -m "Initial USRAI integrated project"
git remote add origin https://github.com/Nono0325/USRAI.git
git push -u origin main
```

## 注意事項

- `.env`、`.venv/`、`db.sqlite3`、`media/` 已由 `.gitignore` 排除。
- 部署到 Render / PythonAnywhere 時請設定正式的 `SECRET_KEY`、`OPENAI_API_KEY` 與資料庫。
- 開發用 SQLite 不建議直接上傳到 GitHub。
