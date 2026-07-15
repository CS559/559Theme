# Math in the theme

## How math is rendered

Math is rendered at **build time** (not in the browser) by Hugo's native
`transform.ToMath` function (KaTeX, embedded in Hugo ≥ 0.144). There is **no
client-side JavaScript** — no MathJax, no KaTeX JS, no CDN. This was a
deliberate goal (compile-time, not page-view-time); as of Hugo 0.144 the native
function achieves it, so the theme's math shortcodes are thin wrappers over it
— with one addition: the MathML `transform.ToMath` returns is then piped
through a second, theme-owned build-time pass (`partial
"math/variant-fix.html"`) that rewrites bold/script/etc. glyphs for
cross-browser correctness. See "Bold math" below.

Entry points (see `docs/shortcodes.md` for full usage):

- `math` — inline math. `{{< math "a^2+b^2=c^2" >}}` (add `display="true"` for a
  bare display equation).
- `displaymath` — a **numbered** display equation, with an optional `id`:
  `{{% displaymath id="euler" %}}e^{i\pi}+1=0{{% /displaymath %}}`.
- `eqref` — a cross-reference to a numbered equation: `{{< eqref "euler" >}}`
  renders "Equation N". Numbering is tracked per page via `.Page.Scratch`
  (`eq_counter` / `eq_refs`).

The removed `mathjax.html` partial (MathJax 2.x from a CDN, client-side) is gone
— `transform.ToMath` makes it unnecessary.

## What it needs to display correctly (read this — it has bitten us)

`transform.ToMath` emits **MathML** (its default output), wrapped in a
`<span class="katex">`. MathML is laid out **natively by the browser**.

- **Modern browsers render it with no extra CSS.** Verified: MathML support is
  native in Chromium ≥ 109 (Jan 2023), Firefox (always), and Safari ≥ 14.1. A
  build-time-rendered integral shows correct stacked limits and fractions with
  zero stylesheet.
- **Bold math (fixed).** `\mathbf{…}` / `\boldsymbol{…}` render at normal
  weight in Chromium-family browsers if left alone — KaTeX emits `<mi
  mathvariant="bold">A</mi>` and Chromium's MathML Core ignores the
  `mathvariant` attribute (Firefox honors it and needs no fix). There is **no
  CSS-only fix** (`font-weight` has no effect on the math font). The theme
  fixes this at build time: `math.html` and `displaymath.html` pipe
  `transform.ToMath`'s output through `partial "math/variant-fix.html"`,
  which rewrites every `mathvariant`-carrying character to the real Unicode
  Mathematical-Alphanumeric glyph (𝐀, 𝐱, 𝛉…) using the generated mapping in
  `data/mathvariants.yaml` — so it's genuinely bold in every browser, no CSS
  involved. A build-time canary (`partial "math/variant-canary.html"`) probes
  `\mathbf{A}` once per build and `warnf`s if a future Hugo/KaTeX bump changes
  the MathML shape this relies on. Full investigation, evidence, and
  validation results are in
  [`math-bold-research/`](math-bold-research/README.md); **not yet ported to
  Workbook** (a separate theme also affected — see that doc for status).
- **The theme CSS math depends on**: the numbered-display-equation layout —
  `.math-display`, `.math-content`, `.math-number` in
  `assets/css/_559.scss`. These position the `(N)` number to the right and let
  long equations scroll. There's also `.mv-pseudobold`, the fallback rule
  `variant-fix.html` applies on the rare total miss (a character with no
  Unicode bold mapping) — a `-webkit-text-stroke` pseudo-bold, strictly
  worse-but-present rather than silently plain. All of these are compiled into
  every site's CSS unconditionally (via `main.scss` → `_559.scss`). **Keep
  them** — without `.math-display`/etc. numbered equations lose their layout
  (the number won't sit beside the equation, no horizontal scroll for wide
  equations). Inline math and un-numbered display math need no theme CSS
  beyond the pseudo-bold fallback.

### The gotcha (why "compile-time math still needs CSS")

`transform.ToMath` also has `output: "html"` and `output: "htmlAndMathml"`
modes. Those emit KaTeX's **HTML+CSS** representation (spans with classes like
`.mord`, `.mfrac`, `.strut`), which is **unreadable garbage without
`katex.css` and the KaTeX web-fonts** loaded. The theme deliberately uses the
**default MathML output**, which needs none of that. So:

- **Do not** set `output` to `html`/`htmlAndMathml` in the shortcodes unless you
  also bundle `katex.css` + the KaTeX fonts into the theme's asset pipeline.
  That is the failure mode that has burned us before: switch the output mode,
  forget the CSS, and every equation renders as overlapping garbled glyphs.
- Trade-off if you ever need it: `htmlAndMathml` renders identically on very old
  browsers (pre-2023 Chromium) that lack MathML, at the cost of bundling
  ~concat KaTeX CSS + fonts. We chose MathML-only because all current browsers
  support it and it keeps the theme dependency-free.

## Deferred: goldmark passthrough (`$…$` / `$$…$$`) — investigation notes

Investigated 2026-07; **not implemented** (no current site needs inline-delimiter
authoring). Recorded so we don't re-derive it.

Passthrough lets authors write math with delimiters directly in markdown instead
of via shortcodes. To keep it **build-time**, pair it with a render hook that
calls `transform.ToMath`:

~~~toml
# hugo.toml (per site that opts in)
[markup.goldmark.extensions.passthrough]
enable = true
[markup.goldmark.extensions.passthrough.delimiters]
block  = [['$$', '$$'], ['\[', '\]']]
inline = [['\(', '\)']]          # NB: deliberately NOT '$'…'$' — see footgun
~~~

~~~go-html-template
{{/* layouts/_markup/render-passthrough.html */}}
{{- $display := eq .Type "block" -}}
{{- with try (transform.ToMath .Inner (dict "displayMode" $display)) -}}
  {{- with .Err -}}{{ errorf "math %s: %s" $.Position . }}
  {{- else -}}{{ .Value }}{{- end -}}
{{- end -}}
~~~

Findings from a prototype build:

- **Works, build-time MathML** — same rendering path as the shortcodes.
- **Numbering carries over** — a `.Page.Scratch` counter in the hook can number
  `$$…$$` blocks exactly like `displaymath`.
- **`$…$` inline is a footgun (confirmed).** With single-dollar inline enabled,
  prose like "it costs $5 today and $10 tomorrow" parses `$5 … $10` as math.
  **Use `\(…\)` for inline**, never `$…$`.
- **`eqref` cross-refs are not free.** KaTeX's `\label`/`\eqref` support is
  limited, so a passthrough setup would need the hook to parse a label out of
  the math source and register it in Scratch (as `displaymath` does), plus keep
  an `eqref`-style resolver. Moderate work — the main reason to keep the
  `displaymath`/`eqref` shortcodes even if passthrough is added later.

If adopted, it is **additive**: the shortcodes stay for numbered / cross-
referenced equations; passthrough just adds ergonomic inline authoring.
