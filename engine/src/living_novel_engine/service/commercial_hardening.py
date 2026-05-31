"""v1.0-beta Commercial Hardening Scope-A.

只读整理商业化加固范围：先明确本地优先边界和延后项，不直接进入云端
多租户、对象存储、计费或权限系统实现。
"""

from __future__ import annotations

from typing import Any

_VERSION = "v1.0-beta-commercial-hardening-scope-a"


def _domain(
    *,
    domain_id: str,
    label: str,
    current_coverage: list[str],
    gaps: list[str],
    local_first_next: str,
    platform_next: str,
    risk_level: str,
    decision: str,
) -> dict[str, Any]:
    return {
        "id": domain_id,
        "label": label,
        "decision": decision,
        "risk_level": risk_level,
        "current_coverage": current_coverage,
        "gaps": gaps,
        "local_first_next": local_first_next,
        "platform_next": platform_next,
    }


def get_commercial_hardening_scope() -> dict[str, Any]:
    """Return a read-only v1.0-beta hardening scope report.

    The report intentionally avoids reading secrets, creating clients, writing files,
    or implying that platform work has started.
    """

    domains = [
        _domain(
            domain_id="account_project_space",
            label="账号与项目空间",
            decision="defer_platform_implementation",
            risk_level="high",
            current_coverage=[
                "本地 projects/ 与 samples/ 已区分用户导入项目和内置样例。",
                "长篇项目工作台已按故事 slug 聚合项目资产、审计和创作闭环。",
            ],
            gaps=[
                "没有真实账号、团队空间、跨设备项目归属或成员管理。",
                "本地文件目录仍是单用户使用假设。",
            ],
            local_first_next="先定义项目空间清单和迁移边界，保持本地 artifact 可被后续平台层托管。",
            platform_next="接真实外部用户前再设计账号、团队、成员与项目归属模型。",
        ),
        _domain(
            domain_id="permission_model",
            label="权限模型",
            decision="define_before_build",
            risk_level="high",
            current_coverage=[
                "HTTP-facing slug/run_id/branch_id 已走安全校验。",
                "写操作多处已有确认、白名单字段和 400/404/409 降级。",
            ],
            gaps=[
                "没有 owner/editor/viewer 角色，也没有项目级访问控制列表。",
                "尚未定义导入原文、holdout 私有集、导出章节的访问边界。",
            ],
            local_first_next="先把本地项目能力映射为 owner/editor/viewer 权限矩阵，不接认证系统。",
            platform_next="平台化时把权限矩阵接入真实认证和团队空间。",
        ),
        _domain(
            domain_id="cloud_persistence",
            label="云端持久化",
            decision="defer_platform_implementation",
            risk_level="high",
            current_coverage=[
                "核心产物保持文件型 artifact，可审计、可导出、可回放。",
                "断点续传、项目工作台、选择世界线和 closeout 记录已能本地持久化。",
            ],
            gaps=[
                "没有对象存储、数据库、云端队列或跨机器恢复。",
                "没有数据保留、删除、备份和迁移策略。",
            ],
            local_first_next="先沉淀 artifact 目录到平台资源的映射表和数据保留规则。",
            platform_next="真实团队试用前再接对象存储、数据库和持久队列。",
        ),
        _domain(
            domain_id="quota_cost_guard",
            label="配额与成本护栏",
            decision="extend_lite_controls",
            risk_level="medium",
            current_coverage=[
                "Provider & Cost Gateway Lite 已有脱敏 provider 状态、usage 汇总和手动单价估算。",
                "未配置模型时默认 mock/占位降级，测试可隔离外网调用。",
            ],
            gaps=[
                "没有用户级、项目级或团队级调用配额。",
                "没有预算阈值、超额拦截或成本告警。",
            ],
            local_first_next="先给本地设置层定义项目级软配额报告和超额 warning。",
            platform_next="平台化时接入真实计费、余额、账单和限流系统。",
        ),
        _domain(
            domain_id="audit_log",
            label="审计日志",
            decision="safe_local_candidate",
            risk_level="medium",
            current_coverage=[
                "多数关键动作已有 additive artifact：导入报告、评审、回放、导出 guard、状态 overlay 报告。",
                "creation loop closeout 能给出收口证据。",
            ],
            gaps=[
                "缺少统一的操作审计日志 schema。",
                "无法按项目连续追踪导入、设置修改、导出、状态覆盖和回滚。",
            ],
            local_first_next="优先做本地 project_audit_log.jsonl schema 与只读聚合，不改变既有 artifact。",
            platform_next="平台化后把审计日志落到不可篡改或追加式后端存储。",
        ),
        _domain(
            domain_id="copyright_share_guard",
            label="版权与分享边界",
            decision="extend_existing_guard",
            risk_level="high",
            current_coverage=[
                "导出章节和合集已有中文版权与分享 guard。",
                "产品文档明确不默认公开分享受保护文本续写。",
            ],
            gaps=[
                "没有项目级版权来源声明、授权记录或公开分享审批。",
                "没有面向团队协作的内容可见性和导出风险分级。",
            ],
            local_first_next="先增加项目级版权/来源声明状态，延续本地导出前确认。",
            platform_next="公开发布或商业使用前再接授权证明、分享审批和内容风控。",
        ),
        _domain(
            domain_id="deployment_observability",
            label="部署与观测",
            decision="define_before_build",
            risk_level="medium",
            current_coverage=[
                "本地 CLI/API/前端构建已有稳定验证门禁。",
                "服务端错误多数可降级为明确 400/404/409 或前端空态。",
            ],
            gaps=[
                "没有线上部署拓扑、健康检查、指标、日志聚合或告警策略。",
                "没有真实用户会话、任务队列和长耗时任务观测。",
            ],
            local_first_next="先定义最小健康检查、错误分类和本地 smoke checklist。",
            platform_next="外部试用前再接部署、日志、指标、告警和运行时追踪。",
        ),
    ]

    return {
        "version": _VERSION,
        "status": "scope_defined",
        "stage": "local_first_scope_review",
        "scope": {
            "name": "Commercial Hardening Scope-A",
            "implementation_mode": "read_only_scope_report",
            "principle": "先确认商业化边界与本地可推进项，再决定是否进入平台化实现。",
            "source_documents": [
                "memory.md",
                "docs/living-novel-engine-iteration-plan.md",
                "docs/productization-phase-map.md",
                "docs/living-novel-engine-prd.md",
                "engine/README.md",
            ],
        },
        "local_first_boundaries": [
            {
                "id": "no_cloud_migration_by_default",
                "label": "不默认迁移云端存储",
                "status": "active",
            },
            {
                "id": "no_multi_tenant_auth_by_default",
                "label": "不默认接多租户账号权限",
                "status": "active",
            },
            {
                "id": "no_billing_system_by_default",
                "label": "不默认接商业计费系统",
                "status": "active",
            },
            {
                "id": "preserve_artifact_contracts",
                "label": "继续保持既有 artifact 契约 additive",
                "status": "active",
            },
        ],
        "domains": domains,
        "ready_actions": [
            {
                "id": "project_audit_log_schema",
                "label": "定义本地项目审计日志 schema 与只读聚合",
                "status": "candidate",
            },
            {
                "id": "permission_matrix_draft",
                "label": "把现有写操作映射为 owner/editor/viewer 权限矩阵草案",
                "status": "candidate",
            },
            {
                "id": "project_copyright_statement",
                "label": "补项目级版权/来源声明状态",
                "status": "candidate",
            },
        ],
        "deferred_actions": [
            {
                "id": "multi_tenant_auth",
                "label": "真实多租户账号、团队与成员系统",
                "reason": "需要外部用户/团队使用场景和部署边界后再定。",
            },
            {
                "id": "cloud_object_storage",
                "label": "对象存储、数据库和跨设备恢复",
                "reason": "当前文件型 artifact 仍是本地优先，先定义映射和保留策略。",
            },
            {
                "id": "billing_system",
                "label": "付费、余额、账单和硬配额",
                "reason": "v0.9.1 仅有用量与手动成本估算，真实计费需另立平台化方案。",
            },
        ],
        "next_steps": [
            "优先落地本地 project_audit_log.jsonl schema 与只读审计聚合。",
            "随后补 owner/editor/viewer 权限矩阵草案，但暂不接真实认证。",
            "版权声明继续沿用本地导出 guard，公开分享和商业发布留到平台化阶段。",
        ],
    }
