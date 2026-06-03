"""Bundled Release / Desktop Packaging MVP：本地发行准备只读清单。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

VERSION = "bundled-release-readiness-mvp"


def get_bundled_release_readiness(*, root_dir: Path | None = None) -> dict[str, Any]:
    """Return local packaging readiness without building or writing artifacts."""

    root = root_dir or _repo_root()
    checks = _checks(root)
    ready_count = sum(1 for item in checks if item["status"] == "ready")
    attention_count = sum(1 for item in checks if item["status"] == "attention")
    targets = _package_targets()
    return {
        "version": VERSION,
        "mode": "read_only_packaging_readiness",
        "status": "ready" if attention_count == 0 else "attention",
        "summary": {
            "check_count": len(checks),
            "ready_count": ready_count,
            "attention_count": attention_count,
            "deferred_target_count": len(targets),
            "writes_artifacts": False,
            "external_services_required": False,
            "plaintext_key_returned": False,
            "builds_package": False,
            "bundles_runtime": False,
        },
        "checks": checks,
        "package_targets": targets,
        "boundaries": [
            "只读检查本地发行准备度，不创建安装包或桌面壳。",
            "不内置 Python、Node、pnpm runtime，也不自动升级。",
            "不读取、不返回也不记录明文密钥。",
            "不上传文件，不接 GitHub Release、对象存储或云端部署。",
        ],
        "next_steps": [
            "先补齐脚本、README、前端构建和本地日志口径。",
            "后续如需安装包，再做 opt-in packager spike，并明确 runtime、签名和密钥注入方式。",
        ],
        "warnings": [
            f"{item['label']} 仍需补齐：{item['next_step']}"
            for item in checks
            if item["status"] == "attention"
        ],
    }


def _checks(root: Path) -> list[dict[str, Any]]:
    return [
        _file_check(
            root,
            "windows_start_script",
            "Windows 一键启动脚本",
            "scripts/start-local.ps1",
            "补齐 Windows 启动脚本，保持 CheckOnly 和 NoBrowser 可用。",
        ),
        _file_check(
            root,
            "unix_start_script",
            "macOS / Linux 一键启动脚本",
            "scripts/start-local.sh",
            "补齐 shell 启动脚本，保持 check-only 和 no-browser 可用。",
        ),
        _file_check(
            root,
            "backend_package",
            "后端 Python 包声明",
            "engine/pyproject.toml",
            "确认后端可通过 editable install 安装。",
        ),
        _file_check(
            root,
            "frontend_package",
            "前端 package 声明",
            "engine/ui/package.json",
            "确认前端依赖与 build 脚本存在。",
        ),
        _file_check(
            root,
            "frontend_dist",
            "前端静态构建产物",
            "engine/ui/dist/index.html",
            "执行 pnpm run build 生成 dist 入口。",
        ),
        _file_check(
            root,
            "distribution_plan",
            "发行路径说明",
            "docs/distribution-phase-plan.md",
            "补齐本地 clone、安装包和服务器体验的边界说明。",
        ),
        _file_check(
            root,
            "readme_local_run",
            "README 本地运行说明",
            "engine/README.md",
            "在 README 保留本地启动、配置和验证命令。",
        ),
        {
            "id": "secret_boundary",
            "label": "密钥边界",
            "status": "ready",
            "status_label": "已具备",
            "evidence": "设置页与 API 只展示脱敏状态；发行准备清单不读取明文密钥。",
            "source_path": "service/runtime_settings.py",
            "next_step": "安装包阶段继续使用用户本机配置或安全注入，不内置密钥。",
        },
    ]


def _file_check(
    root: Path,
    check_id: str,
    label: str,
    rel_path: str,
    next_step: str,
) -> dict[str, Any]:
    path = root / Path(rel_path)
    ready = path.is_file()
    return {
        "id": check_id,
        "label": label,
        "status": "ready" if ready else "attention",
        "status_label": "已具备" if ready else "需留意",
        "evidence": rel_path if ready else "未找到",
        "source_path": rel_path,
        "bytes": path.stat().st_size if ready else 0,
        "next_step": "保持当前文件随发行流程同步。" if ready else next_step,
    }


def _package_targets() -> list[dict[str, str]]:
    return [
        {
            "id": "windows_release_zip",
            "label": "Windows 解压即用包",
            "status": "deferred",
            "reason": "需要先确定是否内置 runtime、如何启动后端和前端。",
        },
        {
            "id": "macos_app_or_dmg",
            "label": "macOS app / dmg",
            "status": "deferred",
            "reason": "需要后续处理签名、权限提示和启动器形态。",
        },
        {
            "id": "desktop_shell",
            "label": "桌面壳",
            "status": "deferred",
            "reason": "需要先稳定本地 API 契约，再评估 Tauri/Electron 等壳层。",
        },
        {
            "id": "bundled_runtime",
            "label": "内置 runtime",
            "status": "deferred",
            "reason": "需要明确 Python/Node/pnpm 的内置或 bootstrap 策略。",
        },
    ]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
