#!/usr/bin/env python3
"""Render Traditional Chinese Hermes skill pages as static HTML.

The JSON data supplies Traditional Chinese content that follows the source
skill's major structure while keeping the static site readable.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "skills_zh.json"
OUTPUT_DIR = REPO_ROOT / "skills"

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
    headings: list[tuple[int, str]] = field(default_factory=list)
    support_files: list[str] = field(default_factory=list)


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


def extract_headings(markdown: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2)))
    return headings


def find_support_files(skill_dir: Path) -> list[str]:
    files: list[str] = []
    for path in skill_dir.rglob("*"):
        if path.is_file() and path.name != "SKILL.md":
            files.append(path.relative_to(skill_dir).as_posix())
    return sorted(files)


def find_skill_source(skill_name: str) -> SourceSkill:
    for root in SKILL_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("SKILL.md"):
            if path.parent.name == skill_name:
                text = path.read_text(encoding="utf-8")
                meta, body = read_frontmatter(text)
                return SourceSkill(
                    name=skill_name,
                    path=path,
                    description=meta.get("description", ""),
                    version=meta.get("version", ""),
                    headings=extract_headings(body),
                    support_files=find_support_files(path.parent),
                )
    return SourceSkill(name=skill_name, path=None)


def load_skill_data() -> dict[str, dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_text(value: Any) -> str:
    """Escape text and render inline code markers as code elements."""
    text = esc(value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def render_list(items: list[str], *, ordered: bool = False, checklist: bool = False) -> str:
    if not items:
        return "<p class=\"muted\">尚未整理。</p>"
    tag = "ol" if ordered else "ul"
    class_name = " class=\"checklist\"" if checklist else ""
    rendered = "".join(f"<li>{render_text(item)}</li>" for item in items)
    return f"<{tag}{class_name}>{rendered}</{tag}>"


def render_commands(commands: list[dict[str, str]]) -> str:
    if not commands:
        return "<p class=\"muted\">尚未整理命令範例。</p>"
    blocks = []
    for item in commands:
        label = esc(item.get("label", "命令"))
        command = esc(item.get("command", ""))
        note = item.get("note")
        note_html = f"<p>{render_text(note)}</p>" if note else ""
        blocks.append(
            "<article class=\"command-card\">"
            f"<h3>{label}</h3>"
            f"{note_html}<pre><code>{command}</code></pre>"
            "</article>"
        )
    return "".join(blocks)


def render_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class=\"muted\">尚未整理。</p>"
    headers = list(rows[0].keys())
    head = "".join(f"<th>{esc(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{render_text(row.get(header, ''))}</td>" for header in headers)
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<div class=\"table-wrap\"><table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"


def render_content_block(block: dict[str, Any]) -> str:
    kind = block.get("type", "paragraph")
    if kind == "paragraph":
        return f"<p>{render_text(block.get('text', ''))}</p>"
    if kind == "list":
        return render_list(block.get("items", []), ordered=bool(block.get("ordered")))
    if kind == "checklist":
        return render_list(block.get("items", []), checklist=True)
    if kind == "steps":
        return render_list(block.get("items", []), ordered=True)
    if kind == "commands":
        return f"<div class=\"commands\">{render_commands(block.get('items', []))}</div>"
    if kind == "code":
        label = block.get("label")
        label_html = f"<h3>{esc(label)}</h3>" if label else ""
        return f"<div class=\"code-block\">{label_html}<pre><code>{esc(block.get('code', ''))}</code></pre></div>"
    if kind == "table":
        return render_table(block.get("rows", []))
    if kind == "callout":
        title = block.get("title", "注意")
        return f"<aside class=\"callout\"><strong>{esc(title)}</strong><p>{render_text(block.get('text', ''))}</p></aside>"
    return f"<p>{render_text(block.get('text', ''))}</p>"


def render_translated_sections(sections: list[dict[str, Any]]) -> str:
    if not sections:
        return ""
    cards = []
    for index, section in enumerate(sections, start=1):
        heading = section.get("heading", f"章節 {index}")
        source_heading = section.get("source_heading")
        source_html = f"<p class=\"source-heading\">對應來源章節：{esc(source_heading)}</p>" if source_heading else ""
        blocks = "".join(render_content_block(block) for block in section.get("blocks", []))
        cards.append(
            "<article class=\"panel span-2 translated-section\">"
            f"<div class=\"section-number\">{index:02d}</div>"
            f"<h2>{esc(heading)}</h2>"
            f"{source_html}{blocks}"
            "</article>"
        )
    return "".join(cards)


def render_source_outline(source: SourceSkill, translated_outline: list[str]) -> str:
    if translated_outline:
        return render_list(translated_outline)
    if not source.headings:
        return "<p class=\"muted\">未能讀取來源章節。</p>"
    items = [f"H{level}: {title}" for level, title in source.headings]
    return render_list(items)


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
    <button class="theme-toggle" type="button" aria-label="切換深色模式" aria-pressed="false">深色</button>
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
    <p>繁體中文整理版。{generated}</p>
  </footer>
</body>
</html>
"""


def render_skill_page(slug: str, data: dict[str, Any], source: SourceSkill) -> str:
    title = data.get("title", slug)
    tags = data.get("tags", [])
    source_path = str(source.path) if source.path else "未找到本機來源"
    source_description = data.get("source_description_zh") or source.description or "本機來源未提供描述。"
    support_files = data.get("source_support_files") or source.support_files
    tag_html = "".join(f"<span>{esc(tag)}</span>" for tag in tags)
    support_html = render_list(support_files) if support_files else "<p class=\"muted\">來源 skill 沒有額外支援檔，或本機未找到。</p>"
    translated_sections = data.get("translated_sections", [])
    section_html = render_translated_sections(translated_sections)
    if not section_html:
        section_html = f"""
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
"""

    body = f"""    <section class="hero skill-hero">
      <p class="eyebrow">{esc(data.get('category', 'Hermes Skill'))}</p>
      <h1>{esc(title)}</h1>
      <p class="subtitle">{esc(data.get('subtitle', ''))}</p>
      <div class="tags">{tag_html}</div>
    </section>

    <section class="content-grid">
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
        <h2>來源章節對照</h2>
        {render_source_outline(source, data.get('source_outline_zh', []))}
      </article>
      {section_html}
      <article class="panel span-2 support-files">
        <h2>支援檔資訊</h2>
        <p class="muted">這些是來源 skill 目錄中 `SKILL.md` 以外的檔案；HTML 只列出檔名與用途提示，不直接貼整份英文內容。</p>
        {support_html}
      </article>
    </section>
"""
    return page_shell(str(title), body, data.get("summary", ""), in_skill_dir=True)


def render_index(skills: list[tuple[str, dict[str, Any], SourceSkill]]) -> str:
    cards = []
    for slug, data, source in skills:
        tags = "".join(f"<span>{esc(tag)}</span>" for tag in data.get("tags", [])[:4])
        found = "已連到本機來源" if source.path else "未找到來源"
        card_text = " ".join([slug, data.get("title", ""), data.get("summary", ""), " ".join(data.get("tags", []))])
        section_count = len(data.get("translated_sections", []))
        cards.append(f"""        <article class="skill-card" data-search="{esc(card_text)}">
          <p class="eyebrow">{esc(data.get('category', 'Hermes Skill'))}</p>
          <h2><a href="skills/{esc(slug)}.html">{esc(data.get('title', slug))}</a></h2>
          <p>{esc(data.get('subtitle', data.get('summary', '')))}</p>
          <div class="tags">{tags}</div>
          <p class="source-status">{esc(found)} · {section_count} 個翻譯章節</p>
        </article>""")
    body = f"""    <section class="hero">
      <p class="eyebrow">Hermes Skills 繁體中文導覽</p>
      <h1>技能說明 HTML 站</h1>
      <p class="subtitle">整理 Hermes Skills 的繁體中文頁面，提供技能搜尋、站內導覽與深色模式切換。</p>
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
        "summary": "此頁已建立基本框架，但尚未加入依照來源 SKILL.md 翻譯的章節。請在 data/skills_zh.json 補上 translated_sections 後重新產生。",
        "translated_sections": [],
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
