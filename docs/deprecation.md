# Deprecating theme features

559Theme has consumers **outside this repo** — multiple course webs, the
workbook site family, and future courses. So "no site in the ThemeUpdate
workspace uses X" is **not** evidence that X is safe to delete. Removing a
shortcode/partial that some other consumer still calls would break their build.

Instead we **soft-retire**: keep the feature working, but mark it deprecated and
warn anyone who still uses it. Only after a scan shows no consumer calls it do
we retire it for real.

## How to deprecate a shortcode

Keep the shortcode functional and add two things near the top of its source:

1. A machine-readable marker comment (this is what the checker keys on):

   ```text
   {{/* @deprecated: <one-line reason> [-> <replacement>] */}}
   ```

2. A build-time warning that fires only when the shortcode is actually used:

   ```text
   {{- warnf "559Theme: shortcode %q is deprecated (called from %s) — <reason/replacement>" "<name>" .Position -}}
   ```

`warnf` returns an empty string, so **the rendered HTML is unchanged** — a site
that uses the shortcode builds identically, it just prints one WARN line per
call. Sites that don't use it see nothing. Do not move the file into
`_shortcodes/deprecated/`: Hugo resolves shortcodes by bare name, so a file in
that subdirectory is no longer callable — that is a *removal*, not a
deprecation, and it breaks external consumers.

`_shortcodes/deprecated/` is the **graveyard for the final step** — park a file
there (or delete it) only once the checker below reports zero usage across all
known consumers.

## Checking who still uses deprecated features

```sh
# scan the four in-workspace sites (bare names, resolved against the
# workspace directory that contains 559Theme — NOT your current directory)
conda run -n p314 python tools/check-deprecated.py

# widen to other consumers (recommended before any real removal) — pass
# bare sibling names the same way, or ABSOLUTE paths for anything outside
# that workspace directory; a relative path like "../foo" is resolved
# against the tool's own location, not cwd, so it silently means something
# other than what it looks like
conda run -n p314 python tools/check-deprecated.py \
    765-25 559-sp26 /path/to/other-course-web /path/to/a-workbook
```

The tool lists every `@deprecated`-marked shortcode and its call sites in each
repo, and exits non-zero if any are still in use. Run it against **all** known
consumers — not just this workspace — before retiring anything.

**Scope gap: shortcodes only.** The checker scans `layouts/_shortcodes/` for
the marker comment — it does not look at `layouts/_partials/` at all. A
deprecated *partial* (e.g. the `lunr` sidebar widget, `warnf`-deprecated in
favor of `search` — see `docs/search.md`) is invisible to it: running the
tool reports "No shortcodes are marked @deprecated" even while a real
deprecation warning is live. Track partial/widget deprecations by grepping
consumers directly (e.g. `grep -rn '"lunr"' content/ hugo.toml config.toml`)
until the tool grows a second scan mode for partials.

## Retirement lifecycle

1. **Deprecate** — add the marker + `warnf`; feature keeps working.
2. **Observe** — over a semester or two, `check-deprecated.py` shows who still
   calls it; those consumers migrate to the replacement.
3. **Retire** — once usage is zero across all known consumers, delete the file
   (or move it to `_shortcodes/deprecated/`) and note it in the changelog.
