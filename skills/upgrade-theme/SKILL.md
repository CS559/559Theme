---
name: upgrade-theme
description: Fetch the current 559Theme upgrading instructions and follow them to bump a site's theme submodule to the latest version, at a verification level matched to the size of the change. Use when the user asks to update/upgrade/bump the 559Theme submodule, or wants to bring a Hugo site using 559Theme up to date.
---

# Upgrade a site's 559Theme submodule

Any site that uses `559Theme` as a git submodule (conventionally at
`themes/559Theme`) keeps its authoritative upgrade procedure — pre-flight
checks, the routine-bump steps, and the changelog of breaking changes —
*inside that submodule*, at `themes/559Theme/docs/upgrading.md`. Don't
assume this file's content; always fetch the current version before acting,
since it's the single source of truth and evolves independently of any
particular site.

This creates a chicken-and-egg problem: you want to read the **current**
instructions (most sites track the theme's `master` branch, not a pinned
tag, so "current" keeps moving), but reading them shouldn't require first
disturbing the submodule's checked-out state — that's exactly the kind of
premature action the instructions themselves warn against taking before
you've even read what's coming.

**Not every bump deserves the same scrutiny — and one kind deserves far
more.** Two different operations wear the same `git checkout` command:

- An **update**: the site is already post-unification and moving forward a
  few commits. This is the common case, often docs-only or a one-line string
  fix. Running a full golden-master procedure on one of these is real work
  spent confirming something that was never in doubt.
- An **upgrade**: the site is at or before the `pre-unification` tag. This
  is not a version bump, it's **adopting a different theme** — template
  generation, CSS pipeline, style system, search implementation, shortcode
  inventory, and the length of `theme = [...]` all change at once. It needs a
  working session and its own commit series, and it has no light option.

Steps 4 and 5 below right-size the update case and route the upgrade case to
the heavier path. If the theme's own `docs/upgrading.md` already draws this
same update/upgrade distinction and defines verification levels, **defer to
it** — it's authoritative and this file is the fallback.

## Step 1: Confirm the site actually uses this submodule

Check for `themes/559Theme` (or find it via `.gitmodules`) in the target
repo. If it's not there, this skill doesn't apply — stop and ask, rather
than guessing at a different theme's location or structure.

## Step 2: Read the current instructions without checking anything out

Primary method — fetch and read the file straight out of the remote's
`master` ref, without touching the submodule's working tree, index, or HEAD:

```sh
cd themes/559Theme
git fetch origin
git show origin/master:docs/upgrading.md
cd ../..
```

This is read-only and side-effect-free (`git fetch` only updates the
`origin/master` remote-tracking ref; `git show <ref>:<path>` prints a blob
without checking anything out). It also ties what you're about to follow to
an exact commit — if you want to note which commit you read, `git -C
themes/559Theme rev-parse origin/master`.

Fallback, if `git fetch` can't reach the remote (network/auth restrictions
in your environment) or the submodule isn't initialized yet: fetch the raw
file over HTTPS instead — `559Theme` is a public repo —
`https://raw.githubusercontent.com/CS559/559Theme/master/docs/upgrading.md`.
Note this can lag a push by a few minutes (CDN caching) and isn't tied to a
citable commit, so prefer the `git show` method when it works.

## Step 3: Read the whole thing before acting

The instructions themselves say to read the whole guide once, start to
finish, before running anything — the steps reference each other by number.
Don't skip this, **regardless of how small the bump looks.**

Reading is cheap; verifying is expensive. The verification level chosen in
step 4 governs how much of the guide's *procedure* you execute — never
whether you read it. The changelog is how you find out that this
particular bump crosses something that isn't optional.

## Step 4: Triage the bump, then let the user pick a verification level

Don't try to judge the risk by reasoning about it — there's a mechanical
signal that costs about two seconds and is far more reliable. Gather it
first, *before* moving any pointer:

```sh
cd themes/559Theme
git log --oneline HEAD..origin/master              # how many commits, and what
git diff --stat HEAD..origin/master                # which files changed
git tag -l --contains HEAD                         # where this pin sits vs. tags

# Is this an update, or the unification upgrade? (argument order matters: this
# asks "is HEAD at or before the tag?", and the tag is the last commit BEFORE
# unification, so sitting exactly ON it still means upgrade)
git merge-base --is-ancestor HEAD pre-unification \
  && echo "UPGRADE - theme migration, no light option" \
  || echo "UPDATE - pick a level below"

# Does anything in this range affect rendered output?
git diff --name-only HEAD..origin/master \
  | grep -vE '\.md$|^(docs|tools|archetypes)/|^(\.gitignore|\.gitattributes|LICENSE)$' \
  || echo "NO OUTPUT-AFFECTING CHANGES"

git diff --name-only HEAD..origin/master | grep -E '^tools/'   # verification scripts moved?
cd ../..
hugo version                                       # vs. CI's pin:
grep -rn "HUGO_VERSION" .github/workflows/ 2>/dev/null
```

That filter is the useful part, so get its categories right:

- **Cannot** affect built output: `*.md` anywhere (`readme`, `CRITIQUE`,
  `NOTES-usage`, `THEME-PLAN`, `todo`), `docs/`, `tools/` (dev scripts),
  `archetypes/` (only used by `hugo new`), `.gitignore`, `LICENSE`.
- **Can** affect built output: `layouts/`, `assets/`, `i18n/`, `data/`,
  `static/`, `content/`, and the theme's own top-level `config.toml`.

Two easy-to-miss ones: `i18n/*.yaml` is output-affecting despite looking
like config — it holds the UI strings, and a one-line edit there changes
every page. And the theme's top-level `config.toml` carries theme param
defaults, so it is output-affecting too. Conversely a `tools/` change never
alters output, but it does mean your local `baseline.sh`/`compare.sh` copies
are stale — refresh them from the new version if you're doing level B or C.

If nothing survives the filter, the bump is documentation only and cannot
alter a single byte of the built site. (Validated against four real bumps in
this theme's history: it correctly separates two docs-only ranges from an
`i18n` one-liner and a `layouts/` change.)

**Report the triage to the user in two or three lines** (commit count,
changed files, docs-only or not, Hugo version match), then ask which level
they want. They know things you don't — whether this site is about to be
deployed, whether they care about a footer string moving. Skip the question
only if they already said (e.g. "just bump it", "do the full check").

- **A — Rebuild check** (~1 min). Move the pointer, `hugo --baseURL /`,
  confirm no `ERROR`/`WARN`, commit. Confirms it compiles; does not tell
  you what changed in the output. Right for docs-only bumps and for
  "I'll see it when I look at the site."
- **B — Verified update** (~5 min). Rebuild check plus the golden-master
  diff: baseline before moving the pointer, `compare.sh` after, and
  confirm every remaining diff is explained. Right when a handful of
  output-affecting files changed and you want to know *exactly* what moved.
- **C — Full validation.** The guide's complete routine: full pre-flight
  (including the repeat-build non-determinism check), golden-master loop,
  local-override scan, deprecation checker, config-param grep. Right when
  crossing a tag boundary, many versions, or anything the changelog marks
  as a required migration.

**Escalate regardless of what was asked** — say why, then do C — if any of
these is true:

- Local `hugo version` differs from CI's pinned `HUGO_VERSION`, or this
  bump crosses a Hugo minor-version boundary. Hugo-version drift is
  open-ended in a way theme changes aren't, and the guide's pre-flight
  exists mostly for it.
- A changelog entry between the two commits is marked **REQUIRED**
  migration, or removes something with no deprecated alias.

If the pin is at or before `pre-unification`, none of the levels apply —
that's the upgrade case. Say so plainly, don't offer level A or B, and
follow the guide's migration path.

**One ordering constraint:** level B's baseline must be captured *before*
the submodule pointer moves. So the level has to be chosen up front. It is
recoverable if you guess low and change your mind — `git checkout <old-sha>`
in the submodule, take the baseline, `git checkout origin/master` again —
but it's friction, so ask before moving anything.

## Step 5: Follow the guide at the chosen level

Follow the "Routine bump" procedure for *this specific site*, executing the
verification steps the chosen level calls for. Treat the guide as
authoritative on **what things mean**: if a diff or build error doesn't
match anything in its changelog, stop and report rather than patching
around it — at any level. A lighter level means checking fewer things, never
lowering the bar for an anomaly you do find.

Don't push or deploy anything — the site's repo or the 559Theme repo —
without explicit sign-off first.

If you find the instructions themselves are unclear, incomplete, or wrong
based on what you actually hit during the bump, that's worth fixing at the
source (`themes/559Theme/docs/upgrading.md`, on a branch, merged to the
theme's `master` with sign-off) — not by silently working around it in just
this one site.
