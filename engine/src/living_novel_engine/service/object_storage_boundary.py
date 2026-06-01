"""v1.0-beta Object Storage Boundary Checklist-V：对象存储边界只读清单。"""

from __future__ import annotations

from typing import Any

from living_novel_engine.service.auth_boundary import get_auth_boundary_checklist
from living_novel_engine.service.cloud_persistence_boundary import (
    get_cloud_persistence_boundary,
)
from living_novel_engine.service.deployment_readiness import (
    get_local_deployment_readiness,
)

VERSION = "v1.0-beta-object-storage-boundary-checklist-v"


def get_object_storage_boundary_checklist(
    *,
    api_host: str = "127.0.0.1",
    api_port: int = 8765,
) -> dict[str, Any]:
    """Return a local-first object storage boundary checklist.

    The report only maps existing local evidence to a future adapter contract.
    It does not upload files, create buckets, read secrets, or enable remote
    persistence.
    """

    cloud = get_cloud_persistence_boundary()
    deployment = get_local_deployment_readiness(api_host=api_host, api_port=api_port)
    auth = get_auth_boundary_checklist(api_host=api_host, api_port=api_port)
    resource_count = len(cloud.get("resource_map") or [])
    checks = [
        _check(
            check_id="local_artifact_inventory",
            label="本地 artifact 盘点",
            status="ready" if cloud.get("status") == "boundary_defined" else "attention",
            evidence=_inventory_evidence(cloud.get("local_inventory") or {}),
            source_endpoint="GET /api/settings/cloud-persistence-boundary",
            next_step="先保持 projects/ 与 outputs/ 为迁移源事实。",
        ),
        _check(
            check_id="resource_mapping",
            label="资源映射表",
            status="ready" if resource_count >= 5 else "attention",
            evidence=f"{resource_count} 类本地资源已映射",
            source_endpoint="GET /api/settings/cloud-persistence-boundary",
            next_step="对象存储 adapter 只应消费这些已定义资源类型。",
        ),
        _check(
            check_id="private_source_and_holdout",
            label="原文与 holdout 隔离",
            status="ready" if _has_private_source_rules(cloud.get("resource_map")) else "attention",
            evidence="source_raw 与 holdout_private 已保持私有语义",
            source_endpoint="GET /api/settings/cloud-persistence-boundary",
            next_step="接入对象存储时继续区分 owner_private、runtime_visible 与 evaluator_private。",
        ),
        _check(
            check_id="retention_input",
            label="保留策略输入",
            status="attention",
            evidence="项目级保留策略需替换 slug 后核对",
            source_endpoint="GET /api/stories/<slug>/retention-policy",
            next_step="真实迁移前先确认上传原文、生成产物、holdout 和分片的保留策略。",
        ),
        _check(
            check_id="identity_binding",
            label="项目身份绑定",
            status="attention"
            if auth.get("summary", {}).get("auth_enforced") is False
            else "ready",
            evidence="当前仍是本地单人操作模式",
            source_endpoint="GET /api/settings/auth-boundary",
            next_step="对象存储写入前必须先明确项目归属、操作者身份和权限 guardrail。",
        ),
        _check(
            check_id="adapter_contract",
            label="对象存储 adapter 合约",
            status="attention",
            evidence="尚未实现 bucket/key/presign/delete adapter",
            source_endpoint="future object storage adapter",
            next_step="先定义 adapter 输入输出、错误语义和本地 fallback，再接真实服务。",
        ),
        _check(
            check_id="remote_upload_execution",
            label="远端上传执行",
            status="attention",
            evidence="当前不会上传文件或写远端状态",
            source_endpoint="read-only checklist",
            next_step="外部用户阶段再启用真实上传、删除和失败重试。",
        ),
        _check(
            check_id="local_deployment_guard",
            label="本地部署护栏",
            status="ready" if deployment.get("status") == "ready" else "attention",
            evidence=str(deployment.get("status") or "unknown"),
            source_endpoint="GET /api/settings/deployment-readiness",
            next_step=_first_text(deployment.get("next_steps"), "先确认本地部署就绪。"),
        ),
    ]
    attention = sum(1 for item in checks if item["status"] == "attention")
    ready = len(checks) - attention
    return {
        "version": VERSION,
        "mode": "read_only_object_storage_boundary_checklist",
        "status": "ready" if attention == 0 else "attention",
        "summary": {
            "check_count": len(checks),
            "ready_count": ready,
            "attention_count": attention,
            "adapter_implemented": False,
            "remote_writes_enabled": False,
            "external_services_required": False,
        },
        "checks": checks,
        "warnings": [
            "当前只是对象存储边界清单，不创建 bucket、不生成签名 URL、不上传文件。",
        ],
        "next_steps": [
            "对象存储 adapter 前先冻结资源映射、保留策略、项目归属和错误语义。",
            "继续保持本地文件为 source of truth，真实外部用户前再接远端对象存储。",
        ],
    }


def _check(
    *,
    check_id: str,
    label: str,
    status: str,
    evidence: str,
    source_endpoint: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "status_label": "已具备" if status == "ready" else "需留意",
        "evidence": evidence,
        "source_endpoint": source_endpoint,
        "next_step": next_step,
    }


def _inventory_evidence(inventory: dict[str, Any]) -> str:
    project_count = int(inventory.get("project_count") or 0)
    run_count = int(inventory.get("run_count") or 0)
    session_count = int(inventory.get("ingest_session_count") or 0)
    return f"{project_count} 个项目 / {run_count} 个 run / {session_count} 个分片会话"


def _has_private_source_rules(resources: Any) -> bool:
    if not isinstance(resources, list):
        return False
    ids = {str(item.get("id") or "") for item in resources if isinstance(item, dict)}
    return {"uploaded_source_private", "canon_holdout_private"}.issubset(ids)


def _first_text(items: list[Any] | None, fallback: str) -> str:
    if not items:
        return fallback
    value = items[0]
    return value if isinstance(value, str) and value else fallback
