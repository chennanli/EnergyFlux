#!/usr/bin/env python3
"""Render knowledge_vault/ into a static HTML site at wiki/.

Pure Python, no Node. Reads markdown files from
``knowledge_vault/wiki/``, parses YAML frontmatter for authority and
scope, resolves Obsidian-style ``[[wikilinks]]`` to relative HTML
links, generates an index page with authority + scope navigation, and
emits one HTML file per markdown file.

Output is committable static HTML that any HTTP server can serve.
GitHub Pages serves it directly when the repo's ``docs/`` or root
contains the output.

Run from repo root:

    python scripts/build_wiki.py

Or with custom paths:

    python scripts/build_wiki.py --vault knowledge_vault --out wiki

Goals:

* Wikilinks resolve. ``[[behind_the_meter_siting]]`` becomes
  ``<a href="concepts/behind_the_meter_siting.html">...</a>``.
* Authority is visible. Each page header shows a colored badge
  (authoritative / reviewed / candidate / legacy) so a reader can
  tell at a glance whether the page is auto-citable.
* Scope is visible. Host type, region, equipment, voltage level,
  and applies-when conditions show as a small metadata strip.
* Backlinks are computed automatically. Each page lists which
  other vault pages link to it.
* Index is structured. The home page groups pages by section
  (entities / concepts / sources / synthesis), authority, and
  by scope.

What this deliberately does NOT do:

* Graph view (would need d3.js; the index does the same job at
  text density). Easy to add later.
* Full-text search (markdown→HTML is enough for v1; readers can
  use the AI assistant for search-style questions).
* Watch mode (the build is fast; just re-run).
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SITE_TITLE = "EnergyFlux Knowledge Vault"
SITE_TAGLINE = (
    "A governed engineering knowledge base for industrial AI siting, "
    "energy systems, and the EnergyFlux blog series."
)

AUTHORITY_LABEL = {
    "authoritative": "Authoritative",
    "reviewed": "Reviewed",
    "candidate": "Candidate",
    "legacy": "Legacy",
}

# Order matters for sorting in the index.
AUTHORITY_ORDER = ["authoritative", "reviewed", "candidate", "legacy"]

SECTION_ORDER = ["sources", "blocks", "graphs", "concepts", "entities", "synthesis"]

SECTION_LABEL = {
    "sources": "Sources",
    "blocks": "Blocks",
    "graphs": "Graphs",
    "concepts": "Concepts",
    "entities": "Entities",
    "synthesis": "Synthesis",
}

SECTION_BLURB = {
    "sources": "One page summarizing each ingested raw source. "
               "Filenames mirror the underlying raw file slug.",
    "blocks": "Engineering-block role pages — what each flowsheet block "
              "represents, key sizing variables, upstream / downstream "
              "dependencies, and the source notes that inform it.",
    "graphs": "Pages describing the vault's edge structure — what edges "
              "are AI-suggested candidates vs human-reviewed facts, "
              "and the promotion workflow between them.",
    "concepts": "Domain ideas — framings, decisions, or design rules "
                "that span multiple entities. Behind-the-meter siting, "
                "surrogate models, governance hierarchy.",
    "entities": "Discrete things in the EnergyFlux problem space — "
                "specific GPU racks, BESS configurations, transformer "
                "classes, WWTP archetypes, regulatory documents.",
    "synthesis": "Cross-cutting analyses, comparisons, decision tables. "
                 "Often filed back from query answers.",
}


# ---------------------------------------------------------------------------
# YAML frontmatter (same parser as rag_v2.py — duplicated to keep this
# script standalone and runnable without any project dependencies)
# ---------------------------------------------------------------------------
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(raw: str) -> Tuple[Dict, str]:
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw
    return _parse_yaml_subset(m.group(1)), m.group(2)


def _parse_yaml_subset(text: str) -> Dict:
    out: Dict = {}
    current_dict_key = None
    nested: Dict = {}
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("  ") and current_dict_key is not None:
            key, _, value = line.strip().partition(":")
            nested[key.strip()] = _parse_value(value.strip())
            continue
        if current_dict_key is not None:
            out[current_dict_key] = nested
            current_dict_key = None
            nested = {}
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            current_dict_key = key
            nested = {}
        else:
            out[key] = _parse_value(value)
    if current_dict_key is not None:
        out[current_dict_key] = nested
    return out


def _parse_value(v: str):
    if v == "" or v.lower() == "null":
        return None
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_unquote(it.strip()) for it in inner.split(",")]
    return _unquote(v)


def _unquote(v: str) -> str:
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


# ---------------------------------------------------------------------------
# Page model
# ---------------------------------------------------------------------------
@dataclass
class Page:
    slug: str          # "behind_the_meter_siting"
    section: str       # "concepts"
    rel_path: str      # "concepts/behind_the_meter_siting.md"
    out_path: str      # "concepts/behind_the_meter_siting.html"
    title: str
    authority: str
    scope: Dict
    metadata: Dict
    body: str
    backlinks: List["Page"] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Markdown rendering (small inline renderer; no external markdown lib)
# ---------------------------------------------------------------------------
class WikiLinkRegistry:
    """Slug → Page lookup so [[wikilinks]] resolve."""

    def __init__(self, pages: List[Page]):
        self.by_slug: Dict[str, Page] = {}
        for p in pages:
            self.by_slug[p.slug] = p

    def resolve(self, target: str) -> Optional[Page]:
        return self.by_slug.get(target.strip())


def _resolve_wikilinks(body: str, registry: WikiLinkRegistry, current: Page) -> Tuple[str, List[Page]]:
    """Replace [[slug]] and [[slug|label]] with HTML anchors. Return the
    rewritten body and the list of pages this page links to (for backlinks)."""
    outbound: List[Page] = []

    def repl(m):
        target = m.group(1)
        if "|" in target:
            slug, _, label = target.partition("|")
        else:
            slug, label = target, target
        page = registry.resolve(slug)
        if page is None:
            return f'<span class="wikilink-broken" title="No vault page named &quot;{html.escape(slug)}&quot;">{html.escape(label)}</span>'
        outbound.append(page)
        rel = _relative_url(current.out_path, page.out_path)
        return f'<a class="wikilink" href="{rel}">{html.escape(label)}</a>'

    new_body = re.sub(r"\[\[([^\]]+)\]\]", repl, body)
    return new_body, outbound


def _relative_url(from_path: str, to_path: str) -> str:
    """Compute the relative URL from a page output path to another page."""
    from_dir = Path(from_path).parent
    to = Path(to_path)
    try:
        rel = Path(*([".."] * len(from_dir.parts)) + list(to.parts))
        return rel.as_posix() if rel.parts else to.as_posix()
    except ValueError:
        return to_path


def _render_inline(text: str) -> str:
    """Inline markdown: bold, italic, code, links. Order matters
    (escape HTML first, then apply substitutions)."""
    s = html.escape(text)
    # Code spans first so we don't touch their contents.
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # Standard markdown links [label](url).
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # Bold then italic. Bold with **; italic with single * or _.
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def _render_markdown(body: str) -> str:
    """Block-level markdown → HTML. Handles headings, paragraphs,
    bullet/numbered lists, blockquotes, code blocks, horizontal rules,
    and tables. Inline rewriting happens via _render_inline.

    Wikilink resolution must happen BEFORE this call (we don't want
    to rewrite already-rendered <a class="wikilink"> tags).
    """
    out: List[str] = []
    lines = body.split("\n")
    i = 0
    in_code = False
    code_buf: List[str] = []
    list_stack: List[str] = []  # stack of "ul" or "ol" tags

    def close_lists():
        while list_stack:
            tag = list_stack.pop()
            out.append(f"</{tag}>")

    while i < len(lines):
        line = lines[i]
        # Fenced code blocks
        if line.startswith("```"):
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf = []
                in_code = False
            else:
                close_lists()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Horizontal rule
        if re.match(r"^-{3,}\s*$", stripped):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{_render_inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        # Tables (simple GitHub style)
        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?[-:\s|]+\|[-:\s|]*$", lines[i + 1]):
            close_lists()
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and "|" in lines[i]:
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(row)
                i += 1
            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{_render_inline(h)}</th>" for h in header_cells) + "</tr></thead>")
            out.append("<tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{_render_inline(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        # Blockquote
        if stripped.startswith("> "):
            close_lists()
            buf = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                buf.append(lines[i].strip()[2:])
                i += 1
            out.append("<blockquote><p>" + _render_inline(" ".join(buf)) + "</p></blockquote>")
            continue

        # Unordered list
        if re.match(r"^[\-\*]\s+", stripped):
            if not list_stack or list_stack[-1] != "ul":
                close_lists()
                out.append("<ul>")
                list_stack.append("ul")
            content = re.sub(r"^[\-\*]\s+", "", stripped)
            out.append(f"<li>{_render_inline(content)}</li>")
            i += 1
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            if not list_stack or list_stack[-1] != "ol":
                close_lists()
                out.append("<ol>")
                list_stack.append("ol")
            content = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f"<li>{_render_inline(content)}</li>")
            i += 1
            continue

        # Empty line (paragraph break)
        if stripped == "":
            close_lists()
            i += 1
            continue

        # Default: paragraph. Collect contiguous non-empty lines.
        close_lists()
        para_lines = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        out.append("<p>" + _render_inline(" ".join(para_lines)) + "</p>")

    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    close_lists()
    return "\n".join(out)


def _is_block_start(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("#") or s.startswith(">"):
        return True
    if re.match(r"^[\-\*]\s+", s) or re.match(r"^\d+\.\s+", s):
        return True
    if s.startswith("```"):
        return True
    if re.match(r"^-{3,}\s*$", s):
        return True
    return False


# ---------------------------------------------------------------------------
# Page templating
# ---------------------------------------------------------------------------
CSS = """
:root {
  --blue: #1F4E79;
  --blue-light: #DEEBF7;
  --blue-border: #9DC3E6;
  --alt-row: #F4F7FB;
  --rule: #BFBFBF;
  --text: #222;
  --muted: #666;
  --gold: #E8A33D;
  --green: #2F855A;
  --red: #B91C1C;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: var(--text);
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 32px 80px;
  line-height: 1.55;
  font-size: 15.5px;
  background: #fff;
}
header.site-header {
  border-bottom: 0.5px solid var(--rule);
  padding-bottom: 12px;
  margin-bottom: 18px;
}
header.site-header .site-title {
  color: var(--blue);
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
}
header.site-header .site-tagline {
  font-size: 13px;
  color: var(--muted);
  margin-top: 4px;
}
header.site-header nav {
  margin-top: 8px;
  font-size: 13px;
}
header.site-header nav a {
  color: var(--blue);
  text-decoration: none;
  margin-right: 10px;
  border-bottom: 1px dotted var(--blue-border);
}
h1 {
  color: var(--blue);
  font-size: 24px;
  line-height: 1.25;
  margin: 16px 0 6px;
}
h2 {
  color: var(--blue);
  font-size: 18px;
  margin: 26px 0 8px;
}
h3 {
  color: var(--blue);
  font-size: 15px;
  margin: 18px 0 6px;
}
h4 { font-size: 14px; margin: 14px 0 4px; }
p { margin: 0 0 10px; }
ul, ol { margin: 0 0 10px 24px; padding: 0; }
li { margin: 3px 0; }
strong { color: var(--blue); }
a { color: var(--blue); text-decoration: none; border-bottom: 1px dotted var(--blue-border); }
a:hover { border-bottom: 1px solid var(--blue); }
a.wikilink { background: var(--blue-light); padding: 0 2px; border-radius: 2px; }
a.wikilink:hover { background: #c8dcf2; }
span.wikilink-broken { color: var(--red); border-bottom: 1px dashed var(--red); }
code { font-family: "SF Mono", Menlo, Monaco, "Courier New", monospace; font-size: 13px; background: var(--alt-row); padding: 1px 4px; border-radius: 2px; }
pre { background: var(--alt-row); padding: 10px 14px; border-left: 3px solid var(--blue-border); overflow-x: auto; font-size: 13.5px; border-radius: 2px; }
pre code { background: transparent; padding: 0; }
blockquote { margin: 10px 0 14px 0; padding: 8px 14px; border-left: 3px solid var(--blue-border); background: var(--alt-row); font-style: italic; color: var(--text); }
table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 14px; }
th, td { text-align: left; padding: 8px 10px; border: 1px solid var(--blue-border); }
th { background: var(--blue-light); }
tr:nth-child(even) td { background: var(--alt-row); }
hr { border: 0; border-top: 0.5px solid var(--rule); margin: 18px 0; }

/* Authority badges */
.badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 11.5px;
  font-weight: 600;
  margin-right: 6px;
  vertical-align: middle;
  letter-spacing: 0.02em;
}
.badge.authoritative { background: var(--blue); color: white; }
.badge.reviewed      { background: var(--green); color: white; }
.badge.candidate     { background: var(--gold); color: white; }
.badge.legacy        { background: #888; color: white; }

/* Page metadata strip */
.page-meta {
  font-size: 13px;
  color: var(--muted);
  background: var(--alt-row);
  border: 1px solid var(--blue-border);
  border-radius: 2px;
  padding: 8px 12px;
  margin: 8px 0 18px;
}
.page-meta div { margin: 1px 0; }
.page-meta strong { color: var(--text); }

/* Page footer */
footer.page-footer {
  margin-top: 36px;
  padding-top: 14px;
  border-top: 0.5px solid var(--rule);
  font-size: 13px;
  color: var(--muted);
}
footer.page-footer h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  margin: 16px 0 4px;
}
footer.page-footer ul { margin-left: 18px; }

/* Index page */
.section { margin-bottom: 26px; }
.section h2 { margin-bottom: 4px; }
.section .blurb { font-size: 13.5px; color: var(--muted); margin-bottom: 8px; }
.page-list { list-style: none; padding: 0; margin: 0; }
.page-list li { padding: 4px 0; border-bottom: 0.5px dotted var(--rule); }
.page-list li .title { font-weight: 600; }
.page-list li .scope { font-size: 12.5px; color: var(--muted); margin-left: 4px; }
.stats-bar {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  background: var(--alt-row);
  border: 1px solid var(--blue-border);
  padding: 8px 12px;
  margin: 12px 0 20px;
  border-radius: 2px;
  font-size: 13px;
}
.stats-bar .stat strong { color: var(--blue); font-size: 16px; }
"""


def _badge_html(authority: str) -> str:
    label = AUTHORITY_LABEL.get(authority, authority.title())
    return f'<span class="badge {authority}">{html.escape(label)}</span>'


def _scope_strip(scope: Dict) -> str:
    if not isinstance(scope, dict) or not scope:
        return ""
    bits: List[str] = []
    for field_name, label in [
        ("host_type", "Host"),
        ("region", "Region"),
        ("equipment", "Equipment"),
        ("voltage_level", "Voltage"),
    ]:
        v = scope.get(field_name)
        if v:
            if isinstance(v, list):
                v_str = ", ".join(str(x) for x in v)
            else:
                v_str = str(v)
            bits.append(f"<div><strong>{label}:</strong> {html.escape(v_str)}</div>")
    if scope.get("applies_when"):
        bits.append(f"<div><strong>Applies when:</strong> {html.escape(str(scope['applies_when']))}</div>")
    if not bits:
        return ""
    return f'<div class="page-meta">{"".join(bits)}</div>'


def _site_header(out_path: str) -> str:
    """Top nav bar — relative links back to index."""
    home_rel = _relative_url(out_path, "index.html")
    log_rel = _relative_url(out_path, "log.html")
    governance_rel = _relative_url(out_path, "concepts/governance_hierarchy.html")
    return f"""<header class="site-header">
  <a class="site-title" href="{home_rel}">📚 {SITE_TITLE}</a>
  <div class="site-tagline">{SITE_TAGLINE}</div>
  <nav>
    <a href="{home_rel}">Index</a>
    <a href="{governance_rel}">Governance</a>
    <a href="{log_rel}">Log</a>
    <a href="https://github.com/chennanli/EnergyFlux">GitHub</a>
  </nav>
</header>"""


def _render_page_html(page: Page, body_html: str) -> str:
    backlinks_html = ""
    if page.backlinks:
        items = "".join(
            f'<li><a class="wikilink" href="{_relative_url(page.out_path, b.out_path)}">{html.escape(b.title)}</a></li>'
            for b in sorted(page.backlinks, key=lambda x: x.title)
        )
        backlinks_html = f"<h3>Backlinks</h3><ul>{items}</ul>"

    sources_html = ""
    sources = page.metadata.get("sources")
    if sources:
        items = []
        for s in sources if isinstance(sources, list) else [sources]:
            items.append(f"<li><code>{html.escape(str(s))}</code></li>")
        sources_html = f"<h3>Cites</h3><ul>{''.join(items)}</ul>"

    approval_html = ""
    if page.metadata.get("approved_by") or page.metadata.get("approved_date"):
        approval_html = (
            f"<h3>Approval</h3>"
            f"<ul><li>Approved by: {html.escape(str(page.metadata.get('approved_by') or 'pending'))}</li>"
            f"<li>Date: {html.escape(str(page.metadata.get('approved_date') or 'pending'))}</li></ul>"
        )

    title_html = (
        f'<h1>{_badge_html(page.authority)}{html.escape(page.title)}</h1>'
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page.title)} — {SITE_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
{_site_header(page.out_path)}
{title_html}
{_scope_strip(page.scope)}
{body_html}
<footer class="page-footer">
  {sources_html}
  {approval_html}
  {backlinks_html}
  <p style="margin-top:14px; font-style:italic;">
    File: <code>knowledge_vault/wiki/{html.escape(page.rel_path)}</code> ·
    Authority: {_badge_html(page.authority)}
  </p>
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------
def _render_index_html(pages: List[Page], stats: Dict[str, int]) -> str:
    by_section: Dict[str, List[Page]] = {s: [] for s in SECTION_ORDER}
    for p in pages:
        if p.section in by_section:
            by_section[p.section].append(p)

    stats_bar = '<div class="stats-bar">'
    for a in AUTHORITY_ORDER:
        n = stats.get(a, 0)
        stats_bar += f'<div class="stat">{_badge_html(a)} <strong>{n}</strong> pages</div>'
    stats_bar += f'<div class="stat" style="margin-left:auto;">Total: <strong>{stats.get("total", 0)}</strong></div>'
    stats_bar += "</div>"

    sections_html = ""
    for section in SECTION_ORDER:
        items = by_section.get(section, [])
        if not items:
            continue
        items.sort(key=lambda p: (AUTHORITY_ORDER.index(p.authority) if p.authority in AUTHORITY_ORDER else 99, p.title.lower()))
        items_html = '<ul class="page-list">'
        for p in items:
            scope_summary_parts = []
            if isinstance(p.scope, dict):
                ht = p.scope.get("host_type")
                if isinstance(ht, list) and ht and ht != ["any"]:
                    scope_summary_parts.append("/".join(ht[:3]))
                rg = p.scope.get("region")
                if isinstance(rg, list) and rg and rg != ["any"]:
                    scope_summary_parts.append("/".join(rg[:3]))
            scope_str = " · ".join(scope_summary_parts)
            items_html += (
                f'<li>{_badge_html(p.authority)}'
                f'<a class="title" href="{p.out_path}">{html.escape(p.title)}</a>'
                + (f' <span class="scope">({html.escape(scope_str)})</span>' if scope_str else "")
                + "</li>"
            )
        items_html += "</ul>"
        sections_html += f"""<div class="section">
<h2>{SECTION_LABEL[section]}</h2>
<div class="blurb">{SECTION_BLURB[section]}</div>
{items_html}
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITE_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
{_site_header("index.html")}
<h1>{SITE_TITLE}</h1>
<p>{SITE_TAGLINE}</p>
<p style="font-size: 13.5px; color: var(--muted);">
  This vault is the source material the EnergyFlux blog series'
  AI assistant retrieves from. Each page declares its
  <strong>authority level</strong> (Authoritative, Reviewed,
  Candidate, Legacy) and its <strong>scope</strong> (host type,
  region, equipment, voltage level). The assistant cites only
  Authoritative and Reviewed pages as primary; Candidate and Legacy
  show up in answers only when nothing more reliable exists, and
  always with a "pending review" warning. See
  <a href="concepts/governance_hierarchy.html">the governance page</a>
  for how promotion works.
</p>
{stats_bar}
{sections_html}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Log page (renders log.md from the vault root)
# ---------------------------------------------------------------------------
def _render_log_html(log_md_path: Path) -> Optional[str]:
    if not log_md_path.exists():
        return None
    raw = log_md_path.read_text()
    # Log has no frontmatter; render directly.
    body_html = _render_markdown(raw)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log — {SITE_TITLE}</title>
<style>{CSS}</style>
</head>
<body>
{_site_header("log.html")}
<h1>Vault log</h1>
<p style="font-size: 13.5px; color: var(--muted);">
  Append-only chronological record of vault operations: setup,
  ingest, query, lint, supersede.
</p>
{body_html}
</body>
</html>"""


# ---------------------------------------------------------------------------
# Build pipeline
# ---------------------------------------------------------------------------
def _section_for_path(rel_path: str) -> str:
    """First path component is the section."""
    parts = Path(rel_path).parts
    return parts[0] if parts else "other"


def collect_pages(wiki_dir: Path) -> List[Page]:
    pages: List[Page] = []
    for md in sorted(wiki_dir.rglob("*.md")):
        if md.name.startswith("_"):
            continue
        raw = md.read_text()
        meta, body = parse_frontmatter(raw)
        rel = md.relative_to(wiki_dir).as_posix()
        section = _section_for_path(rel)
        slug = md.stem
        title = meta.get("title") or slug.replace("_", " ").title()
        authority = (meta.get("authority") or "candidate").strip().lower()
        scope = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
        out_path = Path(rel).with_suffix(".html").as_posix()
        pages.append(
            Page(
                slug=slug, section=section, rel_path=rel, out_path=out_path,
                title=title, authority=authority, scope=scope, metadata=meta,
                body=body,
            )
        )
    return pages


def build(vault_root: Path, out_dir: Path) -> Dict:
    wiki_dir = vault_root / "wiki"
    if not wiki_dir.exists():
        raise SystemExit(f"❌ Vault wiki directory not found: {wiki_dir}")

    pages = collect_pages(wiki_dir)
    registry = WikiLinkRegistry(pages)

    # Resolve wikilinks and build backlink graph.
    rendered_bodies: Dict[str, str] = {}
    for p in pages:
        body_with_links, outbound = _resolve_wikilinks(p.body, registry, p)
        rendered_bodies[p.slug] = _render_markdown(body_with_links)
        for target in outbound:
            if p not in target.backlinks:
                target.backlinks.append(p)

    # Make output directory. Best-effort wipe: if the existing output has
    # files we can't delete (e.g., a sandboxed dev environment), keep going
    # — Write below will still overwrite any same-named files.
    if out_dir.exists():
        try:
            shutil.rmtree(out_dir)
        except (PermissionError, OSError):
            pass
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write each page.
    for p in pages:
        out_file = out_dir / p.out_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(_render_page_html(p, rendered_bodies[p.slug]))

    # Stats.
    stats = {a: 0 for a in AUTHORITY_ORDER}
    for p in pages:
        stats[p.authority] = stats.get(p.authority, 0) + 1
    stats["total"] = len(pages)

    # Index page.
    (out_dir / "index.html").write_text(_render_index_html(pages, stats))

    # Log page (optional).
    log_html = _render_log_html(vault_root / "log.md")
    if log_html:
        (out_dir / "log.html").write_text(log_html)

    return {
        "pages_written": len(pages),
        "out_dir": str(out_dir),
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    repo_root = Path(__file__).resolve().parents[1]
    p.add_argument("--vault", default=str(repo_root / "knowledge_vault"),
                   help="Path to knowledge_vault/ root.")
    p.add_argument("--out", default=str(repo_root / "wiki"),
                   help="Output directory for the rendered site. Default 'wiki/' "
                        "matches the URL prefix used by the chat app and Blog 2 links.")
    args = p.parse_args(argv)

    result = build(Path(args.vault), Path(args.out))
    print(f"✅ Built {result['pages_written']} pages → {result['out_dir']}")
    print("   By authority:")
    for a in AUTHORITY_ORDER:
        n = result["stats"].get(a, 0)
        if n:
            print(f"     {a:<14} {n}")
    print(f"     {'total':<14} {result['stats']['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
