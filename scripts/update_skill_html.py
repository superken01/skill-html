#!/usr/bin/env python3
"""Render Traditional Chinese Hermes skill pages as static HTML."""
from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "skills_zh.json"
OUTPUT_DIR = REPO_ROOT / "skills"
ASSET_DIR = REPO_ROOT / "assets"

SKILL_ROOTS = [
    Path("/Users/super/.hermes/hermes-agent/skills"),
    Path("/Users/super/.hermes/skills"),
    Path("/Users/super/.hermes/profiles/dev/skills"),
]

DEFAULT_SKILLS = ["codex", "kanban-codex-lane", "kanban-operations", "autonomous-agent-workflows", "hermes-agent"]


@dataclass
class SourceSkill:
    name: str
    path: Path | None
    description: str = ""
    version: str = ""
    source_excerpt: str = ""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "skill"


def read_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw = parts[1]
    body = parts[2].lstrip()
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def find_skill_source(skill_name: str) -> SourceSkill:
    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("SKILL.md"):
            if path.parent.name == skill_name:
                text = path.read_text(encoding="utf-8")
                meta, body = read_frontmatter(text)
                excerpt = "\n".join(body.splitlines()[:24]).strip()
                return SourceSkill(
                    name=skill_name,
                    path=path,
                    description=meta.get("description", ""),
                    version=meta.get("version", ""),
                    source_excerpt=excerpt,
                )
    return SourceSkill(name=skill_name, path=None)


def load_skill_data() -> dict[str, dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_list(items: list[str]) -> str:
    if not items:
        return "<p class=\"muted\">尚未整理。</p>"
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def render_commands(commands: list[dict[str, str]]) -> str:
    if not commands:
        return "<p class=\"muted\">尚未整理命令範例。</p>"
    blocks = []
    for item in commands:
        label = esc(item.get("label", "命令"))
        command = esc(item.get("command", ""))
        blocks.append(
            "<article class=\"command-card\">"
            f"<h3>{label}</h3>"
            f"<pre><code>{command}</code></pre>"
            "</article>"
        )
    return "".join(blocks)


def page_shell(title: str, body: str, description: str = "", in_skill_dir: bool = False) -> str:
    generated = "由 scripts/update_skill_html.py 產生"
    root = "../" if in_skill_dir else ""
    skills_root = "" if in_skill_dir else "skills/"
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{esc(description or title)}">
  <title>{esc(title)}｜Skill HTML</title>
  <link rel="stylesheet" href="{root}assets/style.css">
  <script src="{root}assets/app.js" defer></script>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{root}index.html">Skill HTML</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">選單</button>
    <nav id="site-nav" class="site-nav">
      <a href="{root}index.html">首頁</a>
      <a href="{skills_root}codex.html">Codex</a>
      <a href="{skills_root}kanban-codex-lane.html">Kanban Codex Lane</a>
      <a href="{skills_root}kanban-operations.html">Kanban Operations</a>
      <a href="{skills_root}autonomous-agent-workflows.html">自主代理</a>
      <a href="{skills_root}hermes-agent.html">Hermes Agent</a>
    </nav>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <p>繁體中文整理版。最後產生：{generated}</p>
  </footer>
</body>
</html>
"""


def render_skill_page(slug: str, data: dict[str, Any], source: SourceSkill) -> str:
    title = data.get("title", slug)
    tags = data.get("tags", [])
    source_path = str(source.path) if source.path else "未找到本機來源"
    source_description = data.get("source_description_zh") or source.description or "本機來源未提供描述。"
    tag_html = "".join(f"<span>{esc(tag)}</span>" for tag in tags)
    body = f"""    <section class="hero skill-hero">
      <p class="eyebrow">{esc(data.get('category', 'Hermes Skill'))}</p>
      <h1>{esc(title)}</h1>
      <p class="subtitle">{esc(data.get('subtitle', ''))}</p>
      <div class="tags">{tag_html}</div>
    </section>

    <section class="content-grid">
      <article class="panel span-2">
        <h2>中文整理</h2>
        <p>{esc(data.get('summary', '尚未整理中文摘要。'))}</p>
      </article>
      <aside class="panel source-card">
        <h2>來源資訊</h2>
        <dl>
          <dt>Skill slug</dt><dd>{esc(slug)}</dd>
          <dt>來源路徑</dt><dd>{esc(source_path)}</dd>
          <dt>來源描述</dt><dd>{esc(source_description)}</dd>
          <dt>版本</dt><dd>{esc(source.version or '未標示')}</dd>
        </dl>
      </aside>

      <article class="panel">
        <h2>何時使用</h2>
        {render_list(data.get('use_when', []))}
      </article>
      <article class="panel">
        <h2>不建議使用情境</h2>
        {render_list(data.get('avoid_when', []))}
      </article>
      <article class="panel span-2">
        <h2>建議流程</h2>
        {render_list(data.get('workflow', []))}
      </article>
      <article class="panel span-2">
        <h2>命令範例</h2>
        <div class="commands">{render_commands(data.get('commands', []))}</div>
      </article>
      <article class="panel span-2">
        <h2>注意事項</h2>
        {render_list(data.get('notes', []))}
      </article>
    </section>
"""
    return page_shell(str(title), body, data.get("summary", ""), in_skill_dir=True)


def render_index(skills: list[tuple[str, dict[str, Any], SourceSkill]]) -> str:
    cards = []
    for slug, data, source in skills:
        tags = "".join(f"<span>{esc(tag)}</span>" for tag in data.get("tags", [])[:4])
        found = "已連到本機來源" if source.path else "未找到來源"
        cards.append(f"""        <article class="skill-card" data-search="{esc(slug + ' ' + data.get('title', '') + ' ' + data.get('summary', ''))}">
          <p class="eyebrow">{esc(data.get('category', 'Hermes Skill'))}</p>
          <h2><a href="skills/{esc(slug)}.html">{esc(data.get('title', slug))}</a></h2>
          <p>{esc(data.get('subtitle', data.get('summary', '')))}</p>
          <div class="tags">{tags}</div>
          <p class="source-status">{esc(found)}</p>
        </article>""")
    body = f"""    <section class="hero">
      <p class="eyebrow">Hermes Skills 繁體中文導覽</p>
      <h1>技能說明 HTML 站</h1>
      <p class="subtitle">把本機 Hermes skills 整理成好閱讀、可搜尋、手機友善的繁體中文頁面。內容不是英文原文直貼，而是整理用途、流程、注意事項與命令範例。</p>
      <label class="search-box" for="skill-search">搜尋技能</label>
      <input id="skill-search" type="search" placeholder="輸入 Codex、Kanban、Hermes、代理..." autocomplete="off">
    </section>

    <section class="skill-list" aria-label="技能列表">
{''.join(cards)}
    </section>
"""
    return page_shell("首頁", body, "Hermes skills 繁體中文 HTML 導覽")


def fallback_data(slug: str, source: SourceSkill) -> dict[str, Any]:
    title = slug.replace("-", " ").title()
    return {
        "title": title,
        "subtitle": source.description or "尚未有人工整理內容。",
        "category": "Hermes Skill",
        "tags": [slug],
        "summary": "此頁已建立基本框架，但尚未加入人工整理的繁體中文說明。請在 data/skills_zh.json 補上 summary、use_when、workflow、notes 與 commands 後重新產生。",
        "use_when": ["需要先建立此技能的 HTML 頁面骨架。"],
        "avoid_when": ["需要正式文件時，請先補齊人工整理內容。"],
        "workflow": ["找到本機 SKILL.md。", "補上繁體中文整理資料。", "重新執行 scripts/update_skill_html.py。"],
        "commands": [],
        "notes": ["這是 fallback 頁面，不代表完整中文整理。"],
    }


def render(skill_names: list[str]) -> list[Path]:
    all_data = load_skill_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    rendered_skills: list[tuple[str, dict[str, Any], SourceSkill]] = []
    for raw_name in skill_names:
        slug = slugify(raw_name)
        source = find_skill_source(slug)
        data = all_data.get(slug) or fallback_data(slug, source)
        html_text = render_skill_page(slug, data, source)
        target = OUTPUT_DIR / f"{slug}.html"
        target.write_text(html_text, encoding="utf-8")
        generated.append(target)
        rendered_skills.append((slug, data, source))
    index = render_index(rendered_skills)
    index_path = REPO_ROOT / "index.html"
    index_path.write_text(index, encoding="utf-8")
    generated.insert(0, index_path)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Traditional Chinese skill HTML pages.")
    parser.add_argument("skills", nargs="*", help="Skill slugs to render. Defaults to the initial curated set.")
    parser.add_argument("--all", action="store_true", help="Render all skills present in data/skills_zh.json.")
    args = parser.parse_args()

    if args.all:
        skill_names = sorted(load_skill_data().keys())
    else:
        skill_names = args.skills or DEFAULT_SKILLS

    generated = render(skill_names)
    for path in generated:
        print(path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
