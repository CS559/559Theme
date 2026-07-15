# Search (MiniSearch)

Phase 5b replaced Lunr with [MiniSearch](https://github.com/lucaong/minisearch).
Lunr's actual problems were the unpinned `unpkg.com/lunr/lunr.js` dependency,
rebuilding the whole index in the browser on every search, and a 140-line
renderer living in `content/` (Go-templated content pages can't use Hugo
Pipes). None of that required a post-build indexing step, so a client-side
library stayed the right fit — site scale here is small (~165–300KB raw text
per site, ~100KB gzipped indexed).

## How it's wired

- **`layouts/index.json`** (Hugo's `JSON` home output, `outputs.home` must
  include `"JSON"`) — one object per page: `uri` (`Permalink`), `title`,
  `section`, `tags`, `description`, and the **full** `plainify`-ed `content`
  (not truncated — a cap would exclude long module pages, exactly what needs
  to be searchable, and would regress recall vs. the old Lunr setup).
- **`assets/js/minisearch.js`** — the official MiniSearch UMD build, vendored
  (not loaded from a CDN). See the header comment in the file for the exact
  version/source. It's unminified as shipped by the npm package (recent
  MiniSearch releases don't ship a prebuilt `.min.js`); `layouts/search.html`
  runs it through `resources.Minify` + `resources.Fingerprint` at build time,
  so the compiled output is minified and cache-busted even though the vendored
  source isn't.
- **`assets/js/search.js`** — the results renderer (this theme's code, not
  vendored). Reads `window.MiniSearch` (set by the UMD script) and
  `window.SEARCH_INDEX_URL` (set inline by `layouts/search.html` from
  `relURL "index.json"` — never hard-coded, so it works under any site's
  subpath baseURL). Builds every result node via `createElement`/
  `createTextNode`, never `innerHTML` for content, so neither page content nor
  the user's `?q=` string can be interpreted as markup. (`innerHTML = ""` is
  used once, to clear the results container between searches — no untrusted
  string ever passes through it.)
- **`layouts/search.html`** — the results page template (`content/search.html`
  sets `layout: "search"` to select it). Replaces the old
  `content/lunr-search.html`, which embedded the whole renderer as an inline
  `<script>` in a markdown content file (the only way to get Hugo Pipes
  treatment for the vendored library is a real template, not content).
- **`layouts/_partials/widgets/search.html`** — the sidebar search box widget.
  `layouts/_partials/widgets/lunr.html` is kept as a **deprecated alias**
  (`warnf`, then delegates to `widgets/search.html`) so existing sites'
  `params.widgets = [...,"lunr",...]` keep working with a one-line build
  warning; rename to `"search"` at your convenience.

## Search tuning: why `combineWith: "AND"`

`assets/js/search.js` configures MiniSearch with `prefix: true`, `fuzzy: 0.2`,
and **`combineWith: "AND"`** (MiniSearch's default is `"OR"`). This isn't
cosmetic — measured on VisSnacks, a two-word test query ("Dis-Aggregating",
which tokenizes to `dis` + `aggregating`) matched **38 of 45 pages** under the
`OR` default: `prefix`/`fuzzy` expand a short, common fragment like `dis` to
match almost any page, and `OR` only needs one query word to hit. Switching to
`AND` (every query word must match somewhere in the document) brought the
same query down to 1–3 results with the true match ranked first by a wide
score margin, while still tolerating typos via `fuzzy`/`prefix` on each
individual word. If you ever revisit this config, re-run a real multi-word
query against real content and look at the result *count*, not just whether
the top hit is right — the looseness doesn't show up in a build or an
HTML-diff, only in actually using the search box.

## Ranking: title matches are prioritized

`assets/js/search.js` indexes three fields per page — `title`, `tags`,
`content` — and configures MiniSearch with `boost: { title: 15, tags: 10,
content: 5 }`. A query word found in the title counts far more toward a
page's relevance score than the same word found in body content, so a page
whose *title* matches the query ranks above pages that merely mention it in
passing. This was the "does it check page titles" question left open by the
old Lunr renderer (which never indexed title at all) — MiniSearch does, and
weights it highest.

**Verified** (2026-07-15) on a real build of VisSnacks: querying `comparison`
returns the page titled "Considerations for Visualizing Comparison" first,
ahead of four other pages that only mention "comparison" in body text
(`critiques/240830-yeping-axis`, `snacks/app-time-graphs`,
`critiques/250517-college-line-chart`, and the auto-generated `allpages`
listing). If you ever change the boost weights or field list, re-verify with
a query like this — a title-vs-content ranking regression won't show up in a
build or an HTML-diff, only in the actual result order.

## Site setup

A site needs, same as before:

```toml
[outputs]
home = ["HTML", "RSS", "JSON"]
```

and `"search"` (or the deprecated `"lunr"` alias) somewhere in the widget
list — a site-wide `params.sidebar.widgets`, or a page's own `widgets:`
front-matter override (see `layouts/_partials/sidebar.html`). No other
per-site content is needed — `content/search.html` ships from the theme
itself, the same way `content/lunr-search.html` did.

## Future option: Pagefind

If a site's index ever exceeds ~1MB gzipped, or full-text relevance ranking
becomes the bottleneck, the recorded upgrade path is
[Pagefind](https://pagefind.app/) — rejected for now because it needs a
post-build indexing step Hugo can't run itself, and `hugo server` renders to
memory so dev search would break under it. The widget/page boundary here
(`widgets/search.html` + `layouts/search.html`) is the seam to swap.
