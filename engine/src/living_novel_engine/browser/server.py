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
from urllib.parse import parse_qs, unquote, urlparse

from living_novel_engine.browser import indexer
from living_novel_engine.browser.paths import static_dir
from living_novel_engine.browser.validators import safe_id

mimetypes.add_type("image/webp", ".webp")


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

    def _extract_run_branch_for_suffix(
        self, path: str, suffix: str
    ) -> tuple[str | None, str | None]:
        rest = path[len("/api/runs/") :]
        run_id_raw, _, branch_part = rest.partition("/branches/")
        run_id = safe_id(run_id_raw.strip("/"))
        branch_raw = branch_part[: -len(suffix)].strip("/")
        branch_id = safe_id(branch_raw)
        return run_id, branch_id

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

            if path.startswith("/api/stories/") and path.endswith("/project-workspace"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/project-workspace")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(indexer.get_project_workspace(slug))

            if path.startswith("/api/stories/") and path.endswith(
                "/graph-memory-evaluation"
            ):
                from living_novel_engine.service import evaluate_graph_memory_trigger

                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/graph-memory-evaluation")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(evaluate_graph_memory_trigger(slug))

            if path.startswith("/api/stories/") and path.endswith("/retrieval-probes"):
                from living_novel_engine.service import evaluate_retrieval_probes

                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/retrieval-probes")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(evaluate_retrieval_probes(slug))

            if path.startswith("/api/stories/") and path.endswith(
                "/creation-loop-closeout"
            ):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/creation-loop-closeout")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                workspace = indexer.get_project_workspace(slug)
                creation_loop = workspace.get("creation_loop") or {}
                closeout = creation_loop.get("closeout")
                completion = creation_loop.get("completion") or {}
                return self._send_json(
                    {
                        "story_slug": slug,
                        "version": "v0.9.0-alpha",
                        "completion_status": completion.get("status") or "unknown",
                        "actions": completion.get("actions") or [],
                        "closeout": closeout,
                    }
                )

            if path.startswith("/api/stories/") and path.endswith("/selected-worldline"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/selected-worldline")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_selected_worldline_get(slug)

            if path.startswith("/api/stories/") and path.endswith("/replay-audit"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/replay-audit")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(indexer.get_replay_audit_workspace(slug))

            if path.startswith("/api/stories/") and path.endswith("/anchor"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/anchor")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(indexer.get_world_anchor(slug))

            if (
                path.startswith("/api/stories/")
                and "/characters/" in path
                and path.endswith("/probe")
            ):
                return self._handle_character_probe(path, qs)

            if path == "/api/settings/runtime":
                from living_novel_engine.service import get_runtime_settings

                return self._send_json(get_runtime_settings().as_dict())

            if path == "/api/settings/providers":
                from living_novel_engine.service import get_provider_gateway_summary

                return self._send_json(get_provider_gateway_summary())

            if path == "/api/settings/provider-usage":
                from living_novel_engine.service import get_provider_usage_summary

                story_raw = _first_qs(qs, "story_slug")
                story = safe_id(story_raw) if story_raw else None
                if story_raw and story is None:
                    return self._send_json({"error": "invalid story_slug"}, status=400)
                return self._send_json(get_provider_usage_summary(story_slug=story))

            if path.startswith("/api/stories/") and path.endswith("/health"):
                from living_novel_engine.service import check_project_health

                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/health")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._send_json(check_project_health(slug).as_dict())

            if path.startswith("/api/stories/") and path.endswith("/visual-assets"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/visual-assets")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_visual_assets_get(slug)

            if path.startswith("/api/stories/") and "/assets/" in path:
                return self._handle_asset_file(path)

            if path.startswith("/api/stories/") and path.endswith("/canon/holdout"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/canon/holdout")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_holdout_get(slug)

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

            if path.startswith("/api/runs/") and path.endswith("/baseline"):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/baseline")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_baseline_get(rid)

            if path.startswith("/api/runs/") and path.endswith("/canon-replay"):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/canon-replay")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_canon_replay_get(rid)

            if path.startswith("/api/runs/") and path.endswith("/emergence-nodes"):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/emergence-nodes")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_emergence_nodes_get(rid)

            if path.startswith("/api/runs/") and path.endswith(
                "/state-execution-report"
            ):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/state-execution-report")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_state_execution_get(rid)

            if (
                path.startswith("/api/runs/")
                and "/branches/" in path
                and path.endswith("/worldline-judgement")
            ):
                run_id, branch_id = self._extract_run_branch_for_suffix(
                    path, "/worldline-judgement"
                )
                if run_id is None or branch_id is None:
                    return self._send_json(
                        {"error": "invalid run_id or branch_id"}, status=400
                    )
                return self._handle_worldline_judgement_get(run_id, branch_id)

            if (
                path.startswith("/api/runs/")
                and "/branches/" in path
                and path.endswith("/chapter-export")
            ):
                run_id, branch_id = self._extract_run_branch_for_suffix(
                    path, "/chapter-export"
                )
                if run_id is None or branch_id is None:
                    return self._send_json(
                        {"error": "invalid run_id or branch_id"}, status=400
                    )
                return self._handle_chapter_export_get(run_id, branch_id)

            if (
                path.startswith("/api/runs/")
                and "/branches/" in path
                and path.endswith("/chapter-collection-export")
            ):
                run_id, branch_id = self._extract_run_branch_for_suffix(
                    path, "/chapter-collection-export"
                )
                if run_id is None or branch_id is None:
                    return self._send_json(
                        {"error": "invalid run_id or branch_id"}, status=400
                    )
                return self._handle_chapter_collection_export_get(run_id, branch_id)

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

            if path.startswith("/api/ingest-sessions/"):
                return self._handle_ingest_session_get(path)

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
            if path == "/api/interventions/guardrail":
                return self._handle_guardrail()
            if path == "/api/diffs/action":
                return self._handle_diff_action()
            if path == "/api/import-novel":
                return self._handle_import_novel()
            if path == "/api/story-genesis":
                return self._handle_story_genesis()
            if path.startswith("/api/stories/") and path.endswith(
                "/visual-assets/generate"
            ):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/visual-assets/generate")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_visual_assets_generate(slug)
            if path.startswith("/api/stories/") and path.endswith("/baseline"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/baseline")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_baseline_generate(slug)
            if path.startswith("/api/stories/") and path.endswith("/canon/holdout"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/canon/holdout")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_holdout_write(slug)
            if path.startswith("/api/stories/") and path.endswith("/canon/replay-range"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/canon/replay-range")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_canon_replay_range_run(slug)
            if path.startswith("/api/stories/") and path.endswith("/canon/replay"):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/canon/replay")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_canon_replay_run(slug)
            if path.startswith("/api/runs/") and path.endswith("/emergence-nodes"):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/emergence-nodes")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_emergence_nodes_run(rid)
            if path.startswith("/api/runs/") and path.endswith(
                "/state-execution-evaluate"
            ):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/state-execution-evaluate")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_state_execution_run(rid)
            if path.startswith("/api/runs/") and path.endswith(
                "/state-execution-apply"
            ):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/state-execution-apply")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_state_execution_apply(rid)
            if path.startswith("/api/runs/") and path.endswith(
                "/state-execution-rollback"
            ):
                rest = path[len("/api/runs/") :]
                rid = safe_id(rest[: -len("/state-execution-rollback")].strip("/"))
                if rid is None:
                    return self._send_json({"error": "invalid run_id"}, status=400)
                return self._handle_state_execution_rollback(rid)
            if (
                path.startswith("/api/runs/")
                and "/branches/" in path
                and path.endswith("/worldline-judgement")
            ):
                run_id, branch_id = self._extract_run_branch_for_suffix(
                    path, "/worldline-judgement"
                )
                if run_id is None or branch_id is None:
                    return self._send_json(
                        {"error": "invalid run_id or branch_id"}, status=400
                    )
                return self._handle_worldline_judgement_run(run_id, branch_id)
            if path.startswith("/api/stories/") and path.endswith("/master-setting"):
                return self._handle_master_setting_update(path)
            if path.startswith("/api/stories/") and path.endswith("/anchor"):
                return self._handle_anchor_update(path)
            if path == "/api/settings/runtime":
                return self._handle_settings_update()
            if path == "/api/settings/runtime/test":
                return self._handle_settings_test()
            if path == "/api/ingest-sessions":
                return self._handle_ingest_session_create()
            if path.startswith("/api/ingest-sessions/") and path.endswith("/chunks"):
                return self._handle_ingest_chunk_write(path)
            if path.startswith("/api/ingest-sessions/") and path.endswith("/complete"):
                return self._handle_ingest_complete(path)
            if path == "/api/jobs/intervention":
                return self._handle_job_intervention()
            if path == "/api/jobs/resume-continue":
                return self._handle_job_resume_continue()
            if path == "/api/jobs/import-novel":
                return self._handle_job_import_novel()
            if path == "/api/jobs/story-genesis":
                return self._handle_job_story_genesis()
            if path.startswith("/api/stories/") and path.endswith(
                "/selected-worldline"
            ):
                rest = path[len("/api/stories/") :]
                slug = safe_id(rest[: -len("/selected-worldline")].strip("/"))
                if slug is None:
                    return self._send_json({"error": "invalid slug"}, status=400)
                return self._handle_selected_worldline_write(slug)
            self.send_error(404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def _handle_chapter_export_get(self, run_id: str, branch_id: str) -> None:
        """v0.9.0-alpha：导出所选世界线章节为 Markdown payload。"""
        from living_novel_engine.service import (
            ChapterExportRequestError,
            build_chapter_export,
        )

        try:
            export = build_chapter_export(run_id=run_id, branch_id=branch_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except ChapterExportRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(export)

    def _handle_chapter_collection_export_get(
        self,
        run_id: str,
        branch_id: str,
    ) -> None:
        """v0.9.0-alpha：沿父链导出世界线章节合集。"""
        from living_novel_engine.service import (
            ChapterExportRequestError,
            build_chapter_collection_export,
        )

        try:
            export = build_chapter_collection_export(run_id=run_id, branch_id=branch_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except ChapterExportRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(export)

    def _handle_selected_worldline_get(self, slug: str) -> None:
        """v0.9.0-alpha：读取项目已选择的继续世界线。"""
        from living_novel_engine.service import (
            WorldlineSelectionRequestError,
            get_selected_worldline,
        )

        try:
            selection = get_selected_worldline(slug)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except WorldlineSelectionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json({"selection": selection})

    def _handle_selected_worldline_write(self, slug: str) -> None:
        """v0.9.0-alpha：持久化用户选择的继续世界线。"""
        from living_novel_engine.service import (
            WorldlineSelectionRequestError,
            select_worldline,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        run_id = safe_id(str(body.get("run_id") or ""))
        branch_id = safe_id(str(body.get("branch_id") or ""))
        if run_id is None or branch_id is None:
            return self._send_json({"error": "invalid run_id or branch_id"}, status=400)
        try:
            selection = select_worldline(
                story_slug=slug,
                run_id=run_id,
                branch_id=branch_id,
                note=str(body.get("note") or ""),
            )
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except WorldlineSelectionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json({"selection": selection})

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
                "act_director_plan": result.extra.get("act_director_plan"),
                "dynamic_action_registry": result.extra.get("dynamic_action_registry"),
                "emergence_nodes": result.extra.get("emergence_nodes"),
                "tree": tree,
            }
        )

    def _handle_guardrail(self) -> None:
        """v0.7.2：干预护栏预检（独立解释层，不阻断主链路、不发起生成）。"""
        from living_novel_engine.service import (
            GuardrailRequestError,
            check_intervention_guardrail,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        story_raw = str(body.get("story_slug") or "")
        story_slug = safe_id(story_raw)
        if story_slug is None:
            return self._send_json({"error": "invalid story_slug"}, status=400)

        try:
            result = check_intervention_guardrail(
                story_slug=story_slug,
                content=str(body.get("content") or ""),
                target=str(body.get("target") or ""),
                intervention_type=body.get("intervention_type"),
                visibility=str(body.get("visibility") or "target_only"),
                strength=str(body.get("strength") or "soft"),
            )
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except GuardrailRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)

        self._send_json(result.model_dump(mode="json"))

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
                upload=body.get("upload"),
                genre=str(body.get("genre") or "xianxia"),
                mock=mock,
                force=bool(body.get("force", False)),
                long_mode=bool(body.get("long_mode", False)),
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
                "import_report": result.import_report,
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

    def _handle_master_setting_update(self, path: str) -> None:
        """v0.9.2：MasterSetting Lite 白名单轻编辑写回。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            MasterSettingConflictError,
            MasterSettingReadOnlyError,
            MasterSettingUpdateError,
            update_master_setting,
        )

        rest = path[len("/api/stories/") :]
        slug = safe_id(rest[: -len("/master-setting")].strip("/"))
        if slug is None:
            return self._send_json({"error": "invalid slug"}, status=400)

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            result = update_master_setting(slug, body if isinstance(body, dict) else {})
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except MasterSettingConflictError as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except (MasterSettingReadOnlyError, MasterSettingUpdateError) as exc:
            return self._send_json({"error": str(exc)}, status=400)

        workspace = indexer.get_project_workspace(slug)
        self._send_json(
            {
                "master_setting_workspace": workspace["master_setting_workspace"],
                "changed": result.changed,
                "backup": result.backup_dir.name if result.backup_dir else None,
            }
        )

    def _handle_character_probe(self, path: str, qs: dict[str, list[str]]) -> None:
        """v0.7.2：角色内心探针（只读，deterministic，不调用 LLM）。

        路径：/api/stories/<slug>/characters/<char_id>/probe
        可选 query：run_id / branch_id / intervention_text
        """
        from living_novel_engine.service import ProbeRequestError, probe_character

        rest = path[len("/api/stories/") :]
        slug_raw, _, after = rest.partition("/characters/")
        char_part = after[: -len("/probe")].strip("/")
        slug = safe_id(slug_raw.strip("/"))
        char_id = safe_id(char_part)
        if slug is None or char_id is None:
            return self._send_json(
                {"error": "invalid slug or character id"}, status=400
            )

        run_id_raw = _first_qs(qs, "run_id")
        branch_id_raw = _first_qs(qs, "branch_id")
        run_id = safe_id(run_id_raw) if run_id_raw else None
        branch_id = safe_id(branch_id_raw) if branch_id_raw else None
        if (run_id_raw and run_id is None) or (branch_id_raw and branch_id is None):
            return self._send_json({"error": "invalid run_id or branch_id"}, status=400)

        try:
            probe = probe_character(
                story_slug=slug,
                character_id=char_id,
                run_id=run_id,
                branch_id=branch_id,
                intervention_text=_first_qs(qs, "intervention_text") or "",
            )
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except ProbeRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)

        self._send_json(probe.model_dump(mode="json"))

    def _handle_visual_assets_get(self, slug: str) -> None:
        """v0.7.3：读取项目级视觉资产清单（缺失/损坏安全降级，不 500）。"""
        from living_novel_engine.service import (
            VisualAssetRequestError,
            get_visual_assets,
        )

        try:
            va = get_visual_assets(slug)
        except VisualAssetRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        self._send_json(va.model_dump(mode="json"))

    def _handle_visual_assets_generate(self, slug: str) -> None:
        """v0.7.3：生成视觉资产。无 Key / mock → 占位条目，不打外网、不阻塞。"""
        from living_novel_engine.service import (
            VisualAssetRequestError,
            generate_visual_assets,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        kinds = body.get("kinds")
        if kinds is not None and not isinstance(kinds, list):
            return self._send_json({"error": "kinds 须为数组"}, status=400)
        char_ids = body.get("character_ids")
        if char_ids is not None and not isinstance(char_ids, list):
            return self._send_json({"error": "character_ids 须为数组"}, status=400)

        try:
            va = generate_visual_assets(
                slug,
                kinds=[str(k) for k in kinds] if kinds is not None else None,
                character_ids=[str(c) for c in char_ids]
                if char_ids is not None
                else None,
                force=bool(body.get("force", False)),
                mock=bool(body.get("mock", False)),
            )
        except VisualAssetRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        self._send_json(va.model_dump(mode="json"))

    def _handle_asset_file(self, path: str) -> None:
        """v0.7.3：提供本地生成的视觉资产文件（安全校验路径，禁止穿越）。"""
        from living_novel_engine.service import (
            VisualAssetPathError,
            VisualAssetRequestError,
            resolve_asset_path,
        )

        rest = path[len("/api/stories/") :]
        slug_raw, _, rel = rest.partition("/assets/")
        slug = safe_id(slug_raw.strip("/"))
        if slug is None:
            return self._send_json({"error": "invalid slug"}, status=400)
        rel = unquote(rel)
        try:
            target = resolve_asset_path(slug, rel)
        except VisualAssetRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except VisualAssetPathError:
            return self._send_json({"error": "禁止访问该路径"}, status=403)
        if target is None:
            return self.send_error(404)
        self._send_file(target)

    def _handle_baseline_generate(self, slug: str) -> None:
        """v0.7.4：生成无干预基线世界线（对照组），不改变干预主链路。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            BaselineRequestError,
            default_mock,
            default_rounds,
            default_runner,
            generate_baseline,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        mock = bool(body["mock"]) if "mock" in body else default_mock()
        rounds = int(body["rounds"]) if "rounds" in body else default_rounds()
        runner = str(body["runner_name"]) if body.get("runner_name") else default_runner()
        from_run = body.get("from_run_id")
        from_branch = body.get("from_branch_id")
        from_run = safe_id(str(from_run)) if from_run else None
        from_branch = safe_id(str(from_branch)) if from_branch else None
        if (body.get("from_run_id") and from_run is None) or (
            body.get("from_branch_id") and from_branch is None
        ):
            return self._send_json(
                {"error": "invalid from_run_id or from_branch_id"}, status=400
            )

        try:
            result = generate_baseline(
                story_slug=slug,
                rounds=rounds,
                mock=mock,
                runner_name=runner,
                from_run_id=from_run,
                from_branch_id=from_branch,
            )
        except BaselineRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)

        tree = indexer.build_worldline_tree(story_slug=result.story_slug)
        self._send_json(
            {
                "run_id": result.run_id,
                "branch_id": result.branch_id,
                "story_slug": result.story_slug,
                "summary": result.summary,
                "report": result.report,
                "tree": tree,
            }
        )

    def _handle_baseline_get(self, run_id: str) -> None:
        """v0.7.4：读取 baseline_report.json（不存在 404，损坏 400，不 500）。"""
        from living_novel_engine.service import (
            BaselineRequestError,
            get_baseline_report,
        )

        try:
            report = get_baseline_report(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except BaselineRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_holdout_get(self, slug: str) -> None:
        """v0.7.4：读取正史 holdout manifest（无 holdout → 空 manifest，不 404）。"""
        from living_novel_engine.service import (
            HoldoutRequestError,
            get_holdout,
        )

        try:
            manifest = get_holdout(slug)
        except HoldoutRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        self._send_json(manifest)

    def _handle_holdout_write(self, slug: str) -> None:
        """v0.7.4：写入正史 holdout 章节（builtin 只读 400，重复 409，非法 400）。"""
        from living_novel_engine.service import (
            HoldoutExistsError,
            HoldoutReadOnlyError,
            HoldoutRequestError,
            write_holdout,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            manifest = write_holdout(
                slug,
                chapters=body.get("chapters") or [],
                force=bool(body.get("force", False)),
            )
        except HoldoutReadOnlyError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except HoldoutExistsError as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except HoldoutRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        self._send_json(manifest)

    def _handle_canon_replay_run(self, slug: str) -> None:
        """v0.7.4：运行正史回放评估，写 canon_replay_report.json（deterministic）。"""
        from living_novel_engine.service import (
            ReplayRequestError,
            run_canon_replay,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        baseline_run = safe_id(str(body.get("baseline_run_id") or ""))
        if baseline_run is None:
            return self._send_json({"error": "invalid baseline_run_id"}, status=400)
        baseline_branch_raw = str(body.get("baseline_branch_id") or "baseline")
        baseline_branch = safe_id(baseline_branch_raw)
        if baseline_branch is None:
            return self._send_json({"error": "invalid baseline_branch_id"}, status=400)

        try:
            report = run_canon_replay(
                story_slug=slug,
                baseline_run_id=baseline_run,
                baseline_branch_id=baseline_branch,
                holdout_chapter=int(body.get("holdout_chapter") or 0),
            )
        except ReplayRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)
        self._send_json(report)

    def _handle_canon_replay_range_run(self, slug: str) -> None:
        """v0.8.9：按章节范围运行正史回放，写 range 报告。"""
        from living_novel_engine.service import (
            ReplayRequestError,
            run_canon_replay_range,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        baseline_run = safe_id(str(body.get("baseline_run_id") or ""))
        if baseline_run is None:
            return self._send_json({"error": "invalid baseline_run_id"}, status=400)
        baseline_branch_raw = str(body.get("baseline_branch_id") or "baseline")
        baseline_branch = safe_id(baseline_branch_raw)
        if baseline_branch is None:
            return self._send_json({"error": "invalid baseline_branch_id"}, status=400)

        try:
            report = run_canon_replay_range(
                story_slug=slug,
                baseline_run_id=baseline_run,
                baseline_branch_id=baseline_branch,
                chapter_start=int(body.get("chapter_start") or 0),
                chapter_end=int(body.get("chapter_end") or 0),
            )
        except ReplayRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except (TypeError, ValueError) as exc:
            return self._send_json({"error": f"参数错误：{exc}"}, status=400)
        self._send_json(report)

    def _handle_canon_replay_get(self, run_id: str) -> None:
        """v0.7.4：读取 canon_replay_report.json（不存在 404，损坏 400，不 500）。"""
        from living_novel_engine.service import (
            ReplayRequestError,
            get_canon_replay_report,
        )

        try:
            report = get_canon_replay_report(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except ReplayRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_worldline_judgement_run(self, run_id: str, branch_id: str) -> None:
        """v0.7.5：生成世界线评审报告（deterministic，不打 LLM）。"""
        from living_novel_engine.service import (
            WorldlineJudgeRequestError,
            judge_worldline,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)
        story_slug_raw = body.get("story_slug") if isinstance(body, dict) else None
        story_slug = safe_id(str(story_slug_raw)) if story_slug_raw else None
        if story_slug_raw and story_slug is None:
            return self._send_json({"error": "invalid story_slug"}, status=400)

        try:
            report = judge_worldline(
                run_id=run_id, branch_id=branch_id, story_slug=story_slug
            )
        except WorldlineJudgeRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        self._send_json(report)

    def _handle_worldline_judgement_get(self, run_id: str, branch_id: str) -> None:
        """v0.7.5：读取 worldline_judgement.json（不存在 404，损坏 400，不 500）。"""
        from living_novel_engine.service import (
            WorldlineJudgeRequestError,
            get_worldline_judgement,
        )

        try:
            report = get_worldline_judgement(run_id, branch_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except WorldlineJudgeRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_emergence_nodes_run(self, run_id: str) -> None:
        """v0.8+：重新挖掘 run 级 emergence_nodes.json。"""
        from living_novel_engine.service import (
            EmergenceMiningRequestError,
            mine_run_emergence,
        )

        try:
            report = mine_run_emergence(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except EmergenceMiningRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_emergence_nodes_get(self, run_id: str) -> None:
        """v0.8+：读取 emergence_nodes.json（不存在 404，损坏 400，不 500）。"""
        from living_novel_engine.service import (
            EmergenceMiningRequestError,
            get_emergence_nodes,
        )

        try:
            report = get_emergence_nodes(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except EmergenceMiningRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_state_execution_run(self, run_id: str) -> None:
        """v0.8.10-A：生成 opt-in dry-run 状态执行评估报告。"""
        from living_novel_engine.service import (
            RunnerStateExecutionConflict,
            RunnerStateExecutionRequestError,
            evaluate_runner_state_execution,
        )

        try:
            report = evaluate_runner_state_execution(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except RunnerStateExecutionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except RunnerStateExecutionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_state_execution_get(self, run_id: str) -> None:
        """v0.8.10-A：读取状态执行评估报告（不存在 404，损坏 400）。"""
        from living_novel_engine.service import (
            RunnerStateExecutionRequestError,
            get_runner_state_execution_report,
        )

        try:
            report = get_runner_state_execution_report(run_id)
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except RunnerStateExecutionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_state_execution_apply(self, run_id: str) -> None:
        """v0.8.10-B：显式确认后写入可回滚的状态 overlay。"""
        from living_novel_engine.service import (
            RunnerStateExecutionConflict,
            RunnerStateExecutionRequestError,
            apply_runner_state_execution,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)
        candidate_ids = body.get("candidate_ids") if isinstance(body, dict) else None
        if candidate_ids is not None and not isinstance(candidate_ids, list):
            return self._send_json({"error": "candidate_ids 必须是数组"}, status=400)
        try:
            report = apply_runner_state_execution(
                run_id,
                confirm=bool(body.get("confirm")) if isinstance(body, dict) else False,
                candidate_ids=[
                    str(item) for item in candidate_ids
                ] if isinstance(candidate_ids, list) else None,
            )
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except RunnerStateExecutionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)
        except RunnerStateExecutionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _handle_state_execution_rollback(self, run_id: str) -> None:
        """v0.8.10-B：移除状态 overlay，原 state_snapshot 不变。"""
        from living_novel_engine.service import (
            RunnerStateExecutionRequestError,
            rollback_runner_state_execution,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)
        try:
            report = rollback_runner_state_execution(
                run_id,
                confirm=bool(body.get("confirm")) if isinstance(body, dict) else False,
            )
        except FileNotFoundError as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except RunnerStateExecutionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        self._send_json(report)

    def _extract_ingest_session_id(self, path: str, suffix: str = "") -> str | None:
        rest = path[len("/api/ingest-sessions/") :]
        if suffix:
            rest = rest[: -len(suffix)]
        return safe_id(rest.strip("/"))

    def _handle_ingest_session_create(self) -> None:
        """v0.8.7：创建可恢复长篇导入上传 session。"""
        from living_novel_engine.service import (
            IngestSessionConflict,
            IngestSessionRequestError,
            create_ingest_session,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            summary = create_ingest_session(
                name=str(body.get("name") or ""),
                filename=str(body.get("filename") or ""),
                total_size=body.get("total_size"),
                chunk_size=body.get("chunk_size"),
                total_chunks=body.get("total_chunks"),
                file_sha256=str(body.get("file_sha256") or ""),
                genre=str(body.get("genre") or "xianxia"),
                mock=bool(body.get("mock", True)),
                force=bool(body.get("force", False)),
                long_mode=bool(body.get("long_mode", True)),
            )
        except IngestSessionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except IngestSessionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)
        self._send_json(summary, status=201)

    def _handle_ingest_session_get(self, path: str) -> None:
        """v0.8.7：读取 session manifest，供刷新后恢复缺失分片。"""
        from living_novel_engine.service import (
            IngestSessionConflict,
            IngestSessionNotFound,
            IngestSessionRequestError,
            get_ingest_session,
        )

        session_id = self._extract_ingest_session_id(path)
        if session_id is None:
            return self._send_json({"error": "invalid ingest session id"}, status=400)
        try:
            summary = get_ingest_session(session_id)
        except IngestSessionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except IngestSessionNotFound as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except IngestSessionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)
        self._send_json(summary)

    def _handle_ingest_chunk_write(self, path: str) -> None:
        """v0.8.7：写入单个分片；重复同内容 chunk 幂等返回 duplicate。"""
        from living_novel_engine.service import (
            IngestSessionConflict,
            IngestSessionNotFound,
            IngestSessionRequestError,
            write_ingest_chunk,
        )

        session_id = self._extract_ingest_session_id(path, "/chunks")
        if session_id is None:
            return self._send_json({"error": "invalid ingest session id"}, status=400)
        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            summary = write_ingest_chunk(
                session_id,
                index=body.get("index"),
                data_b64=str(body.get("data_b64") or ""),
                sha256=str(body.get("sha256") or ""),
            )
        except IngestSessionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except IngestSessionNotFound as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except IngestSessionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)
        self._send_json(summary)

    def _handle_ingest_complete(self, path: str) -> None:
        """v0.8.7：合并 session 分片并提交既有 import_novel job。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            JOBS,
            IngestSessionConflict,
            IngestSessionNotFound,
            IngestSessionRequestError,
            build_upload_from_session,
            import_novel_from_payload,
            import_request_from_session,
            mark_ingest_session_imported,
        )

        session_id = self._extract_ingest_session_id(path, "/complete")
        if session_id is None:
            return self._send_json({"error": "invalid ingest session id"}, status=400)
        try:
            self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        try:
            upload = build_upload_from_session(session_id)
            req = import_request_from_session(session_id)
        except IngestSessionRequestError as exc:
            return self._send_json({"error": str(exc)}, status=400)
        except IngestSessionNotFound as exc:
            return self._send_json({"error": str(exc)}, status=404)
        except IngestSessionConflict as exc:
            return self._send_json({"error": str(exc)}, status=409)

        def run(update):
            update(15, "合并分片")
            result = import_novel_from_payload(
                name=str(req.get("name") or ""),
                chapters=[],
                upload=upload,
                genre=str(req.get("genre") or "xianxia"),
                mock=bool(req.get("mock", True)),
                force=bool(req.get("force", False)),
                long_mode=bool(req.get("long_mode", True)),
                projects_dir=indexer.projects_dir(),
            )
            mark_ingest_session_imported(session_id)
            update(90, "校验项目")
            return {
                "story_slug": result.story_slug,
                "display_name": result.display_name,
                "character_count": result.character_count,
                "chapter_count": result.chapter_count,
                "anchor_chapter_index": result.anchor_chapter_index,
                "extraction_mode": result.extraction_mode,
                "warnings": result.warnings,
                "import_report": result.import_report,
                "anchor_hash": f"#/anchor/{result.story_slug}",
                "ingest_session_id": session_id,
            }

        rec = JOBS.submit("import_novel", run)
        self._send_json({"job_id": rec.job_id, "status": rec.status}, status=202)

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

    def _handle_job_resume_continue(self) -> None:
        """v0.9.0-alpha：异步续写所选世界线到 linear 分支。"""
        from living_novel_engine.browser import indexer
        from living_novel_engine.service import (
            JOBS,
            default_mock,
            default_rounds,
            default_runner,
            run_resume_continue,
        )

        try:
            body = self._read_body_json()
        except (ValueError, json.JSONDecodeError):
            return self._send_json({"error": "请求体不是合法 JSON"}, status=400)

        run_id = safe_id(str(body.get("run_id") or ""))
        branch_id = safe_id(str(body.get("branch_id") or ""))
        if run_id is None or branch_id is None:
            return self._send_json({"error": "invalid run_id or branch_id"}, status=400)
        try:
            rounds = int(body["rounds"]) if "rounds" in body else default_rounds()
        except (TypeError, ValueError):
            return self._send_json({"error": "rounds 必须为整数"}, status=400)
        mock = bool(body["mock"]) if "mock" in body else default_mock()
        runner = str(body["runner_name"]) if body.get("runner_name") else default_runner()

        def run(update):
            update(15, "读取父世界线")
            result = run_resume_continue(
                run_id=run_id,
                branch_id=branch_id,
                rounds=rounds,
                mock=mock,
                runner_name=runner,
            )
            update(85, "刷新世界线")
            tree = indexer.build_worldline_tree(story_slug=result.story_slug)
            return {
                "run_id": result.run_id,
                "branch_id": result.branch_id,
                "story_slug": result.story_slug,
                "source_kind": result.source_kind,
                "parent_run_id": result.parent_run_id,
                "parent_branch_id": result.parent_branch_id,
                "chapter_number": result.chapter_number,
                "llm_mock": result.llm_mock,
                "fallback_reason": result.fallback_reason,
                "tree": tree,
            }

        rec = JOBS.submit("resume_continue", run)
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
        upload = body.get("upload")
        genre = str(body.get("genre") or "xianxia")
        force = bool(body.get("force", False))
        long_mode = bool(body.get("long_mode", False))

        def run(update):
            update(20, "拆分章节")
            result = import_novel_from_payload(
                name=name_raw,
                chapters=chapters,
                upload=upload,
                genre=genre,
                mock=mock,
                force=force,
                long_mode=long_mode,
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
                "import_report": result.import_report,
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


class BrowserHTTPServer(ThreadingHTTPServer):
    """Threaded browser server tuned for short-lived pytest fixtures."""

    daemon_threads = True
    block_on_close = False


def start_browser_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    *,
    open_browser: bool = True,
) -> ThreadingHTTPServer:
    try:
        httpd = BrowserHTTPServer((host, port), BrowserHandler)
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
