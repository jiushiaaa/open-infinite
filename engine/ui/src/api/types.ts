// 与 living_novel_engine.browser.indexer 的 JSON 契约对应（只读）。
// 所有字段都按「可能缺失」处理：缺 artifact 不是错误，而是该分支尚未生成该资料。

export type SourceKind = "builtin" | "imported";
export type RunKind = "intervene" | "resume_continue" | "resume_intervene" | string;

export interface StorySummary {
  slug: string;
  display_name: string;
  source_kind: SourceKind;
  run_count: number;
}

export interface BranchSummaryNode {
  branch_id: string;
  theme: string;
  chapter_chars: number;
  retrieval_count: number;
  has_runtime_memory?: boolean;
  runtime_memory_layer_count?: number;
  has_multi_agent_trace: boolean;
  multi_agent_trace_count: number;
  has_causal_diff: boolean;
  causal_diff_count: number;
  child_runs: RunTreeNode[];
}

export interface RunTreeNode {
  run_id: string;
  kind: RunKind;
  story_slug: string;
  source_kind: SourceKind;
  intervention_preview: string;
  current_chapter: number | null;
  branches: BranchSummaryNode[];
  parent_run_id: string | null;
  parent_branch: string | null;
  is_orphan: boolean;
}

// ── intervention_compilation.json ─────────────────────────

export interface CompatibilityInfo {
  status?: string;
  risk?: string;
  reasons?: string[];
  contract_conflicts?: string[];
}

export interface RealizationInfo {
  mode?: string;
  description?: string;
  in_world?: boolean;
}

export interface BranchAxisItem {
  id: string;
  label: string;
  description?: string;
  stance?: string;
  outcome?: string;
  lineage_type?: string;
}

export interface AbstractIntervention {
  intervention_type?: string;
  intent?: string;
  target_refs?: string[];
  desired_effect?: string;
}

export interface AffectedScope {
  characters?: string[];
  locations?: string[];
  items?: string[];
  rules?: string[];
  scene_flags?: string[];
}

export interface InterventionCompilation {
  abstract_intervention?: AbstractIntervention;
  compatibility?: CompatibilityInfo;
  realization?: RealizationInfo;
  branch_axis?: BranchAxisItem[];
  lineage_type?: string;
  affected_scope?: AffectedScope;
  source?: string;
  compiler_version?: string;
  generation_meta?: Record<string, unknown> | null;
}

// ── causal_diff.json ──────────────────────────────────────

export type DiffStatus = "proposed" | "accepted" | "rejected" | "reverted";
export type DiffOp = "replace" | "insert" | "delete";
export type DiffMode = "local_divergence" | "broad_rewrite" | "alternate_novel_seed";

export interface DiffAnchor {
  chapter?: number;
  kind?: string;
  old_index?: number;
  new_index?: number;
  ref?: string;
}

export interface CausalDiffBlock {
  id: string;
  op: DiffOp;
  old_text: string;
  new_text: string;
  anchor?: DiffAnchor;
  note?: string;
  status?: DiffStatus | null;
}

export type DiffActionKind = "accept" | "reject" | "revert";

export interface DiffActionRequest {
  run_id: string;
  branch_id: string;
  action: DiffActionKind;
  block_id?: string;
}

export interface DiffActionResponse {
  causal_diff: CausalDiffArtifact;
}

export interface CausalDiffArtifact {
  diff_id: string;
  branch_id: string;
  lineage_type?: string;
  diff_mode?: DiffMode;
  status?: DiffStatus;
  intervention_summary?: Record<string, unknown>;
  affected_scope?: AffectedScope;
  blocks?: CausalDiffBlock[];
  reason?: string;
  created_at?: string;
  compiler_version?: string;
}

// ── POST /api/import-novel ────────────────────────────────

export interface ImportChapterInput {
  filename: string;
  content: string;
}

export interface ImportUploadChunk {
  index: number;
  data_b64: string;
}

export interface ImportUploadPayload {
  filename: string;
  total_size: number;
  chunk_size?: number;
  chunks: ImportUploadChunk[];
}

export interface ImportNovelRequest {
  name: string;
  chapters?: ImportChapterInput[];
  upload?: ImportUploadPayload;
  genre?: string;
  mock?: boolean;
  force?: boolean;
  long_mode?: boolean;
}

export interface ImportReportSummary {
  version: string;
  status?: string;
  source?: {
    type?: string;
    name?: string;
    file_count?: number;
    filenames?: string[];
  };
  total_chapters: number;
  total_characters: number;
  chapter_stats?: {
    min_characters?: number;
    max_characters?: number;
    average_characters?: number;
    short_chapters?: number[];
  };
  playable_chapter_limit: number;
  partial_ready: boolean;
  risks: {
    garbled_chapters?: number[];
    duplicate_titles?: string[];
    missing_chapter_numbers?: number[];
    short_chapters?: number[];
  };
  quality_risks?: ImportQualityRisk[];
  recommended_actions?: ImportRecommendedAction[];
  warnings: string[];
}

export interface ImportQualityRisk {
  code: string;
  level: "low" | "medium" | "high" | string;
  message: string;
  chapters?: number[];
  titles?: string[];
  missing_numbers?: number[];
}

export interface ImportRecommendedAction {
  kind: string;
  label: string;
  description: string;
}

export interface ImportChapterPreview {
  index: number;
  title: string;
  characters: number;
  preview: string;
  source_path?: string;
  source_filename?: string;
}

export interface ImportReview {
  status: "ready" | "missing" | "damaged" | string;
  summary: ImportReportSummary;
  quality_risks: ImportQualityRisk[];
  recommended_actions: ImportRecommendedAction[];
  warnings: string[];
  chapter_previews: ImportChapterPreview[];
}

export interface ProjectWorkspaceLayer {
  name: string;
  path: string;
  count: number;
}

export interface ProjectWorkspaceMemory {
  status: "ready" | "missing" | "damaged" | string;
  version: string;
  created_at?: string;
  layer_count: number;
  layers: ProjectWorkspaceLayer[];
  warnings: string[];
}

export interface ProjectMasterSettingWorkspace {
  version: string;
  status: "ready" | "missing" | "damaged" | string;
  mode: string;
  summary: {
    world_rule_count: number;
    character_count: number;
    timeline_event_count: number;
    plot_thread_count: number;
    chapter_brief_count: number;
  };
  sections: Array<{
    id: string;
    label: string;
    status: string;
    count: number;
    source_path: string;
  }>;
  world: {
    display_name: string;
    genre: string;
    world_rules: unknown[];
    locations: unknown[];
    factions: unknown[];
    power_system_limits: unknown[];
    forbidden_additions: unknown[];
  };
  characters: Array<{
    character_id: string;
    name: string;
    narrative_role: string;
    current_state: {
      location: string;
      emotion: string;
      resource_count: number;
    };
    persona_boundaries: unknown[];
    relationship_count: number;
    memory_count: number;
    source_path: string;
  }>;
  timeline: {
    status: string;
    event_count: number;
    samples: Array<{
      chapter?: number | null;
      title: string;
      summary: string;
      source_ref: string;
    }>;
  };
  plot_threads: {
    status: string;
    thread_count: number;
    active_threads: Array<{
      id: string;
      title: string;
      status: string;
      source_refs: unknown[];
    }>;
  };
  chapter_briefs: {
    status: string;
    chapter_count: number;
    samples: Array<{
      chapter?: number | null;
      title: string;
      summary: string;
      characters_present: unknown[];
      source_ref: string;
    }>;
  };
  capabilities: {
    read_only: boolean;
    can_edit: boolean;
    edit_note: string;
  };
  next_steps: string[];
  warnings: string[];
}

export interface MasterSettingPatch {
  display_name?: string;
  genre?: string;
  world_rules?: string[];
  power_system_limits?: string[];
  forbidden_additions?: string[];
}

export interface MasterSettingUpdateResponse {
  master_setting_workspace: ProjectMasterSettingWorkspace;
  changed: string[];
  backup: string | null;
}

export interface ProjectWorkspaceCanonLedger {
  status: "ready" | "missing" | "damaged" | string;
  entry_count: number;
  type_counts: Record<string, number>;
  samples: Array<{
    id: string;
    type: string;
    chapter?: number | null;
    source_ref: string;
    statement: string;
  }>;
  warnings: string[];
}

export interface ProjectWorkspaceRetrieval {
  status: "ready" | "missing" | string;
  hit_count: number;
  samples: Array<{
    run_id: string;
    branch_id: string;
    source?: string;
    source_ref?: string;
    score?: number | null;
    preview: string;
  }>;
  warnings: string[];
}

export interface ProjectWorkspaceAudit {
  status: "ready" | "missing" | "damaged" | string;
  version: string;
  created_at?: string;
  summary: {
    issue_count: number;
    risk_level?: string;
    entity_alias_count?: number;
  };
  dimensions: Array<{
    key: string;
    label: string;
    issue_count: number;
    severity_counts: Record<string, number>;
  }>;
  issues: Array<{
    category: string;
    kind: string;
    severity: string;
    detail: string;
    evidence: string;
  }>;
  repair_suggestions: string[];
  warnings: string[];
}

export interface ProjectWorkspace {
  version: string;
  slug: string;
  source_kind: SourceKind;
  display_name: string;
  source: {
    type?: string;
    name?: string;
    file_count?: number;
    filenames?: string[];
  };
  chapter_overview: {
    total_chapters: number;
    total_characters: number;
    playable_chapter_limit: number;
    partial_ready: boolean;
    previews: ImportChapterPreview[];
  };
  import_review: ImportReview | null;
  memory: ProjectWorkspaceMemory;
  master_setting_workspace: ProjectMasterSettingWorkspace;
  canon_ledger: ProjectWorkspaceCanonLedger;
  entity_aliases: EntityAliasSummary;
  retrieval: ProjectWorkspaceRetrieval;
  audit: ProjectWorkspaceAudit;
  creation_loop?: ProjectCreationLoop;
  run_count: number;
  actions: {
    anchor_hash: string;
    workspace_hash: string;
    can_start_baseline: boolean;
    can_start_intervention: boolean;
    next_steps: string[];
  };
}

export type CreationLoopStepStatus = "done" | "todo" | "warn" | string;

export interface ProjectCreationLoopCandidate {
  run_id: string;
  branch_id: string;
  run_kind: string;
  branch_label: string;
  chapter_chars: number;
  has_export: boolean;
  export_api_path: string;
  has_judgement: boolean;
  recommendation: string;
  overall_score: number | null;
  has_causal_diff: boolean;
  causal_diff_status?: string | null;
  state_overlay_applied: boolean;
  child_run_count: number;
  continue_hint: string;
  is_selected?: boolean;
}

export interface ProjectCreationLoopSelection {
  version: string;
  kind: "selected_worldline" | string;
  status: "ready" | string;
  story_slug: string;
  run_id: string;
  branch_id: string;
  branch_label: string;
  chapter_chars: number;
  export_api_path: string;
  note: string;
  selected_at: string;
}

export interface ProjectCreationLoopChecklistItem {
  id: string;
  label: string;
  status: CreationLoopStepStatus;
  detail: string;
}

export interface ProjectCreationLoopPostRunAudit {
  status: "ready" | "warn" | "todo" | string;
  selected_run_id: string;
  selected_branch_id: string;
  selected_label: string;
  summary: string;
  review_hash: string;
  has_range_replay: boolean;
  risk_level: string;
  static_issue_count: number;
  risk_dimensions: Array<Record<string, unknown>>;
  missing_entities: string[];
  range_replay?: unknown;
  next_actions: string[];
}

export interface ProjectCreationLoopCompletion {
  kind: "creation_loop_completion" | string;
  status: "ready" | "warn" | "todo" | string;
  done_count: number;
  total_count: number;
  blocking_ids: string[];
  blocking_labels: string[];
  evidence: ProjectCreationLoopEvidence[];
  actions: ProjectCreationLoopAction[];
  summary: string;
  can_mark_alpha_complete: boolean;
}

export interface ProjectCreationLoopCloseout {
  kind: "creation_loop_alpha_closeout" | string;
  status: "ready" | "not_ready" | string;
  can_close_alpha: boolean;
  ready_count: number;
  required_count: number;
  remaining_blocker_ids: string[];
  remaining_blockers: string[];
  evidence: ProjectCreationLoopEvidence[];
  summary: string;
  next_step: string;
}

export interface ProjectCreationLoopEvidence {
  id: string;
  label: string;
  status: string;
  source: "artifact" | "api" | "route" | "state" | string;
  ref: string;
  detail: string;
}

export interface ProjectCreationLoopAction {
  id: string;
  label: string;
  status: string;
  kind: "api" | "route" | string;
  method: string;
  api_path?: string;
  route_hash?: string;
  payload?: CanonReplayRangeRequest | WorldlineSelectionRequest | WorldlineJudgementRequest;
  requirements?: ProjectCreationLoopActionRequirement[];
  detail: string;
}

export interface ProjectCreationLoopActionRequirement {
  id: string;
  label: string;
  status: string;
  detail: string;
}

export interface ProjectCreationLoop {
  version: string;
  status: "ready" | "empty" | string;
  recommended: ProjectCreationLoopCandidate | null;
  selected?: ProjectCreationLoopSelection | null;
  post_run_audit?: ProjectCreationLoopPostRunAudit;
  candidates: ProjectCreationLoopCandidate[];
  checklist: ProjectCreationLoopChecklistItem[];
  completion?: ProjectCreationLoopCompletion;
  closeout?: ProjectCreationLoopCloseout;
  next_steps: string[];
}

export interface WorldlineSelectionRequest {
  run_id: string;
  branch_id: string;
  note?: string;
}

export interface WorldlineSelectionResponse {
  selection: ProjectCreationLoopSelection;
}

export interface ImportNovelResponse {
  story_slug: string;
  display_name: string;
  character_count: number;
  chapter_count: number;
  anchor_chapter_index: number;
  extraction_mode: string;
  warnings: string[];
  import_report?: ImportReportSummary;
  anchor_hash: string;
}

export interface IngestSessionCreateRequest {
  name: string;
  filename: string;
  total_size: number;
  chunk_size: number;
  total_chunks?: number;
  file_sha256?: string;
  genre?: string;
  mock?: boolean;
  force?: boolean;
  long_mode?: boolean;
}

export interface IngestChunkRequest {
  index: number;
  data_b64: string;
  sha256?: string;
}

export interface IngestSessionSummary {
  version: string;
  session_id: string;
  status: "uploading" | "ready" | "imported" | "expired" | string;
  filename: string;
  total_size: number;
  chunk_size: number;
  total_chunks: number;
  received_chunks: number[];
  missing_chunks: number[];
  received_bytes: number;
  progress: number;
  created_at: number;
  updated_at: number;
  expires_at: number;
  import_request: {
    name?: string;
    genre?: string;
    mock?: boolean;
    force?: boolean;
    long_mode?: boolean;
  };
  duplicate?: boolean;
}

// ── GET /api/stories/<slug>/health & POST /api/stories/<slug>/anchor ──

export type HealthStatus = "ok" | "warning" | "error";

export interface ProjectHealth {
  slug: string;
  status: HealthStatus;
  errors: string[];
  warnings: string[];
  files: Record<string, "ok" | "missing" | "error">;
  source_kind: SourceKind;
}

export interface AnchorPatch {
  world?: {
    rules?: string[];
    scene_description?: string;
  };
  characters?: Array<{
    id: string;
    persona?: { boundaries?: string[]; traits?: string[] };
    current_state?: { location?: string; emotion?: string };
  }>;
  open_threads?: Array<{
    id?: string;
    title: string;
    description?: string;
    status?: string;
  }>;
}

export interface AnchorUpdateResponse {
  anchor: WorldAnchor;
  health: ProjectHealth;
  changed: string[];
  backup: string | null;
}

// ── /api/jobs/* ───────────────────────────────────────────

export type JobStatus = "queued" | "running" | "succeeded" | "failed";

export interface JobSubmitResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobRecord<T = unknown> {
  job_id: string;
  kind: string;
  status: JobStatus;
  progress: number;
  stage: string;
  created_at: number;
  updated_at: number;
  result: T | null;
  error: string | null;
}

// ── /api/settings/runtime ─────────────────────────────────

export type RunnerName = "lightweight" | "multi_agent_stub" | "multi_agent_llm";

export interface RuntimeSettings {
  llm_api_key_present: boolean;
  masked_key: string;
  llm_base_url: string;
  llm_model_name: string;
  default_mock: boolean;
  default_rounds: number;
  default_runner: string;
  available_runners: string[];
  seedream_enabled: boolean;
  visual_assets_enabled: boolean;
  seedream_key_present: boolean;
  seedream_masked_key: string;
  seedream_base_url: string;
  seedream_model: string;
  llm_input_cost_per_1k: number;
  llm_output_cost_per_1k: number;
}

export interface RuntimeSettingsPatch {
  api_key?: string;
  base_url?: string;
  model_name?: string;
  default_mock?: boolean;
  default_rounds?: number;
  default_runner?: string;
  seedream_api_key?: string;
  seedream_base_url?: string;
  seedream_model?: string;
  visual_assets_enabled?: boolean;
  llm_input_cost_per_1k?: number;
  llm_output_cost_per_1k?: number;
}

export interface ProviderGatewayProvider {
  id: string;
  kind: string;
  display_name: string;
  configured: boolean;
  active: boolean;
  masked_key: string;
  base_url: string;
  model: string;
  fallback: string;
  usage_source: string;
}

export interface ProviderGatewaySummary {
  version: string;
  routing: {
    mode: string;
    llm_route: string;
    visual_route: string;
    fallback_policy: string;
  };
  providers: ProviderGatewayProvider[];
  routes: Array<{
    id: string;
    label: string;
    provider_id: string;
    runner: string | null;
    mode: string;
    fallback: string;
  }>;
  cost_policy: {
    currency: string;
    estimation_mode: string;
    price_table_status: string;
    estimated_total: number | null;
    input_cost_per_1k: number;
    output_cost_per_1k: number;
    usage_fields: string[];
    note: string;
  };
  warnings: Array<{ code: string; message: string }>;
}

export interface TokenUsageTotals {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ProviderUsageRecord {
  provider_id: string;
  run_id: string;
  branch_id: string | null;
  artifact: string;
  source?: string | null;
  model_name?: string | null;
  usage: TokenUsageTotals;
}

export interface ProviderUsageSummary {
  version: string;
  story_slug: string | null;
  run_count: number;
  record_count: number;
  missing_usage_record_count: number;
  totals: TokenUsageTotals;
  by_provider: Array<{ provider_id: string; record_count: number } & TokenUsageTotals>;
  records: ProviderUsageRecord[];
  record_limit: number;
  truncated: boolean;
  cost_estimate: {
    currency: string;
    estimated_total: number | null;
    reason: string;
    input_cost_per_1k: number;
    output_cost_per_1k: number;
  };
}

export interface CommercialStatusDomain {
  id: string;
  label: string;
  status: "ready" | "attention" | "deferred" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface CommercialStatusOverview {
  version: string;
  mode: string;
  overall_status: "ready" | "attention" | string;
  summary: {
    total_domains: number;
    ready_domains: number;
    attention_domains: number;
    deferred_domains: number;
  };
  domains: CommercialStatusDomain[];
  warnings: string[];
  next_steps: string[];
}

export interface ProjectAuditLogEvent {
  event_id: string;
  action: string;
  label: string;
  actor_type: string;
  scope: string;
  artifact: string;
  created_at: string;
  severity: string;
  summary: string;
  metadata: Record<string, unknown>;
}

export interface ProjectAuditLog {
  version: string;
  status: "ready" | "empty" | string;
  story_slug: string;
  source_kind: SourceKind;
  summary: {
    event_count: number;
    source_count: number;
    action_counts: Record<string, number>;
  };
  events: ProjectAuditLogEvent[];
  warnings: Array<{ code: string; message: string }>;
  next_steps: string[];
}

export interface ProjectAuditLogExport {
  version: string;
  kind: "project_audit_log_export" | string;
  status: string;
  story_slug: string;
  source_kind: SourceKind;
  filename: string;
  content_type: string;
  content_md: string;
  metadata: {
    event_count: number;
    source_count: number;
    exported_at: string;
  };
  share_guard: ExportShareGuard;
  audit_log: ProjectAuditLog;
  next_steps: string[];
}

export interface LocalSmokeChecklistItem {
  id: string;
  label: string;
  method: string;
  path: string;
  expected: string;
  status: "ready_to_run" | string;
  example_url: string;
}

export interface LocalSmokeChecklist {
  version: string;
  status: "ready" | "attention" | string;
  mode: string;
  summary: {
    check_count: number;
    ready_to_run_count: number;
    external_services_required: boolean;
  };
  checks: LocalSmokeChecklistItem[];
  run_steps: string[];
  warnings: string[];
  next_steps: string[];
}

export interface ReleasePreflightCheckpoint {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface ReleasePreflightChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  story_slug: string;
  summary: {
    checkpoint_count: number;
    ready_count: number;
    attention_count: number;
    external_services_required: boolean;
  };
  checkpoints: ReleasePreflightCheckpoint[];
  warnings: string[];
  next_steps: string[];
}

// ── v0.7.3 视觉资产 ───────────────────────────────────────

export type AssetStatus = "ready" | "failed" | "placeholder";
export type VisualOverallStatus = "none" | "partial" | "ready" | "failed";

export interface AssetEntry {
  asset_id: string;
  kind: string;
  prompt: string;
  status: AssetStatus;
  path: string;
  created_at: string;
  error: string;
}

export interface VisualAssets {
  version: string;
  story_slug: string;
  provider: string;
  status: VisualOverallStatus;
  cover: AssetEntry | null;
  characters: Record<string, AssetEntry>;
  scenes: Record<string, AssetEntry>;
  worldline_nodes: Record<string, AssetEntry>;
}

export interface VisualAssetsGenerateRequest {
  kinds?: string[];
  character_ids?: string[];
  force?: boolean;
  mock?: boolean;
}

export interface ConnectivityResult {
  available: boolean;
  reason?: string;
  error?: string;
  model?: string | null;
  mode?: string;
}

// ── POST /api/story-genesis ───────────────────────────────

export interface StoryGenesisRequest {
  name: string;
  premise: string;
  genre?: string;
  protagonist_hint?: string;
  style_hint?: string;
  mock?: boolean;
  force?: boolean;
}

export interface StoryGenesisResponse {
  story_slug: string;
  display_name: string;
  chapter_count: number;
  character_count: number;
  generation_mode: string;
  anchor_chapter_index: number;
  warnings: string[];
  anchor_hash: string;
}

// ── GET /api/stories/<slug>/anchor ────────────────────────

export interface WorldLocation {
  id?: string;
  name?: string;
  description?: string;
}

export interface AnchorCharacter {
  id: string;
  name: string;
  narrative_role: string;
  gender: string;
  present_in_scene: boolean;
  persona: {
    traits: string[];
    desires: string[];
    fears: string[];
    boundaries: string[];
  };
  current_state: {
    location: string;
    emotion: string;
    resources: string[];
  };
  memory: string[];
  relationships: Record<string, string>;
  address_rules: string[];
}

export interface AnchorThread {
  id: string;
  title: string;
  description: string;
  status: string;
}

export interface AnchorSummary {
  chapter?: number | null;
  title?: string;
  summary?: string;
  key_events?: string[];
  characters_present?: string[];
}

export interface EntityAliasSummary {
  status: "ready" | "missing" | "damaged" | string;
  path: string;
  count: number;
  sample_entities: Array<{
    entity_id: string;
    canonical_name: string;
    entity_type: string;
    alias_count: number;
  }>;
}

export interface RuntimeMemoryContext {
  version: string;
  query: string;
  current_chapter: number;
  prompt_block?: string;
  consumed_layers: string[];
  entity_aliases?: EntityAliasSummary;
  resolved_query_entities?: string[];
  warnings?: string[];
  retrieval?: Record<string, unknown>;
}

export interface WorldAnchor {
  slug: string;
  source_kind: SourceKind;
  display_name: string;
  divergence_point: string;
  world: {
    display_name: string;
    source_type: string;
    canonical_place_name: string;
    worldline_policy: string;
    scene_description: string;
    current_chapter: number | null;
    rules: string[];
    locations: WorldLocation[];
    factions: string[];
    timeline: string[];
  };
  characters: AnchorCharacter[];
  story_contract: Record<string, unknown> | null;
  open_threads: AnchorThread[];
  summaries: AnchorSummary[];
  entity_aliases?: EntityAliasSummary;
  import_review?: ImportReview | null;
  run_count: number;
}

// ── v0.7.4 基线与正史回放 ─────────────────────────────────

export interface BaselineCharacterStateChange {
  character_id: string;
  name: string;
  location: string;
  emotion: string;
}

export interface BaselineReport {
  version: string;
  kind: "baseline";
  story_slug: string;
  source_kind: SourceKind;
  run_id: string;
  branch_id: string;
  from_run_id: string | null;
  from_branch_id: string | null;
  chapter_number: number;
  runner: string;
  mock: boolean;
  no_intervention: boolean;
  summary: string;
  natural_development_points: string[];
  character_state_changes: BaselineCharacterStateChange[];
  open_threads_touched: string[];
  created_at: string;
}

export interface BaselineGenerateRequest {
  rounds?: number;
  mock?: boolean;
  runner_name?: string;
  from_run_id?: string | null;
  from_branch_id?: string | null;
}

export interface BaselineGenerateResponse {
  run_id: string;
  branch_id: string;
  story_slug: string;
  summary: string;
  report: BaselineReport;
  tree: RunTreeNode[];
}

export interface HoldoutChapter {
  chapter: number;
  title: string;
  path: string;
  chars: number;
}

export interface HoldoutManifest {
  version: string;
  story_slug: string;
  chapters: HoldoutChapter[];
  created_at: string;
  updated_at: string;
  chapter_count: number;
  available_chapters: number[];
}

export interface HoldoutChapterInput {
  chapter: number;
  title?: string;
  content: string;
}

export interface HoldoutWriteRequest {
  chapters: HoldoutChapterInput[];
  force?: boolean;
}

export interface ReplayScores {
  lexical_overlap: number;
  entity_overlap: number;
  thread_overlap: number;
  length_ratio: number;
  state_consistency: number;
  overall: number;
}

export interface CanonReplayReport {
  version: string;
  kind: "canon_replay";
  story_slug: string;
  baseline_run_id: string;
  baseline_branch_id: string;
  holdout_chapter: number;
  scores: ReplayScores;
  matched_entities: string[];
  missing_entities: string[];
  matched_threads: string[];
  warnings: string[];
  interpretation: string;
  created_at: string;
}

export interface CanonReplayRequest {
  baseline_run_id: string;
  baseline_branch_id?: string;
  holdout_chapter: number;
}

export interface CanonReplayRangeRequest {
  baseline_run_id: string;
  baseline_branch_id?: string;
  chapter_start: number;
  chapter_end: number;
}

export interface CanonReplayRiskDimension {
  key: string;
  label: string;
  score: number;
  risk_level: "low" | "medium" | "high" | string;
  message: string;
}

export interface CanonReplayRangeReport {
  version: string;
  kind: "canon_replay_range";
  story_slug: string;
  baseline_run_id: string;
  baseline_branch_id: string;
  chapter_range: {
    start: number;
    end: number;
  };
  available_chapters: number[];
  reports: CanonReplayReport[];
  summary: {
    chapter_count: number;
    average_overall: number;
    risk_level: "low" | "medium" | "high" | string;
    weakest_chapter: number;
    warning_count: number;
  };
  score_averages: ReplayScores;
  risk_dimensions: CanonReplayRiskDimension[];
  entity_audit: {
    matched_entities: string[];
    missing_entities: string[];
    missing_entities_by_chapter: Array<{
      chapter: number;
      entities: string[];
    }>;
  };
  created_at: string;
}

export interface ReplayAuditBaselineRun {
  run_id: string;
  branch_id: string;
  chapter_number?: number | null;
  summary: string;
  created_at: string;
  from_run_id?: string | null;
  from_branch_id?: string | null;
}

export interface ReplayAuditWorkspace {
  version: string;
  slug: string;
  source_kind: SourceKind;
  display_name: string;
  holdout: HoldoutManifest;
  baseline_runs: ReplayAuditBaselineRun[];
  replay_ranges: Array<{
    run_id: string;
    status: string;
    chapter_range: {
      start?: number;
      end?: number;
    };
    available_chapters: number[];
    summary: CanonReplayRangeReport["summary"];
    risk_dimensions: CanonReplayRiskDimension[];
    entity_audit: CanonReplayRangeReport["entity_audit"];
    created_at: string;
  }>;
  audit: ProjectWorkspaceAudit;
  entity_aliases: EntityAliasSummary;
  next_steps: string[];
}

// ── v0.7.5 世界线评审 ───────────────────────────────────

export type WorldlineRecommendation = "推荐继续" | "谨慎继续" | "建议归档";

export interface WorldlineJudgeScores {
  persona_consistency: number;
  contract_risk: number;
  branch_diversity: number;
  narrative_momentum: number;
  emotional_payoff: number;
  anti_slop: number;
  continuation_potential: number;
  emergence_score: number;
  story_arc: number;
  turning_points: number;
  tension: number;
  overall: number;
}

export interface JudgementDimension {
  key: string;
  label: string;
  score: number;
  evidence: string[];
  comment: string;
}

export interface StoryArcPoint {
  label: string;
  tension: number;
  momentum: number;
}

export interface WorldlineJudgement {
  version: string;
  kind: "worldline_judgement";
  story_slug: string;
  source_kind: SourceKind;
  run_id: string;
  branch_id: string;
  chapter_number: number | null;
  recommendation: WorldlineRecommendation;
  scores: WorldlineJudgeScores;
  dimensions: JudgementDimension[];
  turning_points: string[];
  story_arc_curve: StoryArcPoint[];
  strengths: string[];
  warnings: string[];
  suggestions: string[];
  interpretation: string;
  created_at: string;
}

export interface WorldlineJudgementRequest {
  story_slug?: string;
}

// ── v0.9.0-alpha 章节导出 ─────────────────────────────────

export interface ExportShareGuard {
  kind: "export_share_guard" | string;
  status: string;
  source_kind: string;
  private_use_allowed: boolean;
  public_share_allowed: boolean;
  requires_rights_confirmation: boolean;
  notice: string;
  warnings: string[];
}

export interface ChapterExport {
  version: string;
  kind: "chapter_export";
  run_id: string;
  branch_id: string;
  story_slug: string;
  filename: string;
  content_type: string;
  content_md: string;
  share_guard: ExportShareGuard;
  metadata: {
    source_kind: string;
    branch_label: string;
    judgement_recommendation: string;
    judgement_overall?: number | null;
    causal_diff_status?: string | null;
    state_overlay_applied: boolean;
    ai_notice: string;
    source_notice: string;
    exported_at: string;
  };
}

export interface ChapterCollectionExport {
  version: string;
  kind: "chapter_collection_export";
  run_id: string;
  branch_id: string;
  story_slug: string;
  filename: string;
  content_type: string;
  content_md: string;
  chapter_count: number;
  chapters: Array<{
    run_id: string;
    branch_id: string;
    branch_label: string;
  }>;
  warnings: string[];
  share_guard: ExportShareGuard;
  metadata: {
    source_kind: string;
    ai_notice: string;
    source_notice: string;
    exported_at: string;
  };
}

// ── v0.8+ ActDirector / Dynamic Action / Emergence ───────

export interface ActionPlanStep {
  action_id: string;
  branch_axis_id: string;
  branch_label: string;
  character_id: string;
  character_name: string;
  action_type: string;
  action_label: string;
  preconditions: string[];
  effects: string[];
  failure_reason: string;
  repair_suggestions: string[];
  risk: GuardrailRisk;
  visibility: string;
  rationale: string;
  metadata: Record<string, unknown>;
}

export interface CharacterActionPlan {
  version: string;
  kind: "act_director_plan";
  story_slug: string;
  lineage_type: string;
  source_compiler_version: string;
  steps: ActionPlanStep[];
  warnings: string[];
}

export interface ActionRegistryEntry {
  action_type: string;
  action_label: string;
  aliases: string[];
  preconditions: string[];
  effects: string[];
  failure_reasons: string[];
  repair_suggestions: string[];
  risk: GuardrailRisk;
  visibility: string;
  source_step_ids: string[];
  branch_axis_ids: string[];
  metadata: Record<string, unknown>;
}

export interface DynamicActionRegistry {
  version: string;
  kind: "dynamic_action_registry";
  story_slug: string;
  source_plan_version: string;
  actions: ActionRegistryEntry[];
  aliases: Record<string, string>;
  warnings: string[];
  summary: Record<string, unknown>;
}

export type EmergenceNodeStatus = "candidate" | "high_value" | "archive";

export interface EmergenceNode {
  node_id: string;
  branch_id: string;
  node_type: string;
  title: string;
  description: string;
  score: number;
  evidence: string[];
  source_artifacts: string[];
  tags: string[];
  recommendation: string;
  status: EmergenceNodeStatus;
  metadata: Record<string, unknown>;
}

export interface EmergenceReport {
  version: string;
  kind: "emergence_nodes";
  story_slug: string;
  run_id: string;
  nodes: EmergenceNode[];
  summary: Record<string, unknown>;
  warnings: string[];
}

export type StateExecutionGateStatus =
  | "executable"
  | "review_required"
  | "blocked";

export interface RunnerStateDeltaPreview {
  character_id: string;
  field: string;
  old_value: unknown;
  new_value: unknown;
  reason: string;
}

export interface RunnerStateExecutionCandidate {
  candidate_id: string;
  source_step_id: string;
  branch_axis_id: string;
  branch_id: string;
  character_id: string;
  character_name: string;
  action_type: string;
  action_label: string;
  risk: GuardrailRisk | string;
  visibility: string;
  gate_status: StateExecutionGateStatus | string;
  state_deltas: RunnerStateDeltaPreview[];
  blockers: string[];
  warnings: string[];
  evidence: string[];
  source_artifacts: string[];
}

export interface RunnerStateExecutionReport {
  version: string;
  kind: "runner_state_execution_spike";
  mode: "dry_run" | string;
  run_id: string;
  story_slug: string;
  source_artifacts: string[];
  summary: {
    candidate_count: number;
    executable_count: number;
    review_required_count: number;
    blocked_count: number;
    high_risk_count: number;
    applied_count: number;
  };
  safety: {
    default_run_scene_unchanged: boolean;
    writes_state_snapshot: boolean;
    writes_branch_artifacts: boolean;
    apply_mode: string;
    required_before_mvp: string[];
  };
  candidates: RunnerStateExecutionCandidate[];
  emergence_summary: Record<string, unknown>;
  warnings: string[];
  created_at: string;
}

export interface StateExecutionOverlay {
  version: string;
  kind: "state_execution_overlay";
  mode: "overlay" | string;
  run_id: string;
  branch_id: string;
  base_snapshot: string;
  applied_candidate_ids: string[];
  state_deltas: RunnerStateDeltaPreview[];
  state_overlay: Record<string, unknown>;
  rollback: Record<string, unknown>;
  created_at: string;
}

export interface RunnerStateExecutionApplyReport {
  version: string;
  kind: "runner_state_execution_apply";
  mode: "overlay" | string;
  run_id: string;
  story_slug: string;
  status: "applied" | "rolled_back" | string;
  summary: {
    candidate_count: number;
    applied_count: number;
    skipped_count: number;
    overlay_count: number;
  };
  safety: {
    default_run_scene_unchanged: boolean;
    mutates_state_snapshot: boolean;
    writes_branch_artifacts: boolean;
    rollback_available: boolean;
    apply_mode: string;
  };
  branch_overlays: Array<{
    branch_id: string;
    path: string;
    applied_candidate_ids: string[];
    delta_count: number;
  }>;
  skipped_candidates: Array<{
    candidate_id: string;
    reason: string;
  }>;
  created_at: string;
  rolled_back_at?: string;
}

export interface RunnerStateExecutionRollbackReport {
  version: string;
  kind: "runner_state_execution_rollback";
  mode: "overlay" | string;
  run_id: string;
  summary: {
    removed_overlay_count: number;
  };
  removed_artifacts: string[];
  safety: {
    default_run_scene_unchanged: boolean;
    mutates_state_snapshot: boolean;
  };
  created_at: string;
}

export interface NarrativeDiagnostics {
  version: string;
  kind: "narrative_diagnostics";
  branch_id?: string;
  metrics?: {
    char_count?: number;
    sentence_count?: number;
    paragraph_count?: number;
    dialogue_marker_count?: number;
    turning_marker_count?: number;
    pacing?: number;
  };
  tension_curve?: Array<{
    index: number;
    tension: number;
  }>;
  warnings?: string[];
  suggestions?: string[];
}

// ── POST /api/interventions/guardrail （v0.7.2 护栏预检）──────

export type GuardrailRisk = "low" | "medium" | "high";
export type GuardrailCategory =
  | "genre"
  | "time_power"
  | "persona"
  | "world_rule"
  | "visibility"
  | "strength";

export interface GuardrailCheck {
  category: GuardrailCategory;
  label: string;
  passed: boolean;
  risk: GuardrailRisk;
  detail: string;
  repair_suggestion: string;
}

export interface GuardrailRequest {
  story_slug: string;
  content: string;
  target?: string;
  intervention_type?: string;
  visibility?: string;
  strength?: string;
}

export interface GuardrailResult {
  allowed: boolean;
  risk: GuardrailRisk;
  intervention_type: string;
  categories: GuardrailCheck[];
  violations: string[];
  repair_suggestions: string[];
  safer_alternative: string | null;
  rewritten_intent: string | null;
  explanation: string;
}

// ── GET /api/stories/<slug>/characters/<id>/probe （v0.7.2 探针）──

export interface CharacterProbe {
  character_id: string;
  name: string;
  narrative_role: string;
  belief_summary: string;
  current_emotion: string;
  desires: string[];
  fears: string[];
  boundaries: string[];
  known_information: string[];
  unknown_information: string[];
  fourth_wall_awareness: number;
  fourth_wall_level: string;
  likely_intervention_response: string;
  obedience_risk: GuardrailRisk;
  resistance_level: GuardrailRisk;
  explanation: string;
}

// ── /api/runs/<id> ────────────────────────────────────────

export interface RunDetail {
  run_id: string;
  kind: RunKind;
  story_slug: string;
  source_kind: SourceKind;
  branches: unknown[];
  parent_run_id: string | null;
  parent_branch: string | null;
  current_chapter: number | null;
  intervention_preview?: string;
  intervention?: Record<string, unknown>;
  intervention_compilation?: InterventionCompilation;
  meta?: Record<string, unknown>;
  compare_md?: string;
  cli_hints?: string[];
}

// ── POST /api/interventions ───────────────────────────────

export interface InterventionRequest {
  story_slug: string;
  target: string;
  content: string;
  intervention_type?: string;
  branches?: number;
  rounds?: number;
  mock?: boolean;
  runner_name?: string;
}

export interface InterventionResponse {
  run_id: string;
  branch_ids: string[];
  primary_branch: string | null;
  story_slug: string;
  llm_mock: boolean;
  fallback_reason: string | null;
  intervention_compilation: InterventionCompilation;
  act_director_plan?: CharacterActionPlan | null;
  dynamic_action_registry?: DynamicActionRegistry | null;
  emergence_nodes?: EmergenceReport | null;
  tree: RunTreeNode[];
}

// ── POST /api/jobs/resume-continue ───────────────────────

export interface ResumeContinueRequest {
  run_id: string;
  branch_id: string;
  rounds?: number;
  mock?: boolean;
  runner_name?: string;
}

export interface ResumeContinueResponse {
  run_id: string;
  branch_id: string;
  story_slug: string;
  source_kind: SourceKind;
  parent_run_id: string;
  parent_branch_id: string;
  chapter_number: number;
  llm_mock: boolean;
  fallback_reason: string | null;
  tree: RunTreeNode[];
}

// ── /api/runs/<id>/branches/<id> ──────────────────────────

export interface BranchDetail {
  run_id: string;
  branch_id: string;
  theme: string;
  chapter_md: string;
  summary_md: string;
  state_snapshot: Record<string, unknown> | null;
  events: Record<string, unknown> | null;
  retrieval: Record<string, unknown> | null;
  runtime_memory_context?: RuntimeMemoryContext | null;
  act_director_plan?: CharacterActionPlan | null;
  dynamic_action_registry?: DynamicActionRegistry | null;
  narrative_diagnostics?: NarrativeDiagnostics | null;
  emergence_nodes?: EmergenceReport | null;
  runner_state_execution_report?: RunnerStateExecutionReport | null;
  runner_state_execution_apply_report?: RunnerStateExecutionApplyReport | null;
  runner_state_execution_rollback_report?: RunnerStateExecutionRollbackReport | null;
  state_execution_overlay?: StateExecutionOverlay | null;
  multi_agent_trace: Record<string, unknown> | null;
  causal_diff: CausalDiffArtifact | null;
  child_runs: string[];
  cli_hints: string[];
}
