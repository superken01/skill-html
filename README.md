# Skill HTML

Hermes skills 的繁體中文靜態 HTML 說明站。

這個 repo 會從本機 Hermes skills 找來源，並用 `data/skills_zh.json` 裡的翻譯資料產生：

- `index.html`：首頁、搜尋與導覽。
- `skills/<skill>.html`：每個 skill 一個頁面。
- `assets/style.css`：手機友善 responsive 樣式，含深色模式。
- `assets/app.js`：手機選單、首頁搜尋、深色/淺色手動切換。

## 維護者內容整理說明

`SKILL.md` 是內容事實來源。維護者整理 `data/skills_zh.json` 時，應讓繁體中文內容貼近來源並容易閱讀；這段是 repo 內部維護說明，不會產生到公開 HTML。

每個 skill page 應儘量保留來源 `SKILL.md` 的主要結構與資訊型態：

- 主要章節與章節順序。
- 清單、步驟、規則與注意事項。
- 命令範例與程式碼區塊。
- 檢查表。
- 支援檔資訊（只列出檔名/用途提示，不把英文支援檔整篇貼上）。

`data/skills_zh.json` 使用 `translated_sections` 來描述來源章節的繁體中文版本。每個 section 可以標示 `source_heading`，並用 `paragraph`、`list`、`steps`、`checklist`、`commands`、`code`、`table`、`callout` 等 block 呈現。請避免把英文原文整頁貼進 HTML；必要時保留短命令、檔名、CLI flag 與專有名詞。

## 已整理技能

目前初始整理的技能：

- `codex`
- `kanban-codex-lane`
- `autonomous-agent-workflows`
- `kanban-operations`
- `hermes-agent`

## Dark mode

站台支援：

- 系統 `prefers-color-scheme: dark` 自動深色模式。
- Header 的「深色 / 淺色」按鈕手動切換。
- 使用 `localStorage` 記住手動偏好。
- 手機版維持單欄閱讀與可收合導覽。

## 需求

- Python 3.10 以上。
- 本機 Hermes skill 來源優先順序：
  1. `/Users/super/.hermes/hermes-agent/skills`
  2. `/Users/super/.hermes/skills`
  3. `/Users/super/.hermes/profiles/dev/skills`

## 產生全部頁面

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
2. 加入或更新 skill slug 對應的資料，優先維護：
   - `summary`
   - `source_outline_zh`
   - `translated_sections`
   - `source_support_files`（若需要手動補充或覆蓋自動偵測）
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
    python3 -m py_compile scripts/update_skill_html.py scripts/validate_site.py
    git status --short

`validate_site.py` 會檢查必要 HTML/CSS/JS 是否存在、HTML 是否宣告 `zh-Hant`、是否有 responsive viewport、站內連結是否指向存在的檔案、首頁搜尋/技能列表、skill page 基本內容、公開 HTML 不含站台策略標語，以及 dark mode CSS/JS 是否存在。
