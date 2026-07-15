#!/usr/bin/env python3
"""Generate the mathvariant -> Unicode Mathematical-Alphanumeric mapping.

Background: Chromium's MathML Core ignores KaTeX's `mathvariant="bold"` attribute,
so bold math renders at normal weight (Firefox honors it). The theme's build-time
fix (Path B) rewrites `<mi|mn|mo|mtext mathvariant="V">c</...>` to the real Unicode
math glyph for (V, c) and drops the attribute. See ./README.md for the full
rationale, failure-mode analysis, and the build-time canary that guards it.

This script emits that mapping as a Hugo data file (../../data/mathvariants.yaml),
consumed by layouts/_partials/mathvariant-fix.html.

Why generate instead of hand-type: the Mathematical Alphanumeric Symbols block
(U+1D400-U+1D7FF) is regular EXCEPT for ~30 "holes" where the glyph already lived
in the Letterlike Symbols block (e.g. italic h = U+210E PLANCK CONSTANT, script
B = U+212C, double-struck R = U+211D). Those are stable Unicode facts, encoded in
EXCEPTIONS below and asserted at generation time, so a wrong/missing hole fails
loudly here rather than silently dropping a glyph in production.

Run: `conda run -n p314 python gen_mathvariants.py`  (stdlib only; no deps)
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

# KaTeX mathvariant value -> the Unicode NAME fragment for that style.
# We generate the full MathML standard set (not just what Hugo's current KaTeX
# emits) so a future KaTeX that starts emitting, say, sans-serif-italic is
# already covered. `normal` is deliberately absent: it means "upright ASCII",
# has no alphanumeric-block glyph, and is the one value MathML Core still honors
# -- the transform must leave `mathvariant="normal"` untouched.
STYLES: dict[str, str] = {
    "bold": "BOLD",
    "italic": "ITALIC",
    "bold-italic": "BOLD ITALIC",
    "script": "SCRIPT",
    "bold-script": "BOLD SCRIPT",
    "fraktur": "FRAKTUR",
    "bold-fraktur": "BOLD FRAKTUR",
    "double-struck": "DOUBLE-STRUCK",
    "sans-serif": "SANS-SERIF",
    "bold-sans-serif": "SANS-SERIF BOLD",
    "sans-serif-italic": "SANS-SERIF ITALIC",
    "sans-serif-bold-italic": "SANS-SERIF BOLD ITALIC",
    "monospace": "MONOSPACE",
}

# The holes: (variant, base char) -> the actual Unicode NAME to resolve, because
# the glyph lives in Letterlike Symbols instead of the math block. Fully
# enumerated and asserted below; these do not change (Unicode is append-only).
EXCEPTIONS: dict[tuple[str, str], str] = {
    ("italic", "h"): "PLANCK CONSTANT",
    ("script", "B"): "SCRIPT CAPITAL B",
    ("script", "E"): "SCRIPT CAPITAL E",
    ("script", "F"): "SCRIPT CAPITAL F",
    ("script", "H"): "SCRIPT CAPITAL H",
    ("script", "I"): "SCRIPT CAPITAL I",
    ("script", "L"): "SCRIPT CAPITAL L",
    ("script", "M"): "SCRIPT CAPITAL M",
    ("script", "R"): "SCRIPT CAPITAL R",
    ("script", "e"): "SCRIPT SMALL E",
    ("script", "g"): "SCRIPT SMALL G",
    ("script", "o"): "SCRIPT SMALL O",
    ("fraktur", "C"): "BLACK-LETTER CAPITAL C",
    ("fraktur", "H"): "BLACK-LETTER CAPITAL H",
    ("fraktur", "I"): "BLACK-LETTER CAPITAL I",
    ("fraktur", "R"): "BLACK-LETTER CAPITAL R",
    ("fraktur", "Z"): "BLACK-LETTER CAPITAL Z",
    ("double-struck", "C"): "DOUBLE-STRUCK CAPITAL C",
    ("double-struck", "H"): "DOUBLE-STRUCK CAPITAL H",
    ("double-struck", "N"): "DOUBLE-STRUCK CAPITAL N",
    ("double-struck", "P"): "DOUBLE-STRUCK CAPITAL P",
    ("double-struck", "Q"): "DOUBLE-STRUCK CAPITAL Q",
    ("double-struck", "R"): "DOUBLE-STRUCK CAPITAL R",
    ("double-struck", "Z"): "DOUBLE-STRUCK CAPITAL Z",
}

DIGIT_WORDS = ["ZERO", "ONE", "TWO", "THREE", "FOUR",
               "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]


def resolve(variant: str, base: str, residue_name: str) -> str | None:
    """Return the styled glyph for (variant, base), or None if it doesn't exist.

    `residue_name` is the part after the style, e.g. "CAPITAL A" / "DIGIT ZERO"
    / "SMALL ALPHA". Tries the math-block name first, then the explicit
    exception, then gives up (-> None, caller lets it fall to pseudo-bold).
    """
    style_frag = STYLES[variant]
    try:
        return unicodedata.lookup(f"MATHEMATICAL {style_frag} {residue_name}")
    except KeyError:
        pass
    alt = EXCEPTIONS.get((variant, base))
    if alt is not None:
        try:
            return unicodedata.lookup(alt)
        except KeyError as exc:  # a listed exception that won't resolve = a bug
            sys.exit(f"EXCEPTION name failed to resolve: {alt!r} ({exc})")
    return None


def greek_bases() -> list[tuple[str, str]]:
    """(base_char, residue_name) for Greek letters that have math variants.

    KaTeX emits the plain Greek character (e.g. 'θ' U+03B8) as the base, so we
    key on that character and derive the residue from its Unicode name
    ("GREEK SMALL LETTER THETA" -> "SMALL THETA").
    """
    out: list[tuple[str, str]] = []
    # Capitals U+0391-03A9, smalls U+03B1-03C9 (skip the unassigned U+03A2).
    for cp in list(range(0x0391, 0x03AA)) + list(range(0x03B1, 0x03CA)):
        ch = chr(cp)
        try:
            name = unicodedata.name(ch)
        except ValueError:
            continue
        # "GREEK CAPITAL LETTER ALPHA" -> "CAPITAL ALPHA"
        if name.startswith("GREEK CAPITAL LETTER "):
            out.append((ch, "CAPITAL " + name.removeprefix("GREEK CAPITAL LETTER ")))
        elif name.startswith("GREEK SMALL LETTER "):
            out.append((ch, "SMALL " + name.removeprefix("GREEK SMALL LETTER ")))
    return out


def build() -> dict[str, dict[str, str]]:
    table: dict[str, dict[str, str]] = {}
    greeks = greek_bases()
    for variant in STYLES:
        m: dict[str, str] = {}
        # Latin
        for base in [chr(c) for c in range(ord("A"), ord("Z") + 1)]:
            g = resolve(variant, base, f"CAPITAL {base}")
            if g:
                m[base] = g
        for base in [chr(c) for c in range(ord("a"), ord("z") + 1)]:
            g = resolve(variant, base, f"SMALL {base.upper()}")
            if g:
                m[base] = g
        # Digits
        for d, word in enumerate(DIGIT_WORDS):
            g = resolve(variant, str(d), f"DIGIT {word}")
            if g:
                m[str(d)] = g
        # Greek
        for base, residue in greeks:
            g = resolve(variant, base, residue)
            if g:
                m[base] = g
        table[variant] = m
    return table


def sanity_check(table: dict[str, dict[str, str]]) -> None:
    """Assert the well-known counts so a broken generation fails loudly."""
    # Bold, italic, bold-italic, sans-serif-bold, sans-serif-bold-italic are the
    # complete-Latin variants (52 letters each).
    for v in ("bold", "italic", "bold-italic"):
        letters = {c for c in table[v] if c.isascii() and c.isalpha()}
        assert len(letters) == 52, f"{v}: expected 52 Latin, got {len(letters)}"
    # Double-struck must include the 7 Letterlike-hole capitals.
    for cap in "CHNPQRZ":
        assert cap in table["double-struck"], f"double-struck missing {cap}"
    # Italic small h is the Planck-constant hole.
    assert table["italic"]["h"] == "ℎ", "italic h should be U+210E"
    # Digits only exist for these variants.
    for v in ("bold", "double-struck", "sans-serif", "bold-sans-serif", "monospace"):
        assert all(str(d) in table[v] for d in range(10)), f"{v}: missing digits"
    assert "0" not in table["italic"], "italic should have no digits"


def to_yaml(table: dict[str, dict[str, str]]) -> str:
    lines = [
        "# GENERATED by docs/math-bold-research/gen_mathvariants.py -- do not edit by hand.",
        "# Maps KaTeX mathvariant value -> { base character: Unicode math glyph }.",
        "# Consumed by layouts/_partials/mathvariant-fix.html. See the research doc",
        "# for why this exists and when it can be retired.",
    ]
    for variant, m in table.items():
        lines.append(f"{variant}:")
        for base, glyph in m.items():
            # Quote both key and value; both are single chars, some non-ASCII.
            b = base.replace('"', '\\"')
            lines.append(f'  "{b}": "{glyph}"')
    return "\n".join(lines) + "\n"


def main() -> None:
    table = build()
    sanity_check(table)
    out = Path(__file__).resolve().parents[2] / "data" / "mathvariants.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_yaml(table), encoding="utf-8")
    total = sum(len(m) for m in table.values())
    print(f"Wrote {out} ({len(table)} variants, {total} glyph mappings)")
    for v, m in table.items():
        print(f"  {v:24} {len(m):3} glyphs  e.g. A->{m.get('A', '-')}")


if __name__ == "__main__":
    main()
