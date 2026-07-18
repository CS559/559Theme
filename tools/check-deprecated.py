#!/usr/bin/env python3
"""Report where deprecated 559Theme shortcodes are still called.

Deprecation model (see docs/deprecation.md): a deprecated shortcode stays
FUNCTIONAL but carries, near the top of its source, a marker comment

    {{/* @deprecated: <reason> [-> <replacement>] */}}

and emits a build `warnf` when used. This tool finds every shortcode so
marked, then greps a set of consumer repos for call sites, so you can see who
still uses each one before eventually retiring it for real.

Usage:
    conda run -n p314 python 559Theme/tools/check-deprecated.py [REPO ...]

REPO defaults to the in-workspace sites. Pass other consumer repos
(e.g. workbook sites, other course webs) as arguments to widen the scan --
"unused in these sites" is NOT "safe to delete"; the theme has consumers
outside this workspace.

Exit status: 0 if no deprecated shortcode is used by any scanned repo (safe to
remove), 1 if at least one is still in use (report printed either way).
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

THEME = Path(__file__).resolve().parents[1]
WORKSPACE = THEME.parent
DEFAULT_REPOS = ["765-25", "559-sp26", "VisSnacks", "559Tutorials", "gleicher.github.io"]

# Match the `@deprecated:` marker line wherever it sits — a dedicated
# `{{/* @deprecated: … */}}` comment or (the usual case) the doc-header
# `{{- /* … @deprecated: … */ -}}` that shortcode-docs.py also reads. Capture
# the rest of that line; strip a same-line comment close if the tight form is used.
DEPRECATED = re.compile(r"@deprecated:\s*(.*)")
_CLOSE = re.compile(r"\s*\*/\s*-?\}\}.*$")

def deprecated_shortcodes() -> dict[str, str]:
    """name -> reason, for every shortcode carrying an @deprecated marker."""
    out = {}
    d = THEME / "layouts" / "_shortcodes"
    for p in d.rglob("*"):
        if p.suffix not in (".html", ".md"):
            continue
        m = DEPRECATED.search(p.read_text(encoding="utf-8", errors="replace"))
        if m:
            reason = _CLOSE.sub("", m.group(1))
            out[p.stem] = " ".join(reason.split())
    return out

def call_sites(name: str, repo: Path) -> list[str]:
    pat = re.compile(r"\{\{[<%]-?\s*" + re.escape(name) + r"(?=[\s>%}])")
    hits = []
    for sub in ("content", "assets", "layouts"):
        base = repo / sub
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if (not f.is_file() or f.suffix not in (".md", ".html")
                    or "themes/559Theme" in str(f) or "/public/" in str(f)):
                continue
            txt = f.read_text(encoding="utf-8", errors="replace")
            for m in pat.finditer(txt):
                ln = txt[:m.start()].count("\n") + 1
                hits.append(f"{f.relative_to(repo)}:{ln}")
    return hits

def main(argv: list[str]) -> int:
    repos = argv or DEFAULT_REPOS
    dep = deprecated_shortcodes()
    if not dep:
        print("No shortcodes are marked @deprecated in the theme.")
        return 0
    print(f"Deprecated shortcodes in theme: {', '.join(sorted(dep))}\n")
    any_used = False
    for name in sorted(dep):
        print(f"### {name}  — {dep[name]}")
        used_here = False
        for r in repos:
            repo = (WORKSPACE / r) if not Path(r).is_absolute() else Path(r)
            if not repo.exists():
                print(f"  ! repo not found: {repo}")
                continue
            sites = call_sites(name, repo)
            if sites:
                used_here = any_used = True
                print(f"  {r}: {len(sites)} call(s)")
                for s in sites[:20]:
                    print(f"      {s}")
                if len(sites) > 20:
                    print(f"      … +{len(sites) - 20} more")
        if not used_here:
            print("  (no call sites in scanned repos — safe to retire once all "
                  "consumers are scanned)")
        print()
    return 1 if any_used else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
