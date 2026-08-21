#!/usr/bin/env python3
"""
Generate a course site's ``data/readings.yaml`` from a SeaTable base.

SeaTable is the human-curated source of truth for the reading list. Each row
becomes a record keyed by the row's ``Key`` column, holding a pre-formatted
HTML citation under ``html`` plus the individual columns that went into it
(``title``, ``cfile``, ``doi``, ``url``, …). See ``docs/data-contracts.md``
(``readings.yaml``) for the field-by-field contract.

Run it from anywhere inside the course repo::

    python themes/559Theme/tools/seatable-to-readings.py

The script locates the site root by walking up from the current directory
looking for ``hugo.toml`` (override with ``--site``), then reads:

- ``<site>/.canvas.yaml`` — gitignored config holding the SeaTable read-only API
  token (``seatable-readings``) and the table name (``seatable-table``).
- ``<site>/data/files.yaml`` — the Canvas file index, used to turn a row's
  ``cfile`` into a Canvas link. **Must be current**: a ``cfile`` that is not a
  key here renders ``(BAD cfile)`` and warns.

and writes:

- ``<site>/data/readings.yaml`` — the generated data file (consumed by the
  ``reading`` shortcode).
- ``<site>/tmp/readings.html`` — a human-readable preview listing (``tmp/`` is
  gitignored).
"""

import argparse
import sys
from html import escape
from pathlib import Path

import markdown
import yaml
from seatable_api import Base

SERVER_URL = "https://cloud.seatable.io"

# Keys expected in .canvas.yaml
TOKEN_KEY = "seatable-readings"
TABLE_KEY = "seatable-table"

HTML_HEADER = """\
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Readings Listed</title>

</head>

<body>
<ul>
"""

HTML_FOOTER = """\
</ul>
</body>

</html>
"""


def die(message: str):
    """Print an error and exit non-zero."""
    print("error: {}".format(message), file=sys.stderr)
    sys.exit(1)


def find_site_root(start: Path) -> Path:
    """Walk up from `start` looking for the Hugo site root (has hugo.toml)."""
    for candidate in [start, *start.parents]:
        if (candidate / "hugo.toml").is_file():
            return candidate
    die(
        "could not find the site root (no hugo.toml at or above {}). "
        "Run this from inside the course repo, or pass --site.".format(start)
    )


def load_config(site: Path) -> tuple[str, str]:
    """Read the SeaTable token and table name from <site>/.canvas.yaml."""
    path = site / ".canvas.yaml"
    try:
        config = yaml.safe_load(path.read_text()) or {}
    except FileNotFoundError:
        die("no {} — it holds the SeaTable token and is gitignored".format(path))

    missing = [k for k in (TOKEN_KEY, TABLE_KEY) if not config.get(k)]
    if missing:
        die("{} is missing: {}".format(path, ", ".join(missing)))

    return config[TOKEN_KEY], config[TABLE_KEY]


def load_cfiles(site: Path) -> dict:
    """Read the Canvas file index that `cfile` references resolve against."""
    path = site / "data" / "files.yaml"
    try:
        return yaml.safe_load(path.read_text())
    except FileNotFoundError:
        die("the Canvas files list ({}) could not be found".format(path))


def mdToHTML(md: str):
    html = markdown.markdown(md)
    if html.startswith('<p>') and html.endswith('</p>'):
        html = html[3:-4]
    return html.lstrip().rstrip()


def render_row(row: dict, cfiles: dict) -> dict:
    """Render one SeaTable row into its readings.yaml record.

    The record always carries ``html`` — the full pre-rendered citation, which
    is what the ``reading`` shortcode prints. Alongside it sit the individual
    SeaTable columns, so a consumer can reach a single piece (say, just the
    Canvas link) without parsing the HTML. Empty columns are omitted rather
    than written as nulls.

    ``title``/``subtitle`` are markdown-rendered, exactly as they appear inside
    ``html``, so the two never disagree. ``cfile`` is the raw SeaTable filename;
    ``cfile_url`` is that filename resolved through ``files.yaml``, and is
    absent when the reference is bad.
    """
    cite = ""
    rec = {}

    if row["Authors"]:
        cite += "{}. ".format(escape(row["Authors"]))
    if row["Title"]:
        rec["title"] = mdToHTML(row["Title"].rstrip().lstrip())
        cite += "<b>{}</b>. ".format(rec["title"])
    if row["Subtitle"]:
        rec["subtitle"] = mdToHTML(row["Subtitle"])
        cite += "{}. ".format(rec["subtitle"])
    if row["citation"]:
        cite += "{}. ".format(mdToHTML(row["citation"]))
    if row["cfile"]:
        rec["cfile"] = row["cfile"]
        if row["cfile"] in cfiles:
            rec["cfile_url"] = cfiles[row["cfile"]]["url_nodl"]
            cite += "<a href=\"{}\">(Canvas File)</a> ".format(rec["cfile_url"])
        else:
            cite += "(BAD cfile) "
            print("{} has bad cfile {}".format(row["Key"], row["cfile"]))
    if row["doi"]:
        rec["doi"] = row["doi"]
        cite += "<a href=\"{}\">(doi)</a> ".format(row["doi"])
    if row["pdf"]:
        rec["pdf"] = row["pdf"]
        cite += "<a href=\"{}\">(web pdf)</a> ".format(row["pdf"])
    if row["url (web page)"]:
        rec["url"] = row["url (web page)"]
        cite += "<a href=\"{}\">(url)</a> ".format(row["url (web page)"])
    if row["video"]:
        rec["video"] = row["video"]
        cite += "<a href=\"{}\">(video)</a> ".format(row["video"])
    if row["library"]:
        rec["library"] = row["library"]
        cite += "<a href=\"{}\">(UW Library)</a> ".format(row["library"])
    if row["summary"]:
        rec["summary"] = row["summary"]
        cite += "<a href=\"{}\">(Summary)</a> ".format(row["summary"])

    rec["html"] = cite
    return rec


def process_readings(site: Path):
    api_token, table_name = load_config(site)
    cfiles = load_cfiles(site)

    base = Base(api_token, SERVER_URL)
    base.auth()
    rows = base.list_rows(table_name)
    print("Found {} rows in SeaTable table {}\n".format(len(rows), table_name))

    html_out = site / "tmp" / "readings.html"
    html_out.parent.mkdir(parents=True, exist_ok=True)

    with open(html_out, "w") as fo:
        fo.write(HTML_HEADER)
        rd = {}
        for index, row in enumerate(rows):
            if row["Key"]:
                kstr = "<code>[{}]</code>: ".format(row["Key"])
            else:
                print("No Key for {}:{}".format(index, row["Title"]))
                kstr = "[BAD KEY]: "

            rec = render_row(row, cfiles)

            fo.write("<li>{}</li>\n".format(kstr + rec["html"]))
            if row["Key"]:
                rd[row["Key"]] = rec
        fo.write(HTML_FOOTER)

    yaml_out = site / "data" / "readings.yaml"
    with open(yaml_out, "w") as fo:
        yaml.dump(rd, fo)

    print("wrote {} readings to {}".format(len(rd), yaml_out))
    print("wrote preview listing to {}".format(html_out))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--site",
        type=Path,
        help="course site root (default: search upward from the current directory)",
    )
    args = parser.parse_args()

    site = args.site.resolve() if args.site else find_site_root(Path.cwd().resolve())
    print("site root: {}".format(site))
    process_readings(site)


if __name__ == "__main__":
    main()
