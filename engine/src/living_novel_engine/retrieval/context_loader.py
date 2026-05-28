"""Context Loader — 从 projects/<slug>/ 加载检索语料。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class FactItem:
    id: str
    chapter: int
    type: str
    subject: str
    text: str
    object: str = ""
    evidence: str = ""


@dataclass
class SummaryItem:
    chapter: int
    title: str
    summary: str
    key_events: list[str] = field(default_factory=list)
    characters_present: list[str] = field(default_factory=list)
    state_changes: list[str] = field(default_factory=list)
    open_threads: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)


@dataclass
class VolumeBriefItem:
    volume: int
    chapter_range: list[int] = field(default_factory=list)
    summary: str = ""
    main_conflicts: list[str] = field(default_factory=list)
    key_facts: list[str] = field(default_factory=list)
    active_threads: list[str] = field(default_factory=list)
    character_arcs: list[str] = field(default_factory=list)


@dataclass
class ContractData:
    world_rules: list[str] = field(default_factory=list)
    character_boundaries: dict[str, list[str]] = field(default_factory=dict)
    power_system_limits: list[str] = field(default_factory=list)
    forbidden_additions: list[str] = field(default_factory=list)
    unresolved_threads: list[dict] = field(default_factory=list)


@dataclass
class ContextCorpus:
    facts: list[FactItem] = field(default_factory=list)
    summaries: list[SummaryItem] = field(default_factory=list)
    volumes: list[VolumeBriefItem] = field(default_factory=list)
    contract: ContractData | None = None


def load_context_corpus(project_dir: Path) -> ContextCorpus:
    """从项目目录加载检索语料，缺失文件则对应字段为空。"""
    summaries_dir = project_dir / "summaries"
    facts = _load_facts(project_dir / "canon" / "facts.jsonl")
    summaries = _load_summaries(summaries_dir)
    volumes = _load_volumes(summaries_dir)
    contract = _load_contract(project_dir / "story_contract.yaml")
    return ContextCorpus(
        facts=facts, summaries=summaries, volumes=volumes, contract=contract
    )


def _load_facts(path: Path) -> list[FactItem]:
    if not path.exists():
        return []
    items: list[FactItem] = []
    try:
        text = path.read_text(encoding="utf-8")
        for line in text.strip().split("\n"):
            if not line.strip():
                continue
            data = json.loads(line)
            items.append(FactItem(
                id=data.get("id", ""),
                chapter=data.get("chapter", 1),
                type=data.get("type", ""),
                subject=data.get("subject", ""),
                text=data.get("text", ""),
                object=data.get("object", ""),
                evidence=data.get("evidence", ""),
            ))
    except (json.JSONDecodeError, OSError):
        pass
    return items


def _load_summaries(summaries_dir: Path) -> list[SummaryItem]:
    if not summaries_dir.is_dir():
        return []
    items: list[SummaryItem] = []
    for f in sorted(summaries_dir.glob("chapter_*.yaml")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            items.append(SummaryItem(
                chapter=data.get("chapter", 1),
                title=data.get("title", ""),
                summary=data.get("summary", ""),
                key_events=data.get("key_events", []),
                characters_present=data.get("characters_present", []),
                state_changes=data.get("state_changes", []),
                open_threads=data.get("open_threads", []),
                evidence_refs=data.get("evidence_refs", []),
            ))
        except (yaml.YAMLError, OSError):
            continue
    return items


def _load_volumes(summaries_dir: Path) -> list[VolumeBriefItem]:
    if not summaries_dir.is_dir():
        return []
    items: list[VolumeBriefItem] = []
    for f in sorted(summaries_dir.glob("volume_*.yaml")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            cr = data.get("chapter_range", [1, 1])
            if isinstance(cr, list) and len(cr) >= 2:
                chapter_range = [int(cr[0]), int(cr[1])]
            else:
                chapter_range = [1, 1]
            items.append(VolumeBriefItem(
                volume=int(data.get("volume", 1)),
                chapter_range=chapter_range,
                summary=data.get("summary", ""),
                main_conflicts=data.get("main_conflicts", []),
                key_facts=data.get("key_facts", []),
                active_threads=data.get("active_threads", []),
                character_arcs=data.get("character_arcs", []),
            ))
        except (yaml.YAMLError, OSError, TypeError, ValueError):
            continue
    return items


def _load_contract(path: Path) -> ContractData | None:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return ContractData(
            world_rules=data.get("world_rules", []),
            character_boundaries=data.get("character_boundaries", {}),
            power_system_limits=data.get("power_system_limits", []),
            forbidden_additions=data.get("forbidden_additions", []),
            unresolved_threads=data.get("unresolved_threads", []),
        )
    except (yaml.YAMLError, OSError):
        return None
