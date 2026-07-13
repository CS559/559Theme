#!/usr/bin/env python3
"""Generate docs/shortcodes.md from each shortcode's doc-comment header.

Single source of truth = the leading `{{/* ... */}}` comment at the top of each
file in layouts/_shortcodes/. Convention (see docs/shortcodes.md preamble):

    {{- /*
      <name> — <one-line summary>
      usage: {{< name ... >}}   ...
      params: ...
      [notes: ...]
    */ -}}

Edit the shortcode header, then rerun this to regenerate the reference. Also
reports any shortcode missing a header (documentation coverage).

    conda run -n p314 python tools/shortcode-docs.py
"""

from __future__ import annotations
import re
from pathlib import Path

THEME = Path(__file__).resolve().parents[1]
SC = THEME / "layouts" / "_shortcodes"
OUT = THEME / "docs" / "shortcodes.md"

LEAD = re.compile(r"^\s*\{\{-?\s*/\*(.*?)\*/\s*-?\}\}", re.DOTALL)
DEP = re.compile(r"@deprecated:\s*(.*)")
DEAD = re.compile(r"@dead-weight:\s*(.*)")

def dedent(text: str) -> list[str]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    indents = [len(ln) - len(ln.lstrip()) for ln in lines if ln.strip()]
    cut = min(indents) if indents else 0
    return [ln[cut:] if len(ln) >= cut else ln for ln in lines]

def parse(path: Path):
    raw = path.read_text(encoding="utf-8")
    m = LEAD.match(raw)
    name = path.stem
    info = {"name": name, "file": path.name, "summary": "", "body": [],
            "status": "active", "status_note": "", "documented": bool(m)}
    if not m:
        return info
    body = dedent(m.group(1))
    # status markers
    for ln in body:
        d = DEP.search(ln)
        dw = DEAD.search(ln)
        if d:
            info["status"], info["status_note"] = "deprecated", d.group(1).strip()
        elif dw:
            info["status"], info["status_note"] = "dead-weight", dw.group(1).strip()
    # drop marker lines from the shown body
    body = [ln for ln in body if "@deprecated:" not in ln and "@dead-weight:" not in ln]
    body = dedent("\n".join(body))
    if body:
        first = body[0]
        mm = re.match(r"\s*" + re.escape(name) + r"\s*[—-]\s*(.*)", first)
        info["summary"] = mm.group(1).strip() if mm else first.strip()
        info["body"] = body[1:] if mm else body
    # trim leading blank lines of body
    while info["body"] and not info["body"][0].strip():
        info["body"].pop(0)
    return info

def main():
    files = sorted(p for p in SC.glob("*.*") if p.suffix in (".html", ".md"))
    items = [parse(p) for p in files]
    active = [i for i in items if i["status"] == "active"]
    retired = [i for i in items if i["status"] != "active"]
    undoc = [i for i in items if not i["documented"]]

    STATUS_BADGE = {"deprecated": " ⚠️ deprecated", "dead-weight": " 🪦 dead-weight"}

    out = []
    out.append("# 559Theme shortcodes\n")
    out.append("**Generated** by `tools/shortcode-docs.py` from the doc-comment "
               "header of each shortcode in `layouts/_shortcodes/`. Do not edit "
               "this file by hand — edit the shortcode's header comment and "
               "regenerate.\n")
    out.append("Header convention (top of each shortcode):\n")
    out.append("```text\n{{- /*\n  <name> — <one-line summary>\n  usage: {{< name … >}}   …\n"
               "  params: 0 = …, named: …\n  [notes: …]\n*/ -}}\n```\n")
    out.append(f"{len(items)} shortcodes: {len(active)} active, {len(retired)} "
               f"deprecated/dead-weight. Deep-dives: `link` → `docs/link-shortcode.md`; "
               "course-data shortcodes (`assign-*`, `reading`, `mod*`, `page`) → "
               "`docs/data-contracts.md`; math (`math`, `displaymath`, `eqref`) → "
               "`docs/math.md`.\n")
    if undoc:
        out.append("> **Undocumented (no header comment):** "
                   + ", ".join(f"`{i['name']}`" for i in undoc) + "\n")

    out.append("## Index\n")
    out.append("| shortcode | file | summary | status |")
    out.append("|---|---|---|---|")
    for i in items:
        st = i["status"] if i["status"] != "active" else ""
        out.append(f"| [`{i['name']}`](#{i['name']}) | `{i['file']}` | "
                   f"{i['summary'] or '—'} | {st} |")
    out.append("")

    out.append("## Reference\n")
    for i in items:
        badge = STATUS_BADGE.get(i["status"], "")
        out.append(f"### {i['name']}{badge}\n")
        out.append(f"<sup>`layouts/_shortcodes/{i['file']}`</sup>\n")
        if i["status"] != "active" and i["status_note"]:
            out.append(f"> **{i['status']}:** {i['status_note']}\n")
        if i["summary"]:
            out.append(i["summary"] + "\n")
        if i["body"]:
            out.append("```text")
            out.extend(i["body"])
            out.append("```\n")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(THEME)} — {len(items)} shortcodes, "
          f"{len(undoc)} undocumented")

if __name__ == "__main__":
    main()
