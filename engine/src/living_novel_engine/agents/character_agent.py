from __future__ import annotations

from pydantic import BaseModel, Field

from living_novel_engine.llm.client import LLMClient
from living_novel_engine.models import CharacterAgent, Intervention, StoryWorld
from living_novel_engine.models.events import CharacterAction


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
    if perceived:
        user_parts.append(f"【感知到的干预】类型={intervention.type if intervention else ''}, 内容={perceived}")
    else:
        user_parts.append("【干预】未感知到高维信息")
    if forced_stance:
        user_parts.append(f"【分支提示】本世界线倾向立场: {forced_stance}，但仍需符合人设，可折中。")

    user = "\n".join(user_parts)

    if llm.mock:
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
