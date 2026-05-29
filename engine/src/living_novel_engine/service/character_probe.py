"""v0.7.2 Character Probe：角色内心探针（只读、deterministic、不调用 LLM）。

回答："这个角色为什么会相信 / 怀疑 / 拒绝 / 反抗一次干预？"

数据来源：
- characters.yaml（人设、记忆、关系、当前状态）
- world.yaml（规则、开放伏笔——用于推断角色"未知信息"）
- story_contract.yaml（如存在，叠加边界提示）
- state_snapshot.json（若提供 run_id/branch_id，叠加运行后情绪与第四面墙觉察）
- 第四面墙等级（fourth_wall.level_from_score）

行为：
- 找不到故事/角色 → FileNotFoundError（映射 404）。
- YAML 损坏不 500：load_story 失败抛 FileNotFoundError；快照损坏静默忽略。
- 用中文解释"角色不会无条件服从用户"的原因。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from living_novel_engine.fourth_wall import level_from_score
from living_novel_engine.intervention_compiler.classifier import classify
from living_novel_engine.models import CharacterAgent
from living_novel_engine.story_loader import load_story

RiskLevel = Literal["low", "medium", "high"]


class ProbeRequestError(ValueError):
    """入参非法——映射为 HTTP 400。"""


class CharacterProbe(BaseModel):
    """角色内心探针（只读解释，不改变任何运行状态）。"""

    character_id: str
    name: str
    narrative_role: str = "supporting"
    belief_summary: str = ""
    current_emotion: str = "平静"
    desires: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    known_information: list[str] = Field(default_factory=list)
    unknown_information: list[str] = Field(default_factory=list)
    fourth_wall_awareness: float = 0.0
    fourth_wall_level: str = "none"
    likely_intervention_response: str = ""
    obedience_risk: RiskLevel = "low"
    resistance_level: RiskLevel = "low"
    explanation: str = ""


def _obedience_from_resistance(resistance: RiskLevel) -> RiskLevel:
    return {"high": "low", "medium": "medium", "low": "high"}[resistance]


def _belief_summary(char: CharacterAgent) -> str:
    traits = "、".join(char.persona.traits) or "尚未明确"
    parts = [f"{char.name} 的判断由其性格（{traits}）与亲历记忆共同塑造。"]
    if char.persona.boundaries:
        parts.append(f"其行为底线是：{char.persona.boundaries[0]}。")
    if char.memory:
        parts.append(f"她/他记得：{char.memory[0]}")
    return "".join(parts)


def _known_information(char: CharacterAgent) -> list[str]:
    known = list(char.memory)
    if char.current_state.location:
        known.append(f"自己此刻身处：{char.current_state.location}")
    if char.current_state.resources:
        known.append(f"持有：{'、'.join(char.current_state.resources)}")
    return known


def _unknown_information(char: CharacterAgent, world_open_threads: list[str]) -> list[str]:
    memory_blob = " ".join(char.memory)
    unknown: list[str] = []
    for title in world_open_threads:
        if title and title not in memory_blob:
            unknown.append(f"伏笔走向：{title}")
    unknown.append("其他角色私下的盘算与隐瞒")
    unknown.append("来自高维读者的真实干预意图")
    return unknown


def _predict_response(
    char: CharacterAgent,
    intervention_text: str,
    fw_level: str,
) -> tuple[str, RiskLevel]:
    """返回 (likely_intervention_response, resistance_level)。"""
    boundaries = " ".join(char.persona.boundaries)
    obey_resist = any(
        k in boundaries for k in ("不会无理由", "不会无条件", "不会背叛", "不会盲从")
    )
    distrust = "不会轻信" in boundaries

    if not intervention_text.strip():
        # 无具体干预：基于人设与觉察给出基线倾向
        if fw_level in ("aware", "defiant"):
            return "已察觉异常叙事压力，可能反过来质问或利用干预", "high"
        if char.persona.boundaries:
            return "会先以自身人设与记忆衡量，不会无条件服从", "medium"
        return "在合理范围内可能顺势而为，但仍受处境制约", "low"

    itype, _ = classify(intervention_text)
    if itype == "rule_rewrite":
        return "视为不可能之事，强烈抗拒或当作幻觉/异象", "high"
    if itype == "forced_action":
        if obey_resist:
            return "抵抗强令，要求一个符合自身动机的理由", "high"
        return "迟疑、拖延或只部分执行", "medium"
    if itype == "information":
        if distrust:
            return "不轻信，倾向先怀疑并暗中调查", "medium"
        return "可能采信，但仍保留戒心", "low"
    # resource_injection
    return "谨慎对待来历不明之物，质疑来源", "medium"


def _explanation(
    char: CharacterAgent,
    response: str,
    resistance: RiskLevel,
    fw_level: str,
) -> str:
    bound = char.persona.boundaries[0] if char.persona.boundaries else "自身的意志"
    fear = char.persona.fears[0] if char.persona.fears else None
    base = (
        f"{char.name} 不是一个会无条件服从用户的提线木偶——"
        f"其行为受人设边界（{bound}）"
    )
    if fear:
        base += f"、恐惧（{fear}）"
    base += "与亲历记忆约束。"
    if resistance == "high":
        base += f"因此面对这次干预，{response}。想真正改变其选择，应给出贴合其欲望或恐惧的内在理由。"
    elif resistance == "medium":
        base += f"因此面对这次干预，{response}。"
    else:
        base += f"这次干预与其处境冲突不大，{response}。"
    if fw_level in ("aware", "defiant"):
        base += "此外，反复的高维干预已让其觉察到『被注视』，会更加警惕。"
    return base


def _load_snapshot_overrides(
    outputs_root: Path,
    run_id: str | None,
    branch_id: str | None,
    char_id: str,
) -> tuple[str | None, float, str | None]:
    """从 state_snapshot.json 读取 (emotion, fourth_wall_awareness, fourth_wall_level)。

    缺文件/损坏/无该角色 → 返回中性默认，绝不抛。
    """
    if not run_id or not branch_id:
        return None, 0.0, None
    snap_path = outputs_root / run_id / branch_id / "state_snapshot.json"
    if not snap_path.exists():
        return None, 0.0, None
    try:
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None, 0.0, None
    if not isinstance(snap, dict):
        return None, 0.0, None
    chars = snap.get("characters")
    if not isinstance(chars, dict):
        return None, 0.0, None
    entry = chars.get(char_id)
    if not isinstance(entry, dict):
        return None, 0.0, None
    emotion = entry.get("emotion")
    score = entry.get("fourth_wall_awareness")
    level = entry.get("fourth_wall_level")
    return (
        str(emotion) if emotion else None,
        float(score) if isinstance(score, (int, float)) else 0.0,
        str(level) if level else None,
    )


def probe_character(
    *,
    story_slug: str,
    character_id: str,
    run_id: str | None = None,
    branch_id: str | None = None,
    intervention_text: str = "",
    outputs_root: Path | None = None,
) -> CharacterProbe:
    """构造一个角色的内心探针解释。"""
    slug = (story_slug or "").strip()
    cid = (character_id or "").strip()
    if not slug:
        raise ProbeRequestError("缺少 story_slug")
    if not cid:
        raise ProbeRequestError("缺少 character_id")

    try:
        bundle = load_story(slug)
    except FileNotFoundError:
        raise
    except (yaml.YAMLError, UnicodeDecodeError, OSError, TypeError, ValueError) as exc:
        raise ProbeRequestError(f"故事 YAML 或角色数据解析失败：{exc}") from exc
    char_map = bundle.character_map()
    char = char_map.get(cid)
    if char is None:
        raise FileNotFoundError(
            f"角色不存在: {cid}（故事 {slug} 可选: {', '.join(char_map.keys())}）"
        )

    if outputs_root is None:
        from living_novel_engine.browser.paths import outputs_dir

        outputs_root = outputs_dir()

    emotion_override, fw_score, fw_level_override = _load_snapshot_overrides(
        outputs_root, run_id, branch_id, cid
    )

    current_emotion = emotion_override or char.current_state.emotion or "平静"
    fw_score = fw_score or float(getattr(char, "fourth_wall_awareness", 0.0) or 0.0)
    fw_level = fw_level_override or level_from_score(fw_score)

    open_thread_titles = [t.title for t in bundle.world.open_threads]
    response, resistance = _predict_response(char, intervention_text, fw_level)

    return CharacterProbe(
        character_id=char.id,
        name=char.name,
        narrative_role=char.narrative_role,
        belief_summary=_belief_summary(char),
        current_emotion=current_emotion,
        desires=list(char.persona.desires),
        fears=list(char.persona.fears),
        boundaries=list(char.persona.boundaries),
        known_information=_known_information(char),
        unknown_information=_unknown_information(char, open_thread_titles),
        fourth_wall_awareness=fw_score,
        fourth_wall_level=fw_level,
        likely_intervention_response=response,
        obedience_risk=_obedience_from_resistance(resistance),
        resistance_level=resistance,
        explanation=_explanation(char, response, resistance, fw_level),
    )
