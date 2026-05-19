# GitHub 上傳指南

目標 repo：

```text
https://github.com/Nono0325/USRAI.git
```

目前該 repo 是公開空 repo。空 repo 沒有 branch，也沒有 commit，因此需要從本機建立第一個 commit 後推送。

## 1. 確認不要上傳的檔案

`.gitignore` 已排除：

- `.env`
- `.venv/`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- `__pycache__/`

## 2. 在有 Git 的環境推送

在專案根目錄執行：

```bash
git init
git branch -M main
git add .
git commit -m "Initial USRAI integrated project"
git remote add origin https://github.com/Nono0325/USRAI.git
git push -u origin main
```

## 3. 如果 GitHub 要求登入

使用 GitHub Personal Access Token，權限至少需要：

- Repository contents: Read and write

使用 HTTPS 推送時：

```text
Username: Nono0325
Password: 貼上 GitHub token
```

## 4. 推送後檢查

到 GitHub repo 頁面確認：

- `README.md` 是否顯示
- `docs/USRAI_Integration_Manual.md` 是否存在
- `chat/`、`water/`、`inn_app/`、`fengyun/` 是否存在
- `.env`、`.venv/`、`db.sqlite3` 是否沒有被上傳

## 5. 本環境限制

目前這台環境沒有：

- `git`
- `gh`
- `GITHUB_TOKEN`

因此無法直接把檔案推送到 GitHub。若提供 GitHub token，或在本機安裝 Git，就可以完成推送。
