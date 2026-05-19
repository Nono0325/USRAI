#!/bin/bash

echo "==============================================="
echo "   🌊 風雲客棧 - 本地開發環境初始化工具"
echo "==============================================="

# 1. 環境檢查
echo "[1/6] 正在檢查系統環境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python3，請在您的系統上安裝 Python 3.10+"
    exit 1
fi
echo "✅ Python 環境正常"

# 2. 建立虛擬環境
if [ ! -d "venv" ]; then
    echo "[2/6] 正在建立虛擬環境..."
    python3 -m venv venv
else
    echo "[2/6] 虛擬環境已存在，跳過建立步驟。"
fi

# 3. 安裝套件
echo "[3/6] 正在啟動虛擬環境並檢查/更新套件..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 資料庫遷移
echo "[4/6] 正在進行資料庫遷移..."
python manage.py makemigrations
python manage.py migrate

# 5. 填充測試資料
echo "[5/6] 正在填充種子資料與管理員..."
python create_admin.py
python seed.py
python seed_events.py
python seed_portal.py
python create_default_template.py

# 6. 啟動伺服器
echo "[6/6] 啟動開發伺服器..."
echo "-----------------------------------------------"
echo "網站已啟動，請訪問: http://127.0.0.1:8000"
echo "-----------------------------------------------"
python manage.py runserver
