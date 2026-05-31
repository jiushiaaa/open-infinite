"""v1.0-beta Account Project Space Boundary-H：账号与项目空间边界。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir, projects_dir, samples_dir

VERSION = "v1.0-beta-account-project-space-boundary-h"


def get_account_project_space_boundary(
    *,
    projects_root: Path | None = None,
    samples_root: Path | None = None,
    outputs_root: Path | None = None,
) -> dict[str, Any]:
    """Return a read-only local project-space boundary report."""

    projects = projects_root or projects_dir()
    samples = samples_root or samples_dir()
    outputs = outputs_root or outputs_dir()
    inventory = _local_inventory(projects, samples, outputs)

    return {
        "version": VERSION,
        "status": "boundary_defined",
        "account_model": {
            "mode": "local_single_operator",
            "source_of_truth": "local_file_artifacts",
            "auth_provider": "not_configured",
            "team_space": "not_configured",
            "principle": "先把本地项目空间语义讲清楚，再决定是否接账号、团队和 ACL。",
        },
        "local_inventory": inventory,
        "project_spaces": _project_spaces(),
        "future_metadata_fields": _future_metadata_fields(),
        "migration_boundaries": _migration_boundaries(),
        "enforcement": {
            "mode": "not_enforced",
            "reason": "当前 HTTP 服务没有用户上下文，不能伪装成已接认证或团队权限。",
        },
        "deferred_actions": [
            {
                "id": "auth_provider",
                "label": "接入真实登录身份",
                "reason": "需要先确定外部用户、部署边界和项目归属策略。",
            },
            {
                "id": "team_space",
                "label": "团队空间与成员管理",
                "reason": "需与 owner/editor/viewer 权限矩阵和云端持久化一起设计。",
            },
            {
                "id": "acl_enforcement",
                "label": "请求级 ACL 拦截",
                "reason": "当前只定义边界，不改变现有本地单用户行为。",
            },
        ],
        "warnings": [
            {
                "code": "account_space_not_enforced",
                "message": "当前只是账号与项目空间边界报告，不会鉴权、建团队或迁移项目。",
            }
        ],
        "next_steps": [
            "先把本地项目、内置样例、run 产物和世界线选择的归属语义写成产品口径。",
            "再为账号、团队空间和项目 ACL 分别定义最小可验证 adapter。",
            "真实外部用户前再接认证 provider、成员邀请和跨设备项目同步。",
        ],
    }


def _count_dirs(root: Path, *, prefix: str | None = None) -> int:
    try:
        if not root.exists() or not root.is_dir():
            return 0
        return sum(
            1
            for item in root.iterdir()
            if item.is_dir() and (prefix is None or item.name.startswith(prefix))
        )
    except OSError:
        return 0


def _count_selection_files(outputs: Path) -> int:
    root = outputs / "story_selections"
    try:
        if not root.exists() or not root.is_dir():
            return 0
        return sum(1 for item in root.glob("*/selected_worldline.json") if item.is_file())
    except OSError:
        return 0


def _local_inventory(projects: Path, samples: Path, outputs: Path) -> dict[str, Any]:
    return {
        "imported_project_count": _count_dirs(projects),
        "sample_project_count": _count_dirs(samples),
        "run_count": _count_dirs(outputs, prefix="run_"),
        "selection_count": _count_selection_files(outputs),
        "roots": [
            {
                "id": "imported_projects",
                "pattern": "projects/<story_slug>/",
                "status": "present" if projects.exists() else "missing",
            },
            {
                "id": "bundled_samples",
                "pattern": "samples/<sample_slug>/",
                "status": "present" if samples.exists() else "missing",
            },
            {
                "id": "generated_runs",
                "pattern": "outputs/run_*/",
                "status": "present" if outputs.exists() else "missing",
            },
            {
                "id": "selected_worldlines",
                "pattern": "outputs/story_selections/<story_slug>/selected_worldline.json",
                "status": "present" if _count_selection_files(outputs) else "missing",
            },
        ],
    }


def _project_spaces() -> list[dict[str, str]]:
    return [
        {
            "id": "imported_projects",
            "local_pattern": "projects/<story_slug>/",
            "current_owner": "local_operator",
            "future_space": "account_or_team_project",
            "access_default": "owner_private",
            "migration_rule": "slug 可作为本地项目 id，但不能替代账号身份或团队归属。",
        },
        {
            "id": "bundled_samples",
            "local_pattern": "samples/<sample_slug>/",
            "current_owner": "engine_builtin",
            "future_space": "shared_read_only_catalog",
            "access_default": "read_only",
            "migration_rule": "内置样例默认作为只读模板，不写入用户项目空间。",
        },
        {
            "id": "generated_runs",
            "local_pattern": "outputs/run_*/",
            "current_owner": "linked_local_project_or_sample",
            "future_space": "project_run_artifacts",
            "access_default": "project_members",
            "migration_rule": "迁移时需要绑定 story_slug、owner/team 和父链关系。",
        },
        {
            "id": "selected_worldlines",
            "local_pattern": "outputs/story_selections/<story_slug>/selected_worldline.json",
            "current_owner": "linked_local_project",
            "future_space": "project_decision_state",
            "access_default": "project_editors",
            "migration_rule": "作为项目决策状态迁移，继续保持 run/branch 安全校验。",
        },
    ]


def _future_metadata_fields() -> list[dict[str, str]]:
    return [
        {
            "id": "owner_account_id",
            "purpose": "标记项目拥有者",
            "status": "planned_not_written",
        },
        {
            "id": "team_id",
            "purpose": "标记项目所属团队或空间",
            "status": "planned_not_written",
        },
        {
            "id": "visibility",
            "purpose": "区分 owner_private、project_members、shared_read_only 等可见性",
            "status": "planned_not_written",
        },
        {
            "id": "created_by",
            "purpose": "记录创建者身份，供审计日志引用",
            "status": "planned_not_written",
        },
    ]


def _migration_boundaries() -> list[dict[str, str]]:
    return [
        {
            "id": "slug_is_not_identity",
            "rule": "story_slug 只能定位本地项目，不等同于账号、团队或权限主体。",
        },
        {
            "id": "samples_are_read_only",
            "rule": "samples/ 是引擎内置只读目录，不能被当成用户私有项目直接写入。",
        },
        {
            "id": "runs_inherit_project_space",
            "rule": "outputs/run_* 未来必须继承对应项目空间，不单独创建账号归属。",
        },
        {
            "id": "no_cross_device_sync_yet",
            "rule": "当前报告不承诺跨设备同步，真实同步需等云端持久化 adapter。",
        },
    ]
