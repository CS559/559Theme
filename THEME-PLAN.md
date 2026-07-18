# Theme Unification Plan

*July 2026. Execution plan for consolidating the 559Theme/roadster stack into a single core theme serving all Gleicher Hugo sites. Background and evidence: `REVIEW.md` + `ACTION-PLAN.md` (this repo), `765-25/REVIEW.md` (course-site review + four-site addendum).*

**Where this document lives:** here (the hub repo) until work begins. The first act of Phase 0 is copying it into the 559Theme repo on the working branch — the theme repo copy then becomes canonical, since that's where most work happens.

**Intended executor:** Claude Code sessions with Sonnet. Every task below has a mechanical verification step; the golden-master discipline (below) is what makes a weaker agent safe. Exception: Phase 3 (the SCSS collapse) involves the most cross-file reasoning — use Opus for that phase, or run it with Sonnet and review the diff yourself before merging. Phases 0–2 and 4–6 are well within Sonnet's reach *if the ground rules are followed*.

> **⚠ Execution status (kept current during the work).** This plan has been partially executed, and **deviated from the text below in several material ways** — most importantly the Phase 5 pruning policy (the "delete zero-usage" premise was abandoned once we established the theme has consumers *outside* this workspace). Do not read the phase text below as current truth. See **[Execution log: deviations and deferred items](#execution-log-deviations-and-deferred-items)** at the end of this file for what was actually done, what changed and why, and what remains deferred. The live per-session status is in the workspace `PROGRESS.md`.

---

## Decisions already made (do not relitigate in-session)

1. **One core theme.** 559Theme absorbs roadster; roadster is removed from every site. Rationale: four-site evidence in `765-25/REVIEW.md` addendum.
2. **Style presets replace `themestyle`.** Two named presets: `uw-serif` (current "new": Georgia body 1.1rem, Poppins small-caps red headings, red menu) and `mainroad-sans` (current "old": Open Sans .875rem, black normal-case headings, charcoal menu, 1080px container). Sites choose via `params.style.preset`; individual `style.vars` still override. Back-compat: `themestyle = "old"|"new"` maps to the presets with a deprecation `warnf`.
3. **Course machinery moves into the core theme** (assign-link, assign-linkonly, reading, page, moddesc, modlo, modname + the snippet mechanism), reconciling the 765-25/sp26 fork: adopt sp26's error style (include `.Position`), standardize on **`data/assignments.yaml`** (sp26's name), with a fallback read of `assigns.yaml` + `warnf` during transition.
4. **Per-site personality mechanisms:** courses use a thin overlay theme (the sp26 pattern); singleton sites (homepage, VisSnacks) use local `layouts/`. Don't force one mechanism on both.
5. **Lifecycle:** live sites track the theme and get pin bumps deliberately; archived course sites freeze at their pin forever. Migrating an archived site (765-25) is done as a *test* — merge only because the golden master proves output-identical.
6. **Migration order:** VisSnacks → 559-sp26 → 765-25 → gleicher.github.io. Simplest consumer first; the personal site goes last because it's the only `old`-style consumer and validates the `mainroad-sans` preset.
7. **Renames while passing through:** SASS `$font-mono` → `$font-body` (it's Georgia, not mono); collapse `link`/`lnk` into one shortcode (courses only; keep `lnk` as a deprecated alias that `warnf`s).
8. **MiniSearch replaces Lunr** (Phase 5b). Lunr's actual problems here are the unpinned unpkg dependency, per-search in-browser index rebuilds, and the 140-line results renderer living in `content/`. Site scale is small (~250–300KB of Markdown text per site → ~100KB gzipped index), so a client-side index is fine. MiniSearch is vendored into the theme (no CDN, no node), the index JSON stays Hugo-generated (dev search keeps working under `hugo serve -D`), and no CI step is added. *Pagefind was considered and rejected for now:* it requires a post-build indexing step Hugo cannot run itself, and `hugo server` renders to memory so dev search would break. It remains the upgrade path if a site outgrows client-side search — the widget boundary makes the swap contained.
9. **menu.js shrinks to a documented toggle-only script.** Of its 139 lines, only the mobile hamburger toggle (~25 lines) is live; the submenu handler (no site has submenus) and the entire dark-theme system (no toggle button exists in any layout) are dead. Replace with a ~12-line commented script using the same markup/classes — zero visual change.

## Ground rules for every Claude Code session

- **Golden-master discipline.** Before changing anything, build the affected site(s) and save `public/` as a baseline. After the change, rebuild and compare. Phases 1, 2, 4, 5 and every site migration must produce **identical rendered output** (modulo asset fingerprint hashes). Any unexplained diff = stop, investigate, do not proceed. Phase 3 intentionally changes CSS — it uses the probe checklist instead.
- **One phase (or one site migration) per session/branch/PR.** Commit checkpoints after each numbered task. Never combine phases in one diff.
- **Never modify `content/` or `data/`** except where a task explicitly says so (e.g., the `assigns.yaml` rename). Theme work must not touch prose.
- **Pin the toolchain.** Hugo 0.163.3 extended (match `.github/workflows/hugo.yml`). If local Hugo differs, install the matching version rather than upgrading the sites mid-migration. Upgrading Hugo is its own future task, easier after Phase 2.
- **Stop conditions.** If a build errors after a mechanical move, or a diff shows content-bearing changes, or a lookup seems to resolve from an unexpected place: stop and report rather than patching around it.

### Verification harness (create in Phase 0, use everywhere)

`tools/baseline.sh` (per site repo):

```bash
#!/bin/sh
# usage: baseline.sh <label>   — builds and snapshots public/ for comparison
set -e
rm -rf public
hugo --baseURL / --quiet
rm -rf "/tmp/golden-$1" && cp -R public "/tmp/golden-$1"
echo "baseline saved: /tmp/golden-$1"
```

`tools/compare.sh`:

```bash
#!/bin/sh
# usage: compare.sh <label>  — rebuild and diff against saved baseline
set -e
rm -rf public
hugo --baseURL / --quiet
# normalize asset fingerprint hashes before diffing
normalize() { find "$1" -name '*.html' -exec sed -i.bak -E 's/\.[0-9a-f]{40,128}\.(css|js)/.HASH.\1/g' {} \; ; find "$1" -name '*.bak' -delete; }
cp -R public /tmp/candidate.$$ && normalize /tmp/candidate.$$ 
cp -R "/tmp/golden-$1" /tmp/golden.$$ && normalize /tmp/golden.$$
diff -r --exclude='*.css' --exclude='*.js' /tmp/golden.$$ /tmp/candidate.$$ && echo "HTML: IDENTICAL"
rm -rf /tmp/candidate.$$ /tmp/golden.$$
```

CSS/JS are excluded from the strict diff (their filenames/content legitimately change in Phases 1 and 3); when a phase claims "no visual change," verify CSS by diffing the *un-fingerprinted compiled output* and confirming changes are limited to what the task predicts. Where available (VisSnacks), also run `htmltest`.

**Probe checklist** (Phase 3 + final site sign-off; run with a headless browser or by hand):
for each site's homepage + one content page, record: body `font-family`/`font-size`/`line-height`/`color`; `h1` `color`/`font-variant`/`font-family`; menu bar `background`; `.container` `max-width`; widget link color; one dimbox background. Compare to the expected preset values in **Appendix A** (`uw-serif` = current live 765-25 values, `mainroad-sans` = current live personal-site values).

---

## Phase 0 — Setup and baselines (½ day)

1. Clone `github.com:CS559/559Theme` directly (not via a site's submodule). Create branch `unify`. Copy this document into the repo root. **Accept:** branch exists; plan committed.
2. Note the three divergent site pins (`63f35e4`, `db6205c`, `634eb2c`). Diff each against `master` and confirm nothing on master breaks the older consumers' expectations, or record what does. **Accept:** a short `NOTES-pins.md` in the theme repo listing any behavioral differences (may be "none").
3. In each of the four site repos: add `tools/baseline.sh` + `tools/compare.sh`; run `baseline.sh pre-unify`. For 559-sp26 expect a slow build (564MB galleries). **Accept:** four baselines exist and `compare.sh pre-unify` passes trivially on unchanged repos.
4. Record the file inventory that roadster actually contributes per site. Method: `hugo --templateMetrics` per site, plus the known list — `_partials/{header,sidebar,mathjax,post_tags}.html`, `home.html`, `static/js/menu.js`, `assets/css/v2-styles.css`. **Accept:** `NOTES-roadster-files.md` listing every roadster-resolved file per site, verified empirically (temporarily remove roadster from one site's theme list; enumerate what breaks; restore).

## Phase 1 — Absorb roadster into 559Theme (1 day)

Work in the theme repo; test against VisSnacks and gleicher.github.io checkouts with the submodule pointed at the `unify` branch.

1. Copy the Phase 0 inventory files from roadster into 559Theme *in 559Theme's current template-layout convention* (don't mix generation migration into this phase). Keep file contents byte-identical where possible.
2. Fold `v2-styles.css` (93 lines) into the theme's SCSS bundle. Define the four dangling custom properties it references (`--color-menu-bg`, `--color-menu-border`, `--color-inverse-text`, `--color-overlay-shadow`) from the corresponding SASS vars.
3. In each of the two test sites: change `theme = ["559Theme"]` (drop roadster), point the 559Theme submodule at `unify`, run `compare.sh pre-unify`. **Accept: HTML identical** on both sites; CSS diff shows only the v2 merge.
4. Repeat the config change + compare for 765-25 and 559-sp26 (sp26 keeps its overlay: `theme = ["sp26","559Theme"]`). **Accept:** identical HTML on all four.
5. Remove the roadster submodule from all four repos (`.gitmodules`, config). Update each repo's CLAUDE.md/pullall script if it references roadster. **Accept:** clean builds from fresh clones (CI dry-run or `git clone --recurse-submodules` into /tmp).

## Phase 2 — Modern template layout (½–1 day)

Theme repo only. Migrate 559Theme to the current Hugo convention: `layouts/_default/*` → `layouts/*`, `layouts/partials/` → `layouts/_partials/`, etc. This removes the dual-generation lookup risk documented in `REVIEW.md`. Purely mechanical: `hugo mod` isn't in play, so it's file moves + updated partial references. **Accept:** all four sites rebuild with HTML identical to Phase 1 baselines (`baseline.sh post-p1` taken at end of Phase 1).

## Phase 3 — CSS unification and style presets (1–2 days; strongest model / closest review)

1. Replace the Go-templated `main.scss` with: a small generated `_hugo-tokens.scss` (only variable definitions come from Hugo params) + pure SCSS partials that tooling can lint. 
2. Create `presets/uw-serif.scss` and `presets/mainroad-sans.scss` as token bundles. `uw-serif` = today's "new" defaults (including the values currently in the *theme-level* `config.toml`, which should move into the preset). `mainroad-sans` = today's hardcoded "old" values, extracted from the 44 `@if $theme-style == "old"` branches (36 in `_style.scss`, 8 in `_559.scss`).
3. Delete all 44 branches; `themestyle` param maps to preset with `warnf`.
4. Rename `$font-mono` → `$font-body` (keep param alias `fontMono` working with `warnf`).
5. Make the Google Fonts `<link>` in `head.html` preset-driven; load only families the active preset uses (drop Bellota Text / Libre Baskerville if — verify — nothing references them).
6. Prune the theme-repo copy of anything Phase 3 orphans (e.g., roadster's never-loaded `style.css` if any remnant was carried over).

**Verification:** this phase changes CSS text by design, so golden HTML diff still applies (HTML must be identical) but CSS is verified by the **probe checklist**: 765-25 and VisSnacks under `uw-serif` must probe identical to their live values; gleicher.github.io under `mainroad-sans` must probe identical to its live values. Screenshot each site's homepage + one content page before/after at 1440px and 390px and compare visually. **Any probe mismatch = stop.**

## Phase 4 — Promote course machinery (1 day)

1. Copy the reconciled shortcodes into the theme: start from **sp26's versions** (better errors), add 765-25's `reading.html`, `moddesc/modlo/modname`, and the `snippet` mechanism if not already in the theme. Data lookups read `data/assignments.yaml`, falling back to `assigns.yaml` with `warnf`.
2. Write `docs/data-contracts.md` in the theme repo: schema for `assignments.yaml`, `readings.yaml`, `modules.toml`, `pages.yaml` (documented from 765-25's live files; note the sentinel/test entries as schema examples).
3. Collapse `link`/`lnk` (one implementation, `lnk` aliased + deprecated).
4. Test on 765-25: delete its 7 local shortcodes, rebuild. **Accept: HTML identical** to baseline (the fallback read makes the `assigns.yaml` name change unnecessary for the archived site — do *not* rename its data file).
5. Test on 559-sp26: delete the duplicated shortcodes from the `sp26` overlay so they resolve from the core. **Accept: HTML identical** (watch for the `assignments` vs `assigns` key and error-message differences — the overlay versions were the reconciliation source, so output should match).

## Phase 5 — Prune dead weight (½ day)

1. Generate a usage matrix: for each of the theme's shortcodes/partials/widgets, grep all four sites' `content/` + `layouts/` (script it; commit the matrix as `NOTES-usage.md`).
2. Delete everything with zero usage across all four sites. Expected candidates from the reviews: math/displaymath/eqref (superseded by native Hugo math), mikes-notes, draft-only, next/prev, resource-* cruft, `staff/` templates, course content stubs, the vendored html-hint library (replace the single tooltip use in gleicher.github.io content with a `title=` attribute — this is the one permitted content edit).
3. **Replace `menu.js`** (decision 9) with a documented toggle-only script. Keep the exact selectors and class names (`.menu__btn`, `.menu__list`, `menu__list--active`, `menu__list--transition`, `menu__btn--active`, `aria-expanded`). Delete the submenu handler and all theme-toggle/localStorage/matchMedia code. Header-comment the file: what it does, what markup it expects. **Accept:** HTML identical; mobile menu opens/closes on every site at 390px (manual or scripted check); no console errors.
4. **Accept (phase):** all four sites build with HTML identical; theme repo is measurably smaller; `NOTES-usage.md` documents what was deleted and why.

## Phase 5b — Replace Lunr search with MiniSearch (½ day)

Independent of Phases 2–4; requires only Phase 1 (theme owns the widget). Pure-Hugo pipeline: no node, no CI change, dev search keeps working under `hugo serve -D`.

1. Pre-check: grep all four repos for consumers of `index.json` other than `lunr-search` (none expected). **Accept:** documented in commit message.
2. Vendor `minisearch` (single minified file from the official release; record the version in a comment) into the theme's `assets/js/`; serve through Hugo Pipes with fingerprinting.
3. Clean the index template (`layouts/index.json`): title, tags, section, permalink, and **full** `plainify`-ed content — do NOT truncate. (Measured July 2026: full text is only ~165–300KB raw / ~100KB gzipped per site, and on 765-25 a 2,000-char cap would exclude ~⅔ of all text — long module pages are exactly what gets searched. A cap would also regress recall vs. the current Lunr setup, which indexes full content. Revisit only if a site's index exceeds ~1MB gzipped, and prefer Pagefind at that point anyway.)
4. Port the results renderer out of `content/lunr-search.html` into a proper theme layout (e.g., `layouts/page/search.html` + a tiny `content/search.md` stub per site, or a dedicated output — pick the simplest that keeps one canonical implementation in the theme). Rewrite against the MiniSearch API (`new MiniSearch({fields:['title','tags','content'], boost…})`, `search(q, {prefix:true, fuzzy:0.2})`); keep the existing DOM-building approach (it deliberately avoids innerHTML for content) but delete the lunr-specific plumbing and the hard-coded `../index.json` path (derive from `baseURL`/`relref`).
5. Rename the widget `lunr` → `search` (keep `lunr` as an alias in the widget loop with a `warnf`); placeholder text stops saying "lunr search …".
6. Per site (fold into each Phase 6 migration): update `widgets` param; replace `content/lunr-search.html` with the search stub; keep `"JSON"` in `[outputs]` (still needed — the index is still Hugo-generated).

**Verification (exception to golden-master):** intentional HTML changes = widget markup + search page only; everything else identical. Functional check per site, in `hugo serve` (this now works in dev — that's the point): search a term appearing on exactly one page and confirm the link resolves under the site's subpath baseURL; check mobile rendering; grep `public/` to confirm no `unpkg` references remain; record `index.json` size (expect roughly today's size; ~100KB gzipped is fine). **Recall check:** search a term that appears only in the final section of the site's longest page (e.g., deep in a 765-25 module page) and confirm it's found.

*Future option, recorded:* if a site outgrows client-side search, swap this widget for Pagefind (post-build `npx pagefind --site public` in CI; dev search degrades). The widget boundary is the seam.

## Phase 6 — Site migrations (½ day each, in order)

For each site — **VisSnacks, then 559-sp26, then 765-25, then gleicher.github.io**:

1. Bump the 559Theme submodule to the `unify` head; confirm roadster already removed (Phase 1).
2. Set `params.style.preset` (`uw-serif` for the first three; `mainroad-sans` for the personal site). Remove `themestyle`.
3. Site config modernization: rename `config.toml` → `hugo.toml` where applicable (personal site), lowercase `[params]`, delete dead keys (765-25's `weeks-in-vis`/`assigns` section references; personal site's commented-out cruft).
4. Apply the per-site search wiring (Phase 5b step 6): widget param rename, search page stub replaces `lunr-search.html`.
5. Run `compare.sh`, probe checklist, screenshots (desktop + mobile), `htmltest` where configured, and the search functional check.
6. Merge; for **765-25**, tag the result and treat the new pin as its permanent freeze; for live sites, note the pin-bump routine in the repo's CLAUDE.md.

**Accept per site:** identical HTML, probes match preset, CI deploy green, live spot-check.

## Phase 7 — Follow-on work (separate efforts, separate plans)

- **765-26 bootstrap** on the unified theme: overlay theme + `schedule.yaml` architecture, dashboard homepage, archetypes — see Part 4 of `765-25/REVIEW.md`.
- **Personal site visual refresh** on the new base — Phase 3 of `ACTION-PLAN.md` (typography, homepage restructure, red discipline). Now expressible as token changes + a homepage template, since the site runs on presets. Consider whether the homepage simply adopts `uw-serif`.
- Hugo version upgrade across sites (easier post-Phase 2).
- 559-sp26 gallery externalization (564MB in `assets/`) for future semesters.

---

## Session-starter prompt (copy into Claude Code)

> Read THEME-PLAN.md in this repo. We are executing Phase N. Follow the ground rules exactly: golden-master discipline (tools/baseline.sh + tools/compare.sh), one phase per branch, no content/ edits, stop on unexplained diffs. Do the numbered tasks for Phase N in order, committing after each. Report the verification evidence (diff output, probe values) for each acceptance check.

Total estimate: 6–9 focused days across phases, naturally splittable into single-phase sessions.

---

## Appendix A — Preset reference values (the `themestyle` old/new fork, measured July 2026)

The `themestyle` mechanism: `main.scss` is Go-templated (`ExecuteAsTemplate`) before Sass compilation; the param selects Sass variable values plus **44 `@if $theme-style == "old"` branches** (36 in `_style.scss`, 8 in `_559.scss`). "new" values are param-driven with defaults split between `main.scss` and the **theme-level `config.toml`** (which supplies Poppins/Georgia/1.1rem — move these into the preset in Phase 3). "old" values are hardcoded in the branches. `$font-mono` is misnamed: in "new" mode it holds the Georgia *body* font.

| Probe | `mainroad-sans` (= "old", live on gleicher.github.io) | `uw-serif` (= "new", live on 765-25 / VisSnacks / 559-sp26) |
|---|---|---|
| body font-family | "Open Sans", Helvetica, Arial, sans-serif | Georgia (via misnamed `fontMono`) |
| body font-size / line-height | .875rem (14px) / 1.6 | 1.1rem (17.6px) / 1.48 |
| body color | black | #4a4a4a |
| h1–h6 color / font-variant | black / normal | #c5050c / **small-caps**, family = `fontSans` (Poppins-first) |
| menu bar background | #2a2a2a (charcoal) | #c5050c (UW red), underlined hover |
| `.container` max-width | 1080px | 1500px (+5% content side margins) |
| widget link color | black | #006cae (blue) |
| widget accents | thin #ebebeb borders | 5px #c5050c bottom borders |
| dimbox | #ffd bg, #bbd border | #dee7ff bg, borderless |
| code blocks | #f5f5f5 bg, #ebebeb border, inherit color | #f7f7f7 bg, no border, #c5050c color |
| inline buttons | white on darkred | #006cae on white |
| logo/tagline | red logo text, normal case, tight header (25px pad) | red uppercase logo, gray tagline, roomy header (50px pad) |

Other conversation-derived facts an executing agent needs: link color both styles ≈ #c5050c on white (≈5.9:1, passes AA); `head.html` unconditionally loads three Google font families (Poppins, Bellota Text, Libre Baskerville) on every page of every site — Phase 3 step 5 makes this preset-driven; `menu.js` anatomy is in decision 9; Lunr/MiniSearch rationale and site text sizes (165–300KB raw, 2,000-char cap would drop ~⅔ of 765-25's text) are in decision 8 and Phase 5b.

## Appendix B — Document map (where everything lives)

| Document | Contents |
|---|---|
| `gleicher.github.io/REVIEW.md` | Personal-site design + implementation review; theme-stack fragility analysis; options A/B/C |
| `gleicher.github.io/ACTION-PLAN.md` | Personal-site roadmap (Phases 0–4: bugs, editorial, consolidation, visual refresh); the visual-refresh spec lives here |
| `gleicher.github.io/THEME-PLAN.md` | **This file — the canonical execution plan** for theme unification across all sites. Copied to the 559Theme repo at Phase 0; that copy becomes canonical |
| `765-25/REVIEW.md` | Course-site review; data-layer/workflow analysis; 765-26 design suggestions (schedule.yaml, dashboard homepage, archetypes); **four-site addendum** with the unified-theme evidence and verdict |
| Theme repo `NOTES-*.md` (created during execution) | Pin differences, roadster file inventory, usage matrix — Phase 0/5 outputs |

Session records: the reviews were produced from a July 2026 Cowork session that also visually inspected all four live sites (desktop + mobile) and verified every factual claim against the repos. Anything not captured in these five documents was judged not needed for execution.

---

## Execution log: deviations and deferred items

Maintained as the plan is executed. The phase text above is the *original*
intent; where reality diverged, this section is authoritative. Detailed
per-session status lives in the workspace `PROGRESS.md`.

### Status by phase

- **Phases 0–4: DONE** (with the deviations below). Phase 4 course machinery is
  promoted; the sp26 mixin overlay dupes are **not yet removed** (deferred).
- **Phase 5: substantively DONE** (menu.js, expand-old, tooltip, docs +
  deprecation/usage tooling) with a **major policy change** (below). Orphan-layout
  pruning deferred.
- **Phase 5b: DONE** (theme `18173b2`). Lunr replaced by MiniSearch; all four
  sites bumped.
- **Phase 6: DONE** (theme `c1c5005` on all four sites). `themestyle` ->
  `params.style.preset`, `lunr` -> `search` widget, `[params]` lowercased,
  confirmed-dead config keys removed, `gleicher.github.io`'s `config.toml`
  renamed to `hugo.toml`. Phase 6 intended to tag 765-25 `frozen` (permanent
  pin per decision 5) — **that tag was never actually created, and the
  freeze was never maintained** (see deviation 15). See deviations below for
  what Phase 6 turned out to need vs. not.
- **Phase 7: NOT STARTED** (separate follow-on efforts; see plan text).
- **The theme IS pushed.** `master` on `origin` (`github.com/CS559/559Theme`)
  was fast-forwarded from `63f35e4` to `7721c59` (`unify`'s tip, now
  including `docs/upgrading.md`) and pushed, along with two tags: `pre-unification`
  (the old `63f35e4` state — rollback point) and `v1-unification` (this
  rollout, `7721c59`). Rationale + the real (non-`local-unify`) consumer
  workflow: `docs/upgrading.md`.
- **The four consumer sites are still local-only** (unpushed to their own
  origins) and still track the theme via the temporary `local-unify` git
  remote rather than `origin` directly — switching them over is optional
  future cleanup, not required (see workspace `PROGRESS.md`).

### Deviations from the plan as written

1. **Phase 5 pruning policy — CHANGED (most important).** The plan said "delete
   everything with zero usage across all four sites." That premise was abandoned:
   the theme has **consumers outside this workspace** (other course webs, the
   Workbook site family). "Unused by these four sites" ≠ "dead." New policy:
   **soft-retire, don't delete** — keep things working, mark deprecated with a
   `warnf`, and only remove after a checker shows zero use across *all* known
   consumers. Only *structurally* dead code was actually removed (the dark-mode +
   submenu JS in `menu.js`; `expand-old`, which is superseded by `expand`).
   `NOTES-usage.md` is an **information map, not a delete list**.
2. **Phase 4 `link`/`lnk` — bigger breaking change.** `lnk` was **removed
   outright** (not kept as a deprecated alias); two-positional-arg usage
   disallowed; named params required. Migration tool: `tools/migrate-links.py`.
3. **Phase 4 data resolution — no `warnf` fallback; error-if-both instead.**
   Decision 3's "read `assignments.yaml`, fall back to `assigns.yaml` with
   `warnf`" became: **use whichever file is present; build error if BOTH exist;
   no deprecation warning.** Applied to `assign-*` (`assignments.yaml` |
   `assigns.yaml`) and to `page`.
4. **Phase 4 `page` shortcode — CSV primary, YAML fallback.** `page` reads
   `assets/pages.csv` (primary) **or** `data/pages.yaml` (fallback), error if
   both. Driven by the shared-data model: Workbook + course-web sites for one
   semester share a `pages.csv`. (Not anticipated by the plan.)
5. **Phase 5 tooltip / html-hint — kept the feature, replaced the library.** The
   plan wanted to drop html-hint and convert the tooltip use to a `title=`
   attribute (a content edit). Instead the rich `tooltip` shortcode was **kept**
   and its 140KB `hint.css` dependency replaced with ~30 lines of self-contained
   CSS (`+:focus-within` a11y). Unsupported params now `warnf`.
6. **Phase 5 math — the shortcodes are NOT dead.** `math`/`displaymath`/`eqref`
   already use Hugo's native build-time `transform.ToMath`; they were **kept**.
   The genuinely obsolete piece — the `mathjax.html` partial (MathJax 2.x from a
   CDN) — was removed instead.
7. **Hugo version.** Plan pins 0.163.3; execution standardized on **0.164.0**
   (CI bumped Phase 0).
8. **Phase 5b — no prebuilt minified MiniSearch to vendor.** The plan assumed
   "a single minified file from the official release"; as of MiniSearch 7.x the
   npm package ships only an unminified UMD bundle (`dist/umd/index.js`, no
   `.min.js`). Vendored that file as-is (`assets/js/minisearch.js`, header
   comment records version/source) and run it through `resources.Minify` +
   `resources.Fingerprint` in `layouts/search.html` at Hugo build time instead —
   same end result (minified, fingerprinted, no CDN), different starting file.
9. **Phase 5b — MiniSearch `combineWith: "AND"`, not the plan's literal
   `{prefix:true, fuzzy:0.2}` call.** Measured on VisSnacks: MiniSearch's
   default OR-combination plus prefix+fuzzy made a 2-word test query
   ("Dis-Aggregating") match 38 of 45 pages — short/common word-fragments
   fuzzy/prefix-expand to match nearly anything. `combineWith: "AND"` (require
   every query word to match somewhere in the doc) brought that down to 1–3,
   with the true match ranked first by a wide score margin, while keeping
   prefix/fuzzy for typo tolerance. See `docs/search.md`.
10. **Phase 5b — `layouts/index.json` gains a `section` field**, per the plan's
    own field list ("title, tags, section, permalink, ... content"), which the
    pre-existing template omitted.
11. **Phase 6 — less config-filename work than the plan implied.** The plan's
    step 3 reads as if all sites might need a `config.toml`→`hugo.toml` rename;
    in fact three of four (VisSnacks, 559-sp26, 765-25) were already on
    `hugo.toml`. Only `gleicher.github.io` still had the legacy filename.
12. **Phase 6 — the `lunr`→`search` widget rename was low-stakes, not a real
    migration.** Because Phase 5b kept `widgets/lunr.html` as a `warnf` alias,
    all four sites already worked correctly with `"lunr"` in their `widgets`
    param before Phase 6 touched them — confirmed by an HTML-identical
    rebuild both before and after the rename on every site. Phase 6 just
    removed the now-unnecessary deprecation warning.
13. **Phase 6 — additional dead config keys found beyond the plan's named
    example.** The plan named 765-25's `weeks-in-vis`/`assigns` as dead; the
    same pattern (a `mainSections`/`recentSections` entry with no matching
    `content/` directory) was also found and removed in **559-sp26**
    (`week-in-559`, `assignments` — assignments are shortcode/data-driven, not
    a content section). Both removals were verified inert by an
    HTML-identical rebuild before touching them further.
14. **Phase 6 — CLAUDE.md pin-bump documentation only added where a CLAUDE.md
    already existed.** Only `gleicher.github.io` had one (updated: hugo.toml
    filename, `style.preset` instead of `themestyle`, `search` widget, plus a
    new theme-bump-routine section). VisSnacks, 559-sp26, and 765-25 have no
    CLAUDE.md at all — none was created; that's a separate scope decision
    left for the user.
15. **Decision 5 ("archived course sites freeze at their pin forever") —
    never actually implemented, then overridden by later practice.** No
    `frozen` tag was ever created (checked 2026-07-15: absent from both the
    theme repo's tags and 765-25's submodule, local or remote). Without a
    tag to signal "stop here," 765-25 kept getting included in ordinary
    all-four-sites bump sweeps — Phase 5b (Lunr→MiniSearch), the
    math-bold-in-Chromium fix, and a subsequent docs-only update all landed
    on 765-25 same as the three live sites. Confirmed with the user
    (2026-07-15) that this is fine going forward: **765-25 is treated as a
    normal tracking consumer, not a frozen one**, absent a deliberate
    decision to actually freeze it (tag the pin, exclude it from future bump
    sweeps). See `765-25/REVIEW.md`'s update note for the site-side record.

### Additions not in the original plan

- **Deprecation infrastructure:** `docs/deprecation.md` + `tools/check-deprecated.py`
  (soft-retire via `warnf`, retire only after the checker clears all consumers).
- **Documentation pipeline:** `tools/shortcode-docs.py` → `docs/shortcodes.md`
  (every shortcode now has a doc-comment header; generated reference).
- **`docs/data-contracts.md`** (Phase 4 #2) and **`docs/math.md`**.
- **`docs/math-bold-research/`** — full investigation + evidence + re-runnable
  rigs for the MathML bold problem (see deferred item below).
- **`docs/search.md`** (Phase 5b) — MiniSearch architecture, the vendoring/
  Pipes deviation, the `combineWith` tuning finding, site setup, and the
  recorded Pagefind upgrade path.
- **`docs/upgrading.md`** — the site-maintainer-facing guide for the *real*
  (post-push, no `local-unify`) workflow: routine bump procedure, first-time
  setup for a new site, and a changelog of breaking/notable changes across
  the unification. Written when the theme was pushed to `origin/master`
  (`v1-unification`) so a fresh consumer could actually use it.
- **`rimage` resize fix + `resource-image` deprecation** (image-shortcode
  cleanup). Fixed a Go-template scoping bug in `rimage` that discarded the
  `.Fit` result, so rasters were served full-size and scaled by CSS; rimage now
  emits a real downsized copy and links it to the original. Added `width="45%"`
  (fits the file to `params.imageColumnWidth` × percent, with an approximate
  warning — Hugo cannot see the CSS column width) and `width="native"` (no
  resize, raster only). Soft-deprecated `resource-image` (marker + `warnf`;
  still functional). Also aligned `tools/check-deprecated.py` to read the
  `@deprecated:` marker from the doc-header comment (it previously only matched
  a dedicated `{{/* … */}}` comment, which no real deprecation used), and
  documented the header-marker convention in `docs/deprecation.md`.

### Deferred items (open work)

1. **Retire the sp26 mixin overlay dupes** (`page`/`assign-link`/`assign-linkonly`
   in the shared `sp26-mixin-theme` submodule). Deploy caveat: those shortcodes
   are shared across the semester's site family (incl. **Workbook**, a *different*
   theme not in this workspace). Before removing them, provision equivalents into
   the other consumers first. **Not touched in Phase 6** (Phase 6 as executed was
   config-only per-site migration; this needs a separate cross-repo effort) →
   deploy time / whenever that coordination happens. **Still open** — this is
   the one genuinely blocked deferred item; everything else below is either
   done or open for unrelated reasons.
2. **MathML bold does not render in Chromium — DONE (2026-07-14).** Built in
   559Theme itself (not Workbook-first as originally planned — see
   `docs/math-bold-research/README.md`'s "Decision: build in 559Theme first"
   for why). Unicode-glyph substitution (`layouts/_partials/math/variant-fix.html`
   plus `data/mathvariants.yaml`) with a build-time canary; validated on
   559Tutorials (the held-out math-heavy site) in Chromium and Firefox.
   Deployed to all four workspace sites via their normal theme-bump sweeps.
   **Still open:** porting the same transform to the separate **Workbook**
   theme, which currently works around the bug differently (`output:"html"`
   plus a CDN `katex.css`) — not started.
3. **Goldmark passthrough (`$…$`) for math** — investigated, deferred (no current
   need; use `\(…\)` not `$…$` if adopted). Notes in `docs/math.md`.
4. **Orphan layouts** (`staff/`, `talks/`, `video/`, `visual_sum`, `mini`,
   `inline`) — examine usage before removing. **Still not examined** — Phase 6
   did per-site config migration only, not a layout-usage audit.
5. **tooltip base-bundling** — could load `tooltip.scss` from the theme base to
   drop the per-site `customCss` opt-in. **Still open**, optional simplification.
6. **Push to GitHub — DONE for the theme AND all four sites (2026-07-15).**
   The theme has been on `origin/master` since `v1-unification`; as of
   2026-07-15 all four consumer sites are also pushed to their own real
   origins (`uwgraphics/VisSnacks`, `uwgraphics/765-25`, `uwgraphics/559-sp26`,
   `gleicher/gleicher.github.io`), each tracking `origin/master` directly
   (the `local-unify` remote described elsewhere in this plan is now
   historical/obsolete) and deployed to production via GitHub Actions CI on
   push to `main`. **The unification project's core work is complete** — see
   the new section below for what's genuinely still open vs. what's now
   ordinary site-level maintenance.

### External-consumer constraints (why some things are deferred, not forgotten)

The user asked (2026-07-15) to compile every place a decision was "don't do
X because other theme consumers depend on it" — these are scattered through
the deviations/deferred-items above; collected here in one place:

- **Phase 5 pruning policy itself (deviation 1).** The plan's original
  premise — "delete anything with zero usage across these four sites" — was
  abandoned wholesale for this reason. The theme has real consumers outside
  this workspace (other course webs, the Workbook site family), so "unused
  here" is not "dead." This is the umbrella policy; `NOTES-usage.md` is an
  information map, not a delete list (`docs/deprecation.md` has the
  soft-retire/checker mechanics).
- **The sp26 mixin overlay dupes (deferred item 1, above).** Can't retire
  `page`/`assign-link`/`assign-linkonly` from `sp26-mixin-theme` until
  equivalent copies exist in its *other* consumers — principally the
  Workbook theme family, which is not in this workspace and shares the same
  semester data (e.g. `pages.csv`).
- **`files.yaml` is kept/documented even though none of the four workspace
  sites' shortcodes consume it directly.** It's the build input to
  `readings.yaml` generation, but it's *also* read at runtime by a
  Canvas-file link shortcode that lives in other course repos outside this
  workspace (see `docs/data-contracts.md`'s `files.yaml` section) — so it's
  a live data contract to preserve, not dead weight to prune.
- **Math bold was built in 559Theme, not Workbook, despite Workbook being
  the more math-heavy consumer** — a sequencing choice, not a "don't do
  this" one (item 2, above): 559Theme was already on the clean MathML path,
  so it was the faster route to a validated fix; Workbook needs a bigger
  prerequisite change (switching off `output:"html"`+CDN) before it can
  receive the same transform. Full reasoning:
  `docs/math-bold-research/README.md`.

### Workspace `TO-DO.md` extras (beyond this plan)

- Verify thumbnails produce actually-smaller images (`thumbnail`/`rimage`/etc.).
- Standardize on one image shortcode.
