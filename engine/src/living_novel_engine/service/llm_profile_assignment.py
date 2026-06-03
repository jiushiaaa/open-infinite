"""LLM Profile Assignment MVP：任务级模型画像只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.runtime_settings import (
    get_provider_gateway_summary,
    get_runtime_settings,
)

VERSION = "llm-profile-assignment-mvp"


def get_llm_profile_assignment() -> dict[str, Any]:
    """Return task-level model profile suggestions without network calls."""

    settings = get_runtime_settings()
    gateway = get_provider_gateway_summary()
    routes = {route["id"]: route for route in gateway.get("routes", [])}
    routing = gateway.get("routing", {})
    profiles = [
        _text_profile(
            profile_id="reader_intervention",
            label="读者干预生成",
            task_kind="generation",
            route=routes.get("intervention", {}),
            model=settings.llm_model_name,
            temperature=0.65,
            max_tokens=4096,
            budget_tier="high",
            fallback="mock",
            note="主章节生成保持较高创造性，但失败时回退本地模拟。",
        ),
        _text_profile(
            profile_id="story_genesis",
            label="主题创世",
            task_kind="generation",
            route=routes.get("story_genesis", {}),
            model=settings.llm_model_name,
            temperature=0.8,
            max_tokens=4096,
            budget_tier="medium",
            fallback="mock",
            note="创世需要更开放的发散度，但仍可用本地确定性降级。",
        ),
        _text_profile(
            profile_id="import_extraction",
            label="导入抽取",
            task_kind="extraction",
            route=routes.get("import_extraction", {}),
            model=settings.llm_model_name,
            temperature=0.3,
            max_tokens=6000,
            budget_tier="medium",
            fallback="mock_extractor",
            note="抽取任务优先稳定结构和低温度，失败时回退本地模拟抽取器。",
        ),
        _local_profile(
            profile_id="reader_revision",
            label="读者修订建议",
            task_kind="revision",
            temperature=0.4,
            max_tokens=1600,
            budget_tier="low",
            fallback="deterministic_reader_panel",
            note="当前 MVP 使用确定性读者评审；LLM 自动改写保持后置 opt-in。",
        ),
        _local_profile(
            profile_id="worldline_judge",
            label="世界线评审",
            task_kind="evaluation",
            temperature=0.0,
            max_tokens=0,
            budget_tier="none",
            fallback="deterministic_worldline_judge",
            note="当前评审为 deterministic，不消耗模型预算。",
        ),
        _visual_profile(
            route=routes.get("visual_assets", {}),
            visual_route=str(routing.get("visual_route") or "placeholder"),
            model=settings.seedream_model,
        ),
    ]
    mock_count = sum(1 for profile in profiles if profile["mode"] in {"mock", "deterministic"})
    provider_count = sum(1 for profile in profiles if profile["mode"] == "provider")
    status = "ready" if settings.llm_api_key_present and not settings.default_mock else "attention"
    warnings = list(gateway.get("warnings") or [])
    if settings.default_mock:
        warnings.append("当前默认启用模拟生成，真实模型画像只作为配置建议。")

    return {
        "version": VERSION,
        "mode": "read_only_llm_profile_assignment",
        "status": status,
        "summary": {
            "profile_count": len(profiles),
            "provider_profile_count": provider_count,
            "mock_or_deterministic_count": mock_count,
            "writes_artifacts": False,
            "external_services_required": False,
            "plaintext_key_returned": False,
        },
        "routing": {
            "llm_route": routing.get("llm_route") or "mock",
            "visual_route": routing.get("visual_route") or "placeholder",
            "fallback_policy": routing.get("fallback_policy") or "mock/placeholder",
        },
        "profiles": profiles,
        "warnings": warnings,
        "boundaries": [
            "只读汇总当前模型路由矩阵与本地任务建议。",
            "不测试连接，不发起模型请求，不写入环境变量或配置文件。",
            "不返回明文密钥，也不返回密钥环境变量名。",
        ],
        "next_steps": [
            "先用任务画像统一模型、温度、预算和降级口径。",
            "后续如需真实写配置，再做 opt-in 保存和审计，不默认改现有运行链路。",
        ],
    }


def _text_profile(
    *,
    profile_id: str,
    label: str,
    task_kind: str,
    route: dict[str, Any],
    model: str,
    temperature: float,
    max_tokens: int,
    budget_tier: str,
    fallback: str,
    note: str,
) -> dict[str, Any]:
    mode = str(route.get("mode") or "mock")
    provider_id = str(route.get("provider_id") or "mock")
    return {
        "id": profile_id,
        "label": label,
        "task_kind": task_kind,
        "provider_id": provider_id,
        "mode": mode,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "budget_tier": budget_tier,
        "fallback": fallback,
        "note": note,
    }


def _local_profile(
    *,
    profile_id: str,
    label: str,
    task_kind: str,
    temperature: float,
    max_tokens: int,
    budget_tier: str,
    fallback: str,
    note: str,
) -> dict[str, Any]:
    return {
        "id": profile_id,
        "label": label,
        "task_kind": task_kind,
        "provider_id": "local_deterministic",
        "mode": "deterministic",
        "model": "local_rules",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "budget_tier": budget_tier,
        "fallback": fallback,
        "note": note,
    }


def _visual_profile(
    *,
    route: dict[str, Any],
    visual_route: str,
    model: str,
) -> dict[str, Any]:
    mode = "disabled" if visual_route == "disabled" else visual_route
    return {
        "id": "visual_assets",
        "label": "视觉资产生成",
        "task_kind": "image",
        "provider_id": str(route.get("provider_id") or visual_route),
        "mode": mode,
        "model": model,
        "temperature": None,
        "max_tokens": None,
        "budget_tier": "image",
        "fallback": "placeholder",
        "note": "视觉资产失败或关闭时稳定降级为占位图。",
    }
