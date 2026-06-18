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

    for path in sorted([ROOT / "index.html", *(ROOT / "skills").glob("*.html")]):
        text = path.read_text(encoding="utf-8")
        parser = LinkParser()
        parser.feed(text)
        if parser.lang != "zh-Hant":
            errors.append(f"{path.relative_to(ROOT)} does not declare lang=zh-Hant")
        if not parser.has_viewport:
            errors.append(f"{path.relative_to(ROOT)} missing responsive viewport meta")
        if "中文整理" not in text and "繁體中文導覽" not in text:
            errors.append(f"{path.relative_to(ROOT)} does not look localized")
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
