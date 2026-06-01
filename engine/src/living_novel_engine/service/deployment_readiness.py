"""v1.0-beta Local Deployment Readiness-F：本地部署就绪清单。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir, projects_dir, static_dir
from living_novel_engine.service.runtime_settings import get_runtime_settings

VERSION = "v1.0-beta-local-deployment-readiness-f"
SMOKE_CHECKLIST_VERSION = "v1.0-beta-settings-local-smoke-checklist-q"

_STATIC_ASSETS = ("index.html", "app.js", "style.css")


def get_local_deployment_readiness(
    *,
    static_root: Path | None = None,
    outputs_root: Path | None = None,
    projects_root: Path | None = None,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a read-only local deployment checklist.

    The report is intentionally local-first: it inspects filesystem readiness,
    runtime redaction and smoke-test routes, but it does not bind ports, make
    outbound calls, or persist deployment state.
    """

    static = static_root or static_dir()
    outputs = outputs_root or outputs_dir()
    projects = projects_root or projects_dir()
    static_assets = _static_assets(static)
    static_ready = all(item["status"] == "ready" for item in static_assets)
    data_dirs = _data_directories(outputs, projects)
    data_ready = all(item["status"] == "ready" for item in data_dirs)
    settings = get_runtime_settings()
    checks = [
        {
            "id": "backend_http",
            "label": "本地后端 HTTP 入口",
            "status": "ready",
            "evidence": f"http://{api_host}:{api_port}/",
        },
        {
            "id": "frontend_static",
            "label": "前端静态资源",
            "status": "ready" if static_ready else "attention",
            "assets": static_assets,
        },
        {
            "id": "runtime_environment",
            "label": "运行环境脱敏",
            "status": "ready",
            "evidence": "仅返回密钥是否存在与脱敏尾号；不返回明文密钥或变量名。",
        },
        {
            "id": "data_directories",
            "label": "本地数据目录",
            "status": "ready" if data_ready else "attention",
            "directories": data_dirs,
        },
        {
            "id": "api_smoke_plan",
            "label": "API 冒烟路径",
            "status": "ready",
            "routes": _api_smoke_plan(),
        },
    ]
    warnings = [
        item["message"]
        for item in [
            {
                "message": "前端静态资源不完整，请先执行前端构建。",
                "active": not static_ready,
            },
            {
                "message": "本地数据目录尚未就绪，请确认输出与项目目录可用。",
                "active": not data_ready,
            },
        ]
        if item["active"]
    ]

    return {
        "version": VERSION,
        "status": "ready" if not warnings else "attention",
        "readiness": {
            "http_entrypoint": f"http://{api_host}:{api_port}/",
            "frontend_static_ready": static_ready,
            "data_directories_ready": data_ready,
            "secrets_redacted": True,
            "external_services_required": False,
        },
        "environment": {
            "mode": "mock" if settings.default_mock else "provider",
            "llm_key": {
                "present": settings.llm_api_key_present,
                "masked": settings.masked_key,
            },
            "seedream_key": {
                "present": settings.seedream_key_present,
                "masked": settings.seedream_masked_key,
            },
            "visual_assets_enabled": settings.visual_assets_enabled,
        },
        "checks": checks,
        "api_smoke_plan": _api_smoke_plan(),
        "run_steps": [
            "在 engine 目录安装依赖并准备 Python 环境。",
            "执行 lne browse 启动本地后端。",
            "打开本地后端入口，确认故事列表与设置接口返回 200。",
        ],
        "verification_steps": [
            "cd engine && python -m pytest -q",
            "cd engine/ui && pnpm run build",
            "cd .. && git diff --check",
        ],
        "observability": {
            "mode": "local_process",
            "quota_endpoint": "/api/settings/quota-observability",
            "deployment_state": "not_persisted",
        },
        "warnings": warnings,
        "next_steps": [
            "补真实部署前的端口占用与进程守护检查。",
            "上线前再接云端托管、对象存储、多用户账号与外部监控。",
        ],
    }


def get_settings_local_smoke_checklist(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a read-only local smoke checklist for the settings drawer.

    This is a checklist, not a runner: it does not perform HTTP requests, bind
    ports, persist state, or require external model providers.
    """

    checks = _settings_smoke_checks(api_host=api_host, api_port=api_port)
    return {
        "version": SMOKE_CHECKLIST_VERSION,
        "status": "ready",
        "mode": "read_only_local_smoke_checklist",
        "summary": {
            "check_count": len(checks),
            "ready_to_run_count": len(checks),
            "external_services_required": False,
        },
        "checks": checks,
        "run_steps": [
            "在 engine 目录执行 lne browse 启动本地后端。",
            "在 engine/ui 目录执行 pnpm run dev 启动 Vite。",
            "打开 Vite 首页，再按清单核对设置页和项目审计相关接口。",
        ],
        "warnings": [],
        "next_steps": [
            "本清单只验证本地 HTTP/API 冒烟，不代表真实外部部署验收。",
            "真实外部用户阶段再补进程守护、认证、对象存储和云端观测。",
        ],
    }


def _static_assets(root: Path) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    for name in _STATIC_ASSETS:
        path = root / name
        assets.append(
            {
                "name": name,
                "status": "ready" if path.is_file() else "missing",
                "bytes": path.stat().st_size if path.is_file() else 0,
            }
        )
    return assets


def _data_directories(outputs: Path, projects: Path) -> list[dict[str, str]]:
    return [
        {
            "id": "outputs",
            "label": "运行输出目录",
            "status": "ready" if outputs.exists() and outputs.is_dir() else "missing",
        },
        {
            "id": "projects",
            "label": "长篇项目目录",
            "status": "ready" if projects.exists() and projects.is_dir() else "missing",
        },
    ]


def _api_smoke_plan() -> list[dict[str, str]]:
    return [
        {"method": "GET", "path": "/", "expected": "200 HTML"},
        {"method": "GET", "path": "/api/stories", "expected": "200 JSON"},
        {"method": "GET", "path": "/api/settings/runtime", "expected": "200 JSON"},
        {"method": "GET", "path": "/api/settings/providers", "expected": "200 JSON"},
        {
            "method": "GET",
            "path": "/api/settings/quota-observability",
            "expected": "200 JSON",
        },
    ]


def _settings_smoke_checks(api_host: str, api_port: int) -> list[dict[str, str]]:
    base = f"http://{api_host}:{api_port}"
    specs = [
        ("/", "Vite 或静态首页", "200 HTML"),
        ("/api/stories", "故事列表", "200 JSON"),
        ("/api/settings/runtime", "运行设置脱敏", "200 JSON，不含明文密钥"),
        ("/api/settings/providers", "模型与路由状态", "200 JSON"),
        ("/api/settings/provider-usage", "模型用量聚合", "200 JSON"),
        ("/api/settings/quota-observability", "配额与观测摘要", "200 JSON"),
        ("/api/settings/deployment-readiness", "本地部署就绪", "200 JSON"),
        ("/api/settings/commercial-status-overview", "商业化状态总览", "200 JSON"),
        ("/api/stories/<slug>/project-workspace", "项目工作台", "200 JSON，需替换 slug"),
        ("/api/stories/<slug>/audit-log/export", "项目审计导出", "200 JSON，需替换 slug"),
    ]
    return [
        {
            "id": f"smoke_{index}",
            "label": label,
            "method": "GET",
            "path": path,
            "expected": expected,
            "status": "ready_to_run",
            "example_url": f"{base}{path}",
        }
        for index, (path, label, expected) in enumerate(specs, start=1)
    ]
