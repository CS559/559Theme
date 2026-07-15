# Bold math in MathML — research & recommendation

**Status: implemented in 559Theme, validated on 559Tutorials (2026-07-14).**
Path B (Unicode substitution) is built and passing in both Chromium and Firefox.
The decisions and rationale are in
"[Implementation decisions & rationale](#implementation-decisions--rationale-2026-07-14)";
the concrete files and validation results are in
"[What was built](#what-was-built--validation-results)". Not yet ported to
Workbook (a later pass). This document records what was tried, what the evidence
showed, and why the chosen fix is safe, so the reasoning survives the code.

Related: [`../math.md`](../math.md) (how math works in the theme + the
`katex.css`/output-mode gotcha). Re-runnable test rigs: [`rigs/`](rigs/).

---

## TL;DR

- Math is rendered **at build time** by Hugo's `transform.ToMath` (KaTeX). Its
  **default output is MathML**, which the browser lays out natively — **no
  `katex.css`, no JS, no fonts, no CDN.** Structurally it renders beautifully.
- **Bold is the one failure.** `\mathbf{…}` / `\boldsymbol{…}` render at normal
  weight **in Chromium** (and Chromium-family browsers), because **Chromium's
  MathML Core ignores the `mathvariant="bold"` attribute** that KaTeX emits.
  **Firefox honors it** and renders correct bold.
- **There is no CSS-only fix.** `font-weight` (any value) does nothing —
  Chromium won't synthesize bold on the math font. `-webkit-text-stroke`
  *does* thicken glyphs, but it **double-bolds in Firefox** (which is already
  bold), so it needs fragile browser-sniffing.
- **Recommended fix (Path B): rewrite KaTeX's `mathvariant` glyphs to the actual
  Unicode Mathematical-Alphanumeric characters (𝐀, 𝐱, 𝛉…) at build time.** These
  are real bold glyphs, so they render bold in **every** browser with **zero**
  CSS/fonts/CDN and correct scaling. Add a **strip-attribute + `-webkit-text-stroke`
  pseudo-bold fallback** for any character not in the mapping, to remove the only
  risk (mapping completeness).

---

## Background: how math renders here

Two shortcodes call `transform.ToMath` (see [`../math.md`](../math.md)):

- `math.html` — inline. `displaymath.html` — numbered display equations.
- Neither passes an `output` option, so KaTeX uses its **default, MathML**.
- For `\mathbf{A}`, KaTeX emits: `<mi mathvariant="bold">A</mi>` — i.e. a plain
  ASCII "A" carrying a `mathvariant` **attribute**, *not* the bold character.

The relevant fact about that markup is how each browser treats the attribute.

---

## 1. What `katex.css` actually does (and why we don't load it)

`transform.ToMath` can emit MathML (default) or KaTeX **HTML** (`output:"html"`,
a tree of positioned `<span>`s). We render the same equations both ways with
**no `katex.css`**:

![MathML vs HTML output, no katex.css — Chromium](img/01-katexcss-mathml-vs-html-chromium.png)

- **`output:"mathml"` (middle): renders correctly with no CSS** — superscripts,
  the integral, the summation with limits and fractions, all laid out natively.
- **`output:"html"` (right): garbled** — superscripts not raised, integral and
  sum mangled and wrapped. The KaTeX `<span>`s are meaningless without
  `katex.css` positioning them.

**Conclusion:** `katex.css` is mandatory **only** for `output:"html"`. That is
why the Workbook theme (which forces `output:"html"`) loads `katex.css` — and
why removing it there breaks math. The 559Theme uses MathML and correctly needs
no CSS. *Do not switch `output` to `html`/`htmlAndMathml` without bundling
self-hosted `katex.css` + KaTeX fonts.*

---

## 2. The bold problem and its root cause

Rendering one bold expression under several CSS treatments, **in Chromium**:

![bold treatments — Chromium](img/02-bold-treatments-chromium.png)

- **as-is, `font-weight:700`, `font-weight:900`, `font-weight:800`+forced
  `font-synthesis` — all four are pixel-identical, none bold.**
- **`-webkit-text-stroke` (.4px / .7px) and `text-shadow` — visibly bold.**

Root cause, confirmed by probing computed styles (`browser_evaluate`):

- The glyph renders with `font-family: math` (the browser's OpenType math font).
- `font-synthesis: weight` is **enabled**, yet a `font-weight:700` glyph has the
  **same advance width** as normal (measured 13.6px vs 13.6px; at 34px font,
  23.16px identical across *all* weight treatments). **Chromium does not
  synthesize faux-bold for the math font.**
- Chromium also **ignores the `mathvariant="bold"` attribute** entirely (MathML
  Core dropped it — it expects the *content* to already be bold characters).
  Measured: a plain `<mi>A</mi>` and `<mi mathvariant="bold">A</mi>` have the
  **identical** advance width (27.2px) — the attribute does nothing.

So no `font-weight` value can ever work (it is not a threshold problem — 837 or
917 would be identical). The only CSS lever that changes anything is stroking
the glyph outline.

---

## 3. The cross-browser split

The same treatments **in Firefox**:

![bold treatments — Firefox](img/03-bold-treatments-firefox.png)

- **as-is is already properly bold** — Firefox *honors* `mathvariant="bold"` and
  renders real bold math (it looks great; it needs no fix).
- **`-webkit-text-stroke` double-bolds** — bold glyph + stroke = too heavy,
  counters filling in.

So the browsers are split:

| Browser | `mathvariant="bold"` | Result | Needs |
|---|---|---|---|
| Chromium / Edge / Chrome | **ignored** | plain (wrong) | help (stroke or real bold char) |
| Firefox | **honored** | correct native bold | nothing — must NOT be stroked |
| Safari / WebKit | *unverified* (likely MathML-Core-like → ignored) | probably plain | probably help |

An unconditional `-webkit-text-stroke` fixes Chromium but breaks Firefox.
Scoping it to Chromium-only needs browser hacks that are dead or brittle
(`@-moz-document` no longer applies to web content; `@supports(-moz-appearance)`
is fragile). **Not acceptable for math-critical work.**

---

## 4. Approaches evaluated

| # | Approach | Works? | Cost / problem |
|---|---|---|---|
| font-weight | CSS `font-weight`/`font-synthesis` | ❌ | Chromium won't synth-bold math font; zero effect at any value |
| stroke | unconditional `-webkit-text-stroke` | ⚠️ | bold in Chromium, **double-bold in Firefox**; needs fragile sniffing |
| **B** | **Unicode substitution** (mathvariant char → 𝐀…) | ✅ | real bold **all** browsers, no CSS/fonts/CDN; needs a mapping table |
| C | `output:"html"` + self-hosted `katex.css` + fonts | ✅ | standard & robust, but ~400KB fonts + CSS; heaviest |
| strip+stroke | strip `mathvariant`, then uniform stroke | ⚠️ | consistent, but degraded pseudo-bold + throws away Firefox's good bold |

### Why Unicode substitution (B) works

`mathvariant="bold"` is *ignored*, but the actual Unicode **Mathematical Bold
Capital A** (U+1D400, "𝐀") is a real glyph in every math font. Measured widths:

| markup | advance width |
|---|---|
| `<mi>A</mi>` (plain) | 27.2px |
| `<mi mathvariant="bold">A</mi>` (KaTeX's output) | 27.2px — **ignored** |
| `<mi>𝐀</mi>` (U+1D400) | **30.0px — distinct bold glyph** ✅ |

Rewriting `<mi mathvariant="bold">A</mi>` → `<mi>𝐀</mi>` gives true bold in
Chromium **and** Firefox **and** (by construction) Safari, with no CSS and no
per-browser logic, and it scales with math size natively.

### Critique of "strip + uniform stroke"

The idea: normalize every browser to "plain," then thicken uniformly (no
sniffing). Tested directly:

![critique — Chromium](img/04-critique-chromium.png)
![critique — Firefox](img/05-critique-firefox.png)

Findings:

- **Row B: `font-weight:normal` does NOT neutralize Firefox** — it stays bold.
  Firefox's `mathvariant` bold is *glyph substitution*, immune to `font-weight`.
  So "tell Firefox to use regular weight" via CSS is impossible.
- **Row C: stripping the `mathvariant` attribute *does* neutralize Firefox** — it
  then renders plain, matching Chromium; a uniform stroke applies to both. So the
  idea works **only** with a **build-time transform** (strip attribute → class),
  not pure CSS. That is the same transform infrastructure Path B needs.
- **Quality: pseudo-bold is inferior** (compare row C stroke to row D real
  Unicode bold, in both browsers). It also **doesn't scale** — row E: a fixed-px
  stroke on a tiny subscript is proportionally too heavy, while the Unicode
  subscript stays crisp. And it **discards Firefox's free, high-quality native
  bold**.

Verdict: it solves *consistency* but by leveling everything down to a mediocre
pseudo-bold — and it still needs a transform. Since Path B needs the same
transform pass and its only extra cost is the (generatable) mapping table, **B
dominates** — except as a *fallback* for characters the mapping misses.

---

## Recommendation

**Implement Path B (Unicode substitution) with a strip+stroke fallback**:

1. A build-time transform over the `transform.ToMath` MathML output that, for
   each `<mi|mn|mo mathvariant="V">c</mi>`, replaces `c` with the corresponding
   Unicode Mathematical-Alphanumeric codepoint for variant `V` and drops the
   attribute. Cover the variants KaTeX emits: bold, italic, bold-italic,
   script/calligraphic, fraktur, double-struck, sans-serif (+bold/italic),
   monospace.
2. **Generate the mapping** with Python `unicodedata` (look up names like
   "MATHEMATICAL BOLD CAPITAL A"), *don't* hand-type it — this also handles the
   ~30 exception codepoints the block leaves out (ℎ, ℬ, ℯ, ℯ, ℊ, …, and the
   dotless/Planck cases). Emit as a theme data file.
3. **Fallback:** for any `(variant, char)` not in the mapping, instead of
   emitting a wrong/missing glyph, strip the attribute → add a class and apply a
   small `-webkit-text-stroke` pseudo-bold (size-aware if feasible). This removes
   the only real risk of Path B (mapping gaps) at the cost of occasional
   lower-quality bold on exotic glyphs.

**Where to build it:** likely in **Workbook first** (the math-heavy theme,
currently on the `output:"html"`+CDN-`katex.css` approach), then share the
transform with 559Theme so the whole site family renders math identically and
dependency-free. This would also let Workbook **drop its jsDelivr `katex.css`
CDN dependency** (an external dependency of the same class we removed from
559Theme when we deleted the MathJax partial).

**Validate** against real notation — the held-out 5th math-heavy site is the
acceptance set. Check in **Chromium and Firefox** (both drivable locally; see
`rigs/README.md`), and ideally Safari.

### Do NOT

- Do **not** rely on `font-weight` / `font-synthesis` (no effect in Chromium).
- Do **not** apply an unconditional `-webkit-text-stroke` (double-bolds Firefox).
- Do **not** switch to `output:"html"` without **self-hosted** `katex.css`+fonts
  (never a CDN).

---

## Implementation decisions & rationale (2026-07-14)

This section records the decisions made when we moved from "deferred" to
"implementing," and *why* — so the reasoning survives even after the code lands.

### Decision: build in 559Theme first (revises "Workbook first" above)

The recommendation above leaned toward Workbook-first. We chose **559Theme
first** instead, because 559Theme is *already* on the clean MathML path — the
transform slots straight into its existing `math.html`/`displaymath.html`,
whereas Workbook would first have to switch **off** its `output:"html"`+CDN
approach back to MathML *and then* add the transform. 559Theme is also where the
bug is confirmed (validated on 559Tutorials — see
`559Tutorials/docs/math-bold-validation/`), so it's the fastest path to a
validated fix. Workbook gets the shared transform in a later pass (and can then
drop its jsDelivr `katex.css` CDN dependency, as noted above).

### What KaTeX's MathML actually looks like (verified, not assumed)

Probed against Hugo 0.164's bundled KaTeX (`transform.ToMath`). The structure
determines whether a regex rewrite is safe — it is, but with nuance:

- **Letter runs are split into one element per character.** `\mathbf{abc}` →
  `<mi mathvariant="bold">a</mi><mi mathvariant="bold">b</mi>…`, and
  `\boldsymbol{\alpha\beta}` likewise (each Greek letter its own `<mi>`, variant
  `bold-italic`). So most "multiple characters in sequence" are already separate
  single-char elements — trivially handled.
- **Two cases keep a run inside one element**, so the transform must iterate over
  the element's characters, not do a single blind lookup:
  - **Multi-digit numbers:** `\mathbf{123}` → `<mn mathvariant="bold">123</mn>`
    (and `12.5` stays one `<mn>`).
  - **Text runs:** `\textbf{Hello}` → `<mtext mathvariant="bold">Hello</mtext>`
    (note: `mtext` is a **4th** tag beyond `mi|mn|mo`).
- **Bold operators effectively don't occur.** `\mathbf{a+b}` leaves `+` as a
  plain `<mo>+</mo>` (no variant); `<` renders as `<mo>&lt;</mo>` (no variant).
  So the HTML-entity-in-content hazard never coincides with an element we
  rewrite. We still defensively skip any matched content containing `&`.
- **Target elements contain only text**, no nested tags — the one nesting seen
  (`<mi><mrow>…</mrow></mi>` wrapping a `\boldsymbol` group) was on the *outer,
  variant-less* wrapper, which our pattern ignores. So a `<`-free content capture
  is unambiguous.

**Why regex is acceptable here** (it would not be for arbitrary MathML): this
MathML is machine-generated, narrow, well-formed, and `<`-free in the target
elements. We target `mi|mn|mo|mtext` carrying `mathvariant`, per-tag (Hugo's RE2
has no backreferences, so we can't match `</\1>`).

### KaTeX-stability analysis — is this a documented contract? (the key risk)

**No — and that shapes the design.** Findings:

- **`mathvariant` is a standard, documented MathML 3 attribute** — KaTeX emitting
  it is the conventional representation, not a private hack. But **KaTeX does not
  document its exact output structure as a stable API.** Maintainers state KaTeX's
  MathML "was written before MathML Core existed" and was designed for
  accessibility/screen-readers, not visual display
  ([discussion #3893](https://github.com/KaTeX/KaTeX/discussions/3893)).
- **There is a live intent to remove `mathvariant`**
  ([issue #4043](https://github.com/KaTeX/KaTeX/issues/4043), opened Apr 2025) —
  but it's open, unassigned, no PR, no milestone. No imminent change. KaTeX's own
  answer for MathML-Core-correct output is "use **Temml**" (a KaTeX fork), not
  "we'll change KaTeX" — so KaTeX itself is unlikely to move soon.
- **The version is pinned to Hugo** (bundled as a WASM blob via `warpc`). Output
  changes only when *we* bump Hugo — a deliberate, gated step (the theme has an
  upgrade process), never spontaneous.

### Failure-mode analysis (why this is safe to ship)

If a future Hugo/KaTeX bump changes the MathML output, the two directions are
**asymmetric**:

1. **Likely — KaTeX starts emitting real Unicode glyphs** (per #4043 / MathML
   Core). Our regex keys on `mathvariant="…"`, matches nothing → **no-op**, and
   bold is already correct because KaTeX now emits the bold glyph itself.
   **Fails safe;** our transform just becomes redundant.
2. **Dangerous — KaTeX keeps attribute-style styling but renames/restructures
   it.** Then our regex silently misses and bold silently regresses to
   broken-in-Chromium. Low probability (why swap one deprecated approach for
   another?), but the failure would be **silent**.

### Decision: build-time canary (kills the silent-failure case)

To convert case 2 from "silent Chromium regression discovered months later" into
"loud warning at the next build after a Hugo bump," the transform partial renders
a canary (`\mathbf{A}`) once per build and asserts the output still contains
`mathvariant="bold"`. On mismatch it `warnf`s — distinguishing "KaTeX went
Unicode (transform now redundant, safe)" from "KaTeX restructured (review the
transform)." Cheap; removes the only quiet failure mode.

**Bottom line:** this fix is a deliberate **workaround for a KaTeX limitation
that KaTeX itself intends to remove** — so it has a natural, graceful expiry, and
the canary ensures a version bump can't break it quietly.

---

## What was built & validation results

### Files (all in 559Theme)

- **`data/mathvariants.yaml`** — the generated mapping (13 variants, 971 glyph
  entries: Latin, digits, Greek). **Generated, do not hand-edit.**
- **`docs/math-bold-research/gen_mathvariants.py`** — the generator (stdlib
  `unicodedata`; `conda run -n p314 python gen_mathvariants.py`). Encodes the
  hole exceptions and self-checks counts so a bad generation fails loudly.
- **`layouts/_partials/math/variant-fix.html`** — the transform (input
  `dict "html" <MathML>`, returns rewritten MathML). Per-character substitution;
  keeps unmapped chars (e.g. the `.` in `12.5`) literal; pseudo-bold fallback
  only on a total miss.
- **`layouts/_partials/math/variant-canary.html`** — the build-time canary
  (`partialCached`, runs once/build).
- **`layouts/_shortcodes/math.html`, `displaymath.html`** — now pipe
  `transform.ToMath … | string` through `variant-fix`.
- **`assets/css/_559.scss`** — `.mv-pseudobold` fallback rule.

Gotcha for the next editor: inside a partial `$` is the passed-in dict, **not**
the page — use `hugo.Data` (not `.Site.Data`, which is also deprecated) to reach
the mapping.

### Validation (2026-07-14)

On 559Tutorials `content/splines/1/`, equation (2) `x,y=\mathbf{f}(t)`: built the
site against this theme and measured the rendered page. Result: **0
`mathvariant="bold"` left** (15 `mathvariant="normal"` correctly untouched), 28
real bold glyphs on the page.

- **Chromium** (DOM/canvas measurement via Playwright `browser_evaluate`, plus a
  direct headless-Chrome screenshot — the Playwright *screenshot* tool hangs
  because this MCP attaches to the user's shared real Chrome, not fonts; see the
  validation doc's tooling note): the old `<mi mathvariant="bold">A</mi>`
  measured *byte-identical* to plain (23.16px = 23.16px — the bug), while the
  substituted Unicode bold glyphs carry **30–40 % more ink** (canvas pixel count:
  A 1.34×, B 1.38×, x 1.30×, R 1.40×). Ink, not advance width, is the right
  metric — bold upright `𝐟` is narrower than *italic* plain `f`, so a width test
  misleads. Genuinely bold.
- **Firefox** (headless `--screenshot`): the new Unicode form renders bold and is
  **pixel-identical** to the old `mathvariant` form Firefox already bolded — no
  regression, no double-bold (we apply no stroke to substituted glyphs). Evidence:
  `559Tutorials/docs/math-bold-validation/img/after-fix-eq2-compare-firefox.png`.

### Deploying to sites

Changes live in this theme repo. Each consuming site picks them up by bumping its
`themes/559Theme` submodule pointer after the theme is committed/pushed (the
standard upgrade flow). During validation the files were copied into
559Tutorials' submodule working tree, then reverted — no site is committed yet.

### Not done

- **Port to Workbook** — switch it off `output:"html"`+CDN `katex.css` back to
  MathML and share this transform; then drop the jsDelivr dependency.
- **Safari** spot-check (expected to behave like Chromium → fixed).

---

## Files

- `img/` — the evidence screenshots referenced above (Chromium via Playwright;
  Firefox via headless `--screenshot`).
- `rigs/` — the re-runnable test harnesses + how to run them and re-capture.
