"""v0.7 Web 服务层：console-free 编排封装，供 HTTP API 与 CLI 共用。

不复制推演逻辑——内部仍走 orchestrator / intervention_compiler / output.writer。
"""

from .anchor_update import (
    AnchorReadOnlyError,
    AnchorUpdateError,
    AnchorUpdateResult,
    update_world_anchor,
)
from .advanced_runner_evaluation import (
    evaluate_advanced_runner_probes,
    evaluate_advanced_runner_trigger,
)
from .api_contract import get_api_contract
from .auth_boundary import get_auth_boundary_checklist
from .billing_adapter_boundary import get_billing_adapter_boundary_checklist
from .bundled_release_readiness import get_bundled_release_readiness
from .cross_project_retrieval_samples_index import (
    get_cross_project_retrieval_samples_index,
)
from .retrieval_samples_trend_snapshot import get_retrieval_samples_trend_snapshot
from .baseline import (
    BaselineRequestError,
    BaselineServiceResult,
    generate_baseline,
    get_baseline_report,
)
from .canon_replay import (
    HoldoutExistsError,
    HoldoutReadOnlyError,
    HoldoutRequestError,
    ReplayRequestError,
    get_canon_replay_report,
    get_canon_replay_range_report,
    get_holdout,
    run_canon_replay,
    run_canon_replay_range,
    write_holdout,
)
from .cards_workspace import CardsWorkspaceRequestError, get_cards_workspace
from .chapter_export import (
    ChapterExportRequestError,
    build_chapter_collection_export,
    build_chapter_export,
)
from .account_project_space import get_account_project_space_boundary
from .commercial_audit_log import (
    ProjectAuditLogConflictError,
    ProjectAuditLogRequestError,
    append_project_audit_log_event,
    export_project_audit_log,
    get_project_audit_log,
)
from .commercial_hardening import get_commercial_hardening_scope
from .commercial_permissions import get_permission_matrix_draft
from .commercial_status_overview import get_commercial_status_overview
from .cloud_persistence_boundary import get_cloud_persistence_boundary
from .copyright_statement import (
    ProjectCopyrightStatementConflictError,
    ProjectCopyrightStatementRequestError,
    get_project_copyright_statement,
    write_project_copyright_statement,
)
from .deployment_readiness import (
    get_local_deployment_readiness,
    get_settings_local_smoke_checklist,
)
from .deployment_observability import (
    DeploymentObservabilityRequestError,
    get_deployment_observability_checklist,
)
from .diff_actions import (
    VALID_ACTIONS,
    DiffActionError,
    DiffNotFoundError,
    apply_diff_action,
)
from .graph_memory_evaluation import evaluate_graph_memory_trigger
from .graph_memory_trigger_evidence import (
    GraphMemoryTriggerEvidenceRequestError,
    get_graph_memory_trigger_evidence,
)
from .graph_memory_spike_design_pack import (
    GraphMemorySpikeDesignPackRequestError,
    get_graph_memory_spike_design_pack,
)
from .graph_memory_shadow_compare_pack import (
    GraphMemoryShadowComparePackRequestError,
    get_graph_memory_shadow_compare_pack,
)
from .graph_memory_shadow_case_matrix import (
    GraphMemoryShadowCaseMatrixRequestError,
    get_graph_memory_shadow_case_matrix,
)
from .graph_memory_provider_boundary_matrix import (
    GraphMemoryProviderBoundaryMatrixRequestError,
    get_graph_memory_provider_boundary_matrix,
)
from .graph_memory_offline_shadow_replay_plan import (
    GraphMemoryOfflineShadowReplayPlanRequestError,
    get_graph_memory_offline_shadow_replay_plan,
)
from .graph_memory_offline_shadow_replay_report import (
    GraphMemoryOfflineShadowReplayReportRequestError,
    get_graph_memory_offline_shadow_replay_report,
)
from .graph_memory_provider_spike_fixture_pack import (
    GraphMemoryProviderSpikeFixturePackRequestError,
    get_graph_memory_provider_spike_fixture_pack,
)
from .graph_memory_provider_spike_readiness_gate import (
    GraphMemoryProviderSpikeReadinessGateRequestError,
    get_graph_memory_provider_spike_readiness_gate,
)
from .graph_memory_provider_spike_runbook import (
    GraphMemoryProviderSpikeRunbookRequestError,
    get_graph_memory_provider_spike_runbook,
)
from .graph_memory_provider_spike_dry_run_result_template import (
    GraphMemoryProviderSpikeDryRunResultTemplateRequestError,
    get_graph_memory_provider_spike_dry_run_result_template,
)
from .graph_memory_provider_spike_mock_result_report import (
    GraphMemoryProviderSpikeMockResultReportRequestError,
    get_graph_memory_provider_spike_mock_result_report,
)
from .graph_memory_provider_spike_review_gate import (
    GraphMemoryProviderSpikeReviewGateRequestError,
    get_graph_memory_provider_spike_review_gate,
)
from .graph_memory_provider_spike_manual_approval_pack import (
    GraphMemoryProviderSpikeManualApprovalPackRequestError,
    get_graph_memory_provider_spike_manual_approval_pack,
)
from .graph_memory_provider_spike_manual_approval_evidence_checklist import (
    GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError,
    get_graph_memory_provider_spike_manual_approval_evidence_checklist,
)
from .graph_memory_provider_spike_opt_in_evidence_snapshot import (
    GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError,
    get_graph_memory_provider_spike_opt_in_evidence_snapshot,
)
from .graph_memory_provider_spike_opt_in_no_go_matrix import (
    GraphMemoryProviderSpikeOptInNoGoMatrixRequestError,
    get_graph_memory_provider_spike_opt_in_no_go_matrix,
)
from .graph_memory_provider_spike_opt_in_operator_checklist import (
    GraphMemoryProviderSpikeOptInOperatorChecklistRequestError,
    get_graph_memory_provider_spike_opt_in_operator_checklist,
)
from .graph_memory_provider_spike_opt_in_review_packet import (
    GraphMemoryProviderSpikeOptInReviewPacketRequestError,
    get_graph_memory_provider_spike_opt_in_review_packet,
)
from .graph_memory_provider_spike_opt_in_decision_ledger_preview import (
    GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError,
    get_graph_memory_provider_spike_opt_in_decision_ledger_preview,
)
from .graph_memory_provider_spike_opt_in_final_readiness_summary import (
    GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError,
    get_graph_memory_provider_spike_opt_in_final_readiness_summary,
)
from .graph_memory_provider_spike_opt_in_human_signoff_schema_draft import (
    GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError,
    get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft,
)
from .jobs import JOBS, JOB_KINDS, JobRecord, JobStore
from .master_setting_update import (
    MasterSettingConflictError,
    MasterSettingReadOnlyError,
    MasterSettingUpdateError,
    MasterSettingUpdateResult,
    update_master_setting,
)
from .model_configuration import get_model_configuration_summary
from .llm_profile_assignment import get_llm_profile_assignment
from .project_health import HealthReport, check_project_health
from .project_retention_policy import (
    ProjectRetentionPolicyConflictError,
    ProjectRetentionPolicyRequestError,
    get_project_retention_policy,
    write_project_retention_policy,
)
from .quota_observability import (
    QuotaObservabilityRequestError,
    get_quota_observability_lite,
)
from .object_storage_boundary import get_object_storage_boundary_checklist
from .quota_enforcement_boundary import get_quota_enforcement_boundary_checklist
from .release_preflight import (
    ReleasePreflightRequestError,
    get_release_preflight_checklist,
)
from .rights_approval import (
    RightsApprovalRequestError,
    get_rights_approval_checklist,
)
from .retrieval_probe import evaluate_retrieval_probes
from .retrieval_failure_samples import (
    RetrievalFailureSampleConflictError,
    RetrievalFailureSampleRequestError,
    add_retrieval_failure_sample,
    get_retrieval_failure_samples,
)
from .retrieval_sample_export_pack import (
    RetrievalSampleExportPackRequestError,
    get_retrieval_sample_export_pack,
)
from .retrieval_sample_replay_report import (
    RetrievalSampleReplayReportRequestError,
    get_retrieval_sample_replay_report,
)
from .retrieval_sample_migration_pack import (
    RetrievalSampleMigrationPackRequestError,
    get_retrieval_sample_migration_pack,
)
from .runtime_preflight import (
    RuntimePreflightRequestError,
    get_runtime_preflight,
)
from .projection_health import (
    ProjectionHealthRequestError,
    get_projection_health,
)
from .reader_panel import (
    ReaderPanelRequestError,
    get_reader_panel,
)
from .prompt_budget_pack import (
    PromptBudgetPackRequestError,
    get_prompt_budget_pack,
)
from .runtime_settings import (
    RuntimeSettings,
    SettingsError,
    default_mock,
    default_rounds,
    default_runner,
    get_provider_gateway_summary,
    get_provider_usage_summary,
    get_runtime_settings,
    test_connectivity,
    update_runtime_settings,
)
from .runner_state_execution import (
    RunnerStateExecutionConflict,
    RunnerStateExecutionRequestError,
    apply_runner_state_execution,
    evaluate_runner_state_execution,
    get_runner_state_execution_report,
    rollback_runner_state_execution,
)
from .resume_continue import (
    ResumeContinueRequestError,
    ResumeContinueServiceResult,
    run_resume_continue,
)
from .import_novel import (
    ImportRequestError,
    ImportServiceResult,
    ProjectExistsError,
    import_novel_from_payload,
)
from .ingest_sessions import (
    IngestSessionConflict,
    IngestSessionNotFound,
    IngestSessionRequestError,
    build_upload_from_session,
    create_ingest_session,
    get_ingest_session,
    import_request_from_session,
    mark_ingest_session_imported,
    write_ingest_chunk,
)
from .character_probe import (
    CharacterProbe,
    ProbeRequestError,
    probe_character,
)
from .intervene import (
    InterventionRequestError,
    InterventionServiceResult,
    resolve_llm_quietly,
    run_intervention,
)
from .emergence_mining import (
    EmergenceMiningRequestError,
    get_emergence_nodes,
    mine_run_emergence,
)
from .embedding_evaluation_samples import get_embedding_evaluation_samples
from .embedding_mock_evaluation_report import (
    EmbeddingMockEvaluationReportRequestError,
    get_embedding_mock_evaluation_report,
)
from .intervention_guardrail import (
    GuardrailRequestError,
    check_intervention_guardrail,
)
from .story_genesis import (
    GenesisProjectExistsError,
    GenesisRequestError,
    GenesisServiceResult,
    generate_story,
)
from .visual_assets import (
    VisualAssetPathError,
    VisualAssetRequestError,
    generate_visual_assets,
    get_visual_assets,
    resolve_asset_path,
)
from .vector_retrieval_readiness import get_vector_retrieval_readiness
from .worldline_judge import (
    WorldlineJudgeRequestError,
    get_worldline_judgement,
    judge_worldline,
)
from .worldline_selection import (
    WorldlineSelectionRequestError,
    get_selected_worldline,
    select_worldline,
)

__all__ = [
    "VALID_ACTIONS",
    "AnchorReadOnlyError",
    "AnchorUpdateError",
    "AnchorUpdateResult",
    "evaluate_advanced_runner_probes",
    "evaluate_advanced_runner_trigger",
    "get_api_contract",
    "get_auth_boundary_checklist",
    "get_billing_adapter_boundary_checklist",
    "get_bundled_release_readiness",
    "get_cross_project_retrieval_samples_index",
    "get_retrieval_samples_trend_snapshot",
    "BaselineRequestError",
    "BaselineServiceResult",
    "CardsWorkspaceRequestError",
    "ChapterExportRequestError",
    "generate_baseline",
    "get_baseline_report",
    "build_chapter_collection_export",
    "build_chapter_export",
    "get_cards_workspace",
    "get_account_project_space_boundary",
    "ProjectAuditLogConflictError",
    "ProjectAuditLogRequestError",
    "append_project_audit_log_event",
    "export_project_audit_log",
    "get_project_audit_log",
    "get_commercial_hardening_scope",
    "get_permission_matrix_draft",
    "get_commercial_status_overview",
    "get_cloud_persistence_boundary",
    "ProjectCopyrightStatementConflictError",
    "ProjectCopyrightStatementRequestError",
    "get_project_copyright_statement",
    "write_project_copyright_statement",
    "get_local_deployment_readiness",
    "get_settings_local_smoke_checklist",
    "DeploymentObservabilityRequestError",
    "get_deployment_observability_checklist",
    "ProjectRetentionPolicyConflictError",
    "ProjectRetentionPolicyRequestError",
    "get_project_retention_policy",
    "write_project_retention_policy",
    "QuotaObservabilityRequestError",
    "get_quota_observability_lite",
    "get_object_storage_boundary_checklist",
    "get_quota_enforcement_boundary_checklist",
    "ReleasePreflightRequestError",
    "get_release_preflight_checklist",
    "RightsApprovalRequestError",
    "get_rights_approval_checklist",
    "RuntimePreflightRequestError",
    "get_runtime_preflight",
    "ProjectionHealthRequestError",
    "get_projection_health",
    "ReaderPanelRequestError",
    "get_reader_panel",
    "PromptBudgetPackRequestError",
    "get_prompt_budget_pack",
    "HoldoutExistsError",
    "HoldoutReadOnlyError",
    "HoldoutRequestError",
    "ReplayRequestError",
    "ResumeContinueRequestError",
    "ResumeContinueServiceResult",
    "get_canon_replay_report",
    "get_canon_replay_range_report",
    "get_holdout",
    "run_canon_replay",
    "run_canon_replay_range",
    "write_holdout",
    "DiffActionError",
    "DiffNotFoundError",
    "HealthReport",
    "JOBS",
    "JOB_KINDS",
    "JobRecord",
    "JobStore",
    "MasterSettingConflictError",
    "MasterSettingReadOnlyError",
    "MasterSettingUpdateError",
    "MasterSettingUpdateResult",
    "RuntimeSettings",
    "RunnerStateExecutionConflict",
    "RunnerStateExecutionRequestError",
    "SettingsError",
    "CharacterProbe",
    "ProbeRequestError",
    "GuardrailRequestError",
    "EmergenceMiningRequestError",
    "probe_character",
    "check_intervention_guardrail",
    "check_project_health",
    "default_mock",
    "default_rounds",
    "default_runner",
    "get_provider_gateway_summary",
    "get_provider_usage_summary",
    "get_runtime_settings",
    "get_model_configuration_summary",
    "get_llm_profile_assignment",
    "apply_runner_state_execution",
    "evaluate_runner_state_execution",
    "get_runner_state_execution_report",
    "rollback_runner_state_execution",
    "run_resume_continue",
    "test_connectivity",
    "update_master_setting",
    "update_runtime_settings",
    "update_world_anchor",
    "GenesisProjectExistsError",
    "GenesisRequestError",
    "GenesisServiceResult",
    "ImportRequestError",
    "ImportServiceResult",
    "IngestSessionConflict",
    "IngestSessionNotFound",
    "IngestSessionRequestError",
    "InterventionRequestError",
    "InterventionServiceResult",
    "ProjectExistsError",
    "apply_diff_action",
    "build_upload_from_session",
    "create_ingest_session",
    "generate_story",
    "get_ingest_session",
    "import_novel_from_payload",
    "import_request_from_session",
    "mark_ingest_session_imported",
    "get_embedding_evaluation_samples",
    "EmbeddingMockEvaluationReportRequestError",
    "get_embedding_mock_evaluation_report",
    "resolve_llm_quietly",
    "run_intervention",
    "write_ingest_chunk",
    "get_emergence_nodes",
    "evaluate_graph_memory_trigger",
    "GraphMemoryTriggerEvidenceRequestError",
    "get_graph_memory_trigger_evidence",
    "GraphMemorySpikeDesignPackRequestError",
    "get_graph_memory_spike_design_pack",
    "GraphMemoryShadowComparePackRequestError",
    "get_graph_memory_shadow_compare_pack",
    "GraphMemoryShadowCaseMatrixRequestError",
    "get_graph_memory_shadow_case_matrix",
    "GraphMemoryProviderBoundaryMatrixRequestError",
    "get_graph_memory_provider_boundary_matrix",
    "GraphMemoryOfflineShadowReplayPlanRequestError",
    "get_graph_memory_offline_shadow_replay_plan",
    "GraphMemoryOfflineShadowReplayReportRequestError",
    "get_graph_memory_offline_shadow_replay_report",
    "GraphMemoryProviderSpikeFixturePackRequestError",
    "get_graph_memory_provider_spike_fixture_pack",
    "GraphMemoryProviderSpikeReadinessGateRequestError",
    "get_graph_memory_provider_spike_readiness_gate",
    "GraphMemoryProviderSpikeRunbookRequestError",
    "get_graph_memory_provider_spike_runbook",
    "GraphMemoryProviderSpikeDryRunResultTemplateRequestError",
    "get_graph_memory_provider_spike_dry_run_result_template",
    "GraphMemoryProviderSpikeMockResultReportRequestError",
    "get_graph_memory_provider_spike_mock_result_report",
    "GraphMemoryProviderSpikeReviewGateRequestError",
    "get_graph_memory_provider_spike_review_gate",
    "GraphMemoryProviderSpikeManualApprovalPackRequestError",
    "get_graph_memory_provider_spike_manual_approval_pack",
    "GraphMemoryProviderSpikeManualApprovalEvidenceChecklistRequestError",
    "get_graph_memory_provider_spike_manual_approval_evidence_checklist",
    "GraphMemoryProviderSpikeOptInEvidenceSnapshotRequestError",
    "get_graph_memory_provider_spike_opt_in_evidence_snapshot",
    "GraphMemoryProviderSpikeOptInNoGoMatrixRequestError",
    "get_graph_memory_provider_spike_opt_in_no_go_matrix",
    "GraphMemoryProviderSpikeOptInOperatorChecklistRequestError",
    "get_graph_memory_provider_spike_opt_in_operator_checklist",
    "GraphMemoryProviderSpikeOptInReviewPacketRequestError",
    "get_graph_memory_provider_spike_opt_in_review_packet",
    "GraphMemoryProviderSpikeOptInDecisionLedgerPreviewRequestError",
    "get_graph_memory_provider_spike_opt_in_decision_ledger_preview",
    "GraphMemoryProviderSpikeOptInFinalReadinessSummaryRequestError",
    "get_graph_memory_provider_spike_opt_in_final_readiness_summary",
    "GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftRequestError",
    "get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft",
    "evaluate_retrieval_probes",
    "RetrievalFailureSampleConflictError",
    "RetrievalFailureSampleRequestError",
    "RetrievalSampleExportPackRequestError",
    "RetrievalSampleReplayReportRequestError",
    "RetrievalSampleMigrationPackRequestError",
    "add_retrieval_failure_sample",
    "get_retrieval_failure_samples",
    "get_retrieval_sample_export_pack",
    "get_retrieval_sample_replay_report",
    "get_retrieval_sample_migration_pack",
    "mine_run_emergence",
    "VisualAssetPathError",
    "VisualAssetRequestError",
    "generate_visual_assets",
    "get_visual_assets",
    "resolve_asset_path",
    "get_vector_retrieval_readiness",
    "WorldlineJudgeRequestError",
    "WorldlineSelectionRequestError",
    "get_worldline_judgement",
    "get_selected_worldline",
    "judge_worldline",
    "select_worldline",
]
