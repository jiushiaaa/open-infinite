"""v0.7.2 干预护栏服务层（console-free）。

加载故事后调用 `intervention.guardrail.evaluate_guardrail`，
供 HTTP API（POST /api/interventions/guardrail）与 CLI 共用。

- 不发起任何生成、不改变 run_intervention 主行为。
- 故事不存在 → FileNotFoundError（映射 404）；入参非法 → GuardrailRequestError（400）。
"""

from __future__ import annotations

import yaml

from living_novel_engine.intervention.guardrail import (
    InterventionGuardrailResult,
    evaluate_guardrail,
)
from living_novel_engine.story_loader import load_story


class GuardrailRequestError(ValueError):
    """入参非法（缺 content 等）——映射为 HTTP 400。"""


def check_intervention_guardrail(
    *,
    story_slug: str,
    content: str,
    target: str = "",
    intervention_type: str | None = None,
    visibility: str = "target_only",
    strength: str = "soft",
) -> InterventionGuardrailResult:
    """对一次干预做独立护栏预检。

    intervention_type 可传四类抽象类型（information/forced_action/
    resource_injection/rule_rewrite）；None 时由 classifier 自动判定。
    """
    slug = (story_slug or "").strip()
    text = (content or "").strip()
    if not slug:
        raise GuardrailRequestError("缺少 story_slug")
    if not text:
        raise GuardrailRequestError("缺少 content（干预内容）")

    try:
        bundle = load_story(slug)
    except FileNotFoundError:
        raise
    except (yaml.YAMLError, UnicodeDecodeError, OSError, TypeError, ValueError) as exc:
        raise GuardrailRequestError(f"故事 YAML 或角色数据解析失败：{exc}") from exc
    char_map = bundle.character_map()

    declared = None
    if intervention_type in (
        "information",
        "forced_action",
        "resource_injection",
        "rule_rewrite",
    ):
        declared = intervention_type  # type: ignore[assignment]

    return evaluate_guardrail(
        text,
        world=bundle.world,
        characters=char_map,
        target=(target or "").strip(),
        declared_type=declared,
        visibility=visibility or "target_only",
        strength=strength or "soft",
    )
