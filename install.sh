#!/bin/bash

# 「風雲客棧」全自動引導安裝腳本 (Bash 版)
REPO_URL="https://github.com/Nono0325/Shuijing-Fengyun-Inn.git"
FOLDER_NAME="Shuijing-Fengyun-Inn"

clear
echo "==============================================="
echo -e "\033[1;36m   🌊 水井村風雲客棧 - 全自動安裝引導系統   \033[0m"
echo "==============================================="

# 1. 環境檢查
echo -e "\n[1/4] 正在檢查系統環境..."

# 檢查 Git
if ! command -v git &> /dev/null
then
    echo -e "\033[1;31m❌ 找不到 Git！請先安裝 Git: https://git-scm.com/downloads\033[0m"
    exit
fi

# 檢查 Python
if ! command -v python3 &> /dev/null
then
    echo -e "\033[1;31m❌ 找不到 Python！請先安裝 Python 3.12+: https://www.python.org/downloads/\033[0m"
    exit
fi

echo -e "\033[1;32m✅ 環境檢查通過 (Git & Python 已就緒)\033[0m"

# 2. 下載專案
echo -e "\n[2/4] 正在從 GitHub 下載最新專案原始碼..."
if [ -d "$FOLDER_NAME" ]; then
    echo -e "\033[1;30m⚠️ 資料夾 '$FOLDER_NAME' 已存在，正在強制更新至最新版本...\033[0m"
    cd "$FOLDER_NAME"
    git fetch --all
    git reset --hard origin/main
else
    git clone "$REPO_URL"
    cd "$FOLDER_NAME"
fi

# 3. 執行初始化
echo -e "\n[3/4] 正在啟動專案初始化腳本 (init_setup.sh)..."
if [ -f "init_setup.sh" ]; then
    chmod +x init_setup.sh
    ./init_setup.sh
else
    echo -e "\033[1;31m❌ 找不到 init_setup.sh，請確認專案完整性。\033[0m"
    exit
fi

# 4. 完成
echo -e "\n==============================================="
echo -e "\033[1;32m🎉 安裝完成！網站應該已經啟動並運行。\033[0m"
echo "==============================================="
