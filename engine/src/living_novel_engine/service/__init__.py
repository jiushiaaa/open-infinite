"""v0.7 Web 服务层：console-free 编排封装，供 HTTP API 与 CLI 共用。

不复制推演逻辑——内部仍走 orchestrator / intervention_compiler / output.writer。
"""

from .anchor_update import (
    AnchorReadOnlyError,
    AnchorUpdateError,
    AnchorUpdateResult,
    update_world_anchor,
)
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
from .chapter_export import (
    ChapterExportRequestError,
    build_chapter_export,
)
from .diff_actions import (
    VALID_ACTIONS,
    DiffActionError,
    DiffNotFoundError,
    apply_diff_action,
)
from .jobs import JOBS, JOB_KINDS, JobRecord, JobStore
from .project_health import HealthReport, check_project_health
from .runtime_settings import (
    RuntimeSettings,
    SettingsError,
    default_mock,
    default_rounds,
    default_runner,
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
    "BaselineRequestError",
    "BaselineServiceResult",
    "ChapterExportRequestError",
    "generate_baseline",
    "get_baseline_report",
    "build_chapter_export",
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
    "get_runtime_settings",
    "apply_runner_state_execution",
    "evaluate_runner_state_execution",
    "get_runner_state_execution_report",
    "rollback_runner_state_execution",
    "run_resume_continue",
    "test_connectivity",
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
    "resolve_llm_quietly",
    "run_intervention",
    "write_ingest_chunk",
    "get_emergence_nodes",
    "mine_run_emergence",
    "VisualAssetPathError",
    "VisualAssetRequestError",
    "generate_visual_assets",
    "get_visual_assets",
    "resolve_asset_path",
    "WorldlineJudgeRequestError",
    "WorldlineSelectionRequestError",
    "get_worldline_judgement",
    "get_selected_worldline",
    "judge_worldline",
    "select_worldline",
]
