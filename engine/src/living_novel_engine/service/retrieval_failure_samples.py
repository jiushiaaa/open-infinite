"""Retrieval Failure Sample Authoring MVP.

This module lets the local UI append deterministic retrieval failure samples
for later BM25 vs mock embedding evaluation. It never creates embeddings,
never connects to vector stores, and never reads provider secrets.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.project_health import resolve_story_path

VERSION = "retrieval-failure-sample-authoring-mvp"
ARTIFACT_PATH = "memory/retrieval_failure_samples.jsonl"
_EXPECTED_SOURCES = {
    "canon_ledger",
    "runtime_memory",
    "chapter_brief",
    "volume_brief",
    "entity_aliases",
}
_SECRET_MARKERS = (
    "LLM_API_KEY",
    "SEEDREAM_API_KEY",
    "OPENAI_API_KEY",
    "sk-",
    "sd-",
    "secret",
)
_ENTITY_SPLIT_RE = re.compile(r"[,，;；\s]+")


class RetrievalFailureSampleRequestError(ValueError):
    """Invalid retrieval failure sample request, mapped to HTTP 400."""


class RetrievalFailureSampleConflictError(ValueError):
    """Sample append conflict, mapped to HTTP 409."""


def get_retrieval_failure_samples(
    slug: str,
    *,
    projects_dir: Path | None = None,
) -> dict[str, Any]:
    """Return local retrieval failure samples without writing artifacts."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    base = _base_report(sid, source_kind)
    if source_kind == "builtin":
        base["status"] = "builtin_sample"
        base["next_steps"] = ["内置样例只读；请在导入项目中记录失败样本。"]
        return base

    path = project_dir / ARTIFACT_PATH
    status, samples, warnings = _read_samples(path)
    base["status"] = status
    base["samples"] = samples
    base["warnings"] = warnings
    base["summary"] = _summary(samples, writes_artifacts=False)
    base["next_steps"] = _next_steps(status, len(samples))
    return base


def add_retrieval_failure_sample(
    slug: str,
    payload: dict[str, Any],
    *,
    projects_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Append one sanitized sample to memory/retrieval_failure_samples.jsonl."""

    sid = _safe_slug(slug)
    project_dir, source_kind = resolve_story_path(sid, projects_dir)
    if source_kind == "builtin":
        raise RetrievalFailureSampleConflictError("内置样例不可写检索失败样本")
    if not isinstance(payload, dict):
        raise RetrievalFailureSampleRequestError("请求体必须是对象")

    created = now or datetime.now()
    sample = _normalize_sample(
        payload,
        sample_id=f"retrieval-sample-{created.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}",
        created_at=created.isoformat(timespec="seconds"),
    )
    path = project_dir / ARTIFACT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")

    listing = get_retrieval_failure_samples(sid, projects_dir=projects_dir)
    return {
        "version": VERSION,
        "mode": "local_append_retrieval_failure_sample",
        "status": "appended",
        "story_slug": sid,
        "source_kind": source_kind,
        "artifact_path": ARTIFACT_PATH,
        "sample": sample,
        "summary": {
            **listing["summary"],
            "writes_artifacts": True,
        },
        "boundaries": _boundaries(),
        "next_steps": [
            "刷新 Embedding 样本评估，确认该样本属于词面缺口还是记忆缺口。",
            "继续积累换说法失败样本，避免只凭单例接入真实 embedding。",
            "真实向量库、reranker、GraphRAG 或 Zep 仍保持触发式接入。",
        ],
    }


def _safe_slug(slug: str) -> str:
    sid = safe_id(str(slug or ""))
    if sid is None:
        raise RetrievalFailureSampleRequestError("invalid slug")
    return sid


def _base_report(slug: str, source_kind: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "mode": "local_retrieval_failure_sample_authoring",
        "status": "missing",
        "story_slug": slug,
        "source_kind": source_kind,
        "artifact_path": ARTIFACT_PATH,
        "summary": _summary([], writes_artifacts=False),
        "samples": [],
        "sample_schema": {
            "path": ARTIFACT_PATH,
            "required": ["query", "expected_entities"],
            "optional": [
                "expected_item_id",
                "expected_source",
                "reason",
                "current_chapter",
                "actual_top_sources",
            ],
        },
        "warnings": [],
        "boundaries": _boundaries(),
        "next_steps": [],
    }


def _read_samples(path: Path) -> tuple[str, list[dict[str, Any]], list[str]]:
    if not path.exists():
        return "missing", [], []
    samples: list[dict[str, Any]] = []
    warnings: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return "damaged", [], [f"{ARTIFACT_PATH} 读取失败：{exc}"]
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            warnings.append(f"{ARTIFACT_PATH} 第 {index} 行无法解析：{exc}")
            continue
        if not isinstance(data, dict):
            warnings.append(f"{ARTIFACT_PATH} 第 {index} 行不是对象，已跳过。")
            continue
        samples.append(_compact_sample(data))
    return ("damaged" if warnings else "ready"), samples[:50], warnings


def _normalize_sample(
    payload: dict[str, Any],
    *,
    sample_id: str,
    created_at: str,
) -> dict[str, Any]:
    query = _clean_text(payload.get("query"), field="query", max_len=180, required=True)
    expected_entities = _clean_entities(payload.get("expected_entities"))
    expected_source = _clean_choice(
        payload.get("expected_source"),
        allowed=_EXPECTED_SOURCES,
        default="canon_ledger",
        field="expected_source",
    )
    return {
        "schema_version": VERSION,
        "id": sample_id,
        "created_at": created_at,
        "query": query,
        "expected_entities": expected_entities,
        "expected_item_id": _clean_text(
            payload.get("expected_item_id"),
            field="expected_item_id",
            max_len=120,
        ),
        "expected_source": expected_source,
        "reason": _clean_text(payload.get("reason"), field="reason", max_len=220),
        "current_chapter": _clean_chapter(payload.get("current_chapter")),
        "actual_top_sources": _clean_text_list(
            payload.get("actual_top_sources"),
            field="actual_top_sources",
            max_len=80,
            max_items=8,
        ),
    }


def _compact_sample(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(raw.get("id") or "")[:80],
        "created_at": str(raw.get("created_at") or "")[:40],
        "query": str(raw.get("query") or "")[:180],
        "expected_entities": [
            str(item)[:80]
            for item in raw.get("expected_entities", []) or []
            if str(item).strip()
        ][:10],
        "expected_item_id": str(raw.get("expected_item_id") or "")[:120],
        "expected_source": str(raw.get("expected_source") or "canon_ledger")[:80],
        "reason": str(raw.get("reason") or "")[:220],
        "current_chapter": _clean_chapter(raw.get("current_chapter")),
        "actual_top_sources": [
            str(item)[:80]
            for item in raw.get("actual_top_sources", []) or []
            if str(item).strip()
        ][:8],
    }


def _clean_text(
    value: Any,
    *,
    field: str,
    max_len: int,
    required: bool = False,
) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise RetrievalFailureSampleRequestError(f"{field} 不能为空")
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in _SECRET_MARKERS):
        raise RetrievalFailureSampleRequestError(f"{field} 包含疑似密钥内容")
    if len(text) > max_len:
        raise RetrievalFailureSampleRequestError(f"{field} 超过 {max_len} 字符")
    return text


def _clean_entities(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = _ENTITY_SPLIT_RE.split(value)
    elif isinstance(value, list):
        raw_items = [str(item) for item in value]
    else:
        raise RetrievalFailureSampleRequestError("expected_entities 必须是数组或逗号分隔文本")
    cleaned: list[str] = []
    for item in raw_items:
        entity = _clean_text(
            item,
            field="expected_entities",
            max_len=80,
        )
        if entity and entity not in cleaned:
            cleaned.append(entity)
    if not cleaned:
        raise RetrievalFailureSampleRequestError("expected_entities 不能为空")
    if len(cleaned) > 10:
        raise RetrievalFailureSampleRequestError("expected_entities 最多 10 项")
    return cleaned


def _clean_text_list(
    value: Any,
    *,
    field: str,
    max_len: int,
    max_items: int,
) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise RetrievalFailureSampleRequestError(f"{field} 必须是数组")
    cleaned: list[str] = []
    for item in value:
        text = _clean_text(item, field=field, max_len=max_len)
        if text and text not in cleaned:
            cleaned.append(text)
    if len(cleaned) > max_items:
        raise RetrievalFailureSampleRequestError(f"{field} 最多 {max_items} 项")
    return cleaned


def _clean_choice(
    value: Any,
    *,
    allowed: set[str],
    default: str,
    field: str,
) -> str:
    if value in (None, ""):
        return default
    choice = str(value).strip()
    if choice not in allowed:
        raise RetrievalFailureSampleRequestError(f"{field} 不支持: {choice}")
    return choice


def _clean_chapter(value: Any) -> int:
    if value in (None, ""):
        return 1
    try:
        chapter = int(value)
    except (TypeError, ValueError):
        raise RetrievalFailureSampleRequestError("current_chapter 必须是整数")
    if chapter < 1 or chapter > 9999:
        raise RetrievalFailureSampleRequestError("current_chapter 超出范围")
    return chapter


def _summary(samples: list[dict[str, Any]], *, writes_artifacts: bool) -> dict[str, Any]:
    invalid = sum(
        1
        for sample in samples
        if not sample.get("query") or not sample.get("expected_entities")
    )
    return {
        "sample_count": len(samples),
        "invalid_sample_count": invalid,
        "write_policy": "append_only_jsonl_opt_in",
        "writes_artifacts": writes_artifacts,
        "external_services_required": False,
        "uses_embedding_provider": False,
        "uses_vector_store": False,
        "plaintext_key_returned": False,
    }


def _boundaries() -> list[str]:
    return [
        "仅追加本地 retrieval_failure_samples.jsonl。",
        "不生成 embedding，不创建向量索引，不连接向量库或 reranker。",
        "不读取、不返回也不记录明文 API Key。",
        "不替换 retrieve_context，不改变 run_scene 默认行为。",
    ]


def _next_steps(status: str, sample_count: int) -> list[str]:
    if status == "damaged":
        return ["先修复 JSONL 损坏行，再继续记录新样本。"]
    if sample_count == 0:
        return [
            "从工作台记录换说法召回失败样本。",
            "刷新 Embedding 样本评估，确认是否形成 lexical_gap。",
        ]
    return [
        "刷新 Embedding 样本评估，观察 BM25 与 mock 语义命中的差异。",
        "样本数量稳定后再决定是否进入真实 embedding spike。",
    ]
