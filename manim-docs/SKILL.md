---
name: manim-docs
description: >-
  Search and fetch live Manim Community Edition documentation from
  docs.manim.community via the ReadTheDocs v3 API, raw .md.txt/.rst.txt
  sources, or local Python introspection. Use when verifying exact Manim API
  signatures, parameters, examples, or recent changelog additions.
version: 0.22.0
---

# Searching & Reading Manim Community Documentation

This skill teaches you how to look up authoritative, current **Manim Community Edition (`manimce`)** documentation instead of relying on stale memorized signatures. For general Manim rules, see [manim-best-practices](../manim-best-practices/SKILL.md).

---

## 1. Fast CLI Lookup (`scripts/search_manim_docs.py`)

Use the bundled zero-dependency Python 3 script [search_manim_docs.py](./scripts/search_manim_docs.py) to search ReadTheDocs and fetch clean documentation text without HTML navigation bloat.

### Search by Class, Method, Flag, or Concept
```bash
python "<path-to-manim-docs>/scripts/search_manim_docs.py" search "TransformMatchingTex"
python "<path-to-manim-docs>/scripts/search_manim_docs.py" search "MathTypst" --limit 5
python "<path-to-manim-docs>/scripts/search_manim_docs.py" search "video-codec" --version stable
```

### Read a Full Narrative Guide or API Reference Page
`page` automatically fetches raw MyST Markdown (`.md.txt`) or reStructuredText (`.rst.txt`) for tutorials/guides/changelogs, and automatically extracts `<article id="furo-main-content">` for Sphinx `autodoc` API reference pages:

```bash
# Narrative guides, tutorials, FAQs, and changelogs:
python "<path-to-manim-docs>/scripts/search_manim_docs.py" page "guides/using_text"
python "<path-to-manim-docs>/scripts/search_manim_docs.py" page "changelog/0.22.0-changelog"

# API Reference classes/modules (accepts full URL, reference/... path, or manim.* qualified name):
python "<path-to-manim-docs>/scripts/search_manim_docs.py" page "manim.mobject.text.code_mobject.Code"
python "<path-to-manim-docs>/scripts/search_manim_docs.py" page "https://docs.manim.community/en/stable/reference/manim.scene.scene.Scene.html"
```

Pass `--max-chars 0` if a large reference page is truncated at the default 16,000-character safety limit.

---

## 2. Direct HTTP Endpoints (No Script Needed)

If making direct HTTP requests (`curl`, `Invoke-RestMethod`, `fetch`):

### Keyless ReadTheDocs v3 Search API
```http
GET https://docs.manim.community/_/api/v3/search/?q=project%3Amanimce+version%3Astable+<url-encoded-query>&page_size=10
```
Each item in `results[]` includes `title`, `domain`, `path`, and `blocks[]` (containing rendered class signatures, parameter docs, and example snippets).

### Raw Source URLs vs Sphinx Autodoc Pages
- **Guides, Tutorials, Installation, FAQ, Changelogs**: Hosted under `/_sources/<path>.md.txt` (MyST Markdown, used by `installation/uv`, `faq/*`, and `changelog/0.20.0+`) or `/_sources/<path>.rst.txt` (reStructuredText, used by `tutorials/*` and `guides/*`):
  - `https://docs.manim.community/en/stable/_sources/tutorials/quickstart.rst.txt`
  - `https://docs.manim.community/en/stable/_sources/guides/deep_dive.rst.txt`
  - `https://docs.manim.community/en/stable/_sources/installation/uv.md.txt`
  - `https://docs.manim.community/en/stable/_sources/changelog/0.22.0-changelog.md.txt`
- **API Reference (`reference/manim.*.html`) Caveat**: Do **not** fetch `/_sources/reference/manim.*.rst.txt`—those source files only contain 3-line `.. autoclass::` directives without docstrings! Always read API reference details via the **v3 Search API** or `search_manim_docs.py page` (which extracts `#furo-main-content` from the rendered `.html` page).

---

## 3. High-Value Documentation Sitemap (`en/stable/`)

| Category | Paths |
| :--- | :--- |
| **Tutorials** | `tutorials/quickstart`, `tutorials/output_and_config`, `tutorials/building_blocks` |
| **Thematic Guides** | `guides/configuration`, `guides/deep_dive`, `guides/using_text`, `guides/add_voiceovers` |
| **Installation** | `installation/uv`, `installation/conda`, `installation/docker`, `installation/jupyter` |
| **FAQ** | `faq/general`, `faq/help`, `faq/installation`, `faq/internals`, `faq/opengl` |
| **Ecosystem** | `examples`, `plugins` |
| **Reference Indices** | `reference_index/animations`, `reference_index/cameras`, `reference_index/configuration`, `reference_index/mobjects`, `reference_index/scenes`, `reference_index/utilities_misc` |
| **Recent Changelogs** | `changelog/0.22.0-changelog`, `changelog/0.21.0-changelog`, `changelog/0.20.0-changelog`, `changelog/0.19.0-changelog` |

---

## 4. Offline / Local Python Introspection

When `manim` is installed in the active environment (or via `uv run`), inspect the exact installed version's signatures directly—especially helpful if a project pins an older Manim version (e.g., `v0.18` vs `v0.22`):

```bash
# Check installed Manim flavor and version + CLI flags
manim --version
manim render --help

# Inspect exact constructor signature and docstring in Python
python -c "import inspect, manim; print(manim.__version__); print(inspect.signature(manim.Code)); print(inspect.getdoc(manim.Code))"
```
