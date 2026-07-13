#!/usr/bin/env python3
"""Migrate legacy `link`/`lnk` shortcode calls to the unified `link` shortcode.

559Theme once had two link shortcodes with a confusingly overloaded second
positional argument:

    {{< link  "page" "anchor" >}}   # old link: 2nd positional = anchor
    {{< lnk   "page" "text"   >}}   # old lnk : 2nd positional = link text

They were unified into a single `link` shortcode that takes NAMED parameters
(and `lnk` was removed). See docs/link-shortcode.md. This script rewrites a
site's content to the new form:

    {{< link "page" >}}                     (one positional arg)  -> unchanged
    {{< link "page" "anchor" >}}                                  -> {{< link page="page" anchor="anchor" >}}
    {{< lnk  "page" >}}                                           -> {{< link page="page" >}}
    {{< lnk  "page" "text" >}}                                    -> {{< link page="page" text="text" >}}

It preserves the delimiter style ({{< >}} vs {{% %}}), is quote-aware
(shlex), skips calls that already use named parameters, and leaves
single-positional `link` calls untouched (they are still valid).

Usage
-----
    # dry run (default): report what WOULD change, touch nothing
    python migrate-links.py <dir> [<dir> ...]

    # apply the rewrite in place
    python migrate-links.py --apply <dir> [<dir> ...]

IMPORTANT — where shortcodes live. Shortcodes are rendered not only from a
site's `content/` tree but also from course *snippet* files pulled in by the
`snippet` shortcode (conventionally `assets/snippets/`). Point this script at
BOTH, e.g.:

    python migrate-links.py --apply  mysite/content  mysite/assets/snippets

Each named directory is scanned recursively for *.md and *.html files.

After running (with --apply), rebuild the site and diff the rendered output
against a pre-migration snapshot. Every difference should be either
whitespace-only or a Last-Modified/pubDate change (editing content updates its
git-based .Lastmod). Any change to actual link text/target/anchor is a bug —
investigate. See docs/link-shortcode.md for the full verification recipe.
"""
import re
import sys
import shlex
import glob
import os
from collections import Counter

CALL = re.compile(r'\{\{(<|%)\s*(link|lnk)\s+(.*?)\s*(>|%)\}\}', re.S)
NAMED = re.compile(r'[A-Za-z_]+\s*=')


def quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def make_replacer(stats, anomalies):
    def repl(m):
        op, sc, args, cl = m.group(1), m.group(2), m.group(3), m.group(4)
        if NAMED.search(args):
            stats['already-named (skipped)'] += 1
            return m.group(0)
        try:
            toks = shlex.split(args)
        except ValueError:
            anomalies.append(('unparseable args', sc, args))
            return m.group(0)
        if sc == 'link':
            if len(toks) <= 1:
                stats['link 1-positional (unchanged)'] += 1
                return m.group(0)
            if len(toks) > 2:
                anomalies.append(('link with >2 positional args (only page+anchor kept)', args))
            new = f'page={quote(toks[0])} anchor={quote(toks[1])}'
            stats['link 2-positional -> page/anchor'] += 1
        else:  # lnk
            if not toks:
                anomalies.append(('lnk with no args', args))
                return m.group(0)
            if len(toks) == 1:
                new = f'page={quote(toks[0])}'
                stats['lnk 1-arg -> link page'] += 1
            else:
                if len(toks) > 2:
                    anomalies.append(('lnk with >2 positional args (only page+text kept)', args))
                new = f'page={quote(toks[0])} text={quote(toks[1])}'
                stats['lnk 2-arg -> link page/text'] += 1
        return '{{' + op + ' link ' + new + ' ' + cl + '}}'
    return repl


def main(argv):
    apply = '--apply' in argv
    dirs = [a for a in argv if not a.startswith('--')]
    if not dirs:
        print(__doc__)
        print('ERROR: name at least one directory to scan '
              '(e.g. a site content/ and assets/snippets/).')
        return 2
    stats = Counter()
    anomalies = []
    repl = make_replacer(stats, anomalies)
    changed = []
    for d in dirs:
        for f in glob.glob(os.path.join(d, '**', '*'), recursive=True):
            if not f.endswith(('.md', '.html')):
                continue
            try:
                txt = open(f, encoding='utf-8').read()
            except (OSError, UnicodeDecodeError):
                continue
            new = CALL.sub(repl, txt)
            if new != txt:
                changed.append(f)
                if apply:
                    open(f, 'w', encoding='utf-8').write(new)

    print('MODE:', 'APPLIED' if apply else 'DRY-RUN (pass --apply to write)')
    for k in sorted(stats):
        print(f'  {k:34} {stats[k]}')
    print(f'  files changed: {len(changed)}')
    if anomalies:
        print('  ANOMALIES — review by hand:')
        for a in anomalies:
            print('    ', a)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
