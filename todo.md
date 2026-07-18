# Known to-dos for the 559 Theme

Backlog for the theme itself. Merged in the workspace-level `TO-DO.md`
(2026-07-15) now that the theme-unification project is complete and that
workspace isn't version-controlled — this is the one authoritative copy
going forward. Checked items are done; unchecked items are open and
independent of each other.

- [x] Update to the new mathematics implementation / get rid of runtime
      latex (mathjax) — done: `math`/`displaymath` now render via Hugo's
      native `transform.ToMath` (KaTeX) at build time, no client-side JS.
      See `docs/math.md`.
- [x] come back to the math bold problem — fully done and deployed. Path B
      (Unicode substitution) built in 559Theme, validated on 559Tutorials
      (Chromium + Firefox); see `docs/math-bold-research/`. All four
      workspace sites bumped past the fix (2026-07-15). Remaining: port the
      same transform to the separate Workbook theme.
- [x] test on the "holdout site" - 559Tutorials (with Splines)
- [x] (note: this was 4.3) get rid of lnk, disallow two unnamed parameter link
- [x] new setup instructions — `docs/upgrading.md` (first-time setup +
      routine-bump procedure + changelog), written and verified against real
      bumps of all four sites.
- [x] Full and complete documentation — substantially done: `readme.md`,
      `docs/*.md` (upgrading, math, search, data-contracts, link-shortcode,
      deprecation, shortcodes) all audited against the actual code and
      brought current (2026-07-15). "Full and complete" is aspirational by
      nature, so treat this as done rather than perpetually open — reopen
      only if a specific gap is found.
- [ ] try out better permalink structure for tags/taxonomies — this seemed
      to come around Hugo 1.115 and 1.118
- [x] Make sure that thumbnails really produce smaller images, not just
      showing big images at large size. This should also work for rimage
      and whatever other image display code there is.
      rimage fixed (scoping bug dropped the .Fit result → served full-size);
      now emits a downsized copy + links the original, plus width="45%" and
      width="native" modes. resource-image deprecated in favor of rimage.
      STILL OPEN: post_thumbnail.html serves full-size images as thumbnails
      (no .Fit) — list-page perf; and figure.html doesn't resize.
- [ ] standardize on one image shortcode
- [ ] proper footer, colophon
- [ ] get rid of i18n (?)
- [ ] look at social media stuff (does removing it simplify)
- [x] auto checks (make sure that roadster isn't included anymore) —
      roadster *is* structurally gone (no submodule, no references, verified
      repeatedly), but no automated CI check asserts this; still open if you
      want a guard against it creeping back in.
- [ ] make sure that we can create new presets, and experiment with an
      example — the preset *system* works (`uw-serif`, `mainroad-sans` are
      two real, independently-verified presets), but a third preset was
      never built as an explicit test of "can a new one be added easily."
      Still open.
- [ ] alternate mechanism for mobile menus to avoid the JS
- [ ] reconsile with Workbook theme — separate theme, not in this
      workspace; the math-bold fix and the sp26-mixin-shortcode retirement
      (see `THEME-PLAN.md`'s "External-consumer constraints") both have an
      open dependency on this happening eventually.
- [ ] test the new tooltips extensively
