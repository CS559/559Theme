# Site theme pins vs. `master` (Phase 0 task 2)

> **Historical, one-off audit — not a living doc.** This was a single Phase 0
> pre-check; the question it answers (were all four sites converged on the
> same theme commit before the unification work started) no longer applies
> now that Phases 0–6 are done and the sites have moved on. Kept for the
> record, not maintained going forward.

Recorded 2026-07-12, from the `unify` branch (currently identical to `master` plus `THEME-PLAN.md`).

| Site | Pin (at start of session) | Status |
|---|---|---|
| VisSnacks | `db6205c` | Ancestor of `master`; **tree-identical** to `master` (`git diff db6205c master` is empty). No behavioral difference at all. |
| 765-25 | `63f35e4` | Is `master` tip. No diff. |
| gleicher.github.io | `63f35e4` | Is `master` tip. No diff. |
| 559-sp26 | `634eb2c` (pre-fix) | Diverged from `master` by 5 commits. Fixed as a Phase-0 pre-step (see below) — now also pinned at `63f35e4`. |

## 559-sp26: `634eb2c` → `63f35e4` (already bumped, see 559-sp26 commit `3ee553b`)

This bump was pulled forward from Phase 6 as a pre-step, because 559-sp26 wouldn't build under Hugo 0.164.0 without it (`.Site.LanguageCode` deprecation warning; separately, a `[security] allowContent` config gap caused a hard build error, fixed independently in 559-sp26's own `hugo.toml`).

The 5 commits between the two pins touch 4 files:

- `layouts/_default/baseof.html` — `.Site.LanguageCode` → `.Site.Language.Locale`. No visible output change (fixes the deprecation warning only).
- `layouts/_default/summary.html` — strips a duplicate image link from the summary when `.Params.resourcethumb` is set. **559-sp26's content never sets `resourcethumb`** (verified via grep), so this path never executes. Confirmed empirically: full-site build diff before/after the bump was whitespace-only (a collapsed newline+tab between `<article>` and `<header>` tags), no content/attribute changes.
- `layouts/shortcodes/draft-only.html` — `{{ .Site.BuildDrafts }}` branch replaced with `{{errorf "BuildDrafts Deprecated"}}` (would be a hard build error if used). **559-sp26's content never uses the `draft-only` shortcode** (verified via grep) — dead code, no effect.
- `readme.md` — theme repo doc only, irrelevant to site output.

**Net result:** all four sites are now behaviorally converged on `master` (`63f35e4`) with no unexplained differences. There is no "record what does break" case to carry forward from this step.
