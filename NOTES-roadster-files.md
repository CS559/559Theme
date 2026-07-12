# Roadster file usage inventory (Phase 0 task 4)

Recorded 2026-07-12. Empirically verified per site by temporarily dropping `roadster`
from each site's `theme = [...]` list, rebuilding, and tracing every resulting error
back to its source, then restoring. Roadster is pinned at the same commit (`cf57f17`)
for all four sites, so its file inventory is identical everywhere — what differs is
which files each site's content/config actually reaches.

**Read this before trusting the "known list" in the plan's Phase 0 task 4 description**
(`_partials/{header,sidebar,mathjax,post_tags}.html`, `home.html`, `static/js/menu.js`,
`assets/css/v2-styles.css`). That list is real but incomplete — see "Gaps in the plan's
hint list" below. Phase 1 task 1 should copy more than that list names.

## Three methodology gotchas, worth internalizing before Phase 1/2/5

1. **Silent drops, not just hard errors.** Hugo aborts the whole build on the first
   *template execution* error, but some missing templates just produce a WARN and
   quietly drop pages — no ERROR at all. Confirmed for `single.html`, `home.html`,
   `404.html`, and `authors/term.html` (where applicable): removing roadster without
   also checking page counts / diffing `public/` file trees would silently delete
   real pages and nobody would see an error to tell them why. **Always diff full file
   trees (`diff -r` / `find | sort`), not just build exit status, when validating a
   roadster removal.**
2. **Static passthrough happens regardless of whether anything links to a file.**
   Hugo copies every theme's `static/` tree into `public/` (subject to shadowing) —
   it doesn't matter whether any template actually emits a `<link>`/`<img>` for that
   path. `static/apple-touch-icon.png`, `static/img/avatar.png`, and
   `static/img/placeholder.png` are a real example: no template in any of the four
   sites references them, but they are currently physically present in every site's
   deployed `public/`. Dropping roadster **will** remove them from `public/` — that's
   a real, correct diff, but `tools/compare.sh`'s exclude list (`*.css`, `*.js`) won't
   hide it, so expect (and accept) a diff on these 3 files specifically during Phase 1
   unless they're deliberately carried forward or the removal is called out as
   intentional.
3. **Stubbing a "confirmed needed" file with empty content can produce false
   positives further down the chain.** While isolating 559-sp26's chain, stubbing
   `header.html` (empty) made `svg/crest.svg` appear to vanish from the build — not
   because `crest.svg` is a roadster file (it isn't; roadster doesn't even ship a
   `crest.svg`), but because roadster's real `header.html` calls 559Theme's own
   `logo.html`, which processes `crest.svg`, and the empty stub broke that call
   chain. **When iteratively stubbing to walk past errors, re-verify every
   surprising result against the actual (non-stubbed) source** before concluding a
   file belongs to roadster.

(A fourth, non-technical lesson: three of the four automated audits used a live
stub-and-rebuild loop and left the site repos in a modified/dirty state — including
one that edited files inside the `roadster` submodule checkout itself and two that
left orphan background `hugo` processes running, which kept re-dirtying the repos
after an initial cleanup. All four site repos were manually restored and verified
clean/building before this note was written. If re-running this kind of audit,
do it synchronously in the foreground, stub/restore one file at a time, and confirm
`git status --short` is empty (including inside submodules) before considering it
done.)

## Master table

Legend: **LIVE** = build breaks or output changes without it, not shadowed.
**shadowed** = an identical-path file in a higher-priority theme/site layout wins;
roadster's copy is provably dead. **passthrough** = physically copied to `public/`
but not referenced by any template (see gotcha #2). **dead** = neither live nor
shadowed nor passthrough-relevant; safe to drop. **n/a** = not reachable given that
site's config (e.g. a widget name not in its `widgets` list).

| File / group | VisSnacks | 559-sp26 | 765-25 | gleicher.github.io |
|---|---|---|---|---|
| `assets/css/v2-styles.css` | LIVE | LIVE | LIVE | LIVE |
| `assets/css/style.css` | dead | dead | dead | dead |
| `assets/images/avatar.png` | dead (no authors content) | LIVE-ish (authorbox.html is live; avatar path may still be internally guarded — not fully isolated) | dead (no authors content) | dead (no authors content) |
| `static/js/menu.js` | LIVE | LIVE | LIVE | LIVE |
| `static/favicon.ico` | shadowed (559Theme's own, md5-verified) | shadowed | shadowed (md5-verified) | shadowed (md5-verified) |
| `static/apple-touch-icon.png` | passthrough (unreferenced but deployed) | passthrough (confirmed via file-tree diff) | passthrough | passthrough |
| `static/img/avatar.png` | passthrough | passthrough (confirmed via file-tree diff) | passthrough | passthrough |
| `static/img/placeholder.png` | passthrough | passthrough (confirmed via file-tree diff) | passthrough | passthrough |
| `layouts/404.html` | LIVE (silent drop) | LIVE (confirmed via file-tree diff) | LIVE (marker test) | LIVE (circumstantial — not fully isolated) |
| `layouts/home.html` | dead — shadowed by site's own `layouts/index.html` (which itself still needs roadster's `svg/files.svg`) | LIVE (no competing home template anywhere) | LIVE (marker test) | LIVE-unverified (no 559Theme home.html exists; not diff-confirmed) |
| `layouts/baseof.html` | shadowed (559Theme `_default/baseof.html`) | shadowed | shadowed | shadowed |
| `layouts/list.html` | shadowed (559Theme `_default/list.html`) | shadowed | shadowed | shadowed |
| `layouts/summary.html` | shadowed (559Theme `_default/summary.html`) | shadowed (not individually re-verified, high confidence) | shadowed | shadowed |
| `layouts/single.html` | LIVE (silent drop; no 559Theme/local equivalent) | **shadowed by this site's own local `layouts/single.html`** | LIVE (silent drop) | LIVE (silent drop, implied — not separately marker-tested) |
| `layouts/authors/term.html` | n/a (no authors taxonomy) | n/a | n/a | n/a — but removing roadster still drops 29 pages via a *different* silent WARN; not fully isolated which template that maps to |
| `_partials/header.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/sidebar.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/mathjax.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/post_toc.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/post_meta.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/footer_links.html` | LIVE (called from 559Theme's own footer.html) | LIVE (same) | LIVE (same) | LIVE (same) |
| `_partials/post_tags.html` | LIVE (renders on tagged pages) | LIVE (SRC-confirmed, called from local single.html) | LIVE (2 tagged pages) | **dead — never called at all** (this site's content templates don't route through a path that calls it) |
| `_partials/post_thumbnail.html` | LIVE | LIVE (hard-error confirmed) | LIVE (unconditional in single.html) | **dead — never called at all** |
| `_partials/authorbox.html` | LIVE (no-op body currently) | LIVE | LIVE (no-op body) | LIVE (no-op body) |
| `_partials/pager.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/comments.html` | LIVE | LIVE | LIVE | LIVE |
| `_partials/head.html` | shadowed | shadowed | shadowed | shadowed |
| `_partials/head/stylesheet.html` | shadowed (559Theme's is what pulls in v2-styles.css) | shadowed (same) | shadowed (same) | shadowed (same) |
| `_partials/head/gfonts.html` | dead (559Theme's head.html doesn't call it) | dead | dead | dead |
| `_partials/head/seo.html` | dead | dead | dead | dead |
| `_partials/logo.html` | shadowed | shadowed | shadowed | shadowed |
| `_partials/menu.html` | shadowed | shadowed | shadowed | shadowed |
| `_partials/footer.html` | shadowed | shadowed | shadowed | shadowed |
| `_partials/pagination.html` | shadowed | shadowed | shadowed | shadowed |
| `_partials/post_meta/author.html` | shadowed (and unused per config) | shadowed (and "author" not in configured post_meta list) | shadowed | shadowed |
| `_partials/post_meta/date.html` | shadowed | shadowed (but pulls in roadster's `svg/time.svg`, see below) | shadowed | shadowed |
| `_partials/post_meta/categories.html` | LIVE (config includes "categories"; no 559Theme equivalent) | LIVE (same) | LIVE (same) | dead per config check? **contradiction — see note** |
| `_partials/post_meta/translations.html` | dead (not in post_meta list) | dead | dead | dead |
| `_partials/widgets/categories.html` | LIVE (in widgets list) | LIVE (in widgets list) | LIVE (in widgets list) | dead (not in widgets list — `["lunr","sectionlinks","links","taglist"]`) |
| `_partials/widgets/taglist.html` | LIVE (renders on 43 pages) | LIVE (in widgets list) | LIVE (in widgets list) | LIVE (in widgets list, but currently renders nothing — `Site.Taxonomies.tags` empty) |
| `_partials/widgets/ddg-search.html` | n/a | n/a | n/a | n/a |
| `_partials/widgets/languages.html` | n/a | n/a | n/a | n/a |
| `_partials/widgets/recent.html` | n/a (config says "recents", singular/plural mismatch) | n/a (same) | n/a (config: no "recent"/"recents" entry checked) | n/a |
| `_partials/widgets/search.html` | n/a ("lunr" resolves to 559Theme's own widget instead) | n/a (same) | n/a | n/a (confirmed: "lunr" = `themes/559Theme/layouts/partials/widgets/lunr.html`, unrelated to roadster) |
| `_partials/widgets/sidemenu.html` | n/a | n/a | n/a | n/a |
| `_partials/widgets/social.html` | n/a | n/a | n/a | n/a |
| `_partials/svg/author.svg` | shadowed (559Theme has its own) | shadowed | shadowed | shadowed |
| `_partials/svg/tag.svg` | LIVE (rendered on tagged pages) | LIVE | LIVE | dead (post_tags.html never called on this site) |
| `_partials/svg/time.svg` | LIVE (pulled in by 559Theme's own, shadowing, `post_meta/date.html`) | LIVE (same mechanism) | LIVE (same) | LIVE (same) |
| `_partials/svg/category.svg` | LIVE where categories used | LIVE | dormant (categories.html live but no page has non-empty `categories:`) | LIVE — confirmed rendered in `public/video/*/index.html` |
| `_partials/svg/files.svg` | LIVE (site's local `home.html` still calls it) | LIVE (roadster's own home.html calls it) | dormant (site always has posts, "zero posts" branch never fires) | not checked |
| `_partials/svg/{bitbucket,bluesky,discourse,email,facebook,github,gitlab,instagram,linkedin,mastodon,telegram,x}.svg` (12 icons) | dead (only reachable via unreachable `widgets/social.html`/`authors/term.html`) | dead (same) | dead (same) | dead (same) |

**Note on the `post_meta/categories.html` row:** VisSnacks/559-sp26/765-25 all set
`post_meta` (or equivalent) to include `"categories"`, making this file live (even
if dormant on sites where no content sets a `categories:` value). gleicher.github.io's
`post_meta` param was not independently re-checked against this specific row before
the audits wrapped up — treat that cell as **unconfirmed**, not a real contradiction,
until someone greps `gleicher.github.io/config.toml`'s `post_meta` list directly.

## Gaps in the plan's Phase 0 "known list"

The plan's hint list (`_partials/{header,sidebar,mathjax,post_tags}.html`,
`home.html`, `static/js/menu.js`, `assets/css/v2-styles.css`) undercounts what Phase 1
task 1 needs to carry into 559Theme. Based on the table above, also plan for:

- `_partials/post_toc.html`, `post_meta.html`, `footer_links.html`,
  `post_thumbnail.html`, `authorbox.html`, `pager.html`, `comments.html` —
  unconditionally called from every site's single-page template chain (roadster's own
  or, on 559-sp26, the site's local override that still delegates to these).
- `layouts/404.html` — silently dropped otherwise, no error to catch it.
- `static/apple-touch-icon.png`, `static/img/avatar.png`, `static/img/placeholder.png`
  — currently deployed via static passthrough on all four sites even though unused;
  decide deliberately whether to carry them forward or drop them (dropping is
  probably right, but it should be a decision, not an accident `compare.sh` flags).
- `_partials/post_meta/categories.html`, `widgets/categories.html`,
  `widgets/taglist.html`, and `svg/{category,tag,time,files}.svg` — all config- and
  content-dependent; carry them since at least one site's config makes each of them
  live, but note two sites (gleicher.github.io for tags/thumbnail; several sites for
  the "dormant" svg rows) don't currently exercise every path — a future content
  change could make a currently-dormant path active, so don't delete these thinking
  they're unused everywhere.
- `home.html` needs a per-site decision, not a blanket copy: VisSnacks has already
  forked it into a local `layouts/index.html` (which itself still needs roadster's
  `svg/files.svg`); the other three sites use roadster's directly (or, for 559-sp26,
  effectively the same file since nothing shadows it).

Confirmed genuinely safe to drop (dead everywhere, all four sites): `assets/css/style.css`,
`_partials/head/gfonts.html`, `_partials/head/seo.html`,
`_partials/post_meta/translations.html`, `_partials/widgets/{ddg-search,languages,
recent,search,sidemenu,social}.html`, `layouts/authors/term.html` (all four sites lack
an authors taxonomy — though see the unresolved 29-page drop on gleicher.github.io,
worth a quick follow-up before deleting), and the 12 non-{author,tag,time,category,files}
SVG social icons.
