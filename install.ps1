# 「風雲客棧」全自動引導安裝腳本 (PowerShell 版)
$repoUrl = "https://github.com/Nono0325/Shuijing-Fengyun-Inn.git"
$folderName = "Shuijing-Fengyun-Inn"

Clear-Host
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   🌊 水井村風雲客棧 - 全自動安裝引導系統   " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. 環境檢查
Write-Host "[1/4] 正在檢查系統環境..." -ForegroundColor Yellow

# 檢查 Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 找不到 Git！請先安裝 Git: https://git-scm.com/downloads" -ForegroundColor Red
    Start-Process "https://git-scm.com/downloads"
    exit
}

# 檢查 Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 找不到 Python！請先安裝 Python 3.12+: https://www.python.org/downloads/" -ForegroundColor Red
    Start-Process "https://www.python.org/downloads/"
    exit
}

Write-Host "✅ 環境檢查通過 (Git & Python 已就緒)" -ForegroundColor Green

# 2. 下載專案
Write-Host "[2/4] 正在從 GitHub 下載最新專案原始碼..." -ForegroundColor Yellow
if (Test-Path $folderName) {
    Write-Host "⚠️ 資料夾 '$folderName' 已存在，正在強制更新至最新版本..." -ForegroundColor Gray
    Set-Location $folderName
    git fetch --all
    git reset --hard origin/main
}
else {
    git clone $repoUrl
    Set-Location $folderName
}

# 3. 執行初始化
Write-Host "[3/4] 正在啟動專案初始化腳本 (init_setup.bat)..." -ForegroundColor Yellow
if (Test-Path "init_setup.bat") {
    Start-Process "cmd.exe" -ArgumentList "/c init_setup.bat" -Wait
}
else {
    Write-Host "❌ 找不到 init_setup.bat，請確認專案完整性。" -ForegroundColor Red
    exit
}

# 4. 完成
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🎉 安裝完成！網站應該已經啟動並運行。" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
