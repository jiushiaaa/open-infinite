"""v0.7.1-C Causal Diff 构建器（基于 stdlib difflib，段落级）。

不接 LLM semantic diff，不改正文，只生成后端数据。
"""

from __future__ import annotations

import difflib
import re
import uuid
from typing import TYPE_CHECKING, Any

from .models import CausalDiffArtifact, CausalDiffBlock, DiffAnchor, DiffMode

if TYPE_CHECKING:
    from living_novel_engine.intervention_compiler.models import InterventionCompilation

_OP_MAP = {"replace": "replace", "delete": "delete", "insert": "insert"}


def _split_paragraphs(text: str) -> list[str]:
    """按空行 / 多换行切段，去掉空白段。"""
    if not text or not text.strip():
        return []
    chunks = re.split(r"\n\s*\n+", text.strip())
    paras = [c.strip() for c in chunks if c.strip()]
    if len(paras) <= 1 and "\n" in text:
        # 无空行分隔时退化为按单行切，避免整章变成一个巨块
        lines = [ln.strip() for ln in text.strip().split("\n") if ln.strip()]
        if len(lines) > 1:
            return lines
    return paras


def _diff_mode(compilation: "InterventionCompilation") -> DiffMode:
    if compilation.lineage_type == "alternate_novel":
        return "alternate_novel_seed"
    if compilation.abstract_intervention.intervention_type == "rule_rewrite":
        return "broad_rewrite"
    return "local_divergence"


def _summarize(compilation: "InterventionCompilation") -> dict[str, Any]:
    ai = compilation.abstract_intervention
    return {
        "intervention_type": ai.intervention_type,
        "intent": ai.intent,
        "target_refs": list(ai.target_refs),
        "desired_effect": ai.desired_effect,
        "compatibility": compilation.compatibility.model_dump(),
        "realization": compilation.realization.model_dump(),
        "branch_axis": [a.model_dump() for a in compilation.branch_axis],
        "lineage_type": compilation.lineage_type,
        "compiler_source": compilation.source,
    }


def build_causal_diff(
    *,
    branch_id: str,
    old_text: str | None,
    new_text: str | None,
    compilation: "InterventionCompilation",
    chapter_number: int = 0,
    parent_diff_id: str | None = None,
) -> CausalDiffArtifact:
    """生成一个分支的 CausalDiffArtifact（status=proposed）。

    - old_text 缺失：写稳定空结构（blocks=[]）并记录 reason。
    - old_text 存在：基于 difflib 段落级 opcodes 生成 replace/insert/delete 块。
    """
    diff_mode = _diff_mode(compilation)
    artifact = CausalDiffArtifact(
        diff_id=f"diff_{uuid.uuid4().hex[:12]}",
        branch_id=branch_id,
        lineage_type=compilation.lineage_type,
        diff_mode=diff_mode,
        status="proposed",
        intervention_summary=_summarize(compilation),
        affected_scope=compilation.affected_scope.model_dump(),
        parent_diff_id=parent_diff_id,
    )

    old_paras = _split_paragraphs(old_text or "")
    new_paras = _split_paragraphs(new_text or "")

    if not old_paras:
        artifact.reason = (
            "缺少 old_text（原章节文本），仅记录稳定空结构，待 UI/后续版本补基线"
            if new_paras
            else "缺少 old_text 与 new_text，无法生成 diff 块"
        )
        return artifact

    artifact.blocks = _build_blocks(
        branch_id, old_paras, new_paras, chapter_number
    )
    if not artifact.blocks:
        artifact.reason = "新旧文本段落一致，未产生差异块"
    return artifact


def _build_blocks(
    branch_id: str,
    old_paras: list[str],
    new_paras: list[str],
    chapter_number: int,
) -> list[CausalDiffBlock]:
    matcher = difflib.SequenceMatcher(a=old_paras, b=new_paras, autojunk=False)
    blocks: list[CausalDiffBlock] = []
    idx = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        op = _OP_MAP.get(tag)
        if op is None:
            continue
        blocks.append(
            CausalDiffBlock(
                id=f"{branch_id}_blk_{idx}",
                op=op,  # type: ignore[arg-type]
                old_text="\n\n".join(old_paras[i1:i2]),
                new_text="\n\n".join(new_paras[j1:j2]),
                anchor=DiffAnchor(
                    chapter=chapter_number,
                    kind="paragraph",
                    old_index=i1 if i1 < i2 else -1,
                    new_index=j1 if j1 < j2 else -1,
                ),
            )
        )
        idx += 1
    return blocks
