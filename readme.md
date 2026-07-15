# CS559 Theme

A theme created by Michael Gleicher to make a class web page. Over time, it evolved to also do my home page, so there is a lot of stuff specific to that.

The theme was originally an overlay on top of an existing Hugo theme (MainRoad,
then Roadster after MainRoad was abandoned). In December 2025, a cleanup pass
unified the SASS compilation pipeline. In summer 2026, a larger "unification"
project (see `THEME-PLAN.md`) absorbed Roadster entirely, promoted several
per-site/per-course shortcodes into the core theme, replaced Lunr search with
MiniSearch, and introduced style presets. **559Theme is now self-contained —
it no longer depends on Roadster or MainRoad at build time.** If you're
bumping an existing site's theme submodule, `docs/upgrading.md` is the guide
to follow (routine bump, first-time setup, and a changelog of breaking
changes); this readme is the general reference.

A course site can still layer its own overlay theme on top (e.g. a
per-semester repo with course-specific content and config), but that overlay
is no longer required — a bare `theme = ["559Theme"]` is enough for a working
site.

- Variables for tuning:
  - noheader - set to true on a page to skip the header (default/baseof.html) - this was meant to allow the home page to look different
  - myreadmore - true (by default) for a less obnoxious read me in a summary (and a link if the summary is the whole page)

Changes (not exhaustive; this list predates the 2026 unification project —
see `THEME-PLAN.md`'s Execution log and `docs/upgrading.md`'s changelog for
everything since):

- Add Section summaries to page list summaries (default/list.html)
- Add lunr search (content/lunr-search, widgets/lunr, index.json) — since
  replaced by MiniSearch, see docs/search.md (`widgets/lunr` kept as a
  deprecated alias for `widgets/search`)
- A taglist for post_meta
- Put the logo in the header (assets/svg, partials/header)
- Sidebar widgets (`layouts/_partials/widgets/`) — see `params.sidebar.widgets`
  (or `params.widgets`) to pick which ones a site shows, in what order:
  - search (search box; `lunr` kept as a deprecated alias)
  - toc (puts a table of contents in the sidebar)
  - links / blogroll (a link list page - must be `content/widgetlinks` - be sure to create **widgetlinks**)
  - sectionlinks (a hand-curated link list page - must be `content/sectionlinks`)
  - sections (auto-generated list of the site's top-level sections)
  - allpages (makes a list of all pages in a site - not sure how to scope it correctly, probably not that valuable)
  - categories / taglist (auto-generated from the site's taxonomies)
  - archive (puts a message that this is an archived class - be sure to set `Site.Params.archive`/`archivenote`, optionally `archivenexturl`/`archivenextname`)
  - recents (useful thing from other blog-like themes) - uses `Site.Params.recentSections` to pick which sections count as "recent"
  - important - makes a list of important pages (uses a site parameter "ImportantPages", optionally "ImportantPagesTitle")
  - thisweek - puts a "this week" page in the sidebar (set `Site.Params.thisweek` to the page, optionally `thishead` for the title)
- change the footer credits (i18n/en)
- SASS friendly CSS loading (baseof)
- multiple built in CSS files (baseof)
- less obnoxious read more (summary.html) (set myreadmore to true)
- shortcodes - see the list below
- pagination of sections is improved
  - pagination controls has first/last
  - section pages can control paginate and top_pagination (this is per section)
    - but there is a site default (for top_pagination)
  - lists show subsections, not just pages (hacky right now)
- switch the "expand" shortcode to use HTML details (see book)
- footer uses lastmod (good with git - *be sure to turn on git*)
- header hard codes wisc styling and logo
- sections for talks and videos (and other collection of objects)
  - some attempts for unification
  - put "visual_summary" as a page parameter (to true) to get it
- some colors and stylings are changed - done since styles.css got converted to scss
- copyrightdate

## CSS Architecture

The theme uses a unified SASS compilation pipeline to keep styles clean and maintainable (originally unified in Dec 2025; a style-preset layer was added on top in the 2026 unification — see "Style presets" below).

*   **`assets/css/main.scss`**: The entry point, and the *only* file run through Hugo's template engine. It turns Hugo params (`config.toml`, `params.style.*`) into SASS variables, picks a style preset, then imports the pure-SASS partials below.
*   **`assets/css/presets/_uw-serif.scss`** & **`assets/css/presets/_mainroad-sans.scss`**: The two style presets (see "Style presets"). Each defines the same set of `!default` SASS variables (fonts, colors, layout widths, etc.) so the partials below don't need to branch on which preset is active.
*   **`assets/css/_style.scss`**, **`assets/css/_559.scss`** & **`assets/css/_v2menu.scss`**: Pure SASS partials containing the actual styles, consuming the variables the preset defined. These files contain **no** Hugo templating syntax (`{{ ... }}`), making them valid SASS files that standard SASS tooling can lint.

## New Section Variables

- visual_summary - uses a format for talks/videos where everything has a place for a thumbnail and links to the various assets are shown

## New Page Variables

- redirect - give a URL that directs to a newer version of the page (for next year) - useful for tutorials and things where pages are updated and we want to go to the newer version
- resourcethumb - allows you to give a thumbnail that is a page resource/ this is resized (based on videosize)

## Shortcodes

The theme provides many shortcodes. Each is documented by a doc-comment header
at the top of its source in `layouts/_shortcodes/`, and
**[`docs/shortcodes.md`](docs/shortcodes.md) is the generated reference**
(index + per-shortcode usage/params). Regenerate it after editing any header:

~~~sh
conda run -n p314 python tools/shortcode-docs.py
~~~

Related deep-dives: `link` → [`docs/link-shortcode.md`](docs/link-shortcode.md);
the course-data shortcodes (`assign-*`, `reading`, `mod*`, `page`) →
[`docs/data-contracts.md`](docs/data-contracts.md). To see which shortcodes each
in-workspace site actually uses, see `NOTES-usage.md`
(`tools/usage-matrix.py`). Deprecation policy and the deprecated-usage checker:
[`docs/deprecation.md`](docs/deprecation.md).

## Math

`math` (inline) and `displaymath` (numbered display equations, with `eqref`
for cross-references) render math via Hugo's native `transform.ToMath`
(KaTeX) at **build time** — there is no client-side JS, CSS, fonts, or CDN.
The output is MathML, which every current browser lays out natively.

The one wrinkle: Chromium ignores the `mathvariant="bold"` attribute KaTeX
emits for `\mathbf{…}`/`\boldsymbol{…}`, so bold math would otherwise render
at normal weight there (Firefox honors the attribute and is unaffected). The
theme fixes this at build time by rewriting those characters to the actual
Unicode Mathematical-Alphanumeric bold glyphs (𝐀, 𝐱, 𝛉…) instead of relying on
the attribute — real bold characters render bold in every browser, no CSS
needed. See `layouts/_partials/math/variant-fix.html` (the rewrite) and
`docs/math-bold-research/README.md` (the investigation, evidence, and
validation results) for the full story.

## Full Width Mode

The site supports a "Full Width Mode" which displays only the main content area, hiding the header, sidebar, and footer. This is useful for embedding pages or taking screenshots where only the content is desired.

### Usage

To enable full width mode, append `?fullwidth` to the URL of any page.

Example: `http://localhost:1313/some-page/?fullwidth`

### Design and Implementation

The feature is implemented entirely on the client-side using JavaScript and CSS, avoiding the need for separate Hugo layouts or complex build configurations.

1.  **Structure Changes**: In `themes/559Theme/layouts/baseof.html`, the header, sidebar, and footer partials were wrapped in `<div>` elements with classes `header-wrapper`, `sidebar-wrapper`, and `footer-wrapper`. This allows them to be easily targeted by CSS.
2.  **CSS**: A `fullwidth-mode` class is defined for the `<body>` element. When this class is present:
    *   `.header-wrapper`, `.sidebar-wrapper`, and `.footer-wrapper` are set to `display: none !important`.
    *   The main content containers (`.container`, `.wrapper`, `.primary`) are forced to `width: 100%` and `max-width: none`.
3.  **JavaScript**: A small script at the end of `baseof.html` checks `window.location.search` for the `fullwidth` parameter. If found, it adds the `fullwidth-mode` class to the `document.body`.
4.  **Style Adjustments**: `themes/559Theme/assets/css/_style.scss` was updated to ensure the new `.sidebar-wrapper` behaves correctly within the flexbox layout (inheriting the order and size properties of the original sidebar).


## Using Links

The **link** shortcode makes a link to a page in the site, looked up by its
logical path, and gets its title for free. It takes **named parameters**
rather than ambiguous positional ones:

~~~text
{{< link "some/page" >}}                          one bare positional arg = the page
{{< link page="some/page" >}}                     named form (page is required)
{{< link page="some/page" anchor="Section" >}}    link to a heading on that page
{{< link page="some/page" text="click me" >}}     custom link text
~~~

If you want to give an arbitrary page title rather than looking it up, it's
simpler to just use regular markdown link notation instead.

Full details, parameter list, and the migration story from the old
two-positional-argument `link`/`lnk` shortcodes are in
[`docs/link-shortcode.md`](docs/link-shortcode.md) (and
`tools/migrate-links.py` if you're migrating a site's content).

One thing to still beware of: if a tag or category has the same name as a page, there can be the potential for name ambiguities.

## Style presets

Pick a look with `params.style.preset` in your site's `hugo.toml`:

~~~toml
[params.style]
preset = "uw-serif"      # or "mainroad-sans"
~~~

- **uw-serif** — the current default look: Georgia body text, Poppins
  small-caps UW-red headings, UW-red menu.
- **mainroad-sans** — the older Roadster/MainRoad-derived look (was
  `themestyle = "old"`).

The old `themestyle = "old"|"new"` config still works via a deprecation
warning (`old` → `mainroad-sans`, `new` → `uw-serif`); rename it when
convenient.

A handful of individual tokens can be overridden per-site without forking a
preset, via `params.style.vars` in `hugo.toml`:

~~~toml
[params.style.vars]
highlightColor = "#e22d30"   # hover/accent color
uwred = "#c5050c"             # base UW dark red
fontSans = "'Poppins', sans-serif"
fontBody = "'Georgia', serif"   # fontMono is a deprecated alias for this
bodyFontSize = "1.1rem"
~~~

(`linkColor`, `dimColor`, and `widgetBackground` are also settable, as
top-level `params.*` rather than `params.style.vars.*` — see
`assets/css/main.scss`.)

Everything else (container width, code block colors, pagination button
colors, sidebar link underlines, and so on) lives as a `!default` SASS
variable in the two preset files themselves —
[`assets/css/presets/_uw-serif.scss`](assets/css/presets/_uw-serif.scss) and
[`assets/css/presets/_mainroad-sans.scss`](assets/css/presets/_mainroad-sans.scss).
Each variable has a doc comment; to change one of these for every site, edit
it there (keep both preset files defining the same variable names, in sync);
to change it for just one site's build, that variable would need to be added
to the `params.style.vars` wiring in `main.scss` first.

## Known bugs / missing features

- it might be better to make this separate / different from my home page, since they have different uses/needs
- pagination is set per page, but top_paginate is global
- paginator could use better icons
- menu active tabs seems to not completely work
- base URLs are still required for the search to work

## startup process

For adding the theme to a new site, or bumping an existing site's theme
version, follow [`docs/upgrading.md`](docs/upgrading.md) — it's the
maintained, step-by-step guide (first-time setup section, plus a routine-bump
checklist and changelog for existing sites). The short version for a brand
new site:

- hugo new site
- git init
- `git submodule add https://github.com/CS559/559Theme themes/559Theme`
- git submodule init
- git submodule update
- create a `hugo.toml` file (`config.toml` was the old way in Hugo)
- create a `content/widgetlinks.md` - with `headless: true` - if you're using the `links`/`blogroll` sidebar widget

These GIT incantations help keep the subrepos on track if you care about that:

- git submodule foreach --recursive git checkout master

### things for the hugo.toml file

Minimum config to make the theme work (see `docs/upgrading.md` for the full
first-time-setup listing, including sidebar widget selection):

~~~toml
theme = ["559Theme"]          # or ["your-overlay","559Theme"] for a course-site overlay

[security]
  allowContent = ["^text/markdown$", "^text/html$"]   # theme ships .html content pages (e.g. search)

[outputs]
home = ["HTML", "RSS", "JSON"]   # JSON is the search index, needed for the search widget

[markup.goldmark.renderer]
unsafe = true                     # theme partials/shortcodes emit raw HTML

[params.style]
preset = "uw-serif"               # or "mainroad-sans" - see "Style presets" above
~~~

You do need to either set `baseURL` or use `hugo --baseURL` even if everything uses relative paths, as the `index.json` (used for text search) does not.

There's also a weird thing with baseURL for GitHub pages - so you probably need
to set the Params.errorBase to the "real" baseURL (especially when baseURL is "")

## for the talks and videos

In general, assets get linked automatically if they are page resources.

However: you might want to put assets in an external directory. Use the `extpdfs` (or similar) page properties to give the link.

- if the link doesn't have "http" in it, it is assumed that it is in the assetStore link (directory) from Site.Params

## Acknowledgement

This theme originated as an overlay on MainRoad, then Roadster, using pieces of each as a base to hack on. As of the 2026 unification, 559Theme is self-contained and no longer depends on either at build time, but it still carries code and structure descended from them.

To comply with the MainRoad/Roadster license, this theme is also released GPL (see `LICENSE`).
