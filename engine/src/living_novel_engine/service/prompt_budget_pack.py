"""Prompt Budget Pack MVP：检索上下文只读预算打包。"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.browser.validators import safe_id

VERSION = "prompt-budget-pack-mvp"
DEFAULT_CHAR_BUDGET = 1600
MIN_CHAR_BUDGET = 80
MAX_CHAR_BUDGET = 12000

_SOURCE_PRIORITY = {
    "contract": 100,
    "canon_ledger": 90,
    "fact": 85,
    "chapter_brief": 70,
    "volume_brief": 60,
}
_SECTION_LABELS = {
    "contract_constraints": "故事合约约束",
    "canon_facts": "正史事实",
    "chapter_summaries": "相关章节摘要",
    "other_memory": "其他记忆",
}


class PromptBudgetPackRequestError(ValueError):
    """Invalid prompt budget pack request, mapped to HTTP 400."""


def get_prompt_budget_pack(
    run_id: str,
    branch_id: str,
    *,
    char_budget: int = DEFAULT_CHAR_BUDGET,
    outputs_root: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only compressed prompt context pack for one branch."""

    rid = _safe_id(run_id, "run_id")
    bid = _safe_id(branch_id, "branch_id")
    budget = _validate_budget(char_budget)
    root = outputs_root or outputs_dir()
    run_dir = root / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"运行不存在: {rid}")
    branch_dir = run_dir / bid
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {rid}/{bid}")

    retrieval_status, retrieval = _read_json_status(branch_dir / "retrieval_context.json")
    runtime_status, runtime_memory = _read_json_status(
        branch_dir / "runtime_memory_context.json"
    )
    warnings = _warnings(retrieval_status, runtime_status)
    source_items = _source_items(retrieval) if retrieval_status == "ready" else []
    deduped_items = _dedupe_items(source_items)
    packed_items, excluded_items = _pack_items(deduped_items, budget)
    sections = _sections(packed_items)
    prompt_block = _render_prompt_block(sections)
    while len(prompt_block) > budget and packed_items:
        excluded_items.insert(0, _mark_excluded(packed_items.pop(), "超出预算"))
        sections = _sections(packed_items)
        prompt_block = _render_prompt_block(sections)

    status = (
        "blocked"
        if retrieval_status == "damaged"
        else "attention"
        if warnings or excluded_items
        else "ready"
    )
    return {
        "version": VERSION,
        "mode": "read_only_prompt_budget_pack",
        "status": status,
        "run_id": rid,
        "branch_id": bid,
        "summary": {
            "char_budget": budget,
            "source_item_count": len(source_items),
            "deduped_item_count": len(deduped_items),
            "included_item_count": len(packed_items),
            "excluded_item_count": len(excluded_items),
            "estimated_prompt_chars": len(prompt_block),
            "estimated_prompt_tokens": _estimate_tokens(prompt_block),
            "compression_ratio": _compression_ratio(retrieval, prompt_block),
            "writes_artifacts": False,
            "external_services_required": False,
            "uses_vector_store": False,
        },
        "sections": sections,
        "packed_items": packed_items,
        "excluded_items": excluded_items,
        "prompt_block": prompt_block,
        "warnings": warnings,
        "boundaries": [
            "只读读取 retrieval_context.json 与 runtime_memory_context.json。",
            "不调用 embedding、向量库、GraphRAG、Zep、reranker 或真实 LLM。",
            "不写 artifact，不改变现有 prompt_block 注入链路。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_id(value: str, label: str) -> str:
    checked = safe_id(str(value or ""))
    if checked is None:
        raise PromptBudgetPackRequestError(f"invalid {label}")
    return checked


def _validate_budget(value: int) -> int:
    try:
        budget = int(value)
    except (TypeError, ValueError) as exc:
        raise PromptBudgetPackRequestError("invalid char_budget") from exc
    if budget < MIN_CHAR_BUDGET or budget > MAX_CHAR_BUDGET:
        raise PromptBudgetPackRequestError("invalid char_budget")
    return budget


def _read_json_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", {}
    return ("ready", data) if isinstance(data, dict) else ("damaged", {})


def _warnings(retrieval_status: str, runtime_status: str) -> list[str]:
    warnings: list[str] = []
    if retrieval_status == "missing":
        warnings.append("retrieval_context.json 缺失，无法生成检索预算包。")
    elif retrieval_status == "damaged":
        warnings.append("retrieval_context.json 损坏，无法解析检索条目。")
    if runtime_status == "damaged":
        warnings.append("runtime_memory_context.json 损坏，已跳过运行时记忆信号。")
    return warnings


def _source_items(retrieval: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = retrieval.get("items")
    if not isinstance(raw_items, list):
        return []
    items: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            continue
        text = str(raw.get("text") or raw.get("content") or "").strip()
        if not text:
            continue
        source = str(raw.get("source") or raw.get("type") or raw.get("kind") or "other")
        item_id = str(raw.get("id") or f"{source}:{index}")
        score = _num(raw.get("score"))
        section_id = _section_for_source(source)
        char_count = len(text)
        items.append(
            {
                "id": item_id,
                "source": source,
                "section_id": section_id,
                "score": score,
                "priority": _SOURCE_PRIORITY.get(source, 40) + score,
                "text": text,
                "char_count": char_count,
                "estimated_tokens": _estimate_tokens(text),
                "evidence": str(raw.get("evidence") or ""),
            }
        )
    return items


def _dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for item in items:
        key = (item["source"], _normalize_text(item["text"]))
        existing = best.get(key)
        if existing is None or item["priority"] > existing["priority"]:
            best[key] = item
    deduped = list(best.values())
    deduped.sort(key=lambda item: (-item["priority"], item["id"]))
    return deduped


def _pack_items(
    items: list[dict[str, Any]], budget: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packed: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    used = 0
    for item in items:
        overhead = 16
        projected = used + item["char_count"] + overhead
        if projected <= budget:
            packed.append({**item, "included": True, "reason": "优先级与预算内"})
            used = projected
        else:
            excluded.append(_mark_excluded(item, "超出预算"))
    return packed, excluded


def _mark_excluded(item: dict[str, Any], reason: str) -> dict[str, Any]:
    return {**item, "included": False, "reason": reason}


def _sections(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for section_id in (
        "contract_constraints",
        "canon_facts",
        "chapter_summaries",
        "other_memory",
    ):
        section_items = [item for item in items if item["section_id"] == section_id]
        result.append(
            {
                "id": section_id,
                "label": _SECTION_LABELS[section_id],
                "item_count": len(section_items),
                "estimated_chars": sum(item["char_count"] for item in section_items),
                "items": section_items,
            }
        )
    return result


def _render_prompt_block(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        items = section.get("items") or []
        if not items:
            continue
        lines = [f"- {item['text']}" for item in items]
        parts.append(f"【{section['label']}】\n" + "\n".join(lines))
    return "\n\n".join(parts)


def _section_for_source(source: str) -> str:
    if source == "contract":
        return "contract_constraints"
    if source in {"canon_ledger", "fact"}:
        return "canon_facts"
    if source in {"chapter_brief", "volume_brief"}:
        return "chapter_summaries"
    return "other_memory"


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text.strip())


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 2))


def _compression_ratio(retrieval: dict[str, Any], prompt_block: str) -> float:
    original = str(retrieval.get("prompt_block") or "")
    if not original:
        return 1.0 if prompt_block else 0.0
    return round(len(prompt_block) / max(1, len(original)), 3)


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _next_steps(status: str) -> list[str]:
    if status == "blocked":
        return ["先修复 retrieval_context.json，再生成上下文预算包。"]
    if status == "attention":
        return [
            "已有条目被预算排除；可调大预算或补充更精准 query。",
            "如果长期排除关键事实，再评估 reranker 或更强检索。",
        ]
    return [
        "当前检索上下文可在预算内稳定注入。",
        "后续可把该预算包接入 opt-in prompt 编排，不改变默认 runner。",
    ]
