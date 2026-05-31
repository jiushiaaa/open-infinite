"""v1.0-beta Permission Matrix Draft-C."""

from __future__ import annotations

from typing import Any

_VERSION = "v1.0-beta-permission-matrix-draft-c"


def _resource(
    *,
    resource_id: str,
    label: str,
    current_endpoints: list[str],
    permissions: dict[str, list[str]],
    notes: list[str],
) -> dict[str, Any]:
    return {
        "id": resource_id,
        "label": label,
        "current_endpoints": current_endpoints,
        "permissions": permissions,
        "notes": notes,
    }


def get_permission_matrix_draft() -> dict[str, Any]:
    """Return a read-only owner/editor/viewer permission matrix draft.

    This report is documentation-as-data: it does not authenticate users or
    enforce the matrix at runtime.
    """

    resources = [
        _resource(
            resource_id="project_workspace",
            label="项目工作台与项目资产",
            current_endpoints=[
                "GET /api/stories/<slug>/project-workspace",
                "GET /api/stories/<slug>",
                "GET /api/stories/<slug>/anchor",
            ],
            permissions={
                "owner": ["read", "manage_project"],
                "editor": ["read"],
                "viewer": ["read"],
            },
            notes=["当前只有本地单用户语义，manage_project 尚未绑定真实账号。"],
        ),
        _resource(
            resource_id="master_setting",
            label="设定工作台轻编辑",
            current_endpoints=[
                "GET /api/stories/<slug>/project-workspace",
                "POST /api/stories/<slug>/master-setting",
            ],
            permissions={
                "owner": ["read", "write"],
                "editor": ["read", "write"],
                "viewer": ["read"],
            },
            notes=["写入仍由白名单字段、备份和 400/409 降级保护。"],
        ),
        _resource(
            resource_id="worldline_selection",
            label="选择世界线与继续起点",
            current_endpoints=[
                "GET /api/stories/<slug>/selected-worldline",
                "POST /api/stories/<slug>/selected-worldline",
            ],
            permissions={
                "owner": ["read", "write"],
                "editor": ["read", "write"],
                "viewer": ["read"],
            },
            notes=["选择记录只影响项目工作台读回，不驱动 runner。"],
        ),
        _resource(
            resource_id="generation_actions",
            label="生成、续写、干预与状态覆盖",
            current_endpoints=[
                "POST /api/interventions",
                "POST /api/jobs/resume-continue",
                "POST /api/runs/<run_id>/state-execution-apply",
                "POST /api/runs/<run_id>/state-execution-rollback",
            ],
            permissions={
                "owner": ["read_status", "execute"],
                "editor": ["read_status", "execute"],
                "viewer": ["read_status"],
            },
            notes=["执行类动作仍需显式确认或 job 状态，不默认赋予 viewer。"],
        ),
        _resource(
            resource_id="audit_log",
            label="项目审计日志",
            current_endpoints=[
                "GET /api/stories/<slug>/audit-log",
                "POST /api/stories/<slug>/audit-log/events",
            ],
            permissions={
                "owner": ["read", "append"],
                "editor": ["read", "append"],
                "viewer": ["read"],
            },
            notes=[
                "Append Policy-I 当前只允许白名单事件本地追加；不代表已接认证或不可篡改审计存储。"
            ],
        ),
        _resource(
            resource_id="exports",
            label="章节导出与合集导出",
            current_endpoints=[
                "GET /api/runs/<run_id>/branches/<branch_id>/chapter-export",
                "GET /api/runs/<run_id>/branches/<branch_id>/chapter-collection-export",
            ],
            permissions={
                "owner": ["read", "export"],
                "editor": ["read", "export"],
                "viewer": ["read"],
            },
            notes=["公开分享或商用前仍需版权确认；viewer 默认不授予 export。"],
        ),
    ]

    return {
        "version": _VERSION,
        "status": "draft",
        "enforcement": {
            "mode": "not_enforced",
            "reason": "当前尚无真实认证、团队空间或请求上下文，本矩阵只作为后续平台化输入。",
        },
        "roles": [
            {
                "id": "owner",
                "label": "拥有者",
                "description": "本地项目创建者或未来团队空间 owner。",
            },
            {
                "id": "editor",
                "label": "协作者",
                "description": "可编辑设定、执行生成和补齐审计的协作角色。",
            },
            {
                "id": "viewer",
                "label": "只读者",
                "description": "可阅读项目、审计和章节，但不触发写入或导出。",
            },
        ],
        "resources": resources,
        "deferred_actions": [
            {
                "id": "auth_provider",
                "label": "接入真实认证身份",
                "reason": "需要外部用户/团队部署边界后再实现。",
            },
            {
                "id": "request_context_enforcement",
                "label": "请求级权限拦截",
                "reason": "当前 HTTP 服务没有用户上下文，不能伪装已强制执行。",
            },
            {
                "id": "team_project_acl",
                "label": "团队项目 ACL",
                "reason": "需与账号、项目空间和云端持久化一起设计。",
            },
        ],
        "next_steps": [
            "下一刀可补项目级版权/来源声明，让 export 权限有明确权利依据。",
            "接真实认证前，所有权限结论仅作为产品和 API 设计草案。",
            "未来接入请求上下文后，再把矩阵逐步变成服务端 guardrail。",
        ],
    }
