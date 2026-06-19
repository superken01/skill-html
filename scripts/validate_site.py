#!/usr/bin/env python3
"""Basic local checks for the generated static site."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "index.html",
    ROOT / "skills" / "codex.html",
    ROOT / "skills" / "kanban-codex-lane.html",
    ROOT / "skills" / "autonomous-agent-workflows.html",
    ROOT / "skills" / "kanban-operations.html",
    ROOT / "skills" / "hermes-agent.html",
    ROOT / "assets" / "style.css",
    ROOT / "assets" / "app.js",
]

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.lang: str | None = None
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value for key, value in attrs}
        if tag == "html":
            self.lang = attrs_dict.get("lang")
        if tag == "meta" and attrs_dict.get("name") == "viewport":
            self.has_viewport = True
        if tag == "a" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"] or "")
        if tag == "link" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"] or "")
        if tag == "script" and attrs_dict.get("src"):
            self.links.append(attrs_dict["src"] or "")


def local_path(url: str, base: Path) -> Path | None:
    if url.startswith("http") or url.startswith("mailto:") or url.startswith("#"):
        return None
    if url.startswith("/"):
        return ROOT / url.lstrip("/")
    return (base.parent / url).resolve()


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8") if (ROOT / "assets" / "style.css").exists() else ""
    js = (ROOT / "assets" / "app.js").read_text(encoding="utf-8") if (ROOT / "assets" / "app.js").exists() else ""
    if "prefers-color-scheme: dark" not in css or "data-theme=\"dark\"" not in css:
        errors.append("assets/style.css missing dark mode support")
    if "localStorage" not in js or "theme-toggle" not in js:
        errors.append("assets/app.js missing persisted manual theme toggle")

    for path in sorted([ROOT / "index.html", *(ROOT / "skills").glob("*.html")]):
        text = path.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        if parser.lang != "zh-Hant":
            errors.append(f"{path.relative_to(ROOT)} does not declare lang=zh-Hant")
        if not parser.has_viewport:
            errors.append(f"{path.relative_to(ROOT)} missing responsive viewport meta")
        if "繁體中文" not in text:
            errors.append(f"{path.relative_to(ROOT)} does not look localized")
        banned_public_text = ["內容策略", "忠實翻譯 + 好讀排版"]
        for banned in banned_public_text:
            if banned in text:
                errors.append(f"{path.relative_to(ROOT)} exposes removed strategy text: {banned}")
        if "content-policy" in text:
            errors.append(f"{path.relative_to(ROOT)} still contains content-policy markup")
        if "theme-toggle" not in text:
            errors.append(f"{path.relative_to(ROOT)} missing dark mode toggle")
        if "site-nav" not in text:
            errors.append(f"{path.relative_to(ROOT)} missing site navigation")
        if path.name == "index.html":
            if "skill-list" not in text or "skill-search" not in text:
                errors.append("index.html missing search or skill list")
        else:
            for required_text in ["來源資訊", "來源章節對照", "支援檔資訊"]:
                if required_text not in text:
                    errors.append(f"{path.relative_to(ROOT)} missing basic skill content: {required_text}")
        for link in parser.links:
            target = local_path(link, path)
            if target is not None and not target.exists():
                errors.append(f"{path.relative_to(ROOT)} links missing file {link}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("site validation passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
