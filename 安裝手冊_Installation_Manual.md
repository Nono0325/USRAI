---

## 壹、 專案目錄結構 (Project Structure)

了解專案的目錄結構有助於後續的維護與開發：

```text
Shuijing-Fengyun-Inn/
├── fengyun/              # 專案核心設定 (Settings, WSGI, Root URLs)
├── inn_app/              # 主要應用程式邏輯 (Models, Views, Admin)
│   ├── migrations/       # 資料庫遷移紀錄
│   └── ...
├── media/                # 媒體檔案 (使用者上傳的圖片、Word 範本)
├── static/               # 靜態檔案原始目錄 (CSS, JS, Images)
├── templates/            # HTML 模板頁面
├── staticfiles/          # 生產環境收集後的靜態檔案 (WhiteNoise 使用)
├── manage.py             # Django 管理腳本
├── requirements.txt      # 專案套件依賴清單
├── Procfile              # 雲端平台啟動定義 (Render/Heroku)
├── render.yaml           # Render 一鍵部署藍圖
├── init_setup.bat/sh     # 本地環境一鍵初始化腳本
├── install.ps1/sh        # 遠端引導安裝腳本 (One-Liner)
└── seed*.py              # 測試資料種子填充指令
```

---

## 貳、 基礎環境要求

在開始安裝之前，請確保您的電腦已安裝下列軟體：
1. **Python 3.12+**: [下載位址](https://www.python.org/downloads/) (建議安裝時勾選 "Add Python to PATH")。
2. **Git** (選配): 用於複製原始碼。
3. **Microsoft Word**: 用於設計或編輯簽到表範本。

---

## 貳、 安裝步驟 (Windows 環境)

### 1. 取得專案原始碼 (快速方式)
您可以直接使用「超·一行指令」自動下載並初始化：
**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/Nono0325/Shuijing-Fengyun-Inn/main/install.ps1 | iex
```

或是手動將專案資料夾 (例如 `Nono`) 複製到您的電腦桌面上，或使用 Git 複製。

### 2. 建立虛擬環境 (Virtual Environment)
開啟 PowerShell 或 CMD，進入專案目錄 (`cd C:\Users\user\Desktop\Nono`)，執行：
```powershell
python -m venv venv
```

### 3. 啟動虛擬環境
```powershell
.\venv\Scripts\activate
```

### 4. 安裝必要套件
本系統依賴多個第三方庫（如 Django, Pillow, docxtpl 等），請執行：
```powershell
pip install -r requirements.txt
```

### 5. 初始化資料庫 (Migrations)
建立資料表結構：
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. 建立最高管理員帳號
執行下列指令並依照提示設定您的帳號、Email 與密碼：
```powershell
python manage.py createsuperuser
```

---

## 參、 系統初始資料填充 (Optional)

為了讓網站一開始就有測試資料（如值班人員、課程預覽），請執行：

### 1. 注入基礎種子資料 (Seeding)
```powershell
python seed.py          # 基礎維護與導覽資料
python seed_events.py   # 活動列表測試資料
python seed_portal.py   # 故事牆、USR成果與科技應用資料
```

### 2. 產製預設 Word 簽到表範本
這是匯出簽到表功能正常運作的關鍵步驟：
```powershell
python create_default_template.py
```

---

---

## 肆、 門戶平台特色功能 (Platform Features)

本系統整合了 USR 計畫門戶平台所需的多項動態功能：

1. **全站搜尋 (Global Search)**: 導覽列頂端設有搜尋框，支援跨模型檢索，範圍包含課程（含**講師名稱**）、USR 成果（含**簡介摘要**）、故事牆、活動資訊及科技專案。
2. **導覽選單優化 (Grouping)**: 「關於風雲客棧」下拉選單整合了地方故事牆與計畫成果展示，提升專業度。
3. **智慧報名回饋 (Interactive Modals)**:
   - **成功報名**: 自動彈出 **QR Code 簽到憑證**，並支援一鍵下載。
   - **自助查詢**: 民眾可於「查詢報名紀錄」頁面隨時透過手機再次調出並 **下載 QR Code 圖片**。
   - **報到追蹤**: 工作人員掃碼後，後台會精確記錄 **報到秒數時間點**，並能同步匯出至 Excel。
   - **候補登記**: 報名額滿時自動排入候補並顯示當前順位。
   - **重複報名防護**: 自動偵測並透過彈窗提示已報名紀錄。
4. **AIoT 科技導覽**: 提供動態、管理員可編輯的科技應用介紹頁面。

---

## 伍、 安全加固與維護 (Security & Maintenance)

為了確保 USR 資料安全與系統穩定，本專案實施了以下加固措施：

1. **IDOR 橫向越權防護**: 取消報名時，系統會強制比對手機與 Email，防止有心人士惡意刪除他人紀錄。
2. **生產環境安全設定**: 
   - `SECURE_BROWSER_XSS_FILTER` 已開啟。
   - `X_FRAME_OPTIONS` 設定為 `DENY` 防止點擊劫持。
   - `SECRET_KEY` 在生產模式 (`IS_PRODUCTION=True`) 下強制使用環境變數讀取。
3. **輸入校驗**: 所有公眾表單（報名、聯絡我們）均具備長度限制與 XSS 過濾，防止惡意腳本注入與資料庫洪水攻擊。

---

## 陸、 啟動與訪問

### 啟動開發伺服器
```powershell
python manage.py runserver
```

### 訪問網址
* **前台大廳**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **管理後台**: [http://127.0.0.1:8000/admin/Nono/](http://127.0.0.1:8000/admin/Nono/)

---

## 柒、 常見問題排除

1. **圖片無法顯示**: 請確保 `media` 資料夾存在且具有寫入權限。
2. **Word 匯出失敗**: 請檢查「管理後台 > 簽到表版型範本」是否已上傳至少一份 `.docx` 檔案。
3. **Email 寄送不見**: 目前測試環境設定為控制台發信，請在執行 `runserver` 的終端機視窗查看信件內容。若要正式發信，請修改 `settings.py` 的 SMTP 設定。

---

---

## 捌、 雲端平台部署指南 (PythonAnywhere)

本系統與 **PythonAnywhere** 免費版高度相容。請依照下列步驟手動佈置您的雲端環境：

### 1. 建立代碼與虛擬環境
請在 PythonAnywhere **Bash Console** 執行：
```bash
git clone https://github.com/Nono0325/Shuijing-Fengyun-Inn.git
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
```

### 2. 環境靜態資源初始化
```bash
python manage.py collectstatic --noinput
python manage.py migrate
python create_admin.py  # 備用，若資料庫為空則執行
```

### 3. WSGI 與 Web 頁籤設定
請登入 PythonAnywhere 後台 [Web] 頁籤：
- **Source code**: `/home/您的帳號/Shuijing-Fengyun-Inn`
- **WSGI configuration file**: 點開後，將預設內容取代為專用配置。
- **Static files Mapping**:
  - `/static/` -> `/home/您的帳號/Shuijing-Fengyun-Inn/staticfiles/`
  - `/media/` -> `/home/您的帳號/Shuijing-Fengyun-Inn/media/`

> [!TIP]
> 完整的 PythonAnywhere 專用 WSGI 配置範本及細節，請參考專案中的 `README.md` 或諮詢開發團隊。

---

> [!NOTE]
> 關於日常營運操作（如新增課程、編輯內容），請參閱另一個檔案：[使用手冊_User_Manual.md](./使用手冊_User_Manual.md)。
