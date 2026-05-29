"""v0.7.4 Canon Replay 评估器：deterministic 轻量评分，不打 LLM。

输入无干预基线续写文本与正史 holdout 文本，输出 0-1 分项分与解释：
- lexical_overlap：中文字级 bigram Jaccard 相似度
- entity_overlap：角色名/地点名/势力名命中
- thread_overlap：开放伏笔标题命中
- length_ratio：篇幅比
- state_consistency：基线 state_snapshot 角色是否仍出现在正史文本
- overall：加权汇总

所有计算确定性（无随机、无网络、无 LLM），分数严格钳制 0-1。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from living_novel_engine.retrieval.bm25 import tokenize

# overall 权重（合计 1.0）
_W_LEXICAL = 0.20
_W_ENTITY = 0.30
_W_THREAD = 0.15
_W_LENGTH = 0.10
_W_STATE = 0.25


@dataclass
class ReplayEvaluation:
    lexical_overlap: float = 0.0
    entity_overlap: float = 0.0
    thread_overlap: float = 0.0
    length_ratio: float = 0.0
    state_consistency: float = 0.0
    overall: float = 0.0
    matched_entities: list[str] = field(default_factory=list)
    missing_entities: list[str] = field(default_factory=list)
    matched_threads: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    interpretation: str = ""


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, round(float(x), 4)))


def _char_bigrams(text: str) -> set[str]:
    """从分词后的 token 序列构造 bigram 集合（中文字级 + 英文/数字词）。"""
    tokens = tokenize(text)
    if len(tokens) < 2:
        return set(tokens)
    return {f"{tokens[i]}{tokens[i + 1]}" for i in range(len(tokens) - 1)}


def _lexical_overlap(baseline_text: str, holdout_text: str) -> float:
    a = _char_bigrams(baseline_text)
    b = _char_bigrams(holdout_text)
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return _clamp(inter / union) if union else 0.0


def _name_present(name: str, text: str) -> bool:
    name = (name or "").strip()
    return bool(name) and name in text


def _entity_overlap(
    entities: list[str], baseline_text: str, holdout_text: str
) -> tuple[float, list[str], list[str]]:
    """命中=正史里出现的实体里，基线也写到的；缺失=正史里出现但基线未写到的。"""
    relevant = [e for e in dict.fromkeys(entities) if _name_present(e, holdout_text)]
    matched = [e for e in relevant if _name_present(e, baseline_text)]
    missing = [e for e in relevant if e not in matched]
    score = len(matched) / len(relevant) if relevant else 0.0
    return _clamp(score), matched, missing


def _thread_overlap(
    threads: list[str], baseline_text: str, holdout_text: str
) -> tuple[float, list[str]]:
    relevant = [t for t in dict.fromkeys(threads) if _thread_hit(t, holdout_text)]
    matched = [t for t in relevant if _thread_hit(t, baseline_text)]
    score = len(matched) / len(relevant) if relevant else 0.0
    return _clamp(score), matched


def _thread_hit(title: str, text: str) -> bool:
    title = (title or "").strip()
    if not title:
        return False
    if title in text:
        return True
    for token in title.replace("，", " ").replace("、", " ").split():
        if len(token) >= 2 and token in text:
            return True
    return False


def _length_ratio(baseline_text: str, holdout_text: str) -> float:
    lb, lh = len(baseline_text or ""), len(holdout_text or "")
    if lb == 0 or lh == 0:
        return 0.0
    return _clamp(min(lb, lh) / max(lb, lh))


def _state_consistency(baseline_state: dict, holdout_text: str) -> float:
    """基线快照里的活跃角色是否仍出现在正史文本中（轻量规则）。"""
    chars = (baseline_state or {}).get("characters") or {}
    names: list[str] = []
    for cid, cs in chars.items():
        if isinstance(cs, dict) and cs.get("name"):
            names.append(str(cs["name"]))
        else:
            names.append(str(cid))
    names = [n for n in dict.fromkeys(names) if n]
    if not names:
        return 0.0
    present = sum(1 for n in names if _name_present(n, holdout_text))
    return _clamp(present / len(names))


def _interpret(overall: float, missing: list[str]) -> str:
    if overall >= 0.66:
        base = "与正史高度接近，关键实体与走向基本对齐。"
    elif overall >= 0.4:
        base = "与正史有部分相似，但仍有偏离。"
    else:
        base = "与正史差异较大，基线走出了与原作不同的方向。"
    if missing:
        base += f" 缺失关键实体：{ '、'.join(missing[:5]) }。"
    return base


def evaluate_replay(
    baseline_text: str,
    holdout_text: str,
    *,
    entities: list[str] | None = None,
    threads: list[str] | None = None,
    baseline_state: dict | None = None,
) -> ReplayEvaluation:
    """对比无干预基线续写与正史 holdout，返回 deterministic 评估结果。"""
    baseline_text = baseline_text or ""
    holdout_text = holdout_text or ""
    entities = entities or []
    threads = threads or []
    baseline_state = baseline_state or {}

    warnings: list[str] = []
    if not baseline_text.strip():
        warnings.append("基线续写文本为空，评估结果不可靠。")
    if not holdout_text.strip():
        warnings.append("正史 holdout 文本为空，评估结果不可靠。")

    lexical = _lexical_overlap(baseline_text, holdout_text)
    entity, matched_entities, missing_entities = _entity_overlap(
        entities, baseline_text, holdout_text
    )
    thread, matched_threads = _thread_overlap(threads, baseline_text, holdout_text)
    length = _length_ratio(baseline_text, holdout_text)
    state = _state_consistency(baseline_state, holdout_text)

    overall = _clamp(
        lexical * _W_LEXICAL
        + entity * _W_ENTITY
        + thread * _W_THREAD
        + length * _W_LENGTH
        + state * _W_STATE
    )

    if missing_entities:
        warnings.append(f"基线缺失正史关键实体：{ '、'.join(missing_entities[:5]) }")
    if length < 0.4:
        warnings.append("基线与正史篇幅差异较大。")

    return ReplayEvaluation(
        lexical_overlap=lexical,
        entity_overlap=entity,
        thread_overlap=thread,
        length_ratio=length,
        state_consistency=state,
        overall=overall,
        matched_entities=matched_entities,
        missing_entities=missing_entities,
        matched_threads=matched_threads,
        warnings=warnings,
        interpretation=_interpret(overall, missing_entities),
    )
