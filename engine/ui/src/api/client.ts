import type {
  AnchorPatch,
  AnchorUpdateResponse,
  BaselineGenerateRequest,
  BaselineGenerateResponse,
  BaselineReport,
  BranchDetail,
  CanonReplayReport,
  CanonReplayRequest,
  CharacterProbe,
  ConnectivityResult,
  DiffActionRequest,
  DiffActionResponse,
  EmergenceReport,
  GuardrailRequest,
  GuardrailResult,
  HoldoutManifest,
  HoldoutWriteRequest,
  IngestChunkRequest,
  IngestSessionCreateRequest,
  IngestSessionSummary,
  ImportNovelRequest,
  ImportNovelResponse,
  JobRecord,
  JobSubmitResponse,
  ProjectHealth,
  InterventionRequest,
  InterventionResponse,
  RunDetail,
  RunTreeNode,
  RuntimeSettings,
  RuntimeSettingsPatch,
  StoryGenesisRequest,
  StoryGenesisResponse,
  StorySummary,
  VisualAssets,
  VisualAssetsGenerateRequest,
  WorldAnchor,
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
  getProjectHealth(storySlug: string): Promise<ProjectHealth> {
    return getJson(`/api/stories/${encodeURIComponent(storySlug)}/health`);
  },
  updateWorldAnchor(storySlug: string, patch: AnchorPatch): Promise<AnchorUpdateResponse> {
    return postJson(`/api/stories/${encodeURIComponent(storySlug)}/anchor`, patch);
  },
  getRun(runId: string): Promise<RunDetail> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}`);
  },
  getBranch(runId: string, branchId: string): Promise<BranchDetail> {
    return getJson(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}`,
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
  postJobIntervention(req: InterventionRequest): Promise<JobSubmitResponse> {
    return postJson("/api/jobs/intervention", req);
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
  // ── v0.8+ 涌现节点 ─────────────────────────────────────
  generateEmergenceNodes(runId: string): Promise<EmergenceReport> {
    return postJson(`/api/runs/${encodeURIComponent(runId)}/emergence-nodes`, {});
  },
  getEmergenceNodes(runId: string): Promise<EmergenceReport> {
    return getJson(`/api/runs/${encodeURIComponent(runId)}/emergence-nodes`);
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
