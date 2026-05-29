"""v0.7 Web 服务层：console-free 编排封装，供 HTTP API 与 CLI 共用。

不复制推演逻辑——内部仍走 orchestrator / intervention_compiler / output.writer。
"""

from .anchor_update import (
    AnchorReadOnlyError,
    AnchorUpdateError,
    AnchorUpdateResult,
    update_world_anchor,
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
from .import_novel import (
    ImportRequestError,
    ImportServiceResult,
    ProjectExistsError,
    import_novel_from_payload,
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

__all__ = [
    "VALID_ACTIONS",
    "AnchorReadOnlyError",
    "AnchorUpdateError",
    "AnchorUpdateResult",
    "DiffActionError",
    "DiffNotFoundError",
    "HealthReport",
    "JOBS",
    "JOB_KINDS",
    "JobRecord",
    "JobStore",
    "RuntimeSettings",
    "SettingsError",
    "CharacterProbe",
    "ProbeRequestError",
    "GuardrailRequestError",
    "probe_character",
    "check_intervention_guardrail",
    "check_project_health",
    "default_mock",
    "default_rounds",
    "default_runner",
    "get_runtime_settings",
    "test_connectivity",
    "update_runtime_settings",
    "update_world_anchor",
    "GenesisProjectExistsError",
    "GenesisRequestError",
    "GenesisServiceResult",
    "ImportRequestError",
    "ImportServiceResult",
    "InterventionRequestError",
    "InterventionServiceResult",
    "ProjectExistsError",
    "apply_diff_action",
    "generate_story",
    "import_novel_from_payload",
    "resolve_llm_quietly",
    "run_intervention",
]
