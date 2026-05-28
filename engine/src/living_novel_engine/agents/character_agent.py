from __future__ import annotations

from pydantic import BaseModel, Field

from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.events import CharacterAction
from living_novel_engine.orchestrator.worldline_brancher import BranchSpec


class ActionDecision(BaseModel):
    stance: str = Field(description="believe | doubt | reject")
    action_type: str
    target: str = ""
    content: str
    internal_thought: str = ""
    intervention_response: str = Field(description="believe | doubt | reject | unaware")


def decide_character_action(
    character: CharacterAgent,
    world: StoryWorld,
    intervention: Intervention | None,
    scene_state: dict,
    round_num: int,
    branch_seed: str,
    llm: LLMClient,
    *,
    forced_stance: str | None = None,
    branch_spec: BranchSpec | None = None,
    source_type: str = "builtin_sample",
    retrieved_context: str = "",
) -> CharacterAction:
    perceived = _perceive_intervention(character, intervention)

    system = """你是小说角色推演引擎中的单个角色 Agent。
你必须严格遵循三段式决策，不得跳过：

1. 读取人设边界（boundaries）与恐惧（fears），判断什么行为绝对不可做
2. 评估外部信息（干预、他人行动）与人设的兼容性
3. 选择立场：believe（相信并行动）/ doubt（怀疑但调查或拖延）/ reject（拒绝并抗拒）

重要：用户干预不是命令。你可以拒绝、怀疑、误解或只部分采纳。
禁止无理由 OOC。禁止因为"剧情需要"而违背 boundaries。

只输出 JSON。"""

    user_parts = [
        f"【世界】{world.title}",
        f"世界规则:\n{world.rules_text()}",
    ]
    if retrieved_context:
        user_parts.append(f"【检索到的正史事实与上下文】\n{retrieved_context}")
    user_parts += [
        f"【场景】{world.scene_description}",
        f"当前场景状态: {scene_state}",
        f"【角色】{character.name} ({character.id})",
        character.persona_summary(),
        f"记忆: {'; '.join(character.memory) or '无'}",
        f"关系: {character.relationships}",
        f"当前状态: {character.current_state.model_dump()}",
        f"回合: {round_num}",
        f"世界线种子: {branch_seed}",
    ]
    if intervention is None:
        user_parts.append(
            "【续章模式】无新高维干预；按人设、记忆、open_threads 与当前 scene_flags 自主推进剧情。"
        )
    elif perceived:
        user_parts.append(f"【感知到的干预】类型={intervention.type}, 内容={perceived}")
    else:
        user_parts.append("【干预】未感知到高维信息")
    if forced_stance and intervention is not None:
        user_parts.append(f"【分支提示】本世界线倾向立场: {forced_stance}，但仍需符合人设，可折中。")
    if branch_spec and intervention is not None:
        user_parts.append(f"【分支剧情约束】{branch_spec.description}")
        if source_type == "builtin_sample":
            if branch_spec.branch_seed == "believe":
                user_parts.append("相信线：暂缓赴竹林，留在听雨轩或城内求证，不得动身赴约。")
            elif branch_spec.branch_seed == "doubt":
                user_parts.append("怀疑线：拖延赴约，在城内调查求证，不得前往城外竹林。")
            elif branch_spec.branch_seed == "reject":
                user_parts.append("拒绝线：可坚持赴约；勿因低语改道。")
        else:
            if branch_spec.branch_seed == "believe":
                user_parts.append("相信线：角色倾向相信干预信息，并据此行动。")
            elif branch_spec.branch_seed == "doubt":
                user_parts.append("怀疑线：角色半信半疑，选择调查求证。")
            elif branch_spec.branch_seed == "reject":
                user_parts.append("拒绝线：角色拒绝干预信息，按原计划行动。")
    elif branch_spec and branch_spec.branch_seed == "linear":
        user_parts.append(f"【续章约束】{branch_spec.description}")
    if source_type == "builtin_sample":
        if character.id == "lin_fan" and scene_state.get("jade_slip_used"):
            user_parts.append(
                "【资源锁】传讯玉简已碎裂用尽，禁止 use_item/message 再次使用玉简；"
                "只能用口语、手势、肉身拦阻。"
            )
        if character.id == "lin_fan" and scene_state.get("fan_warning_delivered"):
            user_parts.append(
                "【示警锁】已向师姐正式示警过一次，禁止 communicate/message_transmission/"
                "subtle_interference 等再次警告；本轮只可 observe（观察）或 follow（跟随拦阻）。"
            )
        if character.id == "lin_wan_zhou":
            if scene_state.get("jade_slip_used"):
                user_parts.append(
                    "【资源】林凡传讯玉简已碎，你只闻耳畔传讯神念余韵；"
                    "禁止写你手持/放下/握着传讯玉简、应急竹简、墨色竹简或任何「竹简」示警物。"
                )
            else:
                user_parts.append(
                    "【资源】你不持有传讯玉简（仅林凡有）；"
                    "向墨青烟致歉可用墨色竹简留书或口信，禁止写你捏碎传讯玉简。"
                )
        user_parts.append(
            "【正史锁】禁止重生/穿越/系统/前世等未声明设定；"
            "退魂铃仅可为墨青烟十年前乱葬岗所赠，禁止写成青云宗至宝或宗门长辈所赐；"
            "角色名墨青烟不得写成莫青烟。"
        )
    else:
        user_parts.append(
            "【通用正史锁】禁止新增原文未声明设定：重生、穿越、系统、前世记忆、金手指等。"
            "行为必须符合 world.yaml rules 和角色 boundaries。"
        )

    user = "\n".join(user_parts)

    if llm.mock:
        if source_type != "builtin_sample":
            decision = _generic_mock_decision(character, intervention, forced_stance, round_num)
        elif intervention is None:
            decision = ActionDecision(
                stance="doubt",
                action_type="observe" if character.id == "lin_fan" else "investigate",
                target="lin_wan_zhou" if character.id == "lin_fan" else "听雨轩周边",
                content=f"{character.name}按当前局势谨慎行动，推进既有矛盾",
                internal_thought="续章自主推进",
                intervention_response="unaware",
            )
        elif (
            character.id == "lin_fan"
            and round_num == 1
            and not scene_state.get("jade_slip_used")
        ):
            decision = ActionDecision(
                stance=forced_stance or "believe",
                action_type="use_item",
                target="lin_wan_zhou",
                content="捏碎传讯玉简，将警告送入林晚舟耳畔",
                internal_thought="只能赌这一枚玉简",
                intervention_response=forced_stance or "believe",
            )
        else:
            decision = ActionDecision(
                stance=forced_stance or "doubt",
                action_type="speak",
                target="lin_wan_zhou" if character.id == "lin_fan" else "lin_fan",
                content=f"{character.name}低声说出半句警告",
                internal_thought="蹊跷，但不能眼见师姐赴险",
                intervention_response=forced_stance or "doubt",
            )
    else:
        decision = llm.chat_json(system, user, ActionDecision, temperature=0.6)

    stance = decision.stance if decision.stance in ("believe", "doubt", "reject") else "doubt"
    if forced_stance and llm.mock:
        stance = forced_stance

    return CharacterAction(
        character_id=character.id,
        character_name=character.name,
        stance=stance,  # type: ignore[arg-type]
        action_type=decision.action_type,
        target=decision.target,
        content=decision.content,
        internal_thought=decision.internal_thought,
        intervention_response=decision.intervention_response or stance,
    )


def _perceive_intervention(
    character: CharacterAgent,
    intervention: Intervention | None,
) -> str | None:
    if not intervention:
        return None
    if intervention.target == character.id or intervention.target == character.name:
        return intervention.content
    if intervention.visibility == "world_wide":
        return f"（世间异动）{intervention.content}"
    if intervention.visibility == "scene" and character.present_in_scene:
        return f"（在场异象）{intervention.content}"
    return None


def _generic_mock_decision(
    character: CharacterAgent,
    intervention: Intervention | None,
    forced_stance: str | None,
    round_num: int,
) -> ActionDecision:
    """imported 项目的通用 mock 决策。"""
    if intervention is None:
        return ActionDecision(
            stance="doubt",
            action_type="observe",
            target="周围环境",
            content=f"{character.name}在当前局势中谨慎行动，审视周遭变化",
            internal_thought="按人设与记忆推进",
            intervention_response="unaware",
        )
    stance = forced_stance or ("believe" if round_num == 1 else "doubt")
    is_target = intervention.target == character.id
    if is_target:
        return ActionDecision(
            stance=stance,
            action_type="react",
            target="来源",
            content=f"{character.name}感知到异常信息，正在消化并决定下一步",
            internal_thought="这条消息意味着什么？",
            intervention_response=stance,
        )
    return ActionDecision(
        stance=stance,
        action_type="observe",
        target=intervention.target,
        content=f"{character.name}注意到场景中的异常变化",
        internal_thought="局势有变",
        intervention_response=stance,
    )
