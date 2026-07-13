#!/usr/bin/env python3
"""Usage matrix for the 559Theme across its consumer sites.

Reports, for every theme shortcode / partial / widget, whether it is used by
any consumer site (or transitively by a live theme template). Intended to find
dead weight to prune (Phase 5). Read-only: writes NOTES-usage.md, deletes
nothing.

Run from the workspace root (parent of 559Theme and the site dirs):
    conda run -n p314 python 559Theme/tools/usage-matrix.py
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
THEME = WORKSPACE / "559Theme"
SITES = ["765-25", "559-sp26", "VisSnacks", "gleicher.github.io"]

# ---- collect theme assets -------------------------------------------------

def theme_shortcodes() -> list[str]:
    d = THEME / "layouts" / "_shortcodes"
    names = set()
    for p in d.glob("*.*"):
        if p.suffix in (".html", ".md"):
            names.add(p.stem)
    return sorted(names)

def theme_partials() -> list[str]:
    """Partial 'names' as Hugo references them: path under _partials/."""
    d = THEME / "layouts" / "_partials"
    out = []
    for p in sorted(d.rglob("*.html")):
        out.append(str(p.relative_to(d)))
    return out

def theme_widgets() -> list[str]:
    d = THEME / "layouts" / "_partials" / "widgets"
    return sorted(p.stem for p in d.glob("*.html"))

# ---- gather searchable text ----------------------------------------------

def iter_files(root: Path, subdirs: list[str], suffixes: tuple[str, ...]):
    for sub in subdirs:
        base = root / sub
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in suffixes and "themes/559Theme" not in str(p):
                yield p

def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

# content/snippet/layout text per site (site's OWN files, not the submodule)
def site_call_text(site: str) -> str:
    root = WORKSPACE / site
    chunks = []
    for p in iter_files(root, ["content", "assets", "layouts"], (".md", ".html")):
        chunks.append(read(p))
    return "\n".join(chunks)

# ---- shortcode usage ------------------------------------------------------

def shortcode_hits(name: str, text: str) -> int:
    # {{< name ... >}} or {{% name ... %}} ; name followed by space, >, %, or }
    pat = re.compile(r"\{\{[<%]-?\s*" + re.escape(name) + r"(?=[\s>%}])")
    return len(pat.findall(text))

# ---- partial reachability -------------------------------------------------

PARTIAL_REF = re.compile(r'partial(?:Cached)?\s+"([^"]+)"')

def all_layout_files() -> list[Path]:
    files = list((THEME / "layouts").rglob("*.html"))
    files += [THEME / "layouts" / "index.json"]
    for site in SITES:
        d = WORKSPACE / site / "layouts"
        if d.exists():
            files += [p for p in d.rglob("*") if p.is_file() and "themes/559Theme" not in str(p)]
    return files

def build_ref_graph():
    """Map each layout file -> set of partial paths it references (literal)."""
    graph = {}
    for f in all_layout_files():
        txt = read(f)
        graph[f] = set(PARTIAL_REF.findall(txt))
    return graph

def partial_reachability(graph, widget_roots: set[str], dynamic_roots: set[str]):
    partials = set(theme_partials())
    # roots: every non-partial template + partials selected by a dynamic
    # dispatcher (widgets/%s.html, post_meta/%s.html) via config/front matter
    reachable = set()
    frontier = []
    for f, refs in graph.items():
        is_partial = "_partials" in f.parts or "partials" in f.parts
        if not is_partial:
            frontier.extend(refs)
    frontier.extend(f"widgets/{w}.html" for w in widget_roots)
    frontier.extend(dynamic_roots)
    # index partials by their reference path (suffix match under _partials/)
    def resolve(ref: str) -> Path | None:
        cand = THEME / "layouts" / "_partials" / ref
        return cand if cand.exists() else None
    # BFS
    seen_refs = set()
    while frontier:
        ref = frontier.pop()
        if ref in seen_refs:
            continue
        seen_refs.add(ref)
        p = resolve(ref)
        if p is None:
            continue  # site-defined or nonexistent partial
        reachable.add(ref)
        # follow refs inside this partial
        for r in graph.get(p, set()):
            if r not in seen_refs:
                frontier.append(r)
    return partials, reachable

# ---- widget selection (config + front matter) -----------------------------

def widget_tokens_for_site(site: str, widgets: list[str]) -> set[str]:
    """Which theme widgets are named anywhere in the site's config/front matter."""
    root = WORKSPACE / site
    text = []
    for name in ("config.toml", "hugo.toml", "config.yaml", "hugo.yaml", "config.json", "hugo.json"):
        p = root / name
        if p.exists():
            text.append(read(p))
    cfgdir = root / "config"
    if cfgdir.exists():
        for p in cfgdir.rglob("*"):
            if p.is_file():
                text.append(read(p))
    # front matter widget/sidebar overrides in content
    for p in iter_files(root, ["content"], (".md", ".html")):
        text.append(read(p))
    blob = "\n".join(text)
    found = set()
    for w in widgets:
        # widget name as a quoted/bare token in a list context
        if re.search(r"[\"'\[,\s]" + re.escape(w) + r"[\"'\],\s]", blob):
            found.add(w)
    return found

POST_META_LIST = re.compile(r"post_meta\s*[:=]\s*\[([^\]]*)\]")

def post_meta_fields_all() -> set[str]:
    """Fields named in any `post_meta = [...]` array (config or front matter),
    across all sites. post_meta.html dispatches partial post_meta/<field>.html."""
    fields = set()
    for site in SITES:
        root = WORKSPACE / site
        texts = []
        for name in ("config.toml", "hugo.toml", "config.yaml", "hugo.yaml"):
            p = root / name
            if p.exists():
                texts.append(read(p))
        cfgdir = root / "config"
        if cfgdir.exists():
            texts += [read(p) for p in cfgdir.rglob("*") if p.is_file()]
        for p in iter_files(root, ["content"], (".md", ".html")):
            texts.append(read(p))
        for blob in texts:
            for m in POST_META_LIST.finditer(blob):
                for tok in re.findall(r"[\"']?([A-Za-z0-9_-]+)[\"']?", m.group(1)):
                    fields.add(tok)
    return fields

# ---- main -----------------------------------------------------------------

def main():
    scs = theme_shortcodes()
    site_texts = {s: site_call_text(s) for s in SITES}

    # shortcode matrix
    sc_rows = []
    for name in scs:
        counts = {s: shortcode_hits(name, site_texts[s]) for s in SITES}
        sc_rows.append((name, counts, sum(counts.values())))

    widgets = theme_widgets()
    widget_use = {w: set() for w in widgets}
    for s in SITES:
        for w in widget_tokens_for_site(s, widgets):
            widget_use[w].add(s)

    graph = build_ref_graph()
    used_widgets = {w for w, ss in widget_use.items() if ss}
    pm_fields = post_meta_fields_all()
    dynamic_roots = {f"post_meta/{f}.html" for f in pm_fields}
    partials, reachable = partial_reachability(graph, used_widgets, dynamic_roots)

    # emit markdown
    out = []
    out.append("# Theme usage matrix\n")
    out.append("Generated by `tools/usage-matrix.py`. Read-only analysis for Phase 5 "
               "pruning. Columns are the four consumer sites; numbers are literal "
               "call-site counts (shortcodes) or reachability (partials).\n")

    out.append("## Shortcodes (call sites in content/assets/layouts)\n")
    out.append("| shortcode | 765-25 | 559-sp26 | VisSnacks | gleicher | total |")
    out.append("|---|--:|--:|--:|--:|--:|")
    for name, counts, total in sc_rows:
        flag = " **← DEAD**" if total == 0 else ""
        out.append(f"| `{name}` | {counts['765-25']} | {counts['559-sp26']} | "
                   f"{counts['VisSnacks']} | {counts['gleicher.github.io']} | {total}{flag} |")
    dead_sc = [n for n, _, t in sc_rows if t == 0]
    out.append(f"\n**Zero-usage shortcodes ({len(dead_sc)}):** "
               + (", ".join(f"`{n}`" for n in dead_sc) or "none") + "\n")

    out.append("## Widgets (named in any site config / front matter)\n")
    out.append("| widget | used by |")
    out.append("|---|---|")
    for w in widgets:
        ss = sorted(widget_use[w])
        flag = "**← DEAD**" if not ss else ", ".join(ss)
        out.append(f"| `widgets/{w}.html` | {flag} |")
    dead_w = [w for w in widgets if not widget_use[w]]
    out.append(f"\n**Zero-usage widgets ({len(dead_w)}):** "
               + (", ".join(f"`{w}`" for w in dead_w) or "none") + "\n")

    out.append("## Partials (reachable from live templates?)\n")
    out.append("Reachability = referenced (transitively) by a non-partial template "
               "in the theme or any site, OR selected by a dynamic dispatcher: "
               "`widgets/%s.html` (from a `widgets` list, see above) or "
               "`post_meta/%s.html` (from a `post_meta` list). "
               f"post_meta fields seen across sites: {sorted(pm_fields)}.\n")
    out.append("| partial | reachable |")
    out.append("|---|---|")
    dead_p = []
    for p in partials:
        if p.startswith("widgets/"):
            continue
        ok = p in reachable
        if not ok:
            dead_p.append(p)
        out.append(f"| `{p}` | {'yes' if ok else '**NO ← DEAD**'} |")
    out.append(f"\n**Unreachable non-widget partials ({len(dead_p)}):** "
               + (", ".join(f"`{p}`" for p in dead_p) or "none") + "\n")

    (THEME / "NOTES-usage.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    # console summary
    print(f"shortcodes: {len(scs)} total, {len(dead_sc)} dead")
    print(f"widgets:    {len(widgets)} total, {len(dead_w)} dead")
    print(f"partials:   {len([p for p in partials if not p.startswith('widgets/')])} non-widget, {len(dead_p)} unreachable")
    print("wrote 559Theme/NOTES-usage.md")

if __name__ == "__main__":
    main()
