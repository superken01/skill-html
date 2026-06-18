# Skill HTML

Hermes skills 的繁體中文靜態 HTML 說明站。

這個 repo 會從本機 Hermes skills 找來源，並用 `data/skills_zh.json` 裡的人工整理內容產生：

- `index.html`：首頁、搜尋與導覽。
- `skills/<skill>.html`：每個 skill 一個頁面。
- `assets/style.css`：手機友善 responsive 樣式。
- `assets/app.js`：手機選單與首頁搜尋。

目前初始整理的技能：

- `codex`
- `kanban-codex-lane`
- `autonomous-agent-workflows`
- `hermes-agent`

內容是繁體中文整理版，重點包含用途、何時使用、流程、注意事項與命令範例；不是把英文 SKILL.md 原文直接貼上。

## 需求

- Python 3.10 以上。
- 本機 Hermes skill 來源優先順序：
  1. `/Users/super/.hermes/hermes-agent/skills`
  2. `/Users/super/.hermes/skills`
  3. `/Users/super/.hermes/profiles/dev/skills`

## 產生全部初始頁面

    python3 scripts/update_skill_html.py --all

或使用預設初始集合：

    python3 scripts/update_skill_html.py

## 只更新某個 skill

例如只更新 Codex 頁面：

    python3 scripts/update_skill_html.py codex

例如只更新 Hermes Agent 頁面：

    python3 scripts/update_skill_html.py hermes-agent

腳本會更新對應的 `skills/<skill>.html`，並重新產生 `index.html`。

## 新增或改善中文內容

1. 編輯 `data/skills_zh.json`。
2. 加入或更新 skill slug 對應的資料，例如 `summary`、`use_when`、`workflow`、`commands`、`notes`。
3. 執行：

       python3 scripts/update_skill_html.py <skill-slug>

4. 驗證：

       python3 scripts/validate_site.py

## 本地預覽

可用 Python 內建 HTTP server：

    python3 -m http.server 8000

然後打開：

    http://localhost:8000/

## 驗證

本 repo 沒有依賴安裝步驟。提交前至少跑：

    python3 scripts/update_skill_html.py --all
    python3 scripts/validate_site.py
    git status --short

`validate_site.py` 會檢查必要 HTML/CSS/JS 是否存在、HTML 是否宣告 `zh-Hant`、是否有 responsive viewport，以及站內連結是否指向存在的檔案。
