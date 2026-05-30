"""v0.7.5 Worldline Judge deterministic evaluator.

第一刀只做轻量本地评审：不打 LLM，不接外部服务，不改 runner 输出。
它从已有 branch artifact 和故事锚定信息推断“这条世界线是否值得继续”。
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from living_novel_engine.retrieval.bm25 import tokenize
from living_novel_engine.worldline_judge.models import (
    JudgementDimension,
    Recommendation,
    StoryArcPoint,
    WorldlineJudgeScores,
    WorldlineJudgement,
)

_TENSION_WORDS = [
    "危机",
    "杀局",
    "封印",
    "裂缝",
    "背叛",
    "追杀",
    "冲突",
    "反击",
    "代价",
    "暴露",
    "逼近",
    "震怒",
    "城破",
]
_TURNING_WORDS = ["忽然", "却", "转而", "意识到", "真相", "暴露", "终于", "反将", "改道"]
_EMOTION_WORDS = ["警惕", "震怒", "恐惧", "愧疚", "迟疑", "决意", "悲", "怒", "惊", "恨"]
_SLOP_PHRASES = [
    "命运的齿轮",
    "无法言说",
    "一切都变得不同",
    "这一刻",
    "似乎有什么",
    "微微一愣",
]
_CONTRACT_RISK_WORDS = [
    "AK47",
    "核弹",
    "手机",
    "飞机",
    "系统降临",
    "穿越者",
    "现代武器",
    "无条件服从",
]


@dataclass
class _EvalContext:
    chapter_text: str
    summary_text: str
    events: dict[str, Any]
    state_snapshot: dict[str, Any]
    known_character_names: list[str]
    world_rules: list[str]
    open_threads: list[str]
    causal_diff: dict[str, Any] | None
    intervention: dict[str, Any] | None
    compilation: dict[str, Any] | None
    warnings: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, round(float(x), 4)))


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _count_hits(text: str, words: list[str]) -> int:
    return sum(1 for w in words if w and w in text)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"[。！？!?；;\n]+", text or "")
    return [p.strip() for p in parts if p.strip()]


def _repetition_penalty(tokens: list[str]) -> float:
    if len(tokens) < 10:
        return 0.0
    counts = Counter(tokens)
    repeated = sum(v - 1 for v in counts.values() if v > 1)
    return _clamp(repeated / max(1, len(tokens)))


def _chapter_number(events: dict[str, Any], state_snapshot: dict[str, Any]) -> int | None:
    raw = events.get("chapter") or state_snapshot.get("chapter")
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _persona_consistency(ctx: _EvalContext) -> tuple[float, list[str]]:
    names = [n for n in ctx.known_character_names if n]
    matched = [n for n in names if n in ctx.chapter_text]
    if not names:
        return 0.55, []
    score = 0.45 + 0.45 * (len(matched) / len(names))
    if "无条件服从" in ctx.chapter_text:
        ctx.warnings.append("正文出现“无条件服从”倾向，可能削弱角色自主性。")
        score -= 0.35
    return _clamp(score), matched[:4]


def _contract_risk(ctx: _EvalContext) -> tuple[float, list[str]]:
    hits = [w for w in _CONTRACT_RISK_WORDS if w in ctx.chapter_text]
    lineage = str(_as_dict(ctx.compilation).get("lineage_type") or "").lower()
    risk = 0.12 * len(hits)
    if "alternate" in lineage or "au" in lineage:
        risk += 0.22
    if hits:
        ctx.warnings.append(f"疑似越界元素：{'、'.join(hits[:4])}。")
    return _clamp(risk), hits[:4]


def _branch_diversity(ctx: _EvalContext) -> tuple[float, list[str]]:
    evidence: list[str] = []
    diff_blocks = _as_dict(ctx.causal_diff).get("blocks") or []
    if isinstance(diff_blocks, list) and diff_blocks:
        evidence.append(f"时空 Diff {len(diff_blocks)} 块")
    seed = str(ctx.events.get("branch_seed") or "")
    theme = str(ctx.events.get("theme") or "")
    base = 0.25
    if seed and seed not in {"linear", "baseline"}:
        base += 0.25
        evidence.append(seed)
    if theme and theme not in {"linear", "baseline"}:
        base += 0.15
        evidence.append(theme[:18])
    if diff_blocks:
        base += min(0.25, len(diff_blocks) * 0.12)
    return _clamp(base), evidence[:4]


def _narrative_momentum(ctx: _EvalContext) -> tuple[float, list[str]]:
    accepted = _as_dict(ctx.events).get("accepted_events") or []
    event_count = len(accepted) if isinstance(accepted, list) else 0
    hook = str(_as_dict(ctx.state_snapshot).get("next_chapter_hook") or "")
    length_score = min(len(ctx.chapter_text) / 220.0, 1.0)
    score = 0.25 + min(event_count, 4) * 0.1 + length_score * 0.25
    evidence: list[str] = []
    if hook:
        score += 0.2
        evidence.append(hook[:40])
    if event_count:
        evidence.append(f"事件 {event_count} 个")
    return _clamp(score), evidence[:4]


def _emotional_payoff(ctx: _EvalContext) -> tuple[float, list[str]]:
    hits = [w for w in _EMOTION_WORDS if w in ctx.chapter_text]
    chars = _as_dict(ctx.state_snapshot).get("characters") or {}
    emotions: list[str] = []
    if isinstance(chars, dict):
        for cs in chars.values():
            if isinstance(cs, dict) and cs.get("emotion"):
                emotions.append(str(cs["emotion"]))
    score = 0.25 + min(len(hits), 4) * 0.12 + min(len(set(emotions)), 3) * 0.09
    return _clamp(score), list(dict.fromkeys(hits + emotions))[:5]


def _anti_slop(ctx: _EvalContext) -> tuple[float, list[str]]:
    text = ctx.chapter_text
    phrases = [p for p in _SLOP_PHRASES if p in text]
    tokens = tokenize(text)
    repetition = _repetition_penalty(tokens)
    score = 1.0 - len(phrases) * 0.12 - repetition * 0.85
    if len(text.strip()) < 40:
        score -= 0.3
        ctx.warnings.append("正文过短，质量评审置信度较低。")
    if phrases:
        ctx.warnings.append(f"存在偏套路化表达：{'、'.join(phrases[:3])}。")
    if repetition > 0.32:
        ctx.warnings.append("文本重复度偏高，可能有水文或空转风险。")
    return _clamp(score), phrases[:4]


def _continuation_potential(ctx: _EvalContext) -> tuple[float, list[str]]:
    hook = str(_as_dict(ctx.state_snapshot).get("next_chapter_hook") or "")
    thread_hits = [t for t in ctx.open_threads if t and t in ctx.chapter_text]
    cliff = _count_hits(ctx.chapter_text, ["必须", "尚未", "仍", "下一章", "黎明前", "真相"])
    score = 0.2 + min(cliff, 4) * 0.12 + min(len(thread_hits), 3) * 0.12
    evidence = thread_hits[:3]
    if hook:
        score += 0.22
        evidence.insert(0, hook[:40])
    return _clamp(score), evidence[:4]


def _emergence_score(ctx: _EvalContext) -> tuple[float, list[str]]:
    evidence: list[str] = []
    score = 0.15
    if ctx.intervention:
        score += 0.2
        content = str(ctx.intervention.get("content") or "")
        if content:
            evidence.append(content[:30])
    diff_blocks = _as_dict(ctx.causal_diff).get("blocks") or []
    if isinstance(diff_blocks, list) and diff_blocks:
        score += 0.25
        evidence.append(f"生成新分歧 {len(diff_blocks)} 处")
    scope = _as_dict(_as_dict(ctx.compilation).get("affected_scope"))
    scope_count = sum(len(v) for v in scope.values() if isinstance(v, list))
    if scope_count:
        score += min(0.25, scope_count * 0.08)
        evidence.append(f"影响范围 {scope_count} 项")
    return _clamp(score), evidence[:4]


def _story_arc(ctx: _EvalContext) -> tuple[float, list[StoryArcPoint]]:
    sents = _sentences(ctx.chapter_text)
    if not sents:
        return 0.0, []
    chunks = [
        ("开端", sents[: max(1, len(sents) // 3)]),
        ("承压", sents[max(1, len(sents) // 3) : max(2, len(sents) * 2 // 3)]),
        ("钩子", sents[max(2, len(sents) * 2 // 3) :]),
    ]
    curve: list[StoryArcPoint] = []
    values: list[float] = []
    for label, part in chunks:
        text = "。".join(part)
        tension = _clamp(0.12 + _count_hits(text, _TENSION_WORDS) * 0.16)
        momentum = _clamp(0.15 + _count_hits(text, _TURNING_WORDS) * 0.14)
        curve.append(StoryArcPoint(label=label, tension=tension, momentum=momentum))
        values.append((tension + momentum) / 2)
    spread = max(values) - min(values) if values else 0.0
    return _clamp(sum(values) / len(values) * 0.7 + spread * 0.3), curve


def _turning_points(ctx: _EvalContext) -> tuple[float, list[str]]:
    found: list[str] = []
    for sent in _sentences(ctx.chapter_text):
        if any(w in sent for w in _TURNING_WORDS):
            found.append(sent[:60])
    score = _clamp(min(len(found), 3) / 3)
    return score, found[:5]


def _tension(ctx: _EvalContext) -> tuple[float, list[str]]:
    hits = [w for w in _TENSION_WORDS if w in ctx.chapter_text]
    score = _clamp(0.2 + min(len(hits), 5) * 0.14)
    return score, hits[:5]


def _recommend(overall: float, contract_risk: float, warnings: list[str]) -> Recommendation:
    if overall >= 0.62 and contract_risk < 0.45:
        return "推荐继续"
    if overall < 0.36 or len(warnings) >= 3:
        return "建议归档"
    return "谨慎继续"


def _interpret(recommendation: Recommendation, scores: WorldlineJudgeScores) -> str:
    if recommendation == "推荐继续":
        return "这条世界线具备继续推进价值：分歧清晰、叙事仍有钩子，且未显著冲突角色与世界合约。"
    if recommendation == "建议归档":
        return "这条世界线当前质量风险偏高，建议先归档或重跑，避免把空转、越界或低张力分支继续扩写。"
    return "这条世界线有可取之处，但还需要观察后续张力与角色一致性，建议谨慎继续。"


def _dimension(key: str, label: str, score: float, evidence: list[str], comment: str) -> JudgementDimension:
    return JudgementDimension(
        key=key, label=label, score=_clamp(score), evidence=evidence, comment=comment
    )


def evaluate_worldline(
    *,
    chapter_text: str,
    summary_text: str = "",
    events: dict[str, Any] | None = None,
    state_snapshot: dict[str, Any] | None = None,
    known_character_names: list[str] | None = None,
    world_rules: list[str] | None = None,
    open_threads: list[str] | None = None,
    causal_diff: dict[str, Any] | None = None,
    intervention: dict[str, Any] | None = None,
    compilation: dict[str, Any] | None = None,
) -> WorldlineJudgement:
    """Evaluate one branch and return a deterministic judgement report."""
    ctx = _EvalContext(
        chapter_text=chapter_text or "",
        summary_text=summary_text or "",
        events=_as_dict(events),
        state_snapshot=_as_dict(state_snapshot),
        known_character_names=known_character_names or [],
        world_rules=world_rules or [],
        open_threads=open_threads or [],
        causal_diff=_as_dict(causal_diff) if causal_diff is not None else None,
        intervention=_as_dict(intervention) if intervention is not None else None,
        compilation=_as_dict(compilation) if compilation is not None else None,
    )

    persona, persona_ev = _persona_consistency(ctx)
    risk, risk_ev = _contract_risk(ctx)
    diversity, diversity_ev = _branch_diversity(ctx)
    momentum, momentum_ev = _narrative_momentum(ctx)
    emotion, emotion_ev = _emotional_payoff(ctx)
    anti_slop, slop_ev = _anti_slop(ctx)
    continuation, continuation_ev = _continuation_potential(ctx)
    emergence, emergence_ev = _emergence_score(ctx)
    arc, curve = _story_arc(ctx)
    turning, turns = _turning_points(ctx)
    tension, tension_ev = _tension(ctx)

    overall = _clamp(
        persona * 0.12
        + (1.0 - risk) * 0.10
        + diversity * 0.10
        + momentum * 0.12
        + emotion * 0.08
        + anti_slop * 0.10
        + continuation * 0.12
        + emergence * 0.10
        + arc * 0.06
        + turning * 0.05
        + tension * 0.05
    )
    scores = WorldlineJudgeScores(
        persona_consistency=persona,
        contract_risk=risk,
        branch_diversity=diversity,
        narrative_momentum=momentum,
        emotional_payoff=emotion,
        anti_slop=anti_slop,
        continuation_potential=continuation,
        emergence_score=emergence,
        story_arc=arc,
        turning_points=turning,
        tension=tension,
        overall=overall,
    )

    if diversity >= 0.55:
        ctx.strengths.append("分支与原走向已有明确差异。")
    if continuation >= 0.55:
        ctx.strengths.append("下一章钩子清晰，具备继续推进空间。")
    if emergence >= 0.5:
        ctx.strengths.append("读者干预产生了可观察的新涌现节点。")
    if momentum < 0.4:
        ctx.suggestions.append("补一个明确行动目标或外部压力，避免章节停在解释层。")
    if tension < 0.4:
        ctx.suggestions.append("增加冲突、代价或倒计时，让世界线更值得继续。")
    if anti_slop < 0.6:
        ctx.suggestions.append("压缩套话和重复句，保留能改变状态的具体动作。")

    rec = _recommend(overall, risk, ctx.warnings)
    return WorldlineJudgement(
        chapter_number=_chapter_number(ctx.events, ctx.state_snapshot),
        recommendation=rec,
        scores=scores,
        dimensions=[
            _dimension("persona_consistency", "角色一致性", persona, persona_ev, "角色是否仍按既有人设行动。"),
            _dimension("contract_risk", "合约风险", risk, risk_ev, "越高表示越可能冲突题材或世界规则。"),
            _dimension("branch_diversity", "分支差异", diversity, diversity_ev, "是否真的走出新世界线。"),
            _dimension("narrative_momentum", "叙事动量", momentum, momentum_ev, "事件推进与下一章钩子。"),
            _dimension("emotional_payoff", "情绪兑现", emotion, emotion_ev, "角色心境与冲突是否有回响。"),
            _dimension("anti_slop", "反水文", anti_slop, slop_ev, "套话、重复和空转风险。"),
            _dimension("continuation_potential", "续写潜力", continuation, continuation_ev, "是否留下可继续运行的债务。"),
            _dimension("emergence_score", "涌现价值", emergence, emergence_ev, "干预是否制造了新节点。"),
            _dimension("story_arc", "故事弧", arc, [p.label for p in curve], "开端、承压、钩子的张力变化。"),
            _dimension("turning_points", "转折点", turning, turns, "是否有明确转向。"),
            _dimension("tension", "张力", tension, tension_ev, "冲突强度与追读压力。"),
        ],
        turning_points=turns,
        story_arc_curve=curve,
        strengths=ctx.strengths,
        warnings=ctx.warnings,
        suggestions=ctx.suggestions,
        interpretation=_interpret(rec, scores),
    )
