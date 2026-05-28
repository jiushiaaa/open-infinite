from __future__ import annotations

import re
import uuid

from living_novel_engine.models.events import AcceptedEvent, CharacterAction
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec

_JADE_KEYWORDS = ("传讯玉简", "玉简", "传讯")
_BAMBOO_GO_KEYWORDS = (
    "赴约",
    "竹林",
    "出城",
    "离城",
    "踏入雨幕",
    "三十里",
    "石亭",
)

# linear 模式：仅强动作/明确离城短语，禁止「望向竹林方向」等提及触发
_DEPARTURE_ACTION_TYPES = frozenset(
    {
        "move",
        "travel",
        "depart",
        "go",
        "go_to",
        "leave",
        "follow",
        "赴约",
    }
)
_DEPARTURE_STRONG_PHRASES = (
    "踏入雨幕",
    "走出城门",
    "出了城门",
    "离城而去",
    "踏入竹林",
    "步入竹林",
    "提灯出城",
    "动身赴约",
    "前往城外竹林",
    "奔赴竹林",
    "离城赴约",
    "出了听雨轩",
)
_STAY_INVESTIGATE_MARKERS = (
    "收回脚步",
    "收回迈",
    "转身回到",
    "回屋",
    "留在",
    "按兵不动",
    "未卸下",
    "驻足于",
    "屏息凝神",
    "感知着城主府",
    "按兵不动",
)
_FAN_WARNING_TYPES = frozenset(
    {
        "communicate",
        "message",
        "message_transmission",
        "subtle_interference",
        "warn",
        "whisper",
        "use_item",
    }
)
_WARNING_CONTENT_MARKERS = (
    "师姐",
    "莫要",
    "不可赴",
    "示警",
    "劝阻",
    "有诈",
    "退魂铃",
    "速回",
    "三思",
)


def is_jade_slip_action(action: CharacterAction) -> bool:
    if action.action_type in ("use_item", "message"):
        return any(k in action.content for k in _JADE_KEYWORDS)
    return "传讯玉简" in action.content or (
        "玉简" in action.content and ("传讯" in action.content or "碎" in action.content)
    )


def is_fan_warning_action(action: CharacterAction) -> bool:
    if action.character_id != "lin_fan":
        return False
    if action.action_type in _FAN_WARNING_TYPES:
        if any(m in action.content for m in _WARNING_CONTENT_MARKERS):
            return True
    return any(m in action.content for m in ("师姐，", "师姐！", "警告", "劝阻"))


def lin_wan_zhou_jade_resource_drift(
    action: CharacterAction, scene_state: dict
) -> bool:
    """林晚舟不得持有/误称林凡传讯玉简；玉简已碎后禁止竹简类示警物描写。"""
    if action.character_id != "lin_wan_zhou":
        return False
    content = action.content
    if "传讯玉简" in content:
        return True
    if scene_state.get("jade_slip_used") and (
        "竹简" in content
        or "应急" in content
        or "玉简" in content
    ):
        return True
    if re.search(
        r"林晚舟.{0,24}(手中的|握着|捏着|拿起|放到|置于|凝视).{0,16}(竹简|玉简|应急)",
        content,
    ):
        return True
    return False


def rewrite_lwz_jade_resource_drift(
    action: CharacterAction, scene_state: dict
) -> CharacterAction:
    """纠正林晚舟侧传讯玉简/竹简资源漂移（勿再替换成「竹简」）。"""
    from living_novel_engine.orchestrator.canon_guard import normalize_jade_slip_terms

    jade_used = bool(scene_state.get("jade_slip_used"))
    text = action.content
    thought = action.internal_thought or ""

    if jade_used and "玉简已碎" not in text and "传讯" in text:
        text = text.replace("玉简", "传讯玉简")

    text = normalize_jade_slip_terms(text, jade_slip_used=jade_used)
    thought = normalize_jade_slip_terms(thought, jade_slip_used=jade_used)

    if jade_used and "林凡" in text and "竹简" in text:
        text = re.sub(
            r"[^，。]{0,8}竹简[^，。]{0,20}一生仅此一枚",
            "传讯玉简已碎，示警已尽",
            text,
        )

    return CharacterAction(
        character_id=action.character_id,
        character_name=action.character_name,
        stance=action.stance,
        action_type=action.action_type,
        target=action.target,
        content=text,
        internal_thought=thought,
        intervention_response=action.intervention_response,
    )


def substitute_jade_exhausted_action(action: CharacterAction) -> CharacterAction:
    return CharacterAction(
        character_id=action.character_id,
        character_name=action.character_name,
        stance=action.stance,
        action_type="observe",
        target=action.target or "lin_wan_zhou",
        content="林凡在暗处屏息守望，传讯玉简早已碎尽，不敢再泄半缕灵力",
        internal_thought=action.internal_thought or "传讯玉简已尽，只能以肉身冒险拦阻",
        intervention_response=action.intervention_response,
    )


def substitute_fan_warning_exhausted(action: CharacterAction) -> CharacterAction:
    return CharacterAction(
        character_id=action.character_id,
        character_name=action.character_name,
        stance=action.stance,
        action_type="observe",
        target="lin_wan_zhou",
        content="林凡十指扣住廊柱，目光紧随师姐背影，却不再出声示警",
        internal_thought="示警已尽，再多一句只会逼她逆反",
        intervention_response=action.intervention_response,
    )


def content_implies_departure(content: str) -> bool:
    """believe/doubt/reject 等分支用的关键词检测（linear 不用）。"""
    return any(k in content for k in _BAMBOO_GO_KEYWORDS)


def action_implies_stay_or_investigate(act: CharacterAction) -> bool:
    if act.character_id != "lin_wan_zhou":
        return False
    if any(m in act.content for m in _STAY_INVESTIGATE_MARKERS):
        return True
    if act.action_type in ("stay", "wait"):
        return True
    return False


def action_implies_physical_departure(act: CharacterAction) -> bool:
    if act.character_id != "lin_wan_zhou":
        return False
    if act.action_type in _DEPARTURE_ACTION_TYPES:
        return True
    target = act.target or ""
    if any(t in target for t in ("竹林", "bamboo", "城外竹林", "三十里")):
        return True
    return any(p in act.content for p in _DEPARTURE_STRONG_PHRASES)


def action_implies_bamboo_arrival(act: CharacterAction) -> bool:
    if act.character_id != "lin_wan_zhou":
        return False
    blob = f"{act.target} {act.content}"
    return any(
        x in blob
        for x in (
            "竹林石亭",
            "城外竹林",
            "三十里竹林",
            "步入竹林",
            "踏入竹林",
            "竹林中",
            "竹林里",
        )
    )


def _events_imply_bamboo_arrival(events: list) -> bool:
    for evt in events:
        if getattr(evt, "subject", None) != "lin_wan_zhou":
            continue
        if getattr(evt, "event_type", "") == "move_to_bamboo_grove":
            return True
        payload = getattr(evt, "payload", None) or {}
        content = str(payload.get("content", ""))
        if any(
            x in content
            for x in (
                "踏入竹林",
                "步入竹林",
                "城外竹林",
                "竹林石亭",
                "三十里竹林",
                "抵达竹林",
            )
        ):
            return True
    return False


def ensure_bamboo_arrival_event(
    scene_state: dict,
    events: list,
    char_map: dict,
    *,
    chapter_number: int,
) -> None:
    """快照已触发竹林但事件层缺少明确赴约时，补一条结构化移动事件。"""
    if not scene_state.get("bamboo_grove_triggered"):
        return
    if _events_imply_bamboo_arrival(events):
        return

    last_round = max((getattr(e, "round_num", 0) for e in events), default=0) or 1
    seed = str(scene_state.get("branch_seed", "reject"))
    stance = "reject" if seed == "reject" else seed

    content = "林晚舟执意赴约，提灯踏入城外三十里竹林，在石亭前止步。"
    if seed == "reject":
        content = "林晚舟拒听劝阻，仍往城外竹林赴约，踏入石亭阵纹之中。"

    evt = AcceptedEvent(
        event_id=f"evt_{uuid.uuid4().hex[:10]}",
        chapter=chapter_number,
        round_num=last_round,
        event_type="move_to_bamboo_grove",
        subject="lin_wan_zhou",
        payload={
            "stance": stance,
            "target": "城外竹林石亭",
            "content": content,
            "thought": "（引擎补全：与 bamboo_grove_triggered 对齐）",
        },
        narrative=f"林晚舟{content}",
    )
    events.append(evt)

    char = char_map.get("lin_wan_zhou")
    if char:
        char.current_state.location = "城外竹林（石亭）"
    scene_state["lin_wan_zhou_departed"] = True


def reconcile_linear_flags_from_events(
    scene_state: dict,
    events: list,
    char_map: dict,
) -> None:
    """linear 续章：以林晚舟最后一条明确行动为准，覆盖关键词误判。"""
    lwz_events = [e for e in events if getattr(e, "subject", None) == "lin_wan_zhou"]
    if not lwz_events:
        return
    for evt in reversed(lwz_events):
        payload = getattr(evt, "payload", None) or {}
        if not payload.get("content"):
            continue
        act = CharacterAction(
            character_id="lin_wan_zhou",
            character_name="林晚舟",
            stance=payload.get("stance", "doubt"),  # type: ignore[arg-type]
            action_type=getattr(evt, "event_type", "speak"),
            target=str(payload.get("target", "")),
            content=str(payload.get("content", "")),
            internal_thought=str(payload.get("thought", "")),
            intervention_response=str(payload.get("stance", "doubt")),
        )
        if action_implies_stay_or_investigate(act):
            scene_state["lin_wan_zhou_departed"] = False
            scene_state["bamboo_grove_triggered"] = False
            scene_state["investigating"] = True
            char = char_map.get("lin_wan_zhou")
            if char:
                char.current_state.location = "听雨轩"
            return
        if action_implies_physical_departure(act):
            scene_state["lin_wan_zhou_departed"] = True
            scene_state["bamboo_grove_triggered"] = action_implies_bamboo_arrival(act)
            scene_state["investigating"] = False
            char = char_map.get("lin_wan_zhou")
            if char:
                if scene_state["bamboo_grove_triggered"]:
                    char.current_state.location = "城外竹林（石亭）"
                else:
                    char.current_state.location = "天荒城门外（赴约途中）"
            return


def enforce_branch_invariants(scene_state: dict, spec: BranchSpec) -> None:
    seed = spec.branch_seed
    if seed == "linear":
        return
    if seed == "believe":
        scene_state["lin_wan_zhou_departed"] = False
        scene_state["bamboo_grove_triggered"] = False
        scene_state["investigating"] = True
    elif seed == "doubt":
        scene_state["lin_wan_zhou_departed"] = False
        scene_state["bamboo_grove_triggered"] = False
        scene_state["investigating"] = True
    elif seed == "reject":
        if not scene_state.get("investigating"):
            scene_state["lin_wan_zhou_departed"] = True
        scene_state["bamboo_grove_triggered"] = bool(scene_state.get("lin_wan_zhou_departed"))


def apply_character_action_to_scene(
    scene_state: dict,
    act: CharacterAction,
    char_map: dict,
    spec: BranchSpec,
) -> None:
    char = char_map.get(act.character_id)
    seed = spec.branch_seed

    if act.character_id == "lin_fan":
        if is_fan_warning_action(act):
            if is_jade_slip_action(act) and not scene_state.get("jade_slip_used"):
                scene_state["jade_slip_used"] = True
                if char:
                    char.current_state.emotion = "决绝"
                    char.current_state.resources = [
                        r for r in char.current_state.resources if "传讯玉简" not in r
                    ]
                    char.current_state.resources.append("传讯玉简（已碎）")
            if not scene_state.get("fan_warning_delivered"):
                scene_state["fan_warning_delivered"] = True
        if seed == "linear":
            if scene_state.get("lin_wan_zhou_departed") and (
                act.action_type in ("follow", "move")
                or any(
                    p in act.content
                    for p in ("跟随师姐", "跟上师姐", "尾随", "一同出城", "追赶师姐")
                )
            ):
                scene_state["lin_fan_followed"] = True
                scene_state["conflict_escalated"] = True
        elif "跟" in act.content or "拦" in act.content or "追上" in act.content:
            scene_state["lin_fan_followed"] = True
            scene_state["conflict_escalated"] = True

    if act.character_id == "lin_wan_zhou":
        if "传讯玉简" in act.content and char:
            scene_state["lwz_jade_mentioned"] = True
            char.current_state.resources = [
                r for r in char.current_state.resources if "传讯玉简" not in r
            ]
        if seed == "linear":
            if action_implies_stay_or_investigate(act):
                scene_state["lin_wan_zhou_departed"] = False
                scene_state["bamboo_grove_triggered"] = False
                scene_state["investigating"] = True
                if char:
                    char.current_state.location = "听雨轩"
                    if "警惕" not in (char.current_state.emotion or ""):
                        char.current_state.emotion = "警惕"
            elif action_implies_physical_departure(act):
                scene_state["lin_wan_zhou_departed"] = True
                scene_state["bamboo_grove_triggered"] = action_implies_bamboo_arrival(act)
                scene_state["investigating"] = False
                if char:
                    char.current_state.location = (
                        "城外竹林（石亭）"
                        if scene_state["bamboo_grove_triggered"]
                        else "天荒城门外（赴约途中）"
                    )
        elif seed in ("believe", "doubt"):
            going = content_implies_departure(act.content)
            scene_state["lin_wan_zhou_departed"] = False
            scene_state["bamboo_grove_triggered"] = False
            scene_state["investigating"] = True
            if char:
                char.current_state.location = (
                    "听雨轩" if seed == "believe" else "天荒城内（调查）"
                )
                char.current_state.emotion = (
                    "迟疑后驻足" if act.stance == "believe" else "警惕"
                )
        elif seed == "reject":
            going = content_implies_departure(act.content)
            if act.stance == "reject" or going:
                scene_state["lin_wan_zhou_departed"] = True
                scene_state["bamboo_grove_triggered"] = going or scene_state.get(
                    "lin_wan_zhou_departed", False
                )
                if char:
                    char.current_state.emotion = "愠怒" if act.stance == "reject" else "决意"
                    char.current_state.location = "院门外" if going else "听雨轩廊下"
            if act.stance == "believe":
                scene_state["lin_wan_zhou_departed"] = True

    if char:
        char.memory.append(f"轮次行动: {act.content[:80]}")

    enforce_branch_invariants(scene_state, spec)
    sync_locations_from_scene_flags(scene_state, char_map)


def sync_locations_from_scene_flags(
    scene_state: dict,
    char_map: dict,
) -> None:
    """场景标志确定后，将角色 location 与 flags 对齐（快照写盘用）。"""
    lwz = char_map.get("lin_wan_zhou")
    if lwz:
        if scene_state.get("bamboo_grove_triggered"):
            lwz.current_state.location = "城外竹林（石亭）"
            scene_state["location"] = "城外三十里竹林"
        elif scene_state.get("lin_wan_zhou_departed"):
            lwz.current_state.location = "天荒城门外（赴约途中）"
        elif scene_state.get("investigating"):
            if scene_state.get("branch_seed") == "doubt":
                lwz.current_state.location = "天荒城内（调查）"
            else:
                lwz.current_state.location = "听雨轩"
        elif scene_state.get("branch_seed") in ("believe", "doubt"):
            lwz.current_state.location = "听雨轩"

    lf = char_map.get("lin_fan")
    if lf:
        if scene_state.get("lin_fan_followed") and scene_state.get("lin_wan_zhou_departed"):
            lf.current_state.location = "城外方向（追赶师姐）"
        elif scene_state.get("jade_slip_used"):
            lf.current_state.location = "听雨轩外暗处"
