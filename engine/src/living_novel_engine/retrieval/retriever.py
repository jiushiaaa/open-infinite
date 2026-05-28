"""Retriever — 主检索接口，组合 BM25 + 距离衰减 + source_weight。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from living_novel_engine.retrieval.bm25 import BM25Lite
from living_novel_engine.retrieval.context_loader import (
    ContextCorpus,
    load_context_corpus,
)
from living_novel_engine.retrieval.decay import distance_decay

SOURCE_WEIGHT: dict[str, float] = {
    "fact": 1.0,
    "chapter_brief": 0.8,
    "volume_brief": 0.7,
    "contract": 1.2,
}


@dataclass
class RetrievedContext:
    """检索结果，格式化为可直接注入 prompt 的文本。"""

    facts_text: str = ""
    summaries_text: str = ""
    contract_text: str = ""
    items: list[dict[str, Any]] = field(default_factory=list)
    query: str = ""
    current_chapter: int = 1

    @property
    def raw_items(self) -> list[dict[str, Any]]:
        """兼容 v0.3.0 字段名。"""
        return self.items

    def as_prompt_block(self) -> str:
        """合并为单一 prompt 注入块；为空时返回空字符串。"""
        parts: list[str] = []
        if self.facts_text:
            parts.append(f"【检索到的正史事实】\n{self.facts_text}")
        if self.summaries_text:
            parts.append(f"【相关章节摘要】\n{self.summaries_text}")
        if self.contract_text:
            parts.append(f"【故事合约约束】\n{self.contract_text}")
        return "\n\n".join(parts)

    def to_artifact(self) -> dict[str, Any]:
        """序列化为 run 分支目录下的 retrieval_context.json 结构。"""
        return {
            "query": self.query,
            "current_chapter": self.current_chapter,
            "prompt_block": self.as_prompt_block(),
            "items": self.items,
        }


def retrieve_context(
    project_dir: Path,
    query: str,
    current_chapter: int = 1,
    top_k: int = 8,
) -> RetrievedContext:
    """从项目的 facts/summaries/contract 中检索与 query 相关的上下文。"""
    corpus = load_context_corpus(project_dir)
    if (
        not corpus.facts
        and not corpus.summaries
        and not corpus.volumes
        and corpus.contract is None
    ):
        return RetrievedContext(query=query, current_chapter=current_chapter)

    documents, doc_ids, doc_chapters, doc_types, doc_meta = _build_corpus(corpus)
    if not documents:
        return RetrievedContext(query=query, current_chapter=current_chapter)

    bm25 = BM25Lite(documents, doc_ids)
    raw_scores = bm25.score(query, top_k=top_k * 2)

    chapter_map = dict(zip(doc_ids, doc_chapters))
    type_map = dict(zip(doc_ids, doc_types))
    meta_map = dict(zip(doc_ids, doc_meta))

    scored: list[tuple[str, float]] = []
    for doc_id, score in raw_scores:
        dtype = type_map.get(doc_id, "fact")
        weight = SOURCE_WEIGHT.get(dtype, 1.0)
        if dtype == "contract":
            decay = 1.0
        else:
            ch = chapter_map.get(doc_id, current_chapter)
            decay = distance_decay(current_chapter, ch)
        scored.append((doc_id, score * weight * decay))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_items = scored[:top_k]

    ctx = _format_results(top_items, type_map, meta_map, chapter_map, corpus)
    ctx.query = query
    ctx.current_chapter = current_chapter
    return ctx


def _build_corpus(
    corpus: ContextCorpus,
) -> tuple[list[str], list[str], list[int], list[str], list[dict[str, Any]]]:
    """构建 BM25 检索文档集。返回 doc_meta 供格式化 items。"""
    documents: list[str] = []
    doc_ids: list[str] = []
    doc_chapters: list[int] = []
    doc_types: list[str] = []
    doc_meta: list[dict[str, Any]] = []

    for fact in corpus.facts:
        documents.append(f"{fact.subject} {fact.text}")
        doc_ids.append(f"fact:{fact.id}")
        doc_chapters.append(fact.chapter)
        doc_types.append("fact")
        doc_meta.append({
            "text": fact.text,
            "chapter": fact.chapter,
            "evidence": fact.evidence,
            "subject": fact.subject,
        })

    for summary in corpus.summaries:
        text = f"{summary.title} {summary.summary}"
        if summary.key_events:
            text += " " + " ".join(summary.key_events)
        if summary.characters_present:
            text += " " + " ".join(summary.characters_present)
        evidence = summary.evidence_refs[0] if summary.evidence_refs else ""
        documents.append(text)
        doc_ids.append(f"chapter_brief:ch{summary.chapter}")
        doc_chapters.append(summary.chapter)
        doc_types.append("chapter_brief")
        doc_meta.append({
            "text": summary.summary,
            "chapter": summary.chapter,
            "evidence": evidence,
            "title": summary.title,
        })

    for vol in corpus.volumes:
        text = vol.summary
        if vol.main_conflicts:
            text += " " + " ".join(vol.main_conflicts)
        if vol.active_threads:
            text += " " + " ".join(vol.active_threads)
        if vol.key_facts:
            text += " " + " ".join(vol.key_facts)
        ch = vol.chapter_range[-1] if vol.chapter_range else 1
        documents.append(text)
        doc_ids.append(f"volume_brief:{vol.volume}")
        doc_chapters.append(ch)
        doc_types.append("volume_brief")
        doc_meta.append({
            "text": text,
            "chapter": ch,
            "evidence": "",
            "volume": vol.volume,
            "chapter_range": vol.chapter_range,
        })

    if corpus.contract:
        contract_parts = _get_contract_parts(corpus.contract)
        for i, part in enumerate(contract_parts):
            documents.append(part)
            doc_ids.append(f"contract:{i}")
            doc_chapters.append(1)
            doc_types.append("contract")
            doc_meta.append({"text": part, "chapter": 1, "evidence": ""})

    return documents, doc_ids, doc_chapters, doc_types, doc_meta


def _format_results(
    top_items: list[tuple[str, float]],
    type_map: dict[str, str],
    meta_map: dict[str, dict[str, Any]],
    chapter_map: dict[str, int],
    corpus: ContextCorpus,
) -> RetrievedContext:
    """将 top_k 检索结果分类格式化。"""
    facts_lines: list[str] = []
    summaries_lines: list[str] = []
    contract_lines: list[str] = []
    items: list[dict[str, Any]] = []

    for doc_id, score in top_items:
        dtype = type_map.get(doc_id, "unknown")
        meta = meta_map.get(doc_id, {})
        ch = chapter_map.get(doc_id, meta.get("chapter", 1))
        text = meta.get("text", "")
        evidence = meta.get("evidence", "")

        items.append({
            "id": doc_id,
            "source": dtype,
            "type": dtype,
            "score": round(score, 4),
            "text": text,
            "chapter": ch,
            "evidence": evidence,
        })

        if dtype == "fact":
            facts_lines.append(f"- [{meta.get('subject', '')}] {text}")
        elif dtype == "chapter_brief":
            title = meta.get("title", "")
            summaries_lines.append(f"- 第{ch}章 {title}: {text}")
        elif dtype == "volume_brief":
            vol = meta.get("volume", 1)
            summaries_lines.append(f"- 第{vol}卷: {text[:200]}")
        elif dtype == "contract":
            contract_lines.append(f"- {text}")

    return RetrievedContext(
        facts_text="\n".join(facts_lines),
        summaries_text="\n".join(summaries_lines),
        contract_text="\n".join(contract_lines),
        items=items,
    )


def _get_contract_parts(contract) -> list[str]:
    """重建 contract 文本片段列表（与 _build_corpus 一致）。"""
    if contract is None:
        return []
    parts: list[str] = []
    for rule in contract.world_rules:
        parts.append(rule)
    for char_id, boundaries in contract.character_boundaries.items():
        parts.append(f"{char_id}: " + "; ".join(boundaries))
    for limit in contract.power_system_limits:
        parts.append(limit)
    for forbidden in contract.forbidden_additions:
        parts.append(f"禁止: {forbidden}")
    for thread in contract.unresolved_threads:
        title = thread.get("title", "")
        if title:
            parts.append(f"未解决: {title}")
    return parts
