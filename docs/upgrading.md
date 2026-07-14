# Upgrading a site to a new 559Theme version

This is the guide for a **site maintainer** (human or agent) who already has
`559Theme` as a submodule and wants to move it forward, or is adding it to a
new site for the first time. If you're working *on the theme itself*, see
`THEME-PLAN.md`'s Execution log instead — that's the internal history of how
the theme got to its current state, not a per-site upgrade checklist.

**This is a verification exercise, not a fix-it exercise.** If a diff or a
build error doesn't match anything in the changelog below, stop and report it
rather than patching around it — especially if you're working in a fresh
session with no other context on this project. Don't push or deploy anything
(this site, or changes to 559Theme itself) without explicit sign-off.

## Routine bump (already using the theme)

1. **Check what you're starting from**, so you can tell "expected from this
   changelog" apart from "pre-existing and unrelated":
   - Current submodule commit: `git -C themes/559Theme log -1 --oneline`.
     Compare against the theme repo's tags (`git -C themes/559Theme tag -l`)
     — if you're at or before `pre-unification`, everything in the changelog
     below applies; if you're already past it, only the entries after your
     current point do.
   - Local Hugo version vs. what this site's CI pins (check
     `.github/workflows/hugo.yml` if present). A Hugo version mismatch
     produces its own diffs, independent of the theme — don't conflate the
     two. Match versions before comparing.

2. **Update the submodule**, pinned to a specific tag (not a floating branch
   tip) for a reproducible comparison:

   ```sh
   cd themes/559Theme
   git checkout -q -- . && git clean -fdq   # discard any local test edits
   git fetch origin --tags
   git checkout v1-unification              # or a later tag; `git tag -l` to see what exists
   cd ../..
   ```

3. **If you're crossing `pre-unification`** (i.e. your site had a separate
   fallback theme before this bump), remove it now — see "Legacy fallback
   theme cleanup" in the changelog below for the exact commands (`roadster`
   and/or `mainroad`). Skip this step if you're already past that point.

4. **Golden-master verify before committing anything.** If your site doesn't
   already have `tools/baseline.sh` / `tools/compare.sh`, copy them from
   another 559Theme site (e.g. `VisSnacks/tools/`) — they're generic, not
   site-specific.

   ```sh
   ./tools/baseline.sh pre-bump    # BEFORE moving the submodule pointer, on the old commit
   # ... do the submodule update (and fallback-theme cleanup, if applicable) above ...
   ./tools/compare.sh pre-bump     # rebuild and diff
   ```

   `compare.sh` excludes `*.css`/`*.js` from the diff (fingerprinted filenames
   legitimately change) and reports `HTML: IDENTICAL` when nothing else moved.
   **Any other HTML diff is a stop-and-investigate signal** — check the
   changelog below for what the new version intentionally changed before
   assuming it's a regression. (One legitimate, expected diff if you're
   crossing `pre-unification` with a fallback theme removed: a now-redundant
   `v2-styles.css` `<link>` tag disappears from `<head>` — its rules are
   compiled into the theme's own CSS bundle instead.)

5. **Check for local overrides that would silently swallow a core update.**
   Several changes in this project *promoted* something from a per-site
   override into the core theme (course shortcodes, the search widget). If
   your site (or an overlay theme in its `theme = [...]` list) has its own
   local copy of something the changelog says is now in core — e.g. a local
   `layouts/_shortcodes/`, `layouts/shortcodes/`, or `layouts/_partials/widgets/`
   file with the same name — **your local copy still wins** (Hugo resolves
   the site's own `layouts/` before any theme's) and you won't get the core
   behavior at all, deprecation warnings included. Delete the local copy
   (after checking for behavior differences) so the core version resolves.

6. **Check for deprecated features you're still using**, both ways:
   - Build with `hugo server` or `hugo --baseURL /` and read the output for
     `WARN 559Theme: ... is deprecated ...` lines — these fire only for
     features your site actually calls, so a clean build with no warnings
     means nothing here needs attention yet.
   - For a fuller check (not just what one build's shortcode calls happen to
     hit), run the theme's checker against your site:
     ```sh
     conda run -n p314 python themes/559Theme/tools/check-deprecated.py .
     ```
     This only covers **shortcodes** (see `docs/deprecation.md`) — it does
     not know about deprecated `hugo.toml` params or widget names (like
     `themestyle`/`lunr`, retired in the changelog below). For those, grep
     your own config; the theme's `warnf` build warnings are the authoritative
     signal.

7. **Commit the bump** (submodule pointer + anything the changelog told you
   to change), with a message noting the version/tag and what you verified.

## First-time setup (adding this theme to a new site)

```sh
git submodule add https://github.com/CS559/559Theme themes/559Theme
```

Minimum `hugo.toml` to make the theme work:

```toml
theme = ["559Theme"]          # or ["your-overlay","559Theme"] for a course-site overlay

[security]
  allowContent = ["^text/markdown$", "^text/html$"]   # theme ships .html content pages (e.g. search)

[outputs]
home = ["HTML", "RSS", "JSON"]   # JSON is the search index (layouts/index.json)

[markup.goldmark.renderer]
unsafe = true                     # theme partials/shortcodes emit raw HTML

[params.style]
preset = "uw-serif"               # or "mainroad-sans" — see docs/search.md's sibling
                                   # doc-comments in assets/css/presets/*.scss for the two options

[params.sidebar]
widgets = ["search", "important", "links", "recents", "categories", "taglist"]
```

Then set up `tools/baseline.sh`/`tools/compare.sh` (copy from an existing
site) before making any further changes, so you have a baseline to diff
against going forward.

## Changelog: notable/breaking changes by version

Full rationale and evidence for all of these lives in `THEME-PLAN.md`'s
Execution log (theme repo, versioned) — this section is the short,
site-facing version: what you need to *do* when crossing each point, not why.

- **Tag `pre-unification`** — the last commit before the unification project
  (`63f35e4`). If a site is still here, it needs a separate `roadster` (or,
  on very old pins, `mainroad`) theme in its `theme = [...]` list, uses
  `themestyle` (no presets), has its own local copies of course shortcodes
  (`assign-link`, `reading`, etc.), and its own `lunr`-based search page.
  None of the rest of this changelog applies until you've moved past this
  point.
- **Roadster absorbed into 559Theme — legacy fallback theme cleanup.** Drop
  `roadster` (or `mainroad`, on older pins) from `theme = [...]` entirely —
  every partial/template/static asset it provided now ships from 559Theme
  directly. Do the config change first, verify with `compare.sh`, *then*
  remove the actual submodule:

  ```sh
  # 1. config: theme = ["559Theme","roadster"] -> theme = ["559Theme"]
  #    (or drop "mainroad" if that's what your site still has)

  # 2. verify with tools/compare.sh — expect only the v2-styles.css <link>
  #    tag to disappear from <head> (see step 4 above), nothing else

  # 3. then remove the submodule for real:
  git submodule deinit -f themes/roadster   # or themes/mainroad
  git rm -f themes/roadster                 # or themes/mainroad
  rm -rf .git/modules/themes/roadster       # or .../mainroad
  ```

  A site can only be tracking one of `roadster`/`mainroad` at a time (the
  project switched from Mainroad to Roadster in 2025) — check `.gitmodules`
  to see which, if either, you have.
- **Style presets replace `themestyle`.** Rename `themestyle = "old"|"new"`
  to `params.style.preset = "mainroad-sans"|"uw-serif"` (`old`→`mainroad-sans`,
  `new`→`uw-serif`). The old param still works via a deprecation `warnf` — not
  urgent, but do it before the alias is ever retired.
- **Course shortcodes promoted into the core theme** (`assign-link`,
  `assign-linkonly`, `reading`, `moddesc`, `modlo`, `modname`, `page`,
  `snippet`). If your site or an overlay theme has local copies of these,
  delete them so the core versions resolve instead (see step 5 above) — check
  for behavior differences first (see `docs/data-contracts.md` for the
  current data-source rules: whichever of `assignments.yaml`/`assigns.yaml`
  is present is used; it's a **build error** if both exist, not a warning).
- **`link`/`lnk` unified** (course sites only). `lnk` is **gone** — no
  deprecated alias. Two bare positional args are now a build error; use named
  params or the migration tool: `tools/migrate-links.py`.
- **Lunr search replaced by MiniSearch** (`docs/search.md`). Rename the
  widget `lunr` → `search` in `params.sidebar.widgets` (or `params.widgets`).
  The old name still works via a deprecation `warnf`. No more CDN dependency
  (`unpkg.com`) — if your site allowlisted that domain anywhere (CSP, etc.),
  it can be removed.
- **`menu.js` trimmed to a toggle-only script.** No site action needed unless
  you had custom JS depending on the old submenu handler or the dark-theme
  toggle — both were dead code (no site used them) and are gone.
- **`hint.css`/tooltip rewritten.** No site action needed; the `tooltip`
  shortcode's public behavior is unchanged, just lighter (a `title=` fallback
  attribute pattern isn't required).

## Known non-fixed issues (not new, not caused by upgrading)

- **MathML bold does not render bold in Chromium** (`\mathbf`/`\boldsymbol`
  show at normal weight; Firefox is fine). This is a Chromium MathML-Core
  limitation, not a theme bug, and it's true on *both* sides of any version
  comparison — the theme's math shortcodes render via Hugo's native
  `transform.ToMath` on every version covered by this guide, so upgrading
  neither introduces nor fixes it. If your site has math-heavy content,
  expect it, and see `docs/math-bold-research/` for the full investigation
  and the planned (not yet implemented) fix.

## What this guide doesn't cover yet

- A full semantic-version tagging scheme — right now there's `pre-unification`
  and a tag per notable rollout (see the theme repo's tag list), not a formal
  version number per commit. If that becomes painful, consider tagging more
  granularly going forward.
- Automated checking of deprecated **params**/**widget names** (only
  shortcodes are covered by `tools/check-deprecated.py` today) — extending it
  would need a second scan mode over `hugo.toml` files.
