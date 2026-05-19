@echo off
setlocal

echo ===============================================
echo   🌊 風雲客棧 - 本地開發環境初始化工具
echo ===============================================

:: 1. 環境檢查
echo [1/6] 正在檢查系統環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 找不到 Python，請安裝 Python 3.10+
    pause
    exit /b %errorlevel%
)
echo ✅ Python 環境正常

:: 2. 建立虛擬環境
if not exist venv (
    echo [2/6] 正在建立虛擬環境...
    python -m venv venv
) else (
    echo [2/6] 虛擬環境已存在，跳過建立步驟。
)

:: 3. 安裝套件
echo [3/6] 正在檢查並安裝相依套件...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. 資料庫遷移
echo [4/6] 正在進行資料庫遷移...
python manage.py makemigrations
python manage.py migrate

:: 5. 填充測試資料
echo [5/6] 正在填充種子資料與管理員...
python create_admin.py
python seed.py
python seed_events.py
python seed_portal.py
python create_default_template.py

:: 6. 啟動伺服器
echo [6/6] 啟動開發伺服器...
echo -----------------------------------------------
echo 網站已啟動，請訪問: http://127.0.0.1:8000
echo -----------------------------------------------
python manage.py runserver
pause
