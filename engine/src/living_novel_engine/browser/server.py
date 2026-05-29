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

            if path.startswith("/api/stories/") and path.endswith("/anchor"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/anchor")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(indexer.get_world_anchor(slug))

            if path == "/api/settings/runtime":
                from living_novel_engine.service import get_runtime_settings

                return self._send_json(get_runtime_settings().as_dict())

            if path.startswith("/api/stories/") and path.endswith("/health"):
                from living_novel_engine.service import check_project_health

                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/health")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(check_project_health(slug).as_dict())

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

            if path.startswith("/api/jobs/"):
                return self._handle_job_get(path)

            self.send_error(404)
        except FileNotFoundError as exc:
            self._send_json({"error": str(exc)}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/interventions":
                return self._handle_intervention()
            if path == "/api/diffs/action":
                return self._handle_diff_action()
            if path == "/api/import-novel":
                return self._handle_import_novel()
            if path == "/api/story-genesis":
                return self._handle_story_genesis()
            if path.startswith("/api/stories/") and path.endswith("/anchor"):
                return self._handle_anchor_update(path)
            if path == "/api/settings/runtime":
                return self._handle_settings_update()
            if path == "/api/settings/runtime/test":
                return self._handle_settings_test()
            if path == "/api/jobs/intervention":
                return self._handle_job_intervention()
            if path == "/api/jobs/import-novel":
                return self._handle_job_import_novel()
            if path == "/api/jobs/story-genesis":
                return self._handle_job_story_genesis()
            self.send_error(404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def _handle_intervention(self) -> None:
        """v0.7 Web Generate Loop：发起一次 intervene，复用 service.run_intervention。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            InterventionRequestError,
            default_mock,
            default_rounds,
            default_runner,
            run_intervention,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        story_raw = str(body.get("story_slug") or "")
        story_slug = safe_id(story_raw)
        if story_raw and story_slug is None:
            return self._send_json({"error": "invalid story_slug"}, status=400)

        # 显式请求参数优先；缺省时回退到运行设置默认值。
        mock = bool(body["mock"]) if "mock" in body else default_mock()
        rounds = int(body["rounds"]) if "rounds" in body else default_rounds()
        runner = str(body["runner_name"]) if body.get("runner_name") else default_runner()

        try:
            result = run_intervention(
                story_slug=story_slug or "",
                target=str(body.get("target") or ""),
                content=str(body.get("content") or ""),
                intervention_type=str(body.get("intervention_type") or "whisper"),
                branches=int(body.get("branches") or 3),
                rounds=rounds,
                mock=mock,
                runner_name=runner,
            )
        except InterventionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)

        # 附带刷新后的世界线树，前端无需二次请求即可定位新分支。
        tree = indexer.build_worldline_tree(story_slug=result.story_slug)
        self._send_json(
            {
                "run_id": result.run_id,
                "branch_ids": result.branch_ids,
                "primary_branch": result.branch_ids[0] if result.branch_ids else None,
                "story_slug": result.story_slug,
                "llm_mock": result.llm_mock,
                "fallback_reason": result.fallback_reason,
                "intervention_compilation": result.compilation.model_dump(mode="json"),
                "tree": tree,
            }
        )

    def _handle_diff_action(self) -> None:
        """v0.7 第三刀：Causal Diff 确立/抹除/回滚，写回 causal_diff.json 状态。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            DiffActionError,
            DiffNotFoundError,
            apply_diff_action,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        run_id = safe_id(str(body.get("run_id") or ""))
        branch_id = safe_id(str(body.get("branch_id") or ""))
        if run_id is None or branch_id is None:
            return self._send_json(
                {"error": "invalid run_id or branch_id"}, status=400
            )
        block_id = body.get("block_id")

        try:
            artifact = apply_diff_action(
                outputs_dir=indexer.outputs_dir(),
                run_id=run_id,
                branch_id=branch_id,
                action=str(body.get("action") or ""),
                block_id=str(block_id) if block_id else None,
            )
        except DiffNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except DiffActionError as exc:
            return self._send_json({"error": str(exc)}, status=400)

        self._send_json({"causal_diff": artifact})

    def _handle_import_novel(self) -> None:
        """v0.7 第五刀：Web 内导入 3-10 章文本，复用 import_novel 流水线。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            ImportRequestError,
            ProjectExistsError,
            default_mock,
            import_novel_from_payload,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        name_raw = str(body.get("name") or "")
        if safe_id(name_raw) is None:
            return self._send_json({"error": "invalid name/slug"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()

        try:
            result = import_novel_from_payload(
                name=name_raw,
                chapters=body.get("chapters") or [],
                genre=str(body.get("genre") or "xianxia"),
                mock=mock,
                force=bool(body.get("force", False)),
                projects_dir=indexer.projects_dir(),
            )
        except ProjectExistsError as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except ImportRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)

        self._send_json(
            {
                "story_slug": result.story_slug,
                "display_name": result.display_name,
                "character_count": result.character_count,
                "chapter_count": result.chapter_count,
                "anchor_chapter_index": result.anchor_chapter_index,
                "extraction_mode": result.extraction_mode,
                "warnings": result.warnings,
                "anchor_hash": f"#/anchor/{result.story_slug}",
            }
        )

    def _handle_story_genesis(self) -> None:
        """v0.7 第六刀：主题创世，复用 service.generate_story 落盘初始项目。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            GenesisProjectExistsError,
            GenesisRequestError,
            default_mock,
            generate_story,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        name_raw = str(body.get("name") or "")
        if safe_id(name_raw) is None:
            return self._send_json({"error": "invalid name/slug"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()

        try:
            result = generate_story(
                name=name_raw,
                premise=str(body.get("premise") or ""),
                genre=str(body.get("genre") or "xianxia"),
                protagonist_hint=str(body.get("protagonist_hint") or ""),
                style_hint=str(body.get("style_hint") or ""),
                mock=mock,
                force=bool(body.get("force", False)),
                projects_dir=indexer.projects_dir(),
            )
        except GenesisProjectExistsError as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except GenesisRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)

        self._send_json(
            {
                "story_slug": result.story_slug,
                "display_name": result.display_name,
                "chapter_count": result.chapter_count,
                "character_count": result.character_count,
                "generation_mode": result.generation_mode,
                "anchor_chapter_index": result.anchor_chapter_index,
                "warnings": result.warnings,
                "anchor_hash": f"#/anchor/{result.story_slug}",
            }
        )

    def _handle_anchor_update(self, path: str) -> None:
        """v0.7 第七刀：世界锚定轻编辑写回（白名单字段 + 备份 + 校验）。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            AnchorReadOnlyError,
            AnchorUpdateError,
            update_world_anchor,
        )

        rest = path[len("/api/stories/") :]
        slug = safe_id(rest[: -len("/anchor")].strip("/"))
        if slug is None:
            return self._send_json({"error": "invalid slug"}, status=400)

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            result = update_world_anchor(slug, body if isinstance(body, dict) else {})
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except (AnchorReadOnlyError, AnchorUpdateError) as exc:
            return self._send_json({"error": str(exc)}, status=400)

        self._send_json(
            {
                "anchor": indexer.get_world_anchor(slug),
                "health": result.health.as_dict(),
                "changed": result.changed,
                "backup": result.backup_dir.name if result.backup_dir else None,
            }
        )

    def _handle_job_get(self, path: str) -> None:
        """v0.7 第九刀：轮询 job 状态。失败 job 也返回 200 + error，不抛 500。"""
        from living_novel_engine.service import JOBS

        job_id = safe_id(path[len("/api/jobs/") :].strip("/"))
        if job_id is None:
            return self._send_json({"error": "invalid job_id"}, status=400)
        rec = JOBS.get(job_id)
        if rec is None:
            return self._send_json({"error": "job not found"}, status=404)
        self._send_json(rec.to_dict())

    def _handle_job_intervention(self) -> None:
        """v0.7 第九刀：异步 intervene，复用 service.run_intervention。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            JOBS,
            default_mock,
            default_rounds,
            default_runner,
            run_intervention,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()
        rounds = int(body["rounds"]) if "rounds" in body else default_rounds()
        runner = str(body["runner_name"]) if body.get("runner_name") else default_runner()
        story_slug = safe_id(str(body.get("story_slug") or "")) or ""
        target = str(body.get("target") or "")
        content = str(body.get("content") or "")
        itype = str(body.get("intervention_type") or "whisper")
        branches = int(body.get("branches") or 3)

        def run(update):
            update(15, "编译干预")
            result = run_intervention(
                story_slug=story_slug,
                target=target,
                content=content,
                intervention_type=itype,
                branches=branches,
                rounds=rounds,
                mock=mock,
                runner_name=runner,
            )
            update(85, "刷新世界线")
            tree = indexer.build_worldline_tree(story_slug=result.story_slug)
            return {
                "run_id": result.run_id,
                "branch_ids": result.branch_ids,
                "primary_branch": result.branch_ids[0] if result.branch_ids else None,
                "story_slug": result.story_slug,
                "llm_mock": result.llm_mock,
                "fallback_reason": result.fallback_reason,
                "intervention_compilation": result.compilation.model_dump(mode="json"),
                "tree": tree,
            }

        rec = JOBS.submit("intervention", run)
        self._send_json({"job_id": rec.job_id, "status": rec.status}, status=202)

    def _handle_job_import_novel(self) -> None:
        """v0.7 第九刀：异步导入，复用 service.import_novel_from_payload。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            JOBS,
            default_mock,
            import_novel_from_payload,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()
        name_raw = str(body.get("name") or "")
        chapters = body.get("chapters") or []
        genre = str(body.get("genre") or "xianxia")
        force = bool(body.get("force", False))

        def run(update):
            update(20, "拆分章节")
            result = import_novel_from_payload(
                name=name_raw,
                chapters=chapters,
                genre=genre,
                mock=mock,
                force=force,
                projects_dir=indexer.projects_dir(),
            )
            update(90, "校验项目")
            return {
                "story_slug": result.story_slug,
                "display_name": result.display_name,
                "character_count": result.character_count,
                "chapter_count": result.chapter_count,
                "anchor_chapter_index": result.anchor_chapter_index,
                "extraction_mode": result.extraction_mode,
                "warnings": result.warnings,
                "anchor_hash": f"#/anchor/{result.story_slug}",
            }

        rec = JOBS.submit("import_novel", run)
        self._send_json({"job_id": rec.job_id, "status": rec.status}, status=202)

    def _handle_job_story_genesis(self) -> None:
        """v0.7 第九刀：异步创世，复用 service.generate_story。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import JOBS, default_mock, generate_story

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()
        name_raw = str(body.get("name") or "")
        premise = str(body.get("premise") or "")
        genre = str(body.get("genre") or "xianxia")
        protagonist = str(body.get("protagonist_hint") or "")
        style = str(body.get("style_hint") or "")
        force = bool(body.get("force", False))

        def run(update):
            update(20, "构思世界")
            result = generate_story(
                name=name_raw,
                premise=premise,
                genre=genre,
                protagonist_hint=protagonist,
                style_hint=style,
                mock=mock,
                force=force,
                projects_dir=indexer.projects_dir(),
            )
            update(90, "校验锚定")
            return {
                "story_slug": result.story_slug,
                "display_name": result.display_name,
                "chapter_count": result.chapter_count,
                "character_count": result.character_count,
                "generation_mode": result.generation_mode,
                "anchor_chapter_index": result.anchor_chapter_index,
                "warnings": result.warnings,
                "anchor_hash": f"#/anchor/{result.story_slug}",
            }

        rec = JOBS.submit("story_genesis", run)
        self._send_json({"job_id": rec.job_id, "status": rec.status}, status=202)

    def _handle_settings_update(self) -> None:
        """v0.7 第八刀：写入运行设置（仅进程环境变量，不落盘/不回显明文）。"""
        from living_novel_engine.service import SettingsError, update_runtime_settings

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            settings = update_runtime_settings(body if isinstance(body, dict) else {})
        except SettingsError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(settings.as_dict())

    def _handle_settings_test(self) -> None:
        """v0.7 第八刀：轻量连通性检查；异常降级，不抛 500。"""
        from living_novel_engine.service import test_connectivity

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            body = {}
        mock = bool(body.get("mock", False)) if isinstance(body, dict) else False
        self._send_json(test_connectivity(mock=mock))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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
