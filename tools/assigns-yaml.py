#!/usr/bin/env python3
"""
Generate a course site's ``data/assigns.yaml`` from Canvas assignments.

Run it from anywhere inside the course repo::

    python themes/559Theme/tools/assigns-yaml.py

The script locates the site root by walking up from the current directory
looking for ``hugo.toml`` (override with ``--site``), reads assignments
through `canvas.Canvas` (which in turn reads `.canvas.yaml` at that same
site root), and writes:

- ``<site>/data/assigns.yaml`` -- the generated data file, consumed by the
  ``assign-link``/``assign-linkonly`` shortcodes. See
  ``docs/data-contracts.md`` for the field-by-field contract.

Pass ``--csv`` to additionally write ``assignments.csv`` to the *current*
directory -- a flat dump of the same assignments for spreadsheet use, not
part of the site's data contract.
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path
from typing import NoReturn

import yaml
from dateutil.parser import isoparse

import canvas

DEFAULT_DATE = datetime.datetime(2024, 1, 1)


def die(message: str) -> NoReturn:
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


def slugify(title: str) -> str:
    return title.replace("–", "-").replace(" - ", "-").replace("?", "").replace(" ", "-").lower()


def parse_due_lock(a: dict, slug: str) -> tuple[datetime.datetime, datetime.datetime]:
    """Parse an assignment's due/lock dates, warning and defaulting when absent.

    `lock` falls back to `due` (matching the documented `assigns.yaml` contract)
    when Canvas has no lock date.
    """
    due = DEFAULT_DATE
    if a["due_at"]:
        due = isoparse(a["due_at"])
    else:
        print("Warning {} has no due date!".format(slug))
    lock = due
    if a["lock_at"]:
        lock = isoparse(a["lock_at"])
    else:
        print("Warning {} has no lock date!".format(slug))
    return due, lock


def assignment_type(a: dict) -> str:
    if "quiz_id" in a:
        return "quiz"
    if "discussion_topic" in a:
        return "discussion"
    return "other"


def build_assigns_yaml(c: canvas.Canvas) -> dict:
    assigns = {}
    for a in c.creq("assignments"):
        slug = slugify(a["name"].split(":")[0].strip())
        due, lock = parse_due_lock(a, slug)
        assigns[slug] = {
            "name": a["name"],
            "shortname": a["name"].split(":")[0],
            "url": a["html_url"],
            "due": "{}".format(due),  # for some reason, YAML doesn't convert?
            "due_string": "{:%a, %b %d}".format(due),
            "lock": "{}".format(lock),
            "lock_string": "{:%a, %b %d}".format(lock),
        }
    return assigns


def write_assigns_yaml(c: canvas.Canvas, site: Path):
    assigns = build_assigns_yaml(c)
    path = site / "data" / "assigns.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fo:
        fo.write(yaml.dump(assigns))
    print("Wrote {} assignments to {}".format(len(assigns), path))


def write_assignments_csv(c: canvas.Canvas, path: Path):
    """Write a flat CSV dump of assignments to `path` (not part of the site's data contract)."""
    cols = ["name", "open", "due", "lock", "group", "type", "points", "allow_liking", "response_needed", "anon"]
    rows = []
    for a in c.creq("assignments"):
        slug = slugify(a["name"].split(":")[0].strip())
        due, lock = parse_due_lock(a, slug)
        kind = assignment_type(a)
        topic = a.get("discussion_topic") or {}
        rows.append({
            "name": a["name"],
            "open": a["unlock_at"],
            "due": "{}".format(due),
            "lock": "{}".format(lock),
            "group": a["assignment_group_id"],
            "type": kind,
            "points": a["points_possible"],
            "allow_liking": topic.get("allow_rating") if kind == "discussion" else None,
            "response_needed": topic.get("require_initial_post") if kind == "discussion" else None,
            "anon": a["anonymize_students"] if kind == "quiz" else None,
        })
    with open(path, "w", newline="") as fo:
        writer = csv.writer(fo)
        writer.writerow(cols)
        for r in rows:
            writer.writerow([r[col] for col in cols])
    print("Wrote {} assignments to {}".format(len(rows), path))


def main():
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    parser.add_argument(
        "--site",
        type=Path,
        help="course site root (default: search upward from the current directory)",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="also write assignments.csv to the current directory",
    )
    args = parser.parse_args()

    site = args.site.resolve() if args.site else find_site_root(Path.cwd().resolve())
    print("site root: {}".format(site))

    c = canvas.Canvas(site=site)
    write_assigns_yaml(c, site)
    if args.csv:
        write_assignments_csv(c, Path.cwd() / "assignments.csv")


if __name__ == "__main__":
    main()
