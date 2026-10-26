#!/usr/bin/env python3
"""Search and fetch live Manim Community Edition documentation (docs.manim.community).

Zero external dependencies (Python 3 standard library only).

Usage:
  python search_manim_docs.py search "TransformMatchingTex"
  python search_manim_docs.py search "MathTypst" --limit 5
  python search_manim_docs.py page "guides/using_text"
  python search_manim_docs.py page "changelog/0.22.0-changelog"
  python search_manim_docs.py page "reference/manim.mobject.text.code_mobject.Code"
  python search_manim_docs.py page "https://docs.manim.community/en/stable/tutorials/quickstart.html"
"""

from __future__ import annotations

import argparse
import html
import html.parser
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HOST = "https://docs.manim.community"
USER_AGENT = "ManimDocsSkill/1.0 (+https://docs.manim.community)"


class _FuroArticleExtractor(html.parser.HTMLParser):
    """Extracts clean readable text from <article id='furo-main-content'>."""

    BLOCK_TAGS = frozenset(
        {"h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "pre", "tr", "div", "section"}
    )
    SKIP_TAGS = frozenset({"script", "style", "svg", "noscript"})

    def __init__(self) -> None:
        super().__init__()
        self.in_main = False
        self.depth = 0
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if not self.in_main:
            if tag == "article" and attr_map.get("id") == "furo-main-content":
                self.in_main = True
                self.depth = 1
            return

        if tag == "article":
            self.depth += 1
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif self.skip_depth == 0 and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if not self.in_main:
            return
        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1
        if tag == "article":
            self.depth -= 1
            if self.depth <= 0:
                self.in_main = False

    def handle_data(self, data: str) -> None:
        if self.in_main and self.skip_depth == 0:
            self.parts.append(data)

    def get_text(self) -> str:
        text = "".join(self.parts)
        text = text.replace("¶", "")
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def _http_get(url: str, timeout: int = 20) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None


def _strip_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    return html.unescape(cleaned).strip()


def cmd_search(query: str, version: str, limit: int) -> int:
    scoped_query = f"project:manimce version:{version} {query}"
    params = urllib.parse.urlencode({"q": scoped_query, "page_size": limit})
    url = f"{HOST}/_/api/v3/search/?{params}"

    raw = _http_get(url)
    if raw is None:
        print(f"ERROR: Failed to reach ReadTheDocs search API at {url}", file=sys.stderr)
        return 1

    data = json.loads(raw)
    results = data.get("results", [])
    if not results:
        print(f"No results found for query: {query!r} (version={version})")
        return 0

    print(f"Found {data.get('count', len(results))} result(s) for {query!r} (showing top {len(results)}):\n")
    for idx, hit in enumerate(results, start=1):
        title = _strip_tags(hit.get("title", "Untitled"))
        domain = hit.get("domain", HOST)
        path = hit.get("path", "")
        full_url = f"{domain}{path}" if path.startswith("/") else f"{HOST}/{path}"
        print(f"[{idx}] {title}")
        print(f"    URL: {full_url}")

        blocks = hit.get("blocks", [])
        for block in blocks[:3]:
            b_type = block.get("type", "section")
            b_title = _strip_tags(block.get("title") or block.get("name") or "")
            b_role = block.get("role", "")
            b_content = _strip_tags(block.get("content", ""))
            b_content = re.sub(r"\s+", " ", b_content)
            if len(b_content) > 280:
                b_content = b_content[:277] + "..."
            header = f"{b_role or b_type}: {b_title}" if b_title else b_type
            print(f"    - ({header}) {b_content}")
        print()
    return 0


def _normalize_rel_path(target: str, version: str) -> tuple[str, str]:
    target = target.strip()
    if target.startswith(("http://", "https://")):
        parsed = urllib.parse.urlparse(target)
        path = parsed.path.lstrip("/")
        m = re.match(r"^en/([^/]+)/(.*)$", path)
        if m:
            version = m.group(1)
            rel = m.group(2)
        else:
            rel = path
    else:
        rel = target.lstrip("/")

    # Strip _sources prefix or trailing extensions if caller passed them
    if rel.startswith("_sources/"):
        rel = rel[len("_sources/") :]
    for suffix in (".rst.txt", ".md.txt", ".html", ".rst", ".md"):
        if rel.endswith(suffix):
            rel = rel[: -len(suffix)]
            break

    # Convenience shorthand: "manim.mobject.text.code_mobject.Code" -> "reference/..."
    if rel.startswith("manim."):
        rel = f"reference/{rel}"

    return rel, version


def cmd_page(target: str, version: str, max_chars: int) -> int:
    rel, version = _normalize_rel_path(target, version)
    base = f"{HOST}/en/{version}"

    is_autodoc_ref = rel.startswith(("reference/", "reference_index/"))

    # 1. For narrative docs, prefer raw MyST Markdown (.md.txt) or reST (.rst.txt)
    if not is_autodoc_ref:
        for ext in (".md.txt", ".rst.txt"):
            src_url = f"{base}/_sources/{rel}{ext}"
            raw_src = _http_get(src_url)
            if raw_src and not raw_src.lstrip().lower().startswith("<!doctype html"):
                print(f"# Source: {src_url}\n")
                if max_chars > 0 and len(raw_src) > max_chars:
                    print(raw_src[:max_chars])
                    print(f"\n... [truncated at {max_chars} chars; pass --max-chars 0 for full page]")
                else:
                    print(raw_src)
                return 0

    # 2. For API reference pages (Sphinx autodoc) or fallback, extract rendered article text
    html_url = f"{base}/{rel}.html"
    raw_html = _http_get(html_url)
    if not raw_html:
        print(f"ERROR: Page not found at {html_url}", file=sys.stderr)
        return 1

    parser = _FuroArticleExtractor()
    parser.feed(raw_html)
    extracted = parser.get_text()
    if not extracted:
        print(f"ERROR: Could not extract main content from {html_url}", file=sys.stderr)
        return 1

    print(f"# Rendered Page: {html_url}\n")
    if max_chars > 0 and len(extracted) > max_chars:
        print(extracted[:max_chars])
        print(f"\n... [truncated at {max_chars} chars; pass --max-chars 0 for full page]")
    else:
        print(extracted)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Search and read live Manim Community Edition docs (docs.manim.community)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search docs via ReadTheDocs v3 API")
    p_search.add_argument("query", help="Search terms (class name, method, CLI flag, or concept)")
    p_search.add_argument("--version", default="stable", help="Docs version (default: stable, or latest)")
    p_search.add_argument("--limit", type=int, default=8, help="Max search hits (default: 8)")

    p_page = sub.add_parser("page", help="Fetch clean Markdown/reST source or rendered API reference")
    p_page.add_argument(
        "target",
        help="Doc path (e.g. 'guides/using_text', 'manim.mobject.text.code_mobject.Code') or full URL",
    )
    p_page.add_argument("--version", default="stable", help="Docs version (default: stable)")
    p_page.add_argument(
        "--max-chars",
        type=int,
        default=16000,
        help="Truncate output to N characters (0 = unlimited, default: 16000)",
    )

    args = parser.parse_args()
    if args.command == "search":
        return cmd_search(args.query, args.version, args.limit)
    if args.command == "page":
        return cmd_page(args.target, args.version, args.max_chars)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
