# The `link` shortcode

`link` makes an internal link to another page in the site, looked up by its
logical path. It replaced two older shortcodes — `link` (whose second
positional argument was an *anchor*) and `lnk` (whose second positional
argument was the *link text*). That overloaded second positional was
ambiguous, so the unified shortcode takes **named parameters** instead.

## Usage

```text
{{< link "some/page" >}}                          one bare positional arg = the page
{{< link page="some/page" >}}                     named form (page is required)
{{< link page="some/page" anchor="Section" >}}    link to a heading on that page
{{< link page="some/page" text="click me" >}}     custom link text
{{< link link="some/page" >}}                     `link` is accepted as an alias for `page`
```

Parameters:

- **page** (required) — the target page's logical path (as passed to Hugo's
  `.Site.GetPage` / `relref`). `link` is accepted as an alias.
- **anchor** (optional) — a heading on the target page. Sets the URL
  `#fragment` (via `anchorize`). No anchor by default.
- **text** (optional) — the link text. Defaults to the target page's title;
  when an `anchor` is given and `text` is not, the text becomes
  `Title (Anchor)`. Explicit `text` is used verbatim (the anchor still sets
  the `#fragment`).

Only these three named parameters are supported, plus the single-positional
`{{< link "page" >}}` shorthand. Passing **two or more positional arguments is
an error** — that was the ambiguous old form — and produces a build error that
names the file, line, and the correct named-parameter form. Linking to a page
that does not exist is also a build error, again with the source position.

## Migrating a site from the old `link`/`lnk`

Use `tools/migrate-links.py`. It rewrites legacy calls to the new form,
quote-aware and preserving the `{{< >}}` / `{{% %}}` delimiter:

| Old call | New call |
|---|---|
| `{{< link "p" >}}` | *unchanged* (one positional arg is still valid) |
| `{{< link "p" "anc" >}}` | `{{< link page="p" anchor="anc" >}}` |
| `{{< lnk "p" >}}` | `{{< link page="p" >}}` |
| `{{< lnk "p" "txt" >}}` | `{{< link page="p" text="txt" >}}` |

Already-named calls are skipped, so the script is safe to re-run (idempotent).

**Scan `content/` AND `assets/snippets/`.** Shortcodes render not only from a
site's `content/` tree but also from course *snippet* files pulled in by the
`snippet` shortcode (conventionally under `assets/snippets/`). A migration that
scans only `content/` will silently miss snippet calls. (Worse: a two-positional
`link` left in a snippet does **not** raise the usual build error — inside a
`markdownify`-rendered snippet, positional arguments past the first don't parse,
so the call quietly degrades to a page-only link, dropping its anchor. Named
parameters work correctly there, which is another reason to migrate.)

```sh
# dry run first — reports what would change, touches nothing
python themes/559Theme/tools/migrate-links.py  mysite/content  mysite/assets/snippets

# apply
python themes/559Theme/tools/migrate-links.py --apply  mysite/content  mysite/assets/snippets
```

Review any `ANOMALIES` the script reports (e.g. a call with more than two
positional args) by hand.

## Verifying a migration

The migration is designed to be **output-preserving**. Verify it:

1. Before migrating, snapshot the built site (e.g. `tools/baseline.sh` in the
   site repos, or `hugo --baseURL / && cp -R public /tmp/before`).
2. Migrate (`--apply`) and rebuild.
3. Diff the new `public/` against the snapshot.

Expect only these differences, all benign:

- **Whitespace** around links. The old `link` and `lnk` emitted *inconsistent*
  incidental newlines (`link`'s anchor branch had a leading newline; `lnk` had
  a trailing one). The unified shortcode trims consistently. This renders
  identically in a browser except that a former-`lnk` call sitting immediately
  before punctuation loses a spurious space (`Tutorial 1 )` → `Tutorial 1)`) —
  a small improvement. Byte-identical output is impossible precisely because
  the two old shortcodes were mutually inconsistent.
- **`Last-Modified` / RSS `pubDate` dates.** Editing content updates its
  git-based `.Lastmod` (sites here set `enableGitInfo = true`), so dates bump
  to the migration's commit date. On a deliberately frozen/archived site this
  is a reason to migrate its content only when you accept that date bump.

Any change to actual link **text, target, or anchor** is a bug — investigate.
A quick way to separate signal from noise is to compare with whitespace and
dates normalized away; if nothing remains, the migration was clean.
