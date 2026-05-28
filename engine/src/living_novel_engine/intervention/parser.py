from __future__ import annotations

import re
import uuid
from datetime import datetime

from living_novel_engine.models import Intervention, InterventionType, StoryWorld
from living_novel_engine.models.intervention import Strength, Visibility


def build_intervention(
    *,
    target: str,
    content: str,
    intervention_type: InterventionType = "whisper",
    strength: Strength | None = None,
    visibility: Visibility | None = None,
    worldline_id: str = "canon",
    branch_seed: str = "",
) -> Intervention:
    fields = parse_intervention_fields(content, intervention_type)
    return Intervention(
        id=f"intervention_{uuid.uuid4().hex[:12]}",
        worldline_id=worldline_id,
        target=target,
        type=intervention_type,
        content=content.strip(),
        strength=strength or fields.get("strength", "soft"),  # type: ignore[arg-type]
        visibility=visibility or fields.get("visibility", "target_only"),  # type: ignore[arg-type]
        branch_seed=branch_seed,
        created_at=datetime.now(),
    )


def parse_intervention_fields(
    content: str,
    intervention_type: InterventionType,
) -> dict[str, str]:
    text = content.lower()
    strength: Strength = "soft"
    if any(w in content for w in ("必须", "立刻", "马上", "不得", "绝不")):
        strength = "strong"
    elif any(w in content for w in ("小心", "或许", "不妨", "试试")):
        strength = "soft"
    else:
        strength = "medium"

    visibility: Visibility = "target_only"
    if intervention_type in ("weather", "rumor", "crisis"):
        visibility = "world_wide"
    elif intervention_type in ("letter", "new_event"):
        visibility = "scene"
    if re.search(r"所有人|全城|举世", content):
        visibility = "world_wide"
    elif re.search(r"在场|众人|一起", content):
        visibility = "scene"

    return {"strength": strength, "visibility": visibility}


def enrich_intervention_from_llm(
    intervention: Intervention,
    world: StoryWorld,
    character_name: str,
    llm_parse: dict | None = None,
) -> Intervention:
    if not llm_parse:
        return intervention
    data = {**intervention.model_dump()}
    for key in ("strength", "visibility", "type"):
        if key in llm_parse and llm_parse[key]:
            data[key] = llm_parse[key]
    data["audit_notes"] = list(intervention.audit_notes)
    if llm_parse.get("reason"):
        data["audit_notes"].append(str(llm_parse["reason"]))
    return Intervention(**data)
