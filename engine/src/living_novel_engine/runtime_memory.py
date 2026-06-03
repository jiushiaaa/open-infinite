"""Runtime memory context builder.

This layer is intentionally read-only: it packages the safe subset of imported
project memory that already feeds retrieval into a compact prompt block and a
separate audit artifact. It does not mutate project memory or runner state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any

from living_novel_engine.entity_aliases import EntityAliasIndex, load_entity_aliases
from living_novel_engine.retrieval import RetrievedContext, retrieve_context

RUNTIME_MEMORY_VERSION = "v0.8.x-runtime-memory"


@dataclass
class RuntimeMemoryContext:
    query: str
    current_chapter: int
    retrieval: RetrievedContext
    entity_aliases: EntityAliasIndex
    resolved_query_entities: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_prompt_block(self) -> str:
        """Return the additive prompt block consumed by character/narrator agents."""
        retrieval_block = self.retrieval.as_prompt_block()
        parts: list[str] = []
        layer_lines = [
            f"- entity_aliases: {self.entity_aliases.status}",
            f"- retrieval_items: {len(self.retrieval.items)}",
        ]
        if self.resolved_query_entities:
            layer_lines.append(
                "- resolved_query_entities: "
                + ", ".join(self.resolved_query_entities)
            )
        if self.warnings:
            layer_lines.append("- warnings: " + "；".join(self.warnings))
        parts.append("【运行时记忆层】\n" + "\n".join(layer_lines))
        if retrieval_block:
            parts.append(retrieval_block)
        return "\n\n".join(parts)

    def to_artifact(self) -> dict[str, Any]:
        retrieval_artifact = self.retrieval.to_artifact()
        return {
            "version": RUNTIME_MEMORY_VERSION,
            "query": self.query,
            "current_chapter": self.current_chapter,
            "prompt_block": self.as_prompt_block(),
            "consumed_layers": _consumed_layers(
                self.retrieval, self.entity_aliases.status
            ),
            "entity_aliases": self.entity_aliases.to_summary(),
            "resolved_query_entities": self.resolved_query_entities,
            "warnings": self.warnings,
            "retrieval": retrieval_artifact,
        }


def build_runtime_memory_context(
    project_dir: Path,
    query: str,
    *,
    current_chapter: int = 1,
    top_k: int = 8,
) -> RuntimeMemoryContext:
    """Build read-only memory context for runtime prompt injection.

    Missing or damaged optional memory files degrade to explicit warnings while
    preserving the existing retrieval fallback behavior.
    """
    aliases = load_entity_aliases(project_dir)
    warnings: list[str] = []
    if aliases.status == "damaged":
        warnings.append("entity_aliases.yaml 损坏，已跳过别名归一化")
    elif aliases.status == "missing":
        warnings.append("entity_aliases.yaml 缺失，已按原始查询检索")

    if _retrieval_strategy() == "hybrid_vector":
        retrieval = _retrieve_hybrid_vector_context(
            project_dir,
            query,
            current_chapter=current_chapter,
            top_k=top_k,
        )
    else:
        retrieval = retrieve_context(
            project_dir,
            query,
            current_chapter=current_chapter,
            top_k=top_k,
        )
    resolved = aliases.resolve_text(query) if aliases.status == "ready" else []
    return RuntimeMemoryContext(
        query=query,
        current_chapter=current_chapter,
        retrieval=retrieval,
        entity_aliases=aliases,
        resolved_query_entities=resolved,
        warnings=warnings,
    )


def _retrieval_strategy() -> str:
    return os.environ.get("LNE_RETRIEVAL_STRATEGY", "bm25").strip().lower() or "bm25"


def _retrieve_hybrid_vector_context(
    project_dir: Path,
    query: str,
    *,
    current_chapter: int,
    top_k: int,
):
    from living_novel_engine.service.vector_retrieval_pipeline import (
        retrieve_hybrid_vector_context,
    )

    return retrieve_hybrid_vector_context(
        project_dir,
        query,
        current_chapter=current_chapter,
        top_k=top_k,
    )


def _consumed_layers(
    retrieval: RetrievedContext,
    alias_status: str,
) -> list[str]:
    layers: set[str] = set()
    if alias_status in {"ready", "damaged", "missing"}:
        layers.add("entity_aliases")
    for item in retrieval.items:
        source = str(item.get("source") or "").strip()
        if source:
            layers.add(source)
        path = str(item.get("retrieval_path") or "")
        if "vector" in path:
            layers.add("vector_retrieval")
        if "rerank" in path:
            layers.add("reranker")
    return sorted(layers)
