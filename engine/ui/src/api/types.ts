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

export interface ImportNovelRequest {
  name: string;
  chapters: ImportChapterInput[];
  genre?: string;
  mock?: boolean;
  force?: boolean;
}

export interface ImportNovelResponse {
  story_slug: string;
  display_name: string;
  character_count: number;
  chapter_count: number;
  anchor_chapter_index: number;
  extraction_mode: string;
  warnings: string[];
  anchor_hash: string;
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
}

export interface RuntimeSettingsPatch {
  api_key?: string;
  base_url?: string;
  model_name?: string;
  default_mock?: boolean;
  default_rounds?: number;
  default_runner?: string;
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
  run_count: number;
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
  multi_agent_trace: Record<string, unknown> | null;
  causal_diff: CausalDiffArtifact | null;
  child_runs: string[];
  cli_hints: string[];
}
