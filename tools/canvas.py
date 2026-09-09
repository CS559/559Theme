"""
Thin wrapper around the Canvas LMS REST API (v1).

External code should only need the `Canvas` class::

    from canvas import Canvas
    c = Canvas()
    assignments = c.creq("assignments")

Configuration (server, token, course, staff) is read from a gitignored
``.canvas.yaml`` the first time a `Canvas` is constructed without those
values passed explicitly - there is no module-level config or state.
The site root is located the same way as ``seatable-to-readings.py``:
walk up from the current directory looking for ``hugo.toml`` (or pass
`site` to use an explicit root instead of searching).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests
import yaml

CONFIG_FILENAME = ".canvas.yaml"


class CanvasConfigError(Exception):
    """Raised when `.canvas.yaml` can't be found or is missing required keys."""


def _find_site_root(start: Path) -> Path:
    """Walk up from `start` looking for the Hugo site root (has hugo.toml)."""
    for candidate in [start, *start.parents]:
        if (candidate / "hugo.toml").is_file():
            return candidate
    raise CanvasConfigError(
        "could not find the site root (no hugo.toml at or above {}). "
        "Run from inside the course repo, or pass `site` explicitly.".format(start)
    )


def _load_config(site: Path) -> dict[str, Any]:
    """Read server/token/course/staff from <site>/.canvas.yaml."""
    path = site / CONFIG_FILENAME
    try:
        config = yaml.safe_load(path.read_text()) or {}
    except FileNotFoundError:
        raise CanvasConfigError(
            "no {} - it holds the Canvas API token and is gitignored".format(path)
        )

    missing = [k for k in ("server", "token", "course") if not config.get(k)]
    if missing:
        raise CanvasConfigError("{} is missing: {}".format(path, ", ".join(missing)))
    return config


def _build_header(token: str) -> dict[str, str]:
    return {"Authorization": "Bearer {}".format(token)}


def _build_url(server: str, path: str) -> str:
    return "https://{}/api/v1/{}".format(server, path)


def _decode_json(r: requests.Response, path: str):
    try:
        return r.json()
    except ValueError:
        print("JSON decode error for {}: {}".format(path, r))
        return None


def _get_paginated(server: str, token: str, path: str, *, max_pages: int = 250,
                    per_page: int = 100, params: dict | None = None):
    """GET `path`, following Canvas's Link: rel="next" pagination."""
    payload = {"per_page": per_page, **(params or {})}
    start = time.time()
    page = 1
    r = requests.get(_build_url(server, path), headers=_build_header(token), params=payload)
    results = _decode_json(r, path)
    while "next" in r.links and page < max_pages:
        r = requests.get(r.links["next"]["url"], headers=_build_header(token), params=payload)
        page += 1
        page_results = _decode_json(r, path)
        if page_results is not None:
            results = (results or []) + page_results
    if "next" in r.links:
        print("WARNING: Too many pages - hit max_pages limit fetching {}".format(path))
    elapsed = time.time() - start
    if results:
        print("Read {:d} entries from `{}' in {:6.1f}s ({} page{})".format(
            len(results), path, elapsed, page, "" if page == 1 else "s"))
    else:
        print("No results from {}".format(path))
    return results


def _resolve_credentials(server: str | None, token: str | None, course: str | None,
                          staff: str | None, site: Path | str | None) -> tuple[str, str, str, str | None]:
    """Fill in any of server/token/course/staff missing from `.canvas.yaml`."""
    if server is not None and token is not None and course is not None:
        return server, token, course, staff

    root = site if isinstance(site, Path) else _find_site_root(Path(site) if site else Path.cwd())
    config = _load_config(root)
    return (
        server or config["server"],
        token or config["token"],
        course or config["course"],
        staff if staff is not None else config.get("staff"),
    )


class Canvas:
    """A session bound to one (server, token, course) triple.

    Pass server/token/course/staff explicitly, or omit them to read from
    `.canvas.yaml` at the Hugo site root (found by walking up from `site`,
    default the current directory).
    """

    def __init__(self, *, server: str | None = None, token: str | None = None,
                 course: str | None = None, staff: str | None = None,
                 site: Path | str | None = None):
        self.server, self.token, self.course, self.staff = _resolve_credentials(
            server, token, course, staff, site
        )
        self._creq_cache: dict[tuple, Any] = {}

    # ---- basic requests ---------------------------------------------------
    def req(self, path: str, *, params: dict | None = None):
        return _get_paginated(self.server, self.token, path, params=params)

    def _put_or_post(self, method, path: str, data, verbose: bool = False, *, json_data: bool = False):
        url = _build_url(self.server, path)
        if verbose:
            print("URL:", url)
            print("Data({}):".format("json" if json_data else "data"), data)
        kwargs = {"json": data} if json_data else {"data": data}
        r = method(url, headers=_build_header(self.token), **kwargs)
        if verbose:
            print("Got back:", r)
        return r.json()

    def put(self, path: str, *, data=None, verbose: bool = False):
        return self._put_or_post(requests.put, path, data or {}, verbose)

    def post(self, path: str, *, data=None, verbose: bool = False, json_data: bool = False):
        return self._put_or_post(requests.post, path, data or {}, verbose, json_data=json_data)

    def delete(self, path: str, *, verbose: bool = False):
        return self._put_or_post(requests.delete, path, None, verbose)

    # ---- course-scoped requests --------------------------------------------
    def creq(self, path: str, *, params: dict | None = None, no_cache: bool = False):
        """GET `courses/{course}/{path}`, cached per-instance by (path, params)."""
        key = (path, tuple(sorted((params or {}).items())))
        if no_cache or key not in self._creq_cache:
            self._creq_cache[key] = self.req("courses/{}/{}".format(self.course, path), params=params)
        return self._creq_cache[key]

    def cput(self, path: str, data, verbose: bool = False):
        return self.put("courses/{}/{}".format(self.course, path), data=data, verbose=verbose)

    def cpost(self, path: str, data, verbose: bool = False, json_data: bool = False):
        return self.post("courses/{}/{}".format(self.course, path), data=data, verbose=verbose, json_data=json_data)

    def cdelete(self, path: str, verbose: bool = False):
        return self.delete("courses/{}/{}".format(self.course, path), verbose=verbose)

    def idelete(self, kind: str, id_: int | str, verbose: bool = False):
        return self.cdelete("{}/{}".format(kind, id_), verbose=verbose)

    # ---- group-scoped requests ---------------------------------------------
    def greq(self, group_id: int | str, path: str):
        """GET `groups/{group_id}/{path}`."""
        return self.req("groups/{}/{}".format(group_id, path))
