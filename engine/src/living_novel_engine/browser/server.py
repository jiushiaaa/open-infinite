"""stdlib HTTP server for the read-only worldline browser.

All identifier-shaped URL parameters (``slug`` / ``run_id`` / ``branch_id``)
are routed through :func:`living_novel_engine.browser.validators.safe_id`
before being used to construct filesystem paths. See ``validators.py`` for
the full URL parameter audit table.
"""

from __future__ import annotations

import json
import mimetypes
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from living_novel_engine.browser import indexer
from living_novel_engine.browser.paths import static_dir
from living_novel_engine.browser.validators import safe_id


def _first_qs(qs: dict[str, list[str]], key: str) -> str | None:
    values = qs.get(key)
    if not values:
        return None
    return values[0]


class BrowserHandler(BaseHTTPRequestHandler):
    server_version = "LNE-Browser/0.4"

    def log_message(self, fmt: str, *args: object) -> None:
        pass

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.is_file():
            self.send_error(404)
            return
        content = path.read_bytes()
        mime, _ = mimetypes.guess_type(str(path))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        try:
            if path == "/" or path == "/index.html":
                return self._send_file(static_dir() / "index.html")

            if path.startswith("/static/"):
                rel = path[len("/static/") :]
                target = (static_dir() / rel).resolve()
                base = static_dir().resolve()
                if not str(target).startswith(str(base)):
                    self.send_error(403)
                    return
                return self._send_file(target)

            if path == "/api/stories":
                return self._send_json(
                    {"stories": [asdict(s) for s in indexer.list_stories()]}
                )

            if path.startswith("/api/stories/"):
                slug = safe_id(path.split("/api/stories/", 1)[1].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(indexer.get_story(slug))

            if path == "/api/runs":
                story_raw = _first_qs(qs, "story_slug")
                story = safe_id(story_raw) if story_raw else None
                if story_raw and story is None:
                    return self._send_json({"error": "invalid story_slug"}, status=400)
                runs = indexer.list_runs(story_slug=story)
                return self._send_json({"runs": [asdict(r) for r in runs]})

            if path == "/api/tree":
                story_raw = _first_qs(qs, "story_slug")
                story = safe_id(story_raw) if story_raw else None
                if story_raw and story is None:
                    return self._send_json({"error": "invalid story_slug"}, status=400)
                return self._send_json(
                    {"tree": indexer.build_worldline_tree(story_slug=story)}
                )

            if path.startswith("/api/runs/") and "/branches/" in path:
                rest = path[len("/api/runs/") :]
                run_id_raw, _, branch_part = rest.partition("/branches/")
                run_id = safe_id(run_id_raw.strip("/"))
                branch_id = safe_id(branch_part.strip("/"))
                if run_id is None or branch_id is None:
                    return self._send_json(
                        {"error": "invalid run_id or branch_id"}, status=400
                    )
                return self._send_json(indexer.get_branch(run_id, branch_id))

            if path.startswith("/api/runs/"):
                run_id = safe_id(path.split("/api/runs/", 1)[1].strip("/"))
                if run_id is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._send_json(indexer.get_run(run_id))

            self.send_error(404)
        except FileNotFoundError as exc:
            self._send_json({"error": str(exc)}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


class BrowserServerStartError(RuntimeError):
    """Raised when the browser HTTP server cannot bind (port in use, etc)."""


def start_browser_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    open_browser: bool = True,
) -> ThreadingHTTPServer:
    try:
        httpd = ThreadingHTTPServer((host, port), BrowserHandler)
    except OSError as exc:
        raise BrowserServerStartError(
            f"无法绑定 {host}:{port}（{exc.strerror or exc}）。请检查端口占用或换 --port。"
        ) from exc
    url = f"http://{host}:{port}/"
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    return httpd
