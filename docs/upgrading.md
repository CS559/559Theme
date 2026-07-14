# Upgrading a site to a new 559Theme version

This is the guide for a **site maintainer** (human or agent) who already has
`559Theme` as a submodule and wants to move it forward, or is adding it to a
new site for the first time. If you're working *on the theme itself*, see
`THEME-PLAN.md`'s Execution log instead — that's the internal history of how
the theme got to its current state, not a per-site upgrade checklist.

**Read this whole guide once, start to finish, before running anything.**
The steps below are ordered and reference each other (e.g. step 2 needs tools
that live in the version you're about to check out) — working through them
without knowing what's coming is how a step gets done out of order or skipped.

**This is a verification exercise, not a fix-it exercise.** If a diff or a
build error doesn't match anything in the changelog below, stop and report it
rather than patching around it — especially if you're working in a fresh
session with no other context on this project. Don't push or deploy anything
(this site, or changes to 559Theme itself) without explicit sign-off.

## Routine bump (already using the theme)

1. **Pre-flight: check what you're starting from, and that the site is
   healthy, before touching anything.** Skipping this means every anomaly
   you find later has multiple possible causes — pre-existing, a Hugo-version
   mismatch, or bump-introduced — with no way to tell them apart short of
   redoing this check retroactively.

   - **Check your current pin against the theme's tags:**
     `git -C themes/559Theme log -1 --oneline` vs.
     `git -C themes/559Theme tag -l`. If you're at or before
     `pre-unification`, everything in the changelog below applies; if you're
     already past it, only the entries after your current point do. If
     you're not just "at or before" but many commits before it, expect the
     golden-master diff in step 4 to be unusually large — see the note
     there before treating diff volume alone as a red flag.
   - **Build clean.** `hugo --baseURL /` (or `hugo server`) should complete
     with no `ERROR` and no `WARN` lines. Fix anything you find now (or
     consciously decide to ignore it, and note why) — don't carry a
     pre-existing warning into the bump where it'll look like something the
     new theme caused.
   - **Build with your current, locally installed Hugo** (`hugo version`),
     not just whatever version this site's CI pins (check
     `.github/workflows/*.yml` if present). A Hugo-version mismatch produces
     its own diffs, independent of the theme — match versions before
     comparing. **Check the size of that gap first**: if CI's pin and your
     local Hugo are many minor versions apart (e.g. CI stuck on `0.147.3`
     while local Hugo is `0.164.0+`), expect *more* than the fixes below —
     every site that has hit a large gap has surfaced additional
     Hugo-level breakage that predates the theme entirely and has nothing
     to do with it. If you're crossing onto **Hugo 0.164.0** (or anything
     since, or anything that crosses the same deprecation boundaries) for
     the first time, all of the following fixes have already been needed on
     other 559Theme sites:
     - **Content-security policy (Hugo v0.162+, CVE-2026-50133 fix).** Hugo
       tightened its default content-type policy and now blocks the theme's
       `text/html` content pages (`content/search.html`, or the legacy
       `content/lunr-search.html`) unless explicitly allowed:

       ```toml
       [security]
         allowContent = ["^text/markdown$", "^text/html$"]
       ```

     - **`languageCode` deprecated (Hugo v0.158+).** Rename it to `locale`
       in your site config:

       ```diff
       -languageCode = "en-us"
       +locale = "en-us"
       ```

       (The theme itself already moved from `.Site.LanguageCode` to
       `.Site.Language.Locale` internally — this site-config rename is the
       only action needed on your end.)
     - **`_build` front matter key removed, not just deprecated (Hugo
       v0.145+).** Any page using the underscore-prefixed key fails with a
       hard `ERROR`, not a warning. Course sites commonly use this on
       per-week/per-module index pages to hide them from section lists
       (e.g. `content/this-weeks/*.md` with `list: never`):

       ```diff
       -_build:
       +build:
           render: false
           list: never
       ```

       This is a general Hugo change, unrelated to 559Theme itself, but
       common enough on course sites to check for up front:
       `grep -rl '^_build:$' content/`.
     - **Markdown-format shortcode templates now enforce their call
       delimiter.** A shortcode whose *template file* is `.md` (e.g.
       `layouts/shortcodes/dimbox.md`) must be invoked with `{{% %}}`, not
       `{{< >}}` — older Hugo tolerated the mismatch silently; newer Hugo
       hard-errors (`no compatible template found for shortcode "x" in
       [...]; note that to use plain text template shortcodes in HTML you
       need to use the shortcode {{% delimiter`). This can surface on *any*
       shortcode call in the site's content, not just ones the theme
       changed — it's exposing a pre-existing mismatch, not introducing
       one. If you hit it, check how every other call to the same
       shortcode in the site is delimited
       (`grep -rn '{{[<%]\s*shortcodename' content/`) — if the rest of the
       site already uses `{{% %}}`, the offending call is almost certainly
       a stray typo, not a real incompatibility, and the fix is to match
       the delimiter, not to touch the template.
     - **If your local Hugo surfaces anything else** — any build error or
       warning beyond these known ones — **stop and confirm with
       whoever's directing the bump before working around it.** Hugo-version
       drift is open-ended in a way the theme changelog below isn't; don't
       silently patch around unfamiliar breakage. (This list only grows
       because someone hit an "anything else" case, resolved it, and added
       it here — if you resolve a new one, do the same.)
   - **Bring CI's Hugo version in line with what you just verified.** Check
     your CI config (e.g. `.github/workflows/*.yml`) for a pinned
     `HUGO_VERSION` or Hugo-install step, and update it to match your local
     `hugo version` — CI should build with the same Hugo you just tested
     against, not a stale pin.
   - **Pre-emptively check for the other common known issue: `lnk` shortcode
     usage** (course sites only — see the changelog's "`link`/`lnk` unified"
     entry). This one's a hard build error with no deprecated alias, so
     finding it now means it's an expected chore in step 4 below, not a
     surprise failure:

     ```sh
     grep -rn '{{<\s*lnk\b\|{{%\s*lnk\b' content/
     ```

   - **Rebuild 2-3 times with no changes at all and diff the output.** Any
     difference between two builds of the *identical* commit is site/Hugo
     non-determinism, not something the bump will introduce or fix. Hugo's
     auto-generated taxonomy term titles are a known source of this: if your
     content spells the same tag/category with inconsistent casing across
     pages (`"javascript"` in one file, `"JavaScript"` in another), Hugo's
     map-iteration tie-break picks a winner **at random per build**. Fix
     content-casing inconsistencies now so the golden-master diff in step 4
     isn't spent chasing a ghost.

2. **Update the submodule, tracking `origin/master`** rather than pinning to
   a specific historical tag — sites should stay current, not frozen at a
   past release. The tradeoff: master can carry commits beyond the newest
   changelog entry below, so if you hit a diff or build error nothing here
   explains, don't assume it's already covered — stop and report it (per the
   top of this guide), and add an entry to the changelog once it's resolved
   so the next site doesn't hit the same surprise.

   Before you move the pointer, get set up: `tools/baseline.sh` /
   `tools/compare.sh` — the scripts you'll use below to snapshot your site's
   rendered output and diff before vs. after — ship inside the *new* theme
   version's own `tools/` directory. You need a "before" snapshot of your
   site taken **before** the submodule pointer moves, so do these in order,
   all within this one step:

   ```sh
   cd themes/559Theme
   git checkout -q -- . && git clean -fdq   # discard any local test edits
   git fetch origin --tags
   ```

   If your site doesn't already have local copies of the tools, pull them out
   of the target version now, without checking it out yet (so your working
   tree is still on the old commit for the snapshot below):

   ```sh
   git show origin/master:tools/baseline.sh > ../../tools/baseline.sh
   git show origin/master:tools/compare.sh  > ../../tools/compare.sh
   chmod +x ../../tools/baseline.sh ../../tools/compare.sh
   cd ../..
   ```

   **Now capture the baseline** — you're still on the old commit:

   ```sh
   ./tools/baseline.sh pre-bump
   ```

   **Only now move the pointer:**

   ```sh
   cd themes/559Theme
   git checkout origin/master
   cd ../..
   ```

3. **If you're crossing `pre-unification`** (i.e. your site had a separate
   fallback theme before this bump), remove it now — see "Legacy fallback
   theme cleanup" in the changelog below for the exact commands (`roadster`
   and/or `mainroad`). Skip this step if you're already past that point.

4. **Golden-master verify: build, then iterate.** Two phases, both *after*
   step 2's checkout — the baseline itself was already captured in step 2,
   before the pointer moved.

   **a. Get it to build.** After step 2's checkout (and step 3's fallback-theme
   cleanup, if applicable), rebuild:

   ```sh
   hugo --baseURL /
   ```

   The build may **fail outright**, not just warn — some changelog entries
   remove a feature with no deprecated alias (e.g. the `lnk` shortcode you
   already checked for in step 1). Check the changelog below for a migration
   tool (e.g. `tools/migrate-links.py`) before treating a build error as a
   bug. Keep fixing and rebuilding until `hugo --baseURL /` completes clean.

   **b. Iterate until it matches well enough.** Rebuild and diff against your
   baseline:

   ```sh
   ./tools/compare.sh pre-bump
   ```

   `compare.sh` excludes `*.css`/`*.js` from the diff (fingerprinted filenames
   legitimately change) and reports `HTML: IDENTICAL` when nothing else moved.
   **Any other HTML diff is a stop-and-investigate signal** — check the
   changelog below for what the new version intentionally changed before
   assuming it's a regression. A few kinds of diff are *not* bump-related and
   can be set aside once you recognize them:

   - `lastmod`/`pubDate` changes on any file you've edited as part of a
     migration — expected, tied to `enableGitInfo`.
   - Non-determinism you already characterized in step 1 (Pre-flight). If you
     skipped step 1 and see something like this now, rebuild the *old* commit
     twice with no changes to confirm it's pre-existing before blaming the
     new theme version.
   - If you're crossing `pre-unification` with a fallback theme removed (step
     3): a now-redundant `v2-styles.css` `<link>` tag disappearing from
     `<head>` — its rules are compiled into the theme's own CSS bundle
     instead. **This "just the one tag" expectation holds for an isolated
     roadster removal on a site that's otherwise current.** If your pin was
     many commits/versions behind (per step 1's tag check), you're crossing
     every intervening internal change at once, and the diff will be much
     bigger than any single changelog entry implies — new wrapper `<div>`s
     around header/sidebar/footer (they exist to support a `fullwidth` mode
     query-string toggle), CSS consolidated into one `main.css`, a
     preset-driven Google Fonts subset (fewer families than before), footer
     copyright wording, and similar. None of this needs site action, so
     it's not itemized as a changelog entry — the full history is in
     `THEME-PLAN.md`'s Execution log, not here. Treat this as expected, not
     a regression, *provided* every diff is confined to `<head>` and
     header/footer/sidebar chrome. Confirm by diffing a content-heavy page
     (not a list/index page) and checking that the article body itself —
     the actual prose between the header and footer — is byte-identical;
     that's the real regression check, not the raw diff-line count.

   Loop between (a) and (b) — fix, rebuild, re-compare — until every
   remaining diff is either `HTML: IDENTICAL` or explained by the changelog
   below.

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
   To check for the promoted course shortcodes specifically:

   ```sh
   find layouts/shortcodes -maxdepth 1 \
     \( -name assign-link.html -o -name assign-linkonly.html -o -name reading.html \
        -o -name moddesc.html -o -name modlo.html -o -name modname.html \
        -o -name page.html -o -name snippet.html \)
   ```

6. **Check for deprecated features you're still using**, both ways — do this
   *before* making any config changes, so you actually watch the deprecation
   warning fire and confirm the old alias currently works, rather than
   renaming things on faith from reading the changelog alone:

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
     your own config as a starting point, e.g.:

     ```sh
     grep -n "themestyle\|\"lunr\"" hugo.toml config.toml 2>/dev/null
     ```

     the `warnf` build warnings above are the authoritative signal; the grep
     just tells you what to search for.

   Once you've confirmed what's deprecated, apply the renames the changelog
   calls for (e.g. `themestyle` → `params.style.preset`, `lunr` → `search`).

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

Then set up `tools/baseline.sh`/`tools/compare.sh` (copy from
`themes/559Theme/tools/`) before making any further changes, so you have a
baseline to diff against going forward.

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

  **Known gap in the migration tool's dry-run.** It tokenizes arguments with
  Python's `shlex`, which merges a quoted string immediately followed by a
  bareword into a single token (`"page"s` parses as one token, `pages`) — so
  it reports the call as an already-fine 1-positional case and leaves it
  untouched. Hugo's own shortcode-argument parser does *not* merge them; it
  sees two positional args and hard-errors, but only *after* you've moved
  the submodule pointer and the migration script has already told you
  everything's clean. In practice this pattern is a content typo — a stray
  trailing letter glued onto a closing quote, e.g. `{{< link
  "genai-policy"s >}}` — not an intentional second argument, and the fix is
  to delete the stray character. After running `migrate-links.py`, also
  grep directly for the shape it can't see — anchored to right after
  `link`/`lnk` so it only matches a *positional* first argument, not a
  legitimate `name="value"` pair (an unanchored `[^}]*` before the quote
  false-positives on any ordinary multi-attribute named call, e.g. `page="x"
  text="y"`, which is the common case once you've applied the renames
  above):

  ```sh
  grep -rnE '\{\{[<%]\s*(link|lnk)\b\s+"[^"]*"[A-Za-z0-9_]' content/ assets/snippets/
  ```

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
- Automated non-determinism detection (step 1 asks you to rebuild a few times
  by hand and eyeball the diff) — could be folded into `compare.sh` itself
  (build twice before touching the submodule, fail loudly if they disagree).
