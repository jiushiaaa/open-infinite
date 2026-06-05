import type {
  AnchorPatch,
  AnchorUpdateResponse,
  ApiContractReport,
  AuthorAdoptionReport,
  AuthBoundaryChecklist,
  BillingAdapterBoundaryChecklist,
  BaselineGenerateRequest,
  BaselineGenerateResponse,
  BaselineReport,
  BranchDetail,
  BundledReleaseReadinessReport,
  CardsWorkspaceReport,
  CanonReplayReport,
  CanonReplayRangeReport,
  CanonReplayRangeRequest,
  CanonReplayRequest,
  ChapterCollectionExport,
  ChapterExport,
  CharacterLensReport,
  CharacterProbe,
  ConnectivityResult,
  CrossProjectRetrievalSamplesIndexReport,
  DiffActionRequest,
  DiffActionResponse,
  EmbeddingEvaluationSamplesReport,
  EmbeddingMockEvaluationReport,
  RetrievalSampleMigrationPackReport,
  RetrievalSampleReplayReport,
  RetrievalSampleExportPackReport,
  RetrievalFailureSampleAppendRequest,
  RetrievalFailureSampleAppendResponse,
  RetrievalFailureSamplesReport,
  EmergenceReport,
  GuardrailRequest,
  GuardrailResult,
  GraphMemoryTriggerEvidenceReport,
  GraphMemorySpikeDesignPackReport,
  GraphMemoryShadowComparePackReport,
  GraphMemoryShadowCaseMatrixReport,
  GraphMemoryProviderBoundaryMatrixReport,
  GraphMemoryOfflineShadowReplayPlanReport,
  GraphMemoryOfflineShadowReplayReport,
  GraphMemoryProviderSpikeFixturePackReport,
  GraphMemoryProviderSpikeReadinessGateReport,
  GraphMemoryProviderSpikeRunbookReport,
  GraphMemoryProviderSpikeDryRunResultTemplateReport,
  GraphMemoryProviderSpikeMockResultReport,
  GraphMemoryProviderSpikeReviewGateReport,
  GraphMemoryProviderSpikeManualApprovalPackReport,
  GraphMemoryProviderSpikeManualApprovalEvidenceChecklistReport,
  GraphMemoryProviderSpikeOptInEvidenceSnapshotReport,
  GraphMemoryProviderSpikeOptInNoGoMatrixReport,
  GraphMemoryProviderSpikeOptInOperatorChecklistReport,
  GraphMemoryProviderSpikeOptInReviewPacketReport,
  GraphMemoryProviderSpikeOptInDecisionLedgerPreviewReport,
  GraphMemoryProviderSpikeOptInFinalReadinessSummaryReport,
  GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftReport,
  GraphMemoryProviderSpikeOptInConfigDraftReport,
  GraphMemoryProviderSpikeLocalProviderContractReport,
  GraphMemoryProviderSpikeSingleFixtureDryRunHarnessReport,
  GraphMemoryProviderSpikeMockCompatibleAdapterReport,
  GraphMemoryProviderSpikeManualMockAdapterReviewReport,
  HoldoutManifest,
  HoldoutWriteRequest,
  IngestChunkRequest,
  IngestSessionCreateRequest,
  IngestSessionSummary,
  ImportNovelRequest,
  ImportNovelResponse,
  JobRecord,
  JobSubmitResponse,
  MasterSettingPatch,
  MasterSettingUpdateResponse,
  DeploymentObservabilityChecklist,
  LLMProfileAssignmentReport,
  LocalSmokeChecklist,
  ObjectStorageBoundaryChecklist,
  QuotaEnforcementBoundaryChecklist,
  ReleasePreflightChecklist,
  RetrievalProviderConfigurationReport,
  RetrievalProviderConnectivityResult,
  RetrievalSamplesTrendSnapshotReport,
  RightsApprovalChecklist,
  ModelConfigurationSummary,
  ProviderGatewaySummary,
  ProviderUsageSummary,
  CommercialStatusOverview,
  ProjectAuditLog,
  ProjectAuditLogExport,
  ProjectWorkspace,
  ProjectHealth,
  ProjectionHealthReport,
  PromptBudgetPackReport,
  ReaderPanelReport,
  RuntimePreflightReport,
  InterventionRequest,
  InterventionResponse,
  RunDetail,
  RunTreeNode,
  RuntimeSettings,
  RuntimeSettingsPatch,
  NarrativeCompensationReport,
  VectorRetrievalIndexReport,
  VectorRetrievalReadinessReport,
  VectorRetrievalSearchReport,
  ReplayAuditWorkspace,
  ResumeContinueRequest,
  RunnerStateExecutionApplyReport,
  RunnerStateExecutionReport,
  RunnerStateExecutionRollbackReport,
  StoryGenesisRequest,
  StoryGenesisResponse,
  StorySummary,
  SubjectiveMemoryReport,
  TianmingBook,
  TianmingInterventionCompileReport,
  VisualAssets,
  VisualAssetsGenerateRequest,
  WorldAnchor,
  WorldAutopilotReport,
  WorldAutopilotCheckpointReplayReport,
  WorldlineDossierReport,
  WorldlineState,
  WorldSandboxRunReport,
  WorldSandboxRunRequest,
  WorldlineSelectionRequest,
  WorldlineSelectionResponse,
  WorldlineJudgement,
  WorldlineJudgementRequest,
} from "./types";

// 复用 `lne browse` 的只读端点。开发时由 vite proxy 转发 /api 到 8765；
// 也可用 VITE_API_BASE 指定绝对地址。任何新 API 必须 additive，不破坏 lne browse。
const API_BASE = (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseOk<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    let detail = `请求失败（HTTP ${resp.status}）`;
    try {
      const body = await resp.json();
      if (body && typeof body.error === "string") detail = body.error;
    } catch {
      /* ignore parse error, keep default */
    }
    throw new ApiError(detail, resp.status);
  }
  return (await resp.json()) as T;
}

async function getJson<T>(path: string): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${API_BASE}${path}`, {
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError(
      `无法连接引擎服务（${API_BASE || "/api"}）。请先运行 lne browse 启动后端。`,
      0,
    );
  }
  return parseOk<T>(resp);
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(
      `无法连接引擎服务（${API_BASE || "/api"}）。请先运行 lne browse 启动后端。`,
      0,
    );
  }
  return parseOk<T>(resp);
}

export const api = {
  listStories(): Promise<{ stories: StorySummary[] }> {
    return getJson("/api/stories");
  },
  getTree(storySlug?: string): Promise<{ tree: RunTreeNode[] }> {
    const q = storySlug ? `?story_slug=${encodeURIComponent(storySlug)}` : "";
    return getJson(`/api/tree${q}`);
  },
  getWorldAnchor(storySlug: string): Promise<WorldAnchor> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/anchor`);
  },
  getProjectWorkspace(storySlug: string): Promise<ProjectWorkspace> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/project-workspace`,
    );
  },
  getRuntimePreflight(storySlug: string): Promise<RuntimePreflightReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/runtime-preflight`,
    );
  },
  getVectorRetrievalReadiness(storySlug: string): Promise<VectorRetrievalReadinessReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/vector-retrieval-readiness`,
    );
  },
  buildVectorRetrievalIndex(
    storySlug: string,
    payload: { refresh?: boolean; limit?: number | null } = {},
  ): Promise<VectorRetrievalIndexReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/vector-retrieval/index`,
      payload,
    );
  },
  searchVectorRetrieval(
    storySlug: string,
    payload: { query: string; current_chapter?: number; top_k?: number },
  ): Promise<VectorRetrievalSearchReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/vector-retrieval/search`,
      payload,
    );
  },
  getGraphMemoryTriggerEvidence(
    storySlug: string,
  ): Promise<GraphMemoryTriggerEvidenceReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-trigger-evidence`,
    );
  },
  getGraphMemorySpikeDesignPack(
    storySlug: string,
  ): Promise<GraphMemorySpikeDesignPackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-spike-design-pack`,
    );
  },
  getGraphMemoryShadowComparePack(
    storySlug: string,
  ): Promise<GraphMemoryShadowComparePackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-shadow-compare-pack`,
    );
  },
  getGraphMemoryShadowCaseMatrix(
    storySlug: string,
  ): Promise<GraphMemoryShadowCaseMatrixReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-shadow-case-matrix`,
    );
  },
  getGraphMemoryProviderBoundaryMatrix(
    storySlug: string,
  ): Promise<GraphMemoryProviderBoundaryMatrixReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-boundary-matrix`,
    );
  },
  getGraphMemoryOfflineShadowReplayPlan(
    storySlug: string,
  ): Promise<GraphMemoryOfflineShadowReplayPlanReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-offline-shadow-replay-plan`,
    );
  },
  getGraphMemoryOfflineShadowReplayReport(
    storySlug: string,
  ): Promise<GraphMemoryOfflineShadowReplayReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-offline-shadow-replay-report`,
    );
  },
  getGraphMemoryProviderSpikeFixturePack(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeFixturePackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-fixture-pack`,
    );
  },
  getGraphMemoryProviderSpikeReadinessGate(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeReadinessGateReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-readiness-gate`,
    );
  },
  getGraphMemoryProviderSpikeRunbook(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeRunbookReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-runbook`,
    );
  },
  getGraphMemoryProviderSpikeDryRunResultTemplate(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeDryRunResultTemplateReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-dry-run-result-template`,
    );
  },
  getGraphMemoryProviderSpikeMockResultReport(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeMockResultReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-mock-result-report`,
    );
  },
  getGraphMemoryProviderSpikeReviewGate(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeReviewGateReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-review-gate`,
    );
  },
  getGraphMemoryProviderSpikeManualApprovalPack(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeManualApprovalPackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-manual-approval-pack`,
    );
  },
  getGraphMemoryProviderSpikeManualApprovalEvidenceChecklist(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeManualApprovalEvidenceChecklistReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-manual-approval-evidence-checklist`,
    );
  },
  getGraphMemoryProviderSpikeOptInEvidenceSnapshot(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInEvidenceSnapshotReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-evidence-snapshot`,
    );
  },
  getGraphMemoryProviderSpikeOptInNoGoMatrix(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInNoGoMatrixReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-no-go-matrix`,
    );
  },
  getGraphMemoryProviderSpikeOptInOperatorChecklist(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInOperatorChecklistReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-operator-checklist`,
    );
  },
  getGraphMemoryProviderSpikeOptInReviewPacket(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInReviewPacketReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-review-packet`,
    );
  },
  getGraphMemoryProviderSpikeOptInDecisionLedgerPreview(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInDecisionLedgerPreviewReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-decision-ledger-preview`,
    );
  },
  getGraphMemoryProviderSpikeOptInFinalReadinessSummary(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInFinalReadinessSummaryReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-final-readiness-summary`,
    );
  },
  getGraphMemoryProviderSpikeOptInHumanSignoffSchemaDraft(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-human-signoff-schema-draft`,
    );
  },
  getGraphMemoryProviderSpikeOptInConfigDraft(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeOptInConfigDraftReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-opt-in-config-draft`,
    );
  },
  getGraphMemoryProviderSpikeLocalProviderContract(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeLocalProviderContractReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-local-provider-contract`,
    );
  },
  getGraphMemoryProviderSpikeSingleFixtureDryRunHarness(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeSingleFixtureDryRunHarnessReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-single-fixture-dry-run-harness`,
    );
  },
  getGraphMemoryProviderSpikeMockCompatibleAdapter(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeMockCompatibleAdapterReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-mock-compatible-adapter`,
    );
  },
  getGraphMemoryProviderSpikeManualMockAdapterReview(
    storySlug: string,
  ): Promise<GraphMemoryProviderSpikeManualMockAdapterReviewReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/graph-memory-provider-spike-manual-mock-adapter-review`,
    );
  },
  getEmbeddingEvaluationSamples(storySlug: string): Promise<EmbeddingEvaluationSamplesReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/embedding-evaluation-samples`,
    );
  },
  getRetrievalSampleExportPack(storySlug: string): Promise<RetrievalSampleExportPackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/retrieval-sample-export-pack`,
    );
  },
  getEmbeddingMockEvaluationReport(storySlug: string): Promise<EmbeddingMockEvaluationReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/embedding-mock-evaluation-report`,
    );
  },
  getRetrievalSampleReplayReport(storySlug: string): Promise<RetrievalSampleReplayReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/retrieval-sample-replay-report`,
    );
  },
  getRetrievalSampleMigrationPack(
    storySlug: string,
  ): Promise<RetrievalSampleMigrationPackReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/retrieval-sample-migration-pack`,
    );
  },
  getRetrievalFailureSamples(storySlug: string): Promise<RetrievalFailureSamplesReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/retrieval-failure-samples`,
    );
  },
  addRetrievalFailureSample(
    storySlug: string,
    req: RetrievalFailureSampleAppendRequest,
  ): Promise<RetrievalFailureSampleAppendResponse> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/retrieval-failure-samples`,
      req,
    );
  },
  getProjectAuditLog(storySlug: string): Promise<ProjectAuditLog> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/audit-log`);
  },
  getProjectAuditLogExport(storySlug: string): Promise<ProjectAuditLogExport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/audit-log/export`,
    );
  },
  getRightsApprovalChecklist(storySlug: string): Promise<RightsApprovalChecklist> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/rights-approval-checklist`,
    );
  },
  getSelectedWorldline(storySlug: string): Promise<WorldlineSelectionResponse> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/selected-worldline`,
    );
  },
  selectWorldline(
    storySlug: string,
    req: WorldlineSelectionRequest,
  ): Promise<WorldlineSelectionResponse> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/selected-worldline`,
      req,
    );
  },
  getProjectHealth(storySlug: string): Promise<ProjectHealth> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/health`);
  },
  updateWorldAnchor(storySlug: string, patch: AnchorPatch): Promise<AnchorUpdateResponse> {
    return postJson(`/api/stories/${encodeURIComponent(storySlug)}/anchor`, patch);
  },
  updateMasterSetting(
    storySlug: string,
    patch: MasterSettingPatch,
  ): Promise<MasterSettingUpdateResponse> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/master-setting`,
      patch,
    );
  },
  getCardsWorkspace(storySlug: string): Promise<CardsWorkspaceReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/cards-workspace`,
    );
  },
  runSandboxRound(
    storySlug: string,
    req: WorldSandboxRunRequest,
  ): Promise<WorldSandboxRunReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/sandbox/run`,
      req,
    );
  },
  getSandboxRun(runId: string): Promise<WorldSandboxRunReport> {
    return getJson(`/api/sandbox-runs/${encodeURIComponent(runId)}`);
  },
  getSubjectiveMemory(
    storySlug: string,
    worldlineId: string,
    characterId: string,
  ): Promise<SubjectiveMemoryReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/characters/${encodeURIComponent(characterId)}/subjective-memory`,
    );
  },
  getWorldlineState(storySlug: string, worldlineId: string): Promise<WorldlineState> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/worldline-state`,
    );
  },
  getWorldlineDossier(
    storySlug: string,
    worldlineId: string,
  ): Promise<WorldlineDossierReport> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/dossier`,
    );
  },
  getTianmingBook(storySlug: string): Promise<TianmingBook> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/tianming`);
  },
  generateTianmingBook(storySlug: string): Promise<TianmingBook> {
    return postJson(`/api/stories/${encodeURIComponent(storySlug)}/tianming/generate`, {});
  },
  confirmTianmingBook(storySlug: string): Promise<TianmingBook> {
    return postJson(`/api/stories/${encodeURIComponent(storySlug)}/tianming/confirm`, {
      confirm: true,
    });
  },
  compileTianmingIntervention(
    storySlug: string,
    req: {
      content: string;
      target?: string;
      worldline_id?: string;
      projection_mode?: "immersive" | "wild_au" | string;
    },
  ): Promise<TianmingInterventionCompileReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/tianming/intervention-compile`,
      req,
    );
  },
  runNarrativeCompensation(
    storySlug: string,
    req: { trigger_event: string; worldline_id?: string },
  ): Promise<NarrativeCompensationReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/narrative-compensation/run`,
      req,
    );
  },
  runWorldAutopilot(
    storySlug: string,
    req: {
      seed_event: string;
      objective_type?: string;
      stop_event?: string;
      time_limit?: string;
      round_limit?: number;
      worldline_id?: string;
    },
  ): Promise<WorldAutopilotReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/world-autopilot/run`,
      req,
      );
    },
  getWorldAutopilotTask(
    storySlug: string,
    worldlineId: string,
    taskId: string,
  ): Promise<Record<string, unknown>> {
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/world-autopilot/tasks/${encodeURIComponent(taskId)}`,
    );
  },
  pauseWorldAutopilotTask(
    storySlug: string,
    worldlineId: string,
    taskId: string,
  ): Promise<Record<string, unknown>> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/world-autopilot/tasks/${encodeURIComponent(taskId)}/pause`,
      {},
    );
  },
  resumeWorldAutopilotTask(
    storySlug: string,
    worldlineId: string,
    taskId: string,
  ): Promise<Record<string, unknown>> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/worldlines/${encodeURIComponent(
        worldlineId,
      )}/world-autopilot/tasks/${encodeURIComponent(taskId)}/resume`,
      {},
    );
  },
  replayWorldAutopilotCheckpoint(
    runId: string,
    checkpointId: string,
  ): Promise<WorldAutopilotCheckpointReplayReport> {
    return getJson(
      `/api/world-autopilot-runs/${encodeURIComponent(
        runId,
      )}/checkpoints/${encodeURIComponent(checkpointId)}`,
    );
  },
  generateCharacterLens(
    storySlug: string,
    req: {
      source_event: string;
      character_id?: string;
      source_run_id?: string;
      worldline_id?: string;
    },
  ): Promise<CharacterLensReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/character-lens/generate`,
      req,
    );
  },
  recordAuthorAdoption(
    storySlug: string,
    req: {
      decision: string;
      original_outline?: string;
      sandbox_summary?: string;
      source_event?: string;
      source_run_id?: string;
      author_note?: string;
      worldline_id?: string;
    },
  ): Promise<AuthorAdoptionReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/author-adoption`,
      req,
    );
  },
    getRun(runId: string): Promise<RunDetail> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}`);
  },
  getBranch(runId: string, branchId: string): Promise<BranchDetail> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}`,
    );
  },
  getProjectionHealth(
    runId: string,
    branchId: string,
  ): Promise<ProjectionHealthReport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/projection-health`,
    );
  },
  getReaderPanel(runId: string, branchId: string): Promise<ReaderPanelReport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/reader-panel`,
    );
  },
  getPromptBudgetPack(
    runId: string,
    branchId: string,
  ): Promise<PromptBudgetPackReport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/prompt-budget-pack`,
    );
  },
  postIntervention(req: InterventionRequest): Promise<InterventionResponse> {
    return postJson("/api/interventions", req);
  },
  checkGuardrail(req: GuardrailRequest): Promise<GuardrailResult> {
    return postJson("/api/interventions/guardrail", req);
  },
  getCharacterProbe(
    storySlug: string,
    charId: string,
    opts?: { runId?: string; branchId?: string; interventionText?: string },
  ): Promise<CharacterProbe> {
    const params = new URLSearchParams();
    if (opts?.runId) params.set("run_id", opts.runId);
    if (opts?.branchId) params.set("branch_id", opts.branchId);
    if (opts?.interventionText) params.set("intervention_text", opts.interventionText);
    const q = params.toString() ? `?${params.toString()}` : "";
    return getJson(
      `/api/stories/${encodeURIComponent(storySlug)}/characters/${encodeURIComponent(charId)}/probe${q}`,
    );
  },
  postDiffAction(req: DiffActionRequest): Promise<DiffActionResponse> {
    return postJson("/api/diffs/action", req);
  },
  postImportNovel(req: ImportNovelRequest): Promise<ImportNovelResponse> {
    return postJson("/api/import-novel", req);
  },
  postStoryGenesis(req: StoryGenesisRequest): Promise<StoryGenesisResponse> {
    return postJson("/api/story-genesis", req);
  },
  getRuntimeSettings(): Promise<RuntimeSettings> {
    return getJson("/api/settings/runtime");
  },
  updateRuntimeSettings(patch: RuntimeSettingsPatch): Promise<RuntimeSettings> {
    return postJson("/api/settings/runtime", patch);
  },
  testConnectivity(mock = false): Promise<ConnectivityResult> {
    return postJson("/api/settings/runtime/test", { mock });
  },
  getProviderGateway(): Promise<ProviderGatewaySummary> {
    return getJson("/api/settings/providers");
  },
  getProviderUsage(): Promise<ProviderUsageSummary> {
    return getJson("/api/settings/provider-usage");
  },
  getModelConfiguration(): Promise<ModelConfigurationSummary> {
    return getJson("/api/settings/model-configuration");
  },
  getRetrievalProviderConfiguration(): Promise<RetrievalProviderConfigurationReport> {
    return getJson("/api/settings/retrieval-provider-configuration");
  },
  testRetrievalProviderConnectivity(
    mock = true,
  ): Promise<RetrievalProviderConnectivityResult> {
    return postJson("/api/settings/retrieval-provider/test", { mock });
  },
  getLLMProfileAssignment(): Promise<LLMProfileAssignmentReport> {
    return getJson("/api/settings/llm-profile-assignment");
  },
  getApiContract(): Promise<ApiContractReport> {
    return getJson("/api/settings/api-contract");
  },
  getRetrievalSamplesIndex(): Promise<CrossProjectRetrievalSamplesIndexReport> {
    return getJson("/api/settings/retrieval-samples-index");
  },
  getRetrievalSamplesTrendSnapshot(): Promise<RetrievalSamplesTrendSnapshotReport> {
    return getJson("/api/settings/retrieval-samples-trend-snapshot");
  },
  getPackagingReadiness(): Promise<BundledReleaseReadinessReport> {
    return getJson("/api/settings/packaging-readiness");
  },
  getCommercialStatusOverview(): Promise<CommercialStatusOverview> {
    return getJson("/api/settings/commercial-status-overview");
  },
  getLocalSmokeChecklist(): Promise<LocalSmokeChecklist> {
    return getJson("/api/settings/local-smoke-checklist");
  },
  getReleasePreflight(): Promise<ReleasePreflightChecklist> {
    return getJson("/api/settings/release-preflight");
  },
  getDeploymentObservability(): Promise<DeploymentObservabilityChecklist> {
    return getJson("/api/settings/deployment-observability");
  },
  getAuthBoundary(): Promise<AuthBoundaryChecklist> {
    return getJson("/api/settings/auth-boundary");
  },
  getObjectStorageBoundary(): Promise<ObjectStorageBoundaryChecklist> {
    return getJson("/api/settings/object-storage-boundary");
  },
  getQuotaEnforcementBoundary(): Promise<QuotaEnforcementBoundaryChecklist> {
    return getJson("/api/settings/quota-enforcement-boundary");
  },
  getBillingAdapterBoundary(): Promise<BillingAdapterBoundaryChecklist> {
    return getJson("/api/settings/billing-adapter-boundary");
  },
  postJobIntervention(req: InterventionRequest): Promise<JobSubmitResponse> {
    return postJson("/api/jobs/intervention", req);
  },
  postJobResumeContinue(req: ResumeContinueRequest): Promise<JobSubmitResponse> {
    return postJson("/api/jobs/resume-continue", req);
  },
  postJobImportNovel(req: ImportNovelRequest): Promise<JobSubmitResponse> {
    return postJson("/api/jobs/import-novel", req);
  },
  postJobStoryGenesis(req: StoryGenesisRequest): Promise<JobSubmitResponse> {
    return postJson("/api/jobs/story-genesis", req);
  },
  getJob<T = unknown>(jobId: string): Promise<JobRecord<T>> {
    return getJson(`/api/jobs/${encodeURIComponent(jobId)}`);
  },
  createIngestSession(req: IngestSessionCreateRequest): Promise<IngestSessionSummary> {
    return postJson("/api/ingest-sessions", req);
  },
  getIngestSession(sessionId: string): Promise<IngestSessionSummary> {
    return getJson(`/api/ingest-sessions/${encodeURIComponent(sessionId)}`);
  },
  putIngestChunk(
    sessionId: string,
    req: IngestChunkRequest,
  ): Promise<IngestSessionSummary> {
    return postJson(`/api/ingest-sessions/${encodeURIComponent(sessionId)}/chunks`, req);
  },
  completeIngestSession(sessionId: string): Promise<JobSubmitResponse> {
    return postJson(
      `/api/ingest-sessions/${encodeURIComponent(sessionId)}/complete`,
      {},
    );
  },
  getVisualAssets(storySlug: string): Promise<VisualAssets> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/visual-assets`);
  },
  generateVisualAssets(
    storySlug: string,
    req: VisualAssetsGenerateRequest,
  ): Promise<VisualAssets> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/visual-assets/generate`,
      req,
    );
  },
  // ── v0.7.4 基线与正史回放 ─────────────────────────────────
  generateBaseline(
    storySlug: string,
    req: BaselineGenerateRequest,
  ): Promise<BaselineGenerateResponse> {
    return postJson(`/api/stories/${encodeURIComponent(storySlug)}/baseline`, req);
  },
  getBaselineReport(runId: string): Promise<BaselineReport> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}/baseline`);
  },
  getHoldout(storySlug: string): Promise<HoldoutManifest> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/canon/holdout`);
  },
  writeHoldout(
    storySlug: string,
    req: HoldoutWriteRequest,
  ): Promise<HoldoutManifest> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/canon/holdout`,
      req,
    );
  },
  runCanonReplay(
    storySlug: string,
    req: CanonReplayRequest,
  ): Promise<CanonReplayReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/canon/replay`,
      req,
    );
  },
  runCanonReplayRange(
    storySlug: string,
    req: CanonReplayRangeRequest,
  ): Promise<CanonReplayRangeReport> {
    return postJson(
      `/api/stories/${encodeURIComponent(storySlug)}/canon/replay-range`,
      req,
    );
  },
  getReplayAuditWorkspace(storySlug: string): Promise<ReplayAuditWorkspace> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/replay-audit`);
  },
  getCanonReplayReport(runId: string): Promise<CanonReplayReport> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}/canon-replay`);
  },
  // ── v0.7.5 世界线评审 ───────────────────────────────────
  generateWorldlineJudgement(
    runId: string,
    branchId: string,
    req: WorldlineJudgementRequest,
  ): Promise<WorldlineJudgement> {
    return postJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/worldline-judgement`,
      req,
    );
  },
  getWorldlineJudgement(
    runId: string,
    branchId: string,
  ): Promise<WorldlineJudgement> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/worldline-judgement`,
    );
  },
  getChapterExport(runId: string, branchId: string): Promise<ChapterExport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/chapter-export`,
    );
  },
  getChapterCollectionExport(
    runId: string,
    branchId: string,
  ): Promise<ChapterCollectionExport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}/chapter-collection-export`,
    );
  },
  // ── v0.8+ 涌现节点 ─────────────────────────────────────
  generateEmergenceNodes(runId: string): Promise<EmergenceReport> {
    return postJson(`/api/runs/${encodeURIComponent(runId)}/emergence-nodes`, {});
  },
  getEmergenceNodes(runId: string): Promise<EmergenceReport> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}/emergence-nodes`);
  },
  // ── v0.8.10-A 状态执行评估 ─────────────────────────────
  evaluateRunnerStateExecution(runId: string): Promise<RunnerStateExecutionReport> {
    return postJson(
      `/api/runs/${encodeURIComponent(runId)}/state-execution-evaluate`,
      {},
    );
  },
  getRunnerStateExecutionReport(runId: string): Promise<RunnerStateExecutionReport> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/state-execution-report`,
    );
  },
  applyRunnerStateExecution(runId: string): Promise<RunnerStateExecutionApplyReport> {
    return postJson(
      `/api/runs/${encodeURIComponent(runId)}/state-execution-apply`,
      { confirm: true },
    );
  },
  rollbackRunnerStateExecution(runId: string): Promise<RunnerStateExecutionRollbackReport> {
    return postJson(
      `/api/runs/${encodeURIComponent(runId)}/state-execution-rollback`,
      { confirm: true },
    );
  },
};

/** 把 artifact 中相对路径（assets/...）转为可直接用于 <img src> 的资产 URL。 */
export function assetUrl(storySlug: string, relPath: string): string {
  const rel = relPath.replace(/^assets\//, "");
  const encoded = rel
    .split("/")
    .map((seg) => encodeURIComponent(seg))
    .join("/");
  return `${API_BASE}/api/stories/${encodeURIComponent(storySlug)}/assets/${encoded}`;
}
