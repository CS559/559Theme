# Updating — and upgrading — a site's 559Theme

This is the guide for a **site maintainer** (human or agent) who already has
`559Theme` as a submodule and wants to move it forward, or is adding it to a
new site for the first time. If you're working *on the theme itself*, see
`THEME-PLAN.md`'s Execution log instead — that's the internal history of how
the theme got to its current state, not a per-site upgrade checklist.

## Two different operations wear the same command

`git checkout origin/master` in the submodule is one command, but it can mean
two very different things:

- **An update.** Your site is already post-unification and you're moving it
  forward a few commits. This is the overwhelmingly common case. Most such
  moves are documentation-only or a one-line string fix, and they deserve
  proportionate effort — minutes, not a session. The **Update path** below
  has three verification levels so you can pick one.
- **An upgrade.** Your site is at or before the `pre-unification` tag. This
  is **not a version bump — it is adopting a different theme.** The template
  layout, the CSS pipeline, the style system, the search implementation, the
  shortcode inventory, and the number of themes in your `theme = [...]` list
  all change at once. Budget a working session, expect to make content and
  config edits, and do it as its own commit series. The **Upgrade path**
  below covers it, and it has no light option.

Getting this distinction wrong is expensive in both directions: running the
full migration checklist on a docs-only update is wasted work, and treating
the unification crossing as a casual bump means discovering the scope of it
one build error at a time.

**Read this whole guide once, start to finish, before running anything** —
including the path you don't think you're on, so you'd recognize it if you
were. The steps are ordered and reference each other (e.g. the update path's
step 2 needs tools that live in the version you're about to check out).
Reading is cheap; verifying is expensive. The level you choose governs how
much you *verify*, never how much you *read*.

**This is a verification exercise, not a fix-it exercise.** If a diff or a
build error doesn't match anything in the changelog below, stop and report it
rather than patching around it — especially if you're working in a fresh
session with no other context on this project. This holds at every
verification level: a lighter level means checking fewer things, never
lowering the bar for an anomaly you do find. Don't push or deploy anything
(this site, or changes to 559Theme itself) without explicit sign-off.

---

## First: which operation is this?

Gather the facts before moving any pointer. This costs seconds and replaces
guesswork:

```sh
cd themes/559Theme
git fetch origin --tags
git log --oneline HEAD..origin/master              # how many commits, and what
git diff --stat HEAD..origin/master                # which files changed
git tag -l --contains HEAD                         # where this pin sits vs. tags

# The decisive question — is this pin still pre-unification?
# (argument order matters: this asks "is HEAD at or before the tag?", and the
#  tag is the last commit BEFORE unification, so sitting ON it means upgrade)
git merge-base --is-ancestor HEAD pre-unification \
  && echo "AT/BEFORE pre-unification -> UPGRADE path (theme migration)" \
  || echo "POST-unification -> Update path"

# For the Update path: does anything in range affect rendered output?
git diff --name-only HEAD..origin/master \
  | grep -vE '\.md$|^(docs|tools|archetypes)/|^(\.gitignore|\.gitattributes|LICENSE)$' \
  || echo "NO OUTPUT-AFFECTING CHANGES"

git diff --name-only HEAD..origin/master | grep -E '^tools/'   # verification scripts moved?
cd ../..
```

### Reading the output-affecting filter

Get its categories right, because the whole point is to avoid both false
alarms and false comfort:

- **Cannot** affect built output: `*.md` anywhere (`readme`, `CRITIQUE`,
  `NOTES-usage`, `THEME-PLAN`, `todo`), `docs/`, `tools/` (dev scripts),
  `archetypes/` (only used by `hugo new`), `.gitignore`, `LICENSE`.
- **Can** affect built output: `layouts/`, `assets/`, `i18n/`, `data/`,
  `static/`, `content/`, and the theme's own top-level `config.toml`.

Two that are easy to miscategorize. `i18n/*.yaml` looks like config but
holds the UI strings — a one-line edit there changes every page on the site
(this is exactly what the footer-credit fix did). The theme's top-level
`config.toml` carries theme param defaults, so it is output-affecting too.
Conversely, a `tools/` change never alters output, but it does mean your
local `baseline.sh`/`compare.sh` copies are stale — refresh them from the
new version if you're verifying at level B or C.

If nothing survives the filter, the update is documentation-only and cannot
alter a single byte of the built site.

---

## Hugo-version drift is a separate axis

**Check this on either path, before anything else.** A Hugo-version change
produces its own diffs and its own build failures, completely independently
of the theme. If you bump both at once without knowing it, every anomaly has
two possible causes and you can't tell them apart.

```sh
hugo version
grep -rn "HUGO_VERSION" .github/workflows/ 2>/dev/null
```

Build with your **local** Hugo, and make sure that's the version you're
actually targeting. **Check the size of the gap:** if CI's pin and your local
Hugo are many minor versions apart (e.g. CI stuck on `0.147.3` while local
Hugo is `0.164.0+`), expect *more* than the fixes below — every site that has
hit a large gap has surfaced additional Hugo-level breakage that predates the
theme entirely.

If you're crossing **Hugo 0.164.0** (or anything since, or anything that
crosses the same deprecation boundaries) for the first time, all of the
following have already been needed on other 559Theme sites:

- **Content-security policy (Hugo v0.162+, CVE-2026-50133 fix).** Hugo
  tightened its default content-type policy and now blocks the theme's
  `text/html` content pages (`content/search.html`, or the legacy
  `content/lunr-search.html`) unless explicitly allowed:

  ```toml
  [security]
    allowContent = ["^text/markdown$", "^text/html$"]
  ```

- **`languageCode` deprecated (Hugo v0.158+).** Rename it to `locale` in your
  site config:

  ```diff
  -languageCode = "en-us"
  +locale = "en-us"
  ```

  (The theme itself already moved from `.Site.LanguageCode` to
  `.Site.Language.Locale` internally — this site-config rename is the only
  action needed on your end.)

- **`_build` front matter key removed, not just deprecated (Hugo v0.145+).**
  Any page using the underscore-prefixed key fails with a hard `ERROR`, not a
  warning. Course sites commonly use this on per-week/per-module index pages
  to hide them from section lists:

  ```diff
  -_build:
  +build:
      render: false
      list: never
  ```

  Check for it up front: `grep -rl '^_build:$' content/`.

- **Markdown-format shortcode templates now enforce their call delimiter.** A
  shortcode whose *template file* is `.md` (e.g.
  `layouts/shortcodes/dimbox.md`) must be invoked with `{{% %}}`, not
  `{{< >}}` — older Hugo tolerated the mismatch silently; newer Hugo
  hard-errors (`no compatible template found for shortcode "x" in [...]; note
  that to use plain text template shortcodes in HTML you need to use the
  shortcode {{% delimiter`). This can surface on *any* shortcode call in the
  site's content, not just ones the theme changed — it's exposing a
  pre-existing mismatch, not introducing one. If you hit it, check how every
  other call to the same shortcode in the site is delimited
  (`grep -rn '{{[<%]\s*shortcodename' content/`) — if the rest of the site
  already uses `{{% %}}`, the offending call is almost certainly a stray typo,
  and the fix is to match the delimiter, not to touch the template.

- **If your local Hugo surfaces anything else** — any build error or warning
  beyond these known ones — **stop and confirm with whoever's directing the
  work before working around it.** Hugo-version drift is open-ended in a way
  the theme changelog isn't. (This list only grows because someone hit an
  "anything else" case, resolved it, and added it here — if you resolve a new
  one, do the same.)

**Then bring CI in line with what you verified.** Update the pinned
`HUGO_VERSION` (or Hugo-install step) in `.github/workflows/*.yml` to match
your local `hugo version` — CI should build with the same Hugo you tested
against, not a stale pin.

---

## Update path (site already post-unification)

### How much verification?

Pick a level from the triage facts. **Report them to whoever's directing the
work and let them choose** — they know things the facts don't show, like
whether this site is about to be deployed or whether they care that a footer
string moved. Choose for them only if they've already said.

- **Level A — Rebuild check** (~1 min). Move the pointer, build, confirm no
  `ERROR`/`WARN`, commit. Confirms the site compiles; tells you nothing about
  what changed in the output. Right for docs-only updates, and for "I'll see
  it when I look at the site."
- **Level B — Verified update** (~5 min). Level A plus the golden-master
  diff: baseline *before* moving the pointer, `compare.sh` after, and confirm
  every remaining diff is explained by the changelog. Right when a handful of
  output-affecting files changed and you want to know exactly what moved.
- **Level C — Full validation.** Everything: repeat-build non-determinism
  check, golden-master loop, local-override scan, deprecation checker,
  config-param grep. Right when many commits land at once, when the changelog
  marks a required migration, or when you're about to deploy something you
  can't easily roll back.

**Escalate to C regardless of what was chosen** — say why first — if any of
these holds:

- Local `hugo version` differs from CI's pin, or this move crosses a Hugo
  minor-version boundary (see the section above).
- A changelog entry in range is marked **REQUIRED** migration, or removes
  something with no deprecated alias.
- The range touches `layouts/` broadly, or `assets/css/`, in a way you can't
  summarize in a sentence.

**One ordering constraint:** level B and C need a baseline captured *before*
the pointer moves, so the level has to be chosen up front. If you guess low
and change your mind it's recoverable — `git checkout <old-sha>` in the
submodule, take the baseline, `git checkout origin/master` again — but it's
friction, so decide before moving anything.

### Steps

Each step is tagged with the levels that need it.

1. **Pre-flight — the site is healthy before you touch it.** *(A, B, C)*

   Build clean: `hugo --baseURL /` (or `hugo server`) should complete with no
   `ERROR` and no `WARN`. Fix anything you find now, or consciously decide to
   ignore it and note why — don't carry a pre-existing warning into the
   update where it'll look like something the new version caused.

   **Additionally at level C:** rebuild 2–3 times with no changes at all and
   diff the output. Any difference between two builds of the *identical*
   commit is site/Hugo non-determinism, not something this move will
   introduce or fix. Hugo's auto-generated taxonomy term titles are a known
   source: if your content spells the same tag/category with inconsistent
   casing across pages (`"javascript"` in one file, `"JavaScript"` in
   another), Hugo's map-iteration tie-break picks a winner **at random per
   build**. Fix content-casing inconsistencies now so the golden-master diff
   isn't spent chasing a ghost.

2. **Capture a baseline, then move the pointer.** *(B, C — level A skips
   straight to the checkout)*

   `tools/baseline.sh` / `tools/compare.sh` ship inside the *new* version's
   `tools/` directory, but you need the "before" snapshot taken while still on
   the old commit. So, in this order:

   ```sh
   cd themes/559Theme
   git checkout -q -- . && git clean -fdq   # discard any local test edits
   git fetch origin --tags
   ```

   If your site doesn't already have current copies of the tools, pull them
   out of the target version now, without checking it out yet:

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

   (These scripts write their snapshots under `/tmp`. If you're running in a
   sandboxed environment, that path may need to be permitted.)

   **Only now move the pointer:**

   ```sh
   cd themes/559Theme
   git checkout origin/master
   cd ../..
   ```

3. **Build.** *(A, B, C)*

   ```sh
   hugo --baseURL /
   ```

   Keep fixing and rebuilding until this completes with no `ERROR`/`WARN`.
   Check the changelog before treating a build error as a bug — some entries
   remove a feature with no deprecated alias, and some name a migration tool.
   **At level A this is the finish line:** a clean build plus the knowledge
   that nothing output-affecting changed is the whole check. Go to step 7.

4. **Golden-master diff.** *(B, C)*

   ```sh
   ./tools/compare.sh pre-bump
   ```

   `compare.sh` excludes `*.css`/`*.js` from the diff (fingerprinted
   filenames legitimately change) and reports `HTML: IDENTICAL` when nothing
   else moved. **Any other HTML diff is a stop-and-investigate signal** —
   check the changelog for what the new version intentionally changed before
   assuming it's a regression.

   When a diff *is* expected, verify its *shape*, not just its existence. A
   one-line theme change should produce one changed line per page and nothing
   else: classify every changed line and confirm no files were added or
   removed, rather than eyeballing the first screen of output. A diff that is
   larger or differently-shaped than the changelog predicts is the signal.

   Diffs that are **not** update-related, and can be set aside once
   recognized:

   - `lastmod`/`pubDate` changes on any file you've edited as part of a
     migration — expected, tied to `enableGitInfo`.
   - Non-determinism you already characterized in step 1. If you skipped that
     check and see something like it now, rebuild the *old* commit twice with
     no changes to confirm it's pre-existing before blaming the new version.

   Loop between steps 3 and 4 — fix, rebuild, re-compare — until every
   remaining diff is either `HTML: IDENTICAL` or explained by the changelog.

5. **Scan for local overrides that would silently swallow a core update.**
   *(C)*

   Several changes in this project *promoted* something from a per-site
   override into the core theme (course shortcodes, the search widget). If
   your site — or an overlay theme in its `theme = [...]` list — has its own
   local copy of something the changelog says is now in core, **your local
   copy still wins** (Hugo resolves the site's own `layouts/` before any
   theme's) and you won't get the core behavior at all, deprecation warnings
   included. Delete the local copy, after checking for behavior differences,
   so the core version resolves.

   ```sh
   find layouts/shortcodes layouts/_shortcodes -maxdepth 1 \
     \( -name assign-link.html -o -name assign-linkonly.html -o -name reading.html \
        -o -name moddesc.html -o -name modlo.html -o -name modname.html \
        -o -name page.html -o -name snippet.html \) 2>/dev/null
   ```

   Two adjacent habits worth keeping, from experience doing this cleanup:

   - **Before deleting what looks like a "dead" config key** (e.g. a
     `mainSections`/`recentSections` entry with no matching `content/`
     directory), don't just trust a changelog's named example — confirm with
     `find content -maxdepth 1 -type d` that the referenced section genuinely
     has no directory, then verify with an identical rebuild before removing
     it. A changelog's example list is illustrative, not exhaustive; the same
     dead-key pattern has shown up in a second, unnamed spot on more than one
     site.
   - **Before renaming a config file** (e.g. `config.toml` → `hugo.toml`),
     grep your CI workflows/scripts for the literal old filename first. Hugo
     auto-detects either name, so a stale hardcoded reference wouldn't fail an
     obvious local build — it'd only surface in CI, later.

6. **Check for deprecated features you're still using.** *(C)*

   Do this *before* making any config changes, so you actually watch the
   deprecation warning fire and confirm the old alias currently works, rather
   than renaming things on faith from reading the changelog.

   - Read the build output for `WARN 559Theme: ... is deprecated ...` lines.
     These fire only for features your site actually calls, so a clean build
     with no warnings means nothing here needs attention.
   - For a fuller check, run the theme's checker against your site —
     **pass an absolute path**, not `.`: the script resolves any relative
     argument against its own location (the directory containing
     `themes/559Theme`), not your current directory, so a bare `.` silently
     scans the wrong tree and reports "no call sites" even when your
     `content/` has one.

     ```sh
     python3 themes/559Theme/tools/check-deprecated.py "$(pwd)"
     ```

     This covers **shortcodes** only, in `content/`, `assets/`, and
     `layouts/`, per repo passed in (see `docs/deprecation.md`). It does not
     scan for deprecated *widgets* (the `lunr` widget alias is invisible to
     it), and it does not know about deprecated `hugo.toml` params. For those,
     grep your own config as a starting point:

     ```sh
     grep -n "themestyle\|\"lunr\"" hugo.toml config.toml 2>/dev/null
     ```

     The `warnf` build warnings are the authoritative signal; the grep just
     tells you what to search for.

   Then apply the renames the changelog calls for (e.g. `themestyle` →
   `params.style.preset`, `lunr` → `search`).

7. **Commit.** *(A, B, C)*

   Commit the submodule pointer plus anything the changelog told you to
   change. Note in the message which version you moved to, **which
   verification level you ran**, and what that level actually confirmed — so
   the next person can tell "builds clean, docs-only" from "golden-master
   verified" without re-deriving it.

---

## Upgrade path — crossing `pre-unification` is a theme migration

If `git merge-base --is-ancestor HEAD pre-unification` said you're at or
before the tag, **stop thinking of this as a version bump.** The site is
about to change themes. There is no light verification level here: run the
Update path's steps at **level C**, plus everything in this section.

### What actually changes

A pre-unification site differs from a current one in all of these ways at
once — this is the scope you're taking on:

- **It has a second theme.** `theme = [...]` includes `roadster` (or
  `mainroad`, on older pins) as a fallback. That submodule goes away
  entirely; everything it provided now ships from 559Theme.
- **Styling is a different system.** `themestyle = "old"|"new"` is replaced
  by named style presets (`params.style.preset`). Three separately compiled
  CSS bundles become one `main.css`. Dead `@if $theme-style` branches are
  gone.
- **Templates are a different generation.** Root `layouts/baseof.html` and
  `_partials/` conventions (Hugo ≥0.146), replacing the older lookup layout.
- **Search is a different implementation.** Lunr from a CDN becomes a
  vendored MiniSearch, and the widget is renamed.
- **Course shortcodes moved into core**, so your local copies now shadow
  them.
- **`lnk` is gone outright**, with no deprecated alias.

### How to approach it

- **Budget a working session**, not a coffee break, and don't interleave it
  with content edits — it's a mechanical migration best verified by diffing
  build output.
- **Do it as its own commit series**, not one commit. Config change →
  verify → submodule removal → verify gives you rollback points; a single
  commit gives you none.
- **Expect to edit content and config**, not just the pointer. That's the
  difference between this and an update.
- **Check the Hugo-version axis first** (section above). Sites this far back
  on the theme are usually also far back on Hugo, and you do not want both
  sets of diffs at once.

### The specific migrations

Work through the changelog below in order — every entry from
`pre-unification` onward applies to you. The ones that need real work:

1. **Remove the fallback theme.** Config change first, verify, *then* remove
   the submodule:

   ```sh
   # 1. config: theme = ["559Theme","roadster"] -> theme = ["559Theme"]
   #    (or drop "mainroad" if that's what your site still has)

   # 2. verify with tools/compare.sh — expect only the v2-styles.css <link>
   #    tag to disappear from <head>, nothing else

   # 3. then remove the submodule for real:
   git submodule deinit -f themes/roadster   # or themes/mainroad
   git rm -f themes/roadster                 # or themes/mainroad
   rm -rf .git/modules/themes/roadster       # or .../mainroad
   ```

   A site can only be tracking one of `roadster`/`mainroad` at a time (the
   project switched from Mainroad to Roadster in 2025) — check `.gitmodules`
   to see which, if either, you have.

2. **Migrate `lnk` → `link`** (course sites). Pre-check before you move the
   pointer, since it's a hard build error with no alias:

   ```sh
   grep -rn '{{<\s*lnk\b\|{{%\s*lnk\b' content/
   ```

   Use `tools/migrate-links.py`, then read the known-gap note in the
   changelog entry — the tool's dry-run misses one pattern, and you want to
   know that before it hard-errors.

3. **Rename `themestyle` → `params.style.preset`**, and the `lunr` widget →
   `search`. Both have deprecation aliases, so do them *after* a verified
   build, watching the warnings fire.

4. **Delete local copies of promoted course shortcodes** (Update path step
   5), or you'll keep running the old ones silently.

### What the diff will look like

Much bigger than any single changelog entry implies — you're crossing every
intervening internal change at once. All of the following are **expected**,
need no site action, and are not itemized as changelog entries (the full
history is in `THEME-PLAN.md`'s Execution log):

- New wrapper `<div>`s around header/sidebar/footer (they support a
  `fullwidth` mode query-string toggle).
- CSS consolidated into one `main.css`.
- A preset-driven Google Fonts subset (fewer families than before).
- Footer copyright wording.

Treat this as expected **provided every diff is confined to `<head>` and
header/footer/sidebar chrome.** Confirm by diffing a content-heavy page (not
a list/index page) and checking that the article body itself — the actual
prose between header and footer — is byte-identical. That's the real
regression check, not the raw diff-line count.

---

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
preset = "uw-serif"               # or "mainroad-sans" — see the doc-comments in
                                   # assets/css/presets/*.scss for the two options

[params.sidebar]
widgets = ["search", "important", "links", "recents", "categories", "taglist"]
```

You also need to either set `baseURL` in `hugo.toml` or build with
`hugo --baseURL /` even if everything else on the site uses relative paths —
`layouts/index.json` (the search index) emits absolute permalinks and needs
one or the other, or search silently breaks.

Then set up `tools/baseline.sh`/`tools/compare.sh` (copy from
`themes/559Theme/tools/`) before making any further changes, so you have a
baseline to diff against going forward.

## Changelog: notable/breaking changes by version

Full rationale and evidence for all of these lives in `THEME-PLAN.md`'s
Execution log (theme repo, versioned) — this section is the short,
site-facing version: what you need to *do* when crossing each point, not why.

- **Tag `pre-unification`** — the last commit before the unification project
  (`63f35e4`). A site still here needs the **Upgrade path** above, not an
  update: it has a separate `roadster` (or, on very old pins, `mainroad`)
  theme in its `theme = [...]` list, uses `themestyle` (no presets), has its
  own local copies of course shortcodes (`assign-link`, `reading`, etc.), and
  its own `lunr`-based search page. None of the rest of this changelog
  applies until you've moved past this point.
- **Roadster absorbed into 559Theme — legacy fallback theme cleanup.** Drop
  `roadster` (or `mainroad`) from `theme = [...]` entirely — every
  partial/template/static asset it provided now ships from 559Theme directly.
  Commands and ordering: Upgrade path, "The specific migrations" §1.
- **Style presets replace `themestyle`.** Rename `themestyle = "old"|"new"`
  to `params.style.preset = "mainroad-sans"|"uw-serif"` (`old`→`mainroad-sans`,
  `new`→`uw-serif`). The old param still works via a deprecation `warnf` — not
  urgent, but do it before the alias is ever retired. Per-site token
  overrides live in `params.style.vars` (e.g. `bodyFontSize`, `fontSans`) and
  win over the preset's defaults, which is the supported way to diverge
  without editing a shared preset.
- **Course shortcodes promoted into the core theme** (`assign-link`,
  `assign-linkonly`, `reading`, `moddesc`, `modlo`, `modname`, `page`,
  `snippet`). If your site or an overlay theme has local copies, delete them
  so the core versions resolve (Update path step 5) — check for behavior
  differences first (see `docs/data-contracts.md` for the current
  data-source rules: whichever of `assignments.yaml`/`assigns.yaml` is
  present is used; it's a **build error** if both exist, not a warning).
- **`link`/`lnk` unified** (course sites only). `lnk` is **gone** — no
  deprecated alias. Two bare positional args are now a build error; use named
  params or the migration tool: `tools/migrate-links.py`.

  **Known gap in the migration tool's dry-run.** It tokenizes arguments with
  Python's `shlex`, which merges a quoted string immediately followed by a
  bareword into a single token (`"page"s` parses as one token, `pages`) — so
  it reports the call as an already-fine 1-positional case and leaves it
  untouched. Hugo's own shortcode-argument parser does *not* merge them; it
  sees two positional args and hard-errors, but only *after* you've moved the
  submodule pointer and the migration script has already told you everything's
  clean. In practice this pattern is a content typo — a stray trailing letter
  glued onto a closing quote, e.g. `{{< link "genai-policy"s >}}` — not an
  intentional second argument, and the fix is to delete the stray character.
  After running `migrate-links.py`, also grep directly for the shape it can't
  see — anchored to right after `link`/`lnk` so it only matches a *positional*
  first argument, not a legitimate `name="value"` pair (an unanchored
  `[^}]*` before the quote false-positives on any ordinary multi-attribute
  named call, e.g. `page="x" text="y"`, which is the common case once you've
  applied the renames above):

  ```sh
  grep -rnE '\{\{[<%]\s*(link|lnk)\b\s+"[^"]*"[A-Za-z0-9_]' content/ assets/snippets/
  ```

- **Lunr search replaced by MiniSearch** (`docs/search.md`). Rename the widget
  `lunr` → `search` wherever your widget list names it: the site-wide
  `params.sidebar.widgets`, or a per-page `widgets:` front-matter override (a
  page's own `widgets:` wins over the site-wide list — see
  `layouts/_partials/sidebar.html`). The old name still works via a
  deprecation `warnf`. No more CDN dependency (`unpkg.com`) — if your site
  allowlisted that domain anywhere (CSP, etc.), it can be removed.

  Note: a top-level site `params.widgets.<name>.cached` is a **different**,
  unrelated setting (a per-widget `partialCached` flag) — it is not an
  alternate place to put the widget *list*, despite the similar name. Don't
  confuse the two when renaming.
- **`menu.js` trimmed to a toggle-only script.** No site action needed unless
  you had custom JS depending on the old submenu handler or the dark-theme
  toggle — both were dead code (no site used them) and are gone.
- **`hint.css`/tooltip rewritten.** The vendored `html-hint` (`hint.css`)
  library is gone, replaced by a small self-contained `assets/css/tooltip.scss`
  (loaded via a site's `customCss`, e.g. `customCss = ["css/tooltip.scss"]` —
  check your site sets this if it uses the `tooltip` shortcode and expects it
  styled). One real behavior change: the old `color` param (and any other
  hint.css option) is **no longer supported** — the shortcode now warns
  (doesn't silently ignore) if you pass it. Grep your content for
  `{{< tooltip` / `{{% tooltip` calls with a `color=` param and drop it.
- **Bold math now renders correctly in Chromium.** `\mathbf{…}`/`\boldsymbol{…}`
  previously rendered at normal weight in Chromium-family browsers (a Chromium
  MathML-Core limitation — it ignores the `mathvariant="bold"` attribute KaTeX
  emits; Firefox was always fine). The `math`/`displaymath` shortcodes now
  rewrite those glyphs to real Unicode bold characters at build time, so bold
  math is correct in every browser. No site action needed — this is automatic
  once you bump past the fix. See `docs/math.md` and
  `docs/math-bold-research/README.md`.
- **`rimage` now truly resizes raster images; `resource-image` deprecated.**
  rimage previously shipped the full-resolution original scaled down with CSS
  (a Go-template scoping bug discarded the `.Fit` result), so pages downloaded
  full-size images. It now generates a properly downsized copy for the `<img>`
  and links that copy to the original — clicking an image now means "see it
  bigger." **No content change is required**; existing `{{< rimage >}}` calls
  simply start emitting smaller images (and real full-size links) on the next
  build. Two new `width` modes: a percent (e.g. `width="45%"`) sizes the *file*
  to that fraction of an assumed content-column width (default 800px; set
  `params.imageColumnWidth` to tune) and prints a "percent width is
  approximate" warning while keeping the CSS width fluid; `width="native"`
  shows a raster at its native pixel size with no resizing (raster only — a
  build error on an SVG). Small images are never upscaled and never get a
  pointless self-link. **`resource-image` is now deprecated** — it still works
  (it also resizes correctly, so nothing breaks, workbook sites included) but
  prints a build `warnf` per call. Migrate to rimage: `size="WxH"` becomes
  `width="W"` (rimage fits width only, height auto). `resource-svg` is
  unchanged and deliberately kept — its `inline`/`highlight`/`link` modes have
  no rimage equivalent.

  **Note for site maintainers:** this fix only applies to images displayed
  *through* a theme shortcode. A site with its own local layout that emits
  `<img src="{{ .RelPermalink }}">` directly still ships full-size originals,
  and no theme update can fix that — check your own `layouts/` for raw
  `.RelPermalink` image tags if page weight matters to you.
- **`figure` deprecated — REQUIRED migration to `rimage`.** The theme's `figure`
  is a modified copy of Hugo's built-in that adds `rsrc` (page/site resource
  lookup) and captions, but it does **not** resize — it ships the full-size
  original. We are unifying all image display on `rimage`, so the theme's
  `figure` override is going away. Migrate now: `{{< figure rsrc="X" caption="…"
  attr="…" attrlink="…" >}}` becomes `{{< rimage src="X" caption="…" attr="…"
  attrlink="…" >}}` (add a `width` to size it; `rsrc` globs work as `src`). It
  still builds today but prints a deprecation `warnf` per call. **Why required,
  not optional:** once the theme's `figure.html` is removed, `{{< figure >}}`
  falls back to Hugo's *built-in* figure, which has no `rsrc` parameter — so any
  un-migrated `rsrc` figure will silently stop finding its image. One caveat:
  `rimage` has no raw external `src="https://…"` mode; the rare figure that
  points at an external URL (none in the course sites) should stay on Hugo's
  built-in `figure` with `src=`.

## What this guide doesn't cover yet

- A full semantic-version tagging scheme — right now there's `pre-unification`
  and a tag per notable rollout (see the theme repo's tag list), not a formal
  version number per commit. If that becomes painful, consider tagging more
  granularly going forward. A real version scheme would also let the
  update/upgrade distinction above be read off a version number instead of an
  `is-ancestor` check.
- Automated checking of deprecated **params**/**widget names** (only
  shortcodes are covered by `tools/check-deprecated.py` today) — extending it
  would need a second scan mode over `hugo.toml` files.
- Automated non-determinism detection (level C asks you to rebuild a few times
  by hand and eyeball the diff) — could be folded into `compare.sh` itself
  (build twice before touching the submodule, fail loudly if they disagree).
- A `triage.sh` that runs the "which operation is this?" block and prints a
  recommended level. The commands are short enough to paste today, but
  scripting them would remove the chance of running the wrong one.
