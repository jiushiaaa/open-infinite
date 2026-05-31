"""console-free 运行设置（v0.7 第八刀：真实 LLM / 运行设置面板）。

把开发者参数（API Key / base_url / model / mock / rounds / runner）暴露给 Web 设置，
只写入当前 Python 进程环境变量，**不落盘、不返回明文 Key、不写 localStorage**。
本地单机设置，不做账号系统 / 云端密钥管理。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

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
        "cost_policy": {
            "currency": "USD",
            "estimation_mode": "usage_metadata_only",
            "price_table_status": "not_configured",
            "estimated_total": None,
            "usage_fields": ["prompt_tokens", "completion_tokens", "total_tokens"],
            "note": "当前只汇总 token 用量来源；精确价格表留给后续按 provider 配置。",
        },
        "warnings": warnings,
    }


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
