"""Entity alias registry and lightweight resolution helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ALIAS_VERSION = "v0.8.x"
_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_\-]+")


@dataclass
class EntityAliasEntry:
    entity_id: str
    canonical_name: str
    entity_type: str
    aliases: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)


@dataclass
class EntityAliasIndex:
    entities: dict[str, EntityAliasEntry] = field(default_factory=dict)
    lookup: dict[str, str] = field(default_factory=dict)
    status: str = "missing"
    path: str = ""

    def aliases_for(self, entity_id: str) -> list[str]:
        entry = self.entities.get(entity_id)
        return list(entry.aliases) if entry else []

    def resolve_text(self, text: str) -> list[str]:
        normalized = _normalize_alias(text)
        if not normalized:
            return []
        resolved: set[str] = set()
        for alias, entity_id in self.lookup.items():
            if alias and alias in normalized:
                resolved.add(entity_id)
        return sorted(resolved)

    def expand_text(self, text: str) -> str:
        resolved = self.resolve_text(text)
        if not resolved:
            return text
        return f"{text} {' '.join(resolved)}"

    def to_summary(self) -> dict[str, Any]:
        samples = [
            {
                "entity_id": e.entity_id,
                "canonical_name": e.canonical_name,
                "entity_type": e.entity_type,
                "alias_count": len(e.aliases),
            }
            for e in list(self.entities.values())[:6]
        ]
        return {
            "status": self.status,
            "path": self.path or "memory/entity_aliases.yaml",
            "count": len(self.entities),
            "sample_entities": samples,
        }


def build_entity_aliases(
    *,
    story_slug: str,
    extraction: Any,
    canon_records: list[dict] | None = None,
) -> dict[str, Any]:
    entities: dict[str, EntityAliasEntry] = {}

    for idx, char in enumerate(
        extraction.characters_yaml.get("characters", []) or [], start=1
    ):
        if not isinstance(char, dict):
            continue
        entity_id = str(char.get("id") or f"character_{idx:03d}")
        name = str(char.get("name") or entity_id)
        aliases = [entity_id, name]
        for value in char.get("address_rules", []) or []:
            aliases.append(str(value))
        _merge_entry(
            entities,
            EntityAliasEntry(
                entity_id=entity_id,
                canonical_name=name,
                entity_type="character",
                aliases=_dedupe(aliases),
                source_refs=["characters.yaml"],
            ),
        )

    world = extraction.world_yaml or {}
    for idx, loc in enumerate(world.get("locations", []) or [], start=1):
        if isinstance(loc, dict):
            entity_id = str(loc.get("id") or _safe_id(loc.get("name")) or f"location_{idx:03d}")
            name = str(loc.get("name") or entity_id)
            aliases = [entity_id, name]
            source_refs = ["world.yaml"]
        else:
            name = str(loc)
            entity_id = _safe_id(name) or f"location_{idx:03d}"
            aliases = [entity_id, name]
            source_refs = ["world.yaml"]
        _merge_entry(
            entities,
            EntityAliasEntry(
                entity_id=entity_id,
                canonical_name=name,
                entity_type="location",
                aliases=_dedupe(aliases),
                source_refs=source_refs,
            ),
        )

    for idx, faction in enumerate(world.get("factions", []) or [], start=1):
        if isinstance(faction, dict):
            entity_id = str(
                faction.get("id") or _safe_id(faction.get("name")) or f"faction_{idx:03d}"
            )
            name = str(faction.get("name") or entity_id)
        else:
            name = str(faction)
            entity_id = _safe_id(name) or f"faction_{idx:03d}"
        _merge_entry(
            entities,
            EntityAliasEntry(
                entity_id=entity_id,
                canonical_name=name,
                entity_type="faction",
                aliases=_dedupe([entity_id, name]),
                source_refs=["world.yaml"],
            ),
        )

    for record in canon_records or []:
        for entity_id in record.get("entities", []) or []:
            entity_id = str(entity_id)
            if not entity_id:
                continue
            _merge_entry(
                entities,
                EntityAliasEntry(
                    entity_id=entity_id,
                    canonical_name=entity_id,
                    entity_type="ledger_entity",
                    aliases=[entity_id],
                    source_refs=["memory/canon_ledger.jsonl"],
                ),
            )

    entries = [
        {
            "entity_id": e.entity_id,
            "canonical_name": e.canonical_name,
            "entity_type": e.entity_type,
            "aliases": _dedupe(e.aliases),
            "source_refs": _dedupe(e.source_refs),
        }
        for e in sorted(entities.values(), key=lambda item: item.entity_id)
    ]
    lookup = _build_lookup(entries)
    return {
        "version": ALIAS_VERSION,
        "story_slug": story_slug,
        "created_at": datetime.now().isoformat(),
        "entities": entries,
        "lookup": lookup,
    }


def write_entity_aliases(
    memory_dir: Path,
    *,
    story_slug: str,
    extraction: Any,
    canon_records: list[dict] | None = None,
) -> dict[str, Any]:
    data = build_entity_aliases(
        story_slug=story_slug,
        extraction=extraction,
        canon_records=canon_records,
    )
    memory_dir.mkdir(parents=True, exist_ok=True)
    with open(memory_dir / "entity_aliases.yaml", "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=120,
        )
    return data


def load_entity_aliases(project_dir: Path) -> EntityAliasIndex:
    path = project_dir / "memory" / "entity_aliases.yaml"
    if not path.exists():
        return EntityAliasIndex(status="missing", path="memory/entity_aliases.yaml")
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries = {}
        for raw in data.get("entities", []) or []:
            if not isinstance(raw, dict):
                continue
            entity_id = str(raw.get("entity_id") or "").strip()
            if not entity_id:
                continue
            aliases = [str(a) for a in raw.get("aliases", []) or [] if str(a).strip()]
            entries[entity_id] = EntityAliasEntry(
                entity_id=entity_id,
                canonical_name=str(raw.get("canonical_name") or entity_id),
                entity_type=str(raw.get("entity_type") or "entity"),
                aliases=_dedupe([entity_id, raw.get("canonical_name", ""), *aliases]),
                source_refs=[
                    str(ref)
                    for ref in raw.get("source_refs", []) or []
                    if str(ref).strip()
                ],
            )
        lookup = {
            _normalize_alias(alias): entity_id
            for entity_id, entry in entries.items()
            for alias in entry.aliases
            if _normalize_alias(alias)
        }
        return EntityAliasIndex(
            entities=entries,
            lookup=lookup,
            status="ready",
            path="memory/entity_aliases.yaml",
        )
    except (OSError, yaml.YAMLError, TypeError, ValueError):
        return EntityAliasIndex(status="damaged", path="memory/entity_aliases.yaml")


def _merge_entry(
    entities: dict[str, EntityAliasEntry], entry: EntityAliasEntry
) -> None:
    existing = entities.get(entry.entity_id)
    if existing is None:
        entities[entry.entity_id] = entry
        return
    if existing.canonical_name == existing.entity_id and entry.canonical_name:
        existing.canonical_name = entry.canonical_name
    if existing.entity_type == "ledger_entity" and entry.entity_type != "ledger_entity":
        existing.entity_type = entry.entity_type
    existing.aliases = _dedupe([*existing.aliases, *entry.aliases])
    existing.source_refs = _dedupe([*existing.source_refs, *entry.source_refs])


def _build_lookup(entries: list[dict[str, Any]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for entry in entries:
        entity_id = str(entry.get("entity_id") or "")
        aliases = [
            entity_id,
            str(entry.get("canonical_name") or ""),
            *[str(a) for a in entry.get("aliases", []) or []],
        ]
        for alias in aliases:
            normalized = _normalize_alias(alias)
            if normalized:
                lookup[normalized] = entity_id
    return dict(sorted(lookup.items()))


def _safe_id(value: object) -> str:
    clean = _SAFE_ID_RE.sub("_", str(value or "")).strip("_").lower()
    return clean


def _normalize_alias(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "").strip().lower())


def _dedupe(values: list[object]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        key = _normalize_alias(text)
        if not text or key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out
