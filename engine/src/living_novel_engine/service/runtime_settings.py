"""console-free 运行设置（v0.7 第八刀：真实 LLM / 运行设置面板）。

把开发者参数（API Key / base_url / model / mock / rounds / runner）暴露给 Web 设置，
只写入当前 Python 进程环境变量，**不落盘、不返回明文 Key、不写 localStorage**。
本地单机设置，不做账号系统 / 云端密钥管理。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.llm.client import LLMClient, LLMSettings
from living_novel_engine.orchestrator import available_runners
from living_novel_engine.visual_assets.seedream_client import (
    DEFAULT_BASE_URL as _SD_DEFAULT_BASE,
)
from living_novel_engine.visual_assets.seedream_client import (
    DEFAULT_MODEL as _SD_DEFAULT_MODEL,
)
from living_novel_engine.visual_assets.seedream_client import SeedreamSettings

# 进程内环境变量键（与既有引擎读取保持一致）。
_KEY = "LLM_API_KEY"
_BASE = "LLM_BASE_URL"
_MODEL = "LLM_MODEL_NAME"
_MOCK = "LNE_MOCK"
_ROUNDS = "LNE_DEFAULT_ROUNDS"
_RUNNER = "LNE_SCENE_RUNNER"
_COST_INPUT = "LNE_LLM_INPUT_COST_PER_1K"
_COST_OUTPUT = "LNE_LLM_OUTPUT_COST_PER_1K"

_SD_KEY = "SEEDREAM_API_KEY"
_SD_BASE = "SEEDREAM_BASE_URL"
_SD_MODEL = "SEEDREAM_MODEL"
_VISUAL_FLAG = "LNE_VISUAL_ASSETS"

_DEFAULT_BASE = "https://api.openai.com/v1"
_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_ROUNDS = 4
_DEFAULT_RUNNER = "lightweight"
_ROUNDS_MIN, _ROUNDS_MAX = 1, 12


class SettingsError(ValueError):
    """设置入参非法（rounds 越界、runner 非法）——映射为 HTTP 400。"""


@dataclass
class RuntimeSettings:
    llm_api_key_present: bool
    masked_key: str
    llm_base_url: str
    llm_model_name: str
    default_mock: bool
    default_rounds: int
    default_runner: str
    available_runners: list[str]
    seedream_enabled: bool = False
    visual_assets_enabled: bool = True
    seedream_key_present: bool = False
    seedream_masked_key: str = ""
    seedream_base_url: str = _SD_DEFAULT_BASE
    seedream_model: str = _SD_DEFAULT_MODEL
    llm_input_cost_per_1k: float = 0.0
    llm_output_cost_per_1k: float = 0.0

    def as_dict(self) -> dict:
        return {
            "llm_api_key_present": self.llm_api_key_present,
            "masked_key": self.masked_key,
            "llm_base_url": self.llm_base_url,
            "llm_model_name": self.llm_model_name,
            "default_mock": self.default_mock,
            "default_rounds": self.default_rounds,
            "default_runner": self.default_runner,
            "available_runners": self.available_runners,
            "seedream_enabled": self.seedream_enabled,
            "visual_assets_enabled": self.visual_assets_enabled,
            "seedream_key_present": self.seedream_key_present,
            "seedream_masked_key": self.seedream_masked_key,
            "seedream_base_url": self.seedream_base_url,
            "seedream_model": self.seedream_model,
            "llm_input_cost_per_1k": self.llm_input_cost_per_1k,
            "llm_output_cost_per_1k": self.llm_output_cost_per_1k,
        }


def _mask_key(key: str) -> str:
    """脱敏展示：仅保留尾 4 位，其余以圆点替代。"""
    if not key:
        return ""
    if len(key) <= 4:
        return "•" * len(key)
    return "•" * 6 + key[-4:]


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


# ── 默认值解析（供 intervene / genesis / import 在请求缺省时回退） ──


def default_mock() -> bool:
    """默认是否 mock：显式 LNE_MOCK 为准；未配置时无 key 默认 True。"""
    raw = os.environ.get(_MOCK)
    if raw is not None and raw != "":
        return _truthy(raw)
    return not LLMSettings.from_env().llm_api_key


def default_rounds() -> int:
    try:
        n = int(os.environ.get(_ROUNDS, _DEFAULT_ROUNDS))
    except (TypeError, ValueError):
        return _DEFAULT_ROUNDS
    return max(_ROUNDS_MIN, min(_ROUNDS_MAX, n))


def default_runner() -> str:
    name = os.environ.get(_RUNNER, "").strip()
    runners = available_runners()
    if name and name in runners:
        return name
    return _DEFAULT_RUNNER


def _cost_rate_from_env(key: str) -> float:
    raw = os.environ.get(key, "").strip()
    if not raw:
        return 0.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 0.0


def get_runtime_settings() -> RuntimeSettings:
    settings = LLMSettings.from_env()
    key = settings.llm_api_key or ""
    sd = SeedreamSettings.from_env()
    return RuntimeSettings(
        llm_api_key_present=bool(key),
        masked_key=_mask_key(key),
        llm_base_url=settings.llm_base_url or _DEFAULT_BASE,
        llm_model_name=settings.llm_model_name or _DEFAULT_MODEL,
        default_mock=default_mock(),
        default_rounds=default_rounds(),
        default_runner=default_runner(),
        available_runners=available_runners(),
        seedream_enabled=bool(sd.enabled and sd.api_key),
        visual_assets_enabled=sd.enabled,
        seedream_key_present=bool(sd.api_key),
        seedream_masked_key=_mask_key(sd.api_key),
        seedream_base_url=sd.base_url,
        seedream_model=sd.model,
        llm_input_cost_per_1k=_cost_rate_from_env(_COST_INPUT),
        llm_output_cost_per_1k=_cost_rate_from_env(_COST_OUTPUT),
    )


def get_provider_gateway_summary() -> dict:
    """v0.9.1 Provider & Cost Gateway Lite：只读、脱敏的 provider 摘要。

    本函数不创建客户端、不做网络请求、不落盘；它只是把当前运行设置解释成
    provider 列表、路由状态、降级策略和成本观测口径，供 Web/CLI 后续复用。
    """
    settings = get_runtime_settings()
    llm_route = (
        "primary_llm"
        if settings.llm_api_key_present and not settings.default_mock
        else "mock"
    )
    if not settings.visual_assets_enabled:
        visual_route = "disabled"
    elif settings.seedream_key_present:
        visual_route = "seedream_visual"
    else:
        visual_route = "placeholder"
    llm_provider_id = "primary_llm" if llm_route == "primary_llm" else "mock"

    warnings: list[dict[str, str]] = []
    if not settings.llm_api_key_present:
        warnings.append(
            {
                "code": "llm_key_missing",
                "message": "文本模型未配置密钥，默认走本地 mock 降级。",
            }
        )
    elif settings.default_mock:
        warnings.append(
            {
                "code": "llm_mock_enabled",
                "message": "文本模型已配置密钥，但当前默认启用 mock。",
            }
        )

    if not settings.visual_assets_enabled:
        warnings.append(
            {
                "code": "visual_assets_disabled",
                "message": "视觉资产生成已关闭，前端会展示占位图。",
            }
        )
    elif not settings.seedream_key_present:
        warnings.append(
            {
                "code": "seedream_key_missing",
                "message": "视觉模型未配置密钥，生成失败时会展示占位图。",
            }
        )

    price_table_configured = (
        settings.llm_input_cost_per_1k > 0 or settings.llm_output_cost_per_1k > 0
    )

    return {
        "version": "v0.9.1-provider-cost-lite",
        "routing": {
            "mode": "single_provider",
            "llm_route": llm_route,
            "visual_route": visual_route,
            "fallback_policy": "未配置、mock 或调用失败时降级为本地 mock/占位结果。",
        },
        "providers": [
            {
                "id": "primary_llm",
                "kind": "llm",
                "display_name": "主文本模型",
                "configured": settings.llm_api_key_present,
                "active": llm_route == "primary_llm",
                "masked_key": settings.masked_key,
                "base_url": settings.llm_base_url,
                "model": settings.llm_model_name,
                "fallback": "mock",
                "usage_source": "generation_meta.usage",
            },
            {
                "id": "seedream_visual",
                "kind": "image",
                "display_name": "视觉资产模型",
                "configured": settings.seedream_key_present,
                "active": visual_route == "seedream_visual",
                "masked_key": settings.seedream_masked_key,
                "base_url": settings.seedream_base_url,
                "model": settings.seedream_model,
                "fallback": "placeholder",
                "usage_source": "visual_assets.json",
            },
        ],
        "routes": [
            {
                "id": "intervention",
                "label": "读者干预生成",
                "provider_id": llm_provider_id,
                "runner": settings.default_runner,
                "mode": "provider" if llm_route == "primary_llm" else "mock",
                "fallback": "mock",
            },
            {
                "id": "story_genesis",
                "label": "主题创世",
                "provider_id": llm_provider_id,
                "runner": None,
                "mode": "provider" if llm_route == "primary_llm" else "mock",
                "fallback": "mock",
            },
            {
                "id": "import_extraction",
                "label": "导入抽取",
                "provider_id": llm_provider_id,
                "runner": None,
                "mode": "provider" if llm_route == "primary_llm" else "mock",
                "fallback": "mock",
            },
            {
                "id": "visual_assets",
                "label": "视觉资产生成",
                "provider_id": visual_route,
                "runner": None,
                "mode": visual_route,
                "fallback": "placeholder",
            },
        ],
        "cost_policy": {
            "currency": "USD",
            "estimation_mode": "usage_metadata_only",
            "price_table_status": (
                "configured" if price_table_configured else "not_configured"
            ),
            "estimated_total": None,
            "input_cost_per_1k": settings.llm_input_cost_per_1k,
            "output_cost_per_1k": settings.llm_output_cost_per_1k,
            "usage_fields": ["prompt_tokens", "completion_tokens", "total_tokens"],
            "note": "当前只汇总 token 用量来源；精确价格表留给后续按 provider 配置。",
        },
        "warnings": warnings,
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}


def _run_story_slug(run_dir: Path) -> str:
    for name in ("meta.json", "intervention.json", "baseline_report.json"):
        data = _read_json(run_dir / name)
        slug = data.get("story_slug") or data.get("sample_slug")
        if slug:
            return str(slug)
    return "tianhuang-night"


def _usage_value(usage: dict[str, Any], key: str) -> int:
    try:
        value = usage.get(key)
        if value is None:
            return 0
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _normalize_usage(usage: dict[str, Any]) -> dict[str, int]:
    prompt = _usage_value(usage, "prompt_tokens")
    completion = _usage_value(usage, "completion_tokens")
    total = _usage_value(usage, "total_tokens") or prompt + completion
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
    }


def _usage_meta_records(run_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    compilation = _read_json(run_dir / "intervention_compilation.json")
    meta = compilation.get("generation_meta")
    if isinstance(meta, dict):
        records.append(
            {
                "artifact": "intervention_compilation.json",
                "branch_id": None,
                "meta": meta,
            }
        )

    try:
        branch_dirs = [p for p in run_dir.iterdir() if p.is_dir()]
    except OSError:
        branch_dirs = []
    for branch_dir in branch_dirs:
        trace = _read_json(branch_dir / "multi_agent_trace.json")
        meta = trace.get("generation_meta")
        if not isinstance(meta, dict):
            continue
        records.append(
            {
                "artifact": "multi_agent_trace.json",
                "branch_id": branch_dir.name,
                "meta": meta,
            }
        )
    return records


def _empty_usage() -> dict[str, int]:
    return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def _cost_estimate(totals: dict[str, int], settings: RuntimeSettings) -> dict[str, Any]:
    input_rate = settings.llm_input_cost_per_1k
    output_rate = settings.llm_output_cost_per_1k
    if input_rate <= 0 and output_rate <= 0:
        return {
            "currency": "USD",
            "estimated_total": None,
            "reason": "price_table_not_configured",
            "input_cost_per_1k": input_rate,
            "output_cost_per_1k": output_rate,
        }
    estimated = (
        totals["prompt_tokens"] / 1000 * input_rate
        + totals["completion_tokens"] / 1000 * output_rate
    )
    return {
        "currency": "USD",
        "estimated_total": round(estimated, 6),
        "reason": "configured",
        "input_cost_per_1k": input_rate,
        "output_cost_per_1k": output_rate,
    }


def get_provider_usage_summary(*, story_slug: str | None = None) -> dict:
    """汇总已有 generation_meta.usage；只用手动单价估算，不联网不改 artifact。"""
    settings = get_runtime_settings()
    root = outputs_dir()
    totals = _empty_usage()
    provider_totals: dict[str, dict[str, int]] = {"primary_llm": _empty_usage()}
    records: list[dict[str, Any]] = []
    missing_usage_record_count = 0
    run_count = 0

    try:
        run_dirs = sorted(root.iterdir(), reverse=True) if root.exists() else []
    except OSError:
        run_dirs = []

    for run_dir in run_dirs:
        try:
            if not run_dir.is_dir() or not run_dir.name.startswith("run_"):
                continue
        except OSError:
            continue
        run_slug = _run_story_slug(run_dir)
        if story_slug and run_slug != story_slug:
            continue
        run_count += 1

        for item in _usage_meta_records(run_dir):
            meta = item["meta"]
            usage = meta.get("usage")
            if not isinstance(usage, dict):
                missing_usage_record_count += 1
                continue
            normalized = _normalize_usage(usage)
            for key, value in normalized.items():
                totals[key] += value
                provider_totals["primary_llm"][key] += value
            records.append(
                {
                    "provider_id": "primary_llm",
                    "run_id": run_dir.name,
                    "branch_id": item["branch_id"],
                    "artifact": item["artifact"],
                    "source": meta.get("source"),
                    "model_name": meta.get("model_name"),
                    "usage": normalized,
                }
            )

    by_provider = [
        {
            "provider_id": provider_id,
            "record_count": sum(1 for r in records if r["provider_id"] == provider_id),
            **usage,
        }
        for provider_id, usage in provider_totals.items()
    ]

    return {
        "version": "v0.9.1-provider-usage-lite",
        "story_slug": story_slug,
        "run_count": run_count,
        "record_count": len(records),
        "missing_usage_record_count": missing_usage_record_count,
        "totals": totals,
        "by_provider": by_provider,
        "records": records[:50],
        "record_limit": 50,
        "truncated": len(records) > 50,
        "cost_estimate": _cost_estimate(totals, settings),
    }


def _parse_cost_rate(value: object, field: str) -> float:
    try:
        rate = float(value)
    except (TypeError, ValueError):
        raise SettingsError(f"{field} 须为非负数字")
    if rate < 0:
        raise SettingsError(f"{field} 须为非负数字")
    return rate


def update_runtime_settings(patch: dict) -> RuntimeSettings:
    """按白名单写入进程环境变量；不落盘。返回更新后的设置。

    抛出 SettingsError（rounds 越界 / runner 非法）→ HTTP 400。
    """
    if not isinstance(patch, dict):
        raise SettingsError("patch 须为对象")

    if "api_key" in patch:
        api_key = str(patch.get("api_key") or "")
        # 空字符串视为清除（设为空串而非 del，避免 .env 再次注入）。
        os.environ[_KEY] = api_key

    if "base_url" in patch:
        base = str(patch.get("base_url") or "").strip()
        os.environ[_BASE] = base or _DEFAULT_BASE

    if "model_name" in patch:
        model = str(patch.get("model_name") or "").strip()
        os.environ[_MODEL] = model or _DEFAULT_MODEL

    if "default_mock" in patch:
        os.environ[_MOCK] = "true" if bool(patch.get("default_mock")) else "false"

    if "default_rounds" in patch:
        try:
            n = int(patch.get("default_rounds"))
        except (TypeError, ValueError):
            raise SettingsError("default_rounds 须为整数")
        if n < _ROUNDS_MIN or n > _ROUNDS_MAX:
            raise SettingsError(f"default_rounds 须在 {_ROUNDS_MIN}-{_ROUNDS_MAX} 之间")
        os.environ[_ROUNDS] = str(n)

    if "default_runner" in patch:
        runner = str(patch.get("default_runner") or "").strip()
        if runner not in available_runners():
            raise SettingsError(
                f"未知 runner: {runner!r}；可用: {', '.join(available_runners())}"
            )
        os.environ[_RUNNER] = runner

    if "llm_input_cost_per_1k" in patch:
        os.environ[_COST_INPUT] = str(
            _parse_cost_rate(patch.get("llm_input_cost_per_1k"), "llm_input_cost_per_1k")
        )

    if "llm_output_cost_per_1k" in patch:
        os.environ[_COST_OUTPUT] = str(
            _parse_cost_rate(
                patch.get("llm_output_cost_per_1k"), "llm_output_cost_per_1k"
            )
        )

    if "seedream_api_key" in patch:
        os.environ[_SD_KEY] = str(patch.get("seedream_api_key") or "")

    if "seedream_base_url" in patch:
        base = str(patch.get("seedream_base_url") or "").strip()
        os.environ[_SD_BASE] = base or _SD_DEFAULT_BASE

    if "seedream_model" in patch:
        model = str(patch.get("seedream_model") or "").strip()
        os.environ[_SD_MODEL] = model or _SD_DEFAULT_MODEL

    if "visual_assets_enabled" in patch:
        os.environ[_VISUAL_FLAG] = (
            "1" if bool(patch.get("visual_assets_enabled")) else "0"
        )

    return get_runtime_settings()


def test_connectivity(mock: bool = False) -> dict:
    """轻量连通性检查；任何异常都被捕获，返回 available=false，不抛 500。"""
    if mock:
        return {"available": True, "mode": "mock", "model": None}

    settings = LLMSettings.from_env()
    if not settings.llm_api_key:
        return {"available": False, "reason": "未配置 API Key", "model": None}

    try:
        llm = LLMClient(settings=settings, mock=False)
        if not llm.available:
            return {"available": False, "reason": "客户端不可用", "model": None}
        # 极小请求：仅验证可达，不追求内容。
        llm.chat("connectivity check", "ping", temperature=0, max_tokens=1)
        return {"available": True, "model": settings.llm_model_name}
    except Exception as exc:  # 网络/鉴权/配额等一律降级，不 500
        return {
            "available": False,
            "reason": "连接失败",
            "error": str(exc),
            "model": settings.llm_model_name,
        }
