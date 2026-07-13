# Test rigs for the math-bold investigation

These are the throwaway harnesses used to produce the evidence in
`../README.md`. They are self-contained and re-runnable. Each renders KaTeX /
MathML output so you can inspect it in a real browser (the whole point: this
behavior can only be judged by *rendering*, not by reading markup).

Requires: Hugo ≥ 0.144 (for `transform.ToMath`) — the repo standard is 0.164.

## `mathcompare/` — what `katex.css` actually does

A Hugo site that renders the same equations two ways side by side:
`transform.ToMath` with `output: "mathml"` vs `output: "html"`, **with no
`katex.css` loaded**. Shows that MathML renders natively while HTML output is
garbled without the stylesheet.

```sh
cd mathcompare && hugo serve --port 1331
# open http://localhost:1331/
```

## `boldwhy/` — why `font-weight` fails, and which pseudo-bold works

A Hugo site rendering one bold expression under several CSS treatments
(`font-weight:700/900`, forced `font-synthesis`, `-webkit-text-stroke`,
`text-shadow`). Compare in **both** Chromium and Firefox — the result differs by
browser, which is the crux.

```sh
cd boldwhy && hugo serve --port 1332
```

## `boldcrit-static.html` — critique of the "strip + uniform stroke" idea

A static HTML page (hand-written MathML, no Hugo needed) comparing: as-is
`mathvariant`, `mathvariant`+`font-weight:normal`, `mathvariant` stripped +
stroke, real Unicode bold (𝐀), and stroke-on-a-subscript (scaling). Serve it and
view in both browsers.

```sh
python3 -m http.server 1333   # from this rigs/ dir; open .../boldcrit-static.html
```

## Capturing screenshots (how the evidence images were made)

- **Chromium:** via the Playwright MCP — `browser_navigate` to the URL, then
  `browser_take_screenshot` with `fullPage: true`.
- **Firefox (headless):** Firefox needs a separate profile if another instance
  is open:

  ```sh
  /Applications/Firefox.app/Contents/MacOS/firefox --headless --new-instance \
    --profile /tmp/ffprof --window-size=420,760 \
    --screenshot /path/out.png http://localhost:PORT/
  ```

- **Programmatic probing** (advance widths, computed styles, MathML support) was
  done with the Playwright MCP `browser_evaluate` — e.g. measuring that a
  `font-weight:700` glyph has the *same* advance width as normal (no synthesis),
  and that U+1D400 (𝐀) is a *wider, distinct* glyph from a plain "A".
