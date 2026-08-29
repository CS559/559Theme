#!/usr/bin/env python3
"""
Generate a course site's ``data/files.yaml`` from the Canvas file index.

Run it from anywhere inside the course repo::

    python themes/559Theme/tools/files-yaml.py

The script locates the site root by walking up from the current directory
looking for ``hugo.toml`` (override with ``--site``), reads files and
folders through `canvas.Canvas` (which in turn reads `.canvas.yaml` at
that same site root), and writes:

- ``<site>/data/files.yaml`` -- the generated data file. See
  ``docs/data-contracts.md`` for the field-by-field contract. Files in
  IGNORE_FOLDERS are skipped; a filename that appears more than once
  prints a warning (the last one encountered wins).
"""

import argparse
import datetime
import sys
from pathlib import Path

import yaml
from dateutil.parser import isoparse

import canvas

IGNORE_FOLDERS = {"LectureNotes-2021"}


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


def build_files_yaml(c: canvas.Canvas, ignore_folders: set = IGNORE_FOLDERS) -> dict:
    folders_by_id = {f["id"]: f for f in c.creq("folders")}

    files = {}
    for f in c.creq("files"):
        name = f["filename"]
        folder = folders_by_id.get(f["folder_id"])
        if folder and folder["name"] in ignore_folders:
            continue

        if name in files:
            print("Warning: {} appears twice!".format(name))
            print("   folder was:", files[name]["folder_path"])
            print("   folder will be:", folder["full_name"] if folder else "/")

        files[name] = {
            "url": f["url"],
            "url_nodl": f["url"].split("download?")[0],
            "filename": name,
            "size": f["size"],
            "size_str": "{:.1f}mb".format(f["size"] / 1000000.0),
            "updated": isoparse(f["updated_at"]).isoformat(),
            "folder": folder["name"] if folder else "/",
            "folder_path": folder["full_name"] if folder else "/",
        }
    return files


def write_files_yaml(c: canvas.Canvas, site: Path):
    files = build_files_yaml(c)
    path = site / "data" / "files.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fo:
        fo.write("# Fetched from Canvas {}\n".format(
            datetime.datetime.now().strftime("%b %d, %Y - %I:%M%p")))
        fo.write(yaml.dump(files))
    print("Wrote {} files to {}".format(len(files), path))


def main():
    parser = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n")[0])
    parser.add_argument(
        "--site",
        type=Path,
        help="course site root (default: search upward from the current directory)",
    )
    args = parser.parse_args()

    site = args.site.resolve() if args.site else find_site_root(Path.cwd().resolve())
    print("site root: {}".format(site))

    c = canvas.Canvas(site=site)
    write_files_yaml(c, site)


if __name__ == "__main__":
    main()
