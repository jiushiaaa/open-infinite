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
  warnings: Array<string | { code: string; message: string }>;
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

export interface CardsWorkspaceField {
  label: string;
  items: string[];
  status: "ready" | "missing" | string;
  empty: string;
}

export interface CardsWorkspaceCard {
  id: string;
  type: "world" | "character" | "style" | string;
  title: string;
  subtitle: string;
  status: "ready" | "attention" | string;
  status_label: string;
  source_paths: string[];
  editable_fields: string[];
  fields: CardsWorkspaceField[];
}

export interface CardsWorkspaceGroup {
  id: string;
  label: string;
  count: number;
  card_ids: string[];
}

export interface CardsWorkspaceReport {
  version: string;
  mode: "read_only_cards_workspace" | string;
  status: "ready" | "attention" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    card_count: number;
    world_card_count: number;
    character_card_count: number;
    style_card_count: number;
    editable_card_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
  };
  groups: CardsWorkspaceGroup[];
  cards: CardsWorkspaceCard[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface WorldSandboxInterventionConstraint {
  status: "active" | "none" | string;
  source: string;
  content: string;
  target?: string;
  projection_mode?: "immersive" | "wild_au" | string;
  intervention_type?: string;
  intervention_level?: string;
  compatibility?: {
    status?: string;
    reason?: string;
    tianming_pressure_level?: string;
    foreign_object_intrusion?: boolean;
  };
  translation_strategy?: {
    strategy?: string;
    packaging?: string;
    original_hint?: string;
    level?: string;
    mode?: string;
    projection_mode?: string;
    foreign_object_intrusion?: boolean;
  };
  worldline_judgement?: {
    kind?: string;
    reason?: string;
  };
  branch_axis?: {
    id?: string;
    target?: string;
    axis?: string;
    question?: string;
  };
  causal_debt?: {
    level?: string;
    score?: number;
    spread?: string[];
  };
  worldline_tianming_snapshot?: {
    artifact: string;
    status: string;
    worldline_id: string;
    root_tianming_mutated: boolean;
    requires_confirmation: boolean;
  } | null;
  boundaries?: string[];
}

export interface WorldSandboxResistanceBehavior {
  type?: string;
  label?: string;
  description?: string;
}

export interface WorldSandboxMemePropagation {
  status?: "source" | "received" | "none" | string;
  source_character_id?: string;
  source_character_name?: string;
  belief_payload?: string;
  source_channel?: string;
  belief_decision?: "accepted" | "doubted" | "rejected" | string;
  belief_reason?: string;
  credibility_score?: number;
  signals?: {
    persona?: string;
    relationship?: string;
    previous_memory?: string;
    anomaly?: string;
  };
  reaction?: WorldSandboxResistanceBehavior;
}

export interface WorldSandboxMemePropagationReadout {
  status?: "source" | "received" | "none" | string;
  source_character_id?: string;
  source_character_name?: string;
  truth_payload?: string;
  belief_status?: "accepted" | "doubted" | "rejected" | string;
  belief_label?: string;
  belief_reason?: string;
  credibility_score?: number;
  source_channel?: string;
  reaction_type?: string;
  reaction_label?: string;
  reaction_description?: string;
  readable_summary?: string;
}

export interface WorldSandboxLLMDecisionAdvisory {
  status?: string;
  generated_by?: string;
  character_id?: string;
  belief_update?: string;
  visible_action?: string;
  true_intent?: string;
  expected_outcome?: string;
  risk?: string;
  deception_strategy?: string;
  propagation_choice?: string;
  resistance_choice?: string;
  situational_judgement?: string;
  trust_shift?: string;
  memory_seed?: string[];
  strategic_interaction?: {
    actor_character_id?: string;
    target_character_id?: string;
    tactic?: string;
    private_goal?: string;
    perceived_leverage?: string;
    assumed_misread?: string;
    risk_assessment?: string;
    expected_world_effect?: string;
    outcome_hook?: string;
  };
  deterministic_baseline?: {
    decision_mode?: string;
    visible_action?: string;
    true_intent?: string;
    expected_outcome?: string;
    risk?: string;
  };
}

export interface WorldSandboxCharacterAction {
  character_id: string;
  character_name: string;
  narrative_role: string;
  known_information: string[];
  previous_subjective_memory: string;
  decision_mode?: string;
  decision_inputs?: Record<string, string | number | boolean | null>;
  intent: string;
  action: string;
  visible_action?: string;
  true_intent?: string;
  expected_outcome?: string;
  risk?: string;
  memory_influence?: string;
  action_outcome?: {
    status?: string;
    reason?: string;
    cost?: string;
  };
  awareness?: {
    level?: string;
    abnormality?: string;
    belief_payload?: string;
  };
  resistance_behavior?: WorldSandboxResistanceBehavior;
  meme_contamination?: {
    status?: string;
    belief_payload?: string;
    spread_vector?: string[];
  };
  meme_propagation?: WorldSandboxMemePropagation;
  meme_propagation_readout?: WorldSandboxMemePropagationReadout;
  llm_decision_advisory?: WorldSandboxLLMDecisionAdvisory;
  strategic_interaction?: WorldSandboxLLMDecisionAdvisory["strategic_interaction"];
  fate_mark?: {
    status?: string;
    label?: string;
    description?: string;
    source_character_id?: string;
    belief_decision?: string;
  };
  reason: string;
  stance: string;
  emotion_delta: string;
  relationship_delta: string;
  memory_seed?: {
    saw?: string[];
    did?: string[];
    inferred?: string[];
  };
}

export interface WorldSandboxConflict {
  id: string;
  title: string;
  participants: string[];
  cause: string;
  pressure: string;
}

export interface WorldSandboxInformationFlow {
  type?: string;
  from: string;
  to: string;
  content: string;
  distortion: string;
}

export interface WorldlineConsequenceState {
  status?: string;
  summary?: string;
  next_round_hint?: string;
  domains?: Record<
    string,
    {
      label?: string;
      current?: string;
      pressure?: string;
      bearer?: string;
    }
  >;
  ledger?: Array<{
    source_run_id?: string;
    major_event?: string;
    debt_score?: number;
    impacts?: Array<{
      domain?: string;
      current?: string;
      pressure?: string;
    }>;
  }>;
}

export interface WorldSandboxRound {
  version: string;
  run_id: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  round_index: number;
  created_at: string;
  major_event: string;
  character_actions: WorldSandboxCharacterAction[];
  conflicts: WorldSandboxConflict[];
  information_flow: WorldSandboxInformationFlow[];
  world_state_delta: {
    status: string;
    trigger: string;
    relationship_changes: Array<{ source: string; change: string }>;
    resource_changes: string[];
    secret_changes: string[];
    anchor_pressure: string;
    causal_debt: string;
    intervention_effects?: string[];
    branch_state?: {
      continuation_status?: string;
      worldline_state_artifact?: string;
    };
    compensation_effects?: string[];
    consequence_state?: WorldlineConsequenceState;
    meme_contamination?: {
      status?: string;
      source_character_id?: string;
      belief_payload?: string;
      propagation?: WorldSandboxMemePropagation[];
      propagation_readouts?: WorldSandboxMemePropagationReadout[];
    };
  };
  next_story_possibilities: Array<{
    id: string;
    title: string;
    brief: string;
  }>;
  boundaries: string[];
  intervention_constraint?: WorldSandboxInterventionConstraint;
  llm_decision_advisory?: {
    status?: string;
    mode?: string;
    requested?: boolean;
    mock?: boolean;
    generated_by?: string;
    summary?: string;
    action_count?: number;
    fallback_reason?: string;
    decisions?: WorldSandboxLLMDecisionAdvisory[];
    usage?: Record<string, number | string | null>;
  };
}

export interface WorldSandboxRunReport {
  version: string;
  mode: "deterministic_world_sandbox_round" | string;
  run_id: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  created_at: string;
  round_count: number;
  summary: {
    character_action_count: number;
    conflict_count: number;
    information_flow_count: number;
    subjective_memory_entries_written: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    run_scene_default_unchanged: boolean;
    llm_decision_status?: string;
    llm_decision_action_count?: number;
    llm_decision_generated_by?: string;
  };
  artifacts: {
    sandbox_rounds: string;
    sandbox_summary: string;
    subjective_memory_delta: string;
    intervention_constraint?: string;
    agent_decision_advisory?: string;
  };
  intervention_constraint?: WorldSandboxInterventionConstraint;
  worldline_state?: WorldlineState;
  rounds: WorldSandboxRound[];
  subjective_memory_delta: {
    entry_count?: number;
    entries?: SubjectiveMemoryEntry[];
    paths?: string[];
  };
  next_steps: string[];
}

export interface WorldSandboxRunRequest {
  major_event: string;
  worldline_id?: string;
  intervention_content?: string;
  intervention_target?: string;
  intervention_projection_mode?: "immersive" | "wild_au" | string;
  intervention_constraint?: WorldSandboxInterventionConstraint;
  llm_decision_mode?: "deterministic" | "advisory" | string;
  llm_decision_mock?: boolean;
}

export interface SubjectiveMemoryEntry {
  version: string;
  source_run_id: string;
  source_round_index: number;
  source_major_event: string;
  created_at: string;
  story_slug: string;
  worldline_id: string;
  character_id: string;
  character_name: string;
  saw: string[];
  did: string[];
  new_belief: string;
  emotion_delta: string;
  trust_delta: string;
  anomaly_delta: string;
  previous_subjective_memory: string;
  source_action: string;
  perceived_event?: string;
  inner_thought?: string;
  inferred_motive?: string;
  emotional_impact?: string;
  trust_shift?: string;
  anomaly_weight?: number;
  secret_visibility?: "hidden" | "partial" | "exposed" | string;
  known_truths?: string[];
  misbeliefs?: string[];
  unknown_canon_facts?: string[];
  suppressed_memory?: string;
  worldline_residue?: string;
  awareness_level?: string;
  decision_mode?: string;
  decision_inputs?: Record<string, string | number | boolean | null>;
  visible_action?: string;
  true_intent?: string;
  expected_outcome?: string;
  risk?: string;
  memory_influence?: string;
  action_outcome?: {
    status?: string;
    reason?: string;
    cost?: string;
  };
  higher_dimensional_awareness?: string;
  fate_mark?: {
    status?: string;
    label?: string;
    description?: string;
  };
  resistance_behavior?: WorldSandboxResistanceBehavior;
  meme_contamination?: {
    status?: string;
    belief_payload?: string;
    spread_vector?: string[];
  };
  meme_propagation?: WorldSandboxMemePropagation;
  meme_propagation_readout?: WorldSandboxMemePropagationReadout;
  llm_decision_advisory?: WorldSandboxLLMDecisionAdvisory;
}

export interface WorldlineState {
  version?: string;
  artifact?: string;
  current_worldline?: string;
  status?: string;
  source_intervention?: {
    status?: string;
    content?: string;
    target?: string;
    projection_mode?: string;
    intervention_level?: string;
  };
  tianming_snapshot?: {
    artifact?: string;
    status?: string;
    audit_status?: string;
    requires_confirmation?: boolean;
    root_tianming_mutated?: boolean;
  };
  branch_state?: {
    continuation_status?: string;
    projection_mode?: string;
    next_round_reads?: string[];
  };
  causal_debt?: {
    score?: number;
    level?: string;
    pressure_order?: string[];
    spread?: string[];
  };
  anchor_status?: {
    status?: string;
    current_anchor?: string;
    current_anchor_pressure?: string;
    no_qualified_anchor?: boolean;
    ensemble_without_mainline?: boolean;
  };
  replacement_anchor_candidates?: Array<{
    character_id?: string;
    character_name?: string;
    score?: number;
    desire?: string;
    capability?: string;
    resources?: string;
    resistance?: string;
    explanation?: string;
  }>;
  meme_contamination?: {
    status?: string;
    source_character_id?: string;
    belief_payload?: string;
    spread_vector?: string[];
    propagation?: WorldSandboxMemePropagation[];
    propagation_readouts?: WorldSandboxMemePropagationReadout[];
  };
  compensation_effects?: string[];
  consequence_state?: WorldlineConsequenceState;
  continuation_inputs?: {
    major_event_hint?: string;
    worldline_id?: string;
  };
  author_adoption?: Record<string, unknown>;
  next_chapter_brief?: Record<string, unknown>;
}

export interface SubjectiveMemoryReport {
  version: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  character_id: string;
  entry_count: number;
  artifact: string;
  entries: SubjectiveMemoryEntry[];
  next_steps: string[];
}

export interface TianmingAttractor {
  id: string;
  title: string;
  pull: string;
  source: string;
  weight?: number;
  category?: string;
}

export interface TianmingGenreConstraint {
  id: string;
  name: string;
  rule: string;
}

export interface TianmingReplacementCandidate {
  character_id: string;
  character_name: string;
  current_role: string;
  desire: string;
  risk: string;
  anchor_fit: number;
  reason: string;
}

export interface TianmingBook {
  version: string;
  constitution_schema_version?: number;
  artifact: string;
  story_slug: string;
  source_kind: SourceKind | string;
  status: "draft" | "confirmed" | string;
  requires_confirmation: boolean;
  created_at: string;
  updated_at: string;
  confirmed_at: string | null;
  narrative_attractors: TianmingAttractor[];
  genre_constraints: TianmingGenreConstraint[];
  anchor_status: {
    status: "anchored" | "needs_anchor" | string;
    current_anchor_character_id: string | null;
    current_anchor_name: string;
    candidate_count: number;
    risk: string;
    anchors?: Array<{
      id: string;
      type: "character" | "faction" | "mystery" | "place" | string;
      name: string;
      status: string;
      stability: number;
      pressure: string;
    }>;
  };
  contract_pressure: {
    level: "low" | "medium" | "high" | string;
    score: number;
    active_tier?: "minor" | "major" | "era" | "collapse" | string;
    pressure_tiers?: Array<{
      id: "minor" | "major" | "era" | "collapse" | string;
      label: string;
      threshold: number;
      active: boolean;
      drivers: string[];
    }>;
    drivers: string[];
  };
  replacement_anchor_candidates: TianmingReplacementCandidate[];
  ordinary_intervention_mutates_tianming: boolean;
  mutation_policy: Record<string, string>;
  boundaries: string[];
  next_steps: string[];
  confirmation?: {
    method: string;
    message: string;
  };
}

export interface TianmingInterventionCompileReport {
  version: string;
  story_slug: string;
  worldline_id?: string;
  projection_mode?: "immersive" | "wild_au" | string;
  target: string;
  content: string;
  tianming: {
    artifact: string;
    status: string;
    anchor_status: TianmingBook["anchor_status"];
    contract_pressure: TianmingBook["contract_pressure"];
    ordinary_intervention_mutates_tianming: boolean;
  };
  intervention_type: string;
  intervention_level: string;
  compatibility: {
    status: string;
    reason: string;
    tianming_pressure_level: string;
    foreign_object_intrusion?: boolean;
  };
  translation_strategy: {
    strategy: string;
    packaging: string;
    original_hint: string;
    level: string;
    mode?: string;
    projection_mode?: string;
    foreign_object_intrusion?: boolean;
  };
  worldline_judgement: {
    kind: "divergent" | "au" | string;
    reason: string;
  };
  branch_axis: {
    id: string;
    target: string;
    axis: string;
    question: string;
  };
  causal_debt: {
    level: "low" | "medium" | "high" | string;
    score: number;
    spread: string[];
  };
  worldline_tianming_snapshot?: {
    artifact: string;
    status: string;
    worldline_id: string;
    root_tianming_mutated: boolean;
    requires_confirmation: boolean;
  } | null;
  audit: {
    required: boolean;
    can_mutate_tianming_snapshot: boolean;
    ordinary_intervention_can_mutate_tianming: boolean;
    message: string;
  };
  ordinary_intervention_mutates_tianming: boolean;
  boundaries: string[];
}

export interface NarrativeCompensationReport {
  version: string;
  artifact: string;
  run_id: string;
  story_slug: string;
  worldline_id: string;
  created_at: string;
  trigger_event: string;
  source_tianming: {
    artifact: string;
    status: string;
    anchor_status: TianmingBook["anchor_status"];
    contract_pressure: TianmingBook["contract_pressure"];
  };
  anchor_transfer: {
    status: "stable" | "transferring" | "unanchored" | string;
    current_anchor: string | null;
    next_anchor_candidate: TianmingReplacementCandidate | null;
    reason: string;
  };
  replacement_anchor_candidates: Array<{
    character_id: string;
    character_name: string;
    desire: string;
    ability_score: number;
    resource_score: number;
    risk_score: number;
    risk: string;
    reason: string;
  }>;
  causal_debt_diffusion: {
    level: "low" | "medium" | "high" | string;
    score: number;
    spread: string[];
  };
  world_pressure_events: Array<{
    id: string;
    domain: string;
    mode: string;
    event: string;
    evidence: string;
  }>;
  boundaries: string[];
  next_steps: string[];
}

export interface WorldAutopilotCheckpoint {
  checkpoint_id?: string;
  round_index: number;
  sandbox_run_id: string;
  major_event: string;
  objective_type: string;
  stage: string;
  anchor_pressure: string;
  causal_debt: string;
  consequence_state?: WorldlineConsequenceState;
  character_action_count: number;
  next_story_possibilities: Array<{
    id: string;
    title: string;
    brief: string;
  }>;
  who_remembered_what?: Array<{ character_id?: string; remembered?: string }>;
  scene_beats?: WorldAutopilotSceneBeat[];
  chapter_seed?: {
    opening_hook?: string;
    viewpoint_misread?: string;
    consequence_pressure?: string;
    conflict_turn?: string;
    next_chapter_hook?: string;
  };
}

export interface WorldAutopilotSceneBeat {
  beat_type: string;
  label: string;
  body: string;
  focus_character_id?: string;
  evidence_refs: string[];
}

export interface WorldAutopilotNarrativeTimelineItem {
  round_index?: number;
  checkpoint_id?: string;
  sandbox_run_id?: string;
  scene_hook: string;
  character_miscalculation: string;
  materialized_consequence: string;
  conflict_escalation: string;
  chapter_handoff: string;
  evidence_refs: string[];
}

export interface WorldAutopilotReadableEntry {
  version: string;
  story_slug: string;
  worldline_id: string;
  run_id: string;
  latest_checkpoint: {
    checkpoint_id: string;
    round_index: number;
    stage: string;
    major_event: string;
    sandbox_run_id: string;
  };
  protagonist: {
    character_id?: string;
    character_name?: string;
  };
  routes: {
    worldline_dossier: string;
    latest_checkpoint: string;
    protagonist_volume: string;
    event_multi_perspective: string;
    continuous_reading: string;
  };
  primary_actions: Array<{
    id: string;
    label: string;
    route: string;
    reason: string;
    status: string;
  }>;
  state_change_explanation: {
    headline: string;
    why_world_changed: string;
    stop_evidence?: string;
    narrative_thread: Array<{
      round_index?: number;
      checkpoint_id?: string;
      scene_hook?: string;
      turn?: string;
      consequence?: string;
      handoff?: string;
    }>;
  };
  memory_readout: {
    summary: string;
    who_remembered_what: Array<{ character_id?: string; remembered?: string }>;
  };
  causal_debt_readout: {
    summary: string;
    level?: string;
    next_round_hint?: string;
    domains?: WorldlineConsequenceState["domains"];
  };
  context_bridge: string[];
  boundaries: string[];
}

export interface WorldAutopilotReport {
  version: string;
  artifact: string;
  status?: string;
  run_id: string;
  story_slug: string;
  worldline_id: string;
  created_at: string;
    objective: {
      type: string;
      round_limit: number;
      seed_event: string;
      stop_event?: string;
      time_limit?: string;
    };
  rounds_completed: number;
  stop_reason: string;
  stop_condition?: {
    type: string;
    matched: boolean;
    evidence: string;
    round_index: number;
    checkpoint_id?: string;
  };
  task?: {
    task_id: string;
    status: string;
    can_pause: boolean;
    can_resume: boolean;
    checkpoint_replay: boolean;
  };
  progress?: {
    current_round: number;
    target_round: number;
    percent: number;
  };
  sandbox_runs: Array<{
    round_index: number;
    sandbox_run_id: string;
    major_event: string;
    character_action_count: number;
  }>;
  checkpoints: WorldAutopilotCheckpoint[];
  final_world_stage: {
    stage: string;
    summary: string;
  };
  overnight_report?: {
    what_happened: string;
    who_remembered_what: Array<{ character_id?: string; remembered?: string }>;
    why_world_changed: string;
    where_to_continue: Array<{
      checkpoint_id?: string;
      sandbox_run_id?: string;
      label?: string;
    }>;
    timeline?: Array<{
      round_index?: number;
      checkpoint_id?: string;
      major_event?: string;
      stage?: string;
      causal_debt?: string;
      remembered_count?: number;
    }>;
    narrative_timeline?: WorldAutopilotNarrativeTimelineItem[];
    memory_changes?: Array<{ character_id?: string; remembered?: string }>;
    checkpoint_recovery?: WorldAutopilotRecovery;
  };
  recovery?: WorldAutopilotRecovery;
  readable_entry?: WorldAutopilotReadableEntry;
  failure?: {
    message?: string;
    failed_round?: number;
    latest_checkpoint?: string;
    recoverable?: boolean;
  };
  artifacts: {
    autopilot_report: string;
    checkpoints_dir: string;
  };
  boundaries: string[];
  next_steps: string[];
}

export interface WorldAutopilotRecovery {
  can_resume?: boolean;
  resume_from_checkpoint?: string;
  latest_report_run_id?: string;
  resume_endpoint?: string;
  resumed_from?: {
    run_id?: string;
    checkpoint_id?: string;
    round_index?: number;
    major_event?: string;
    stage?: string;
    causal_debt?: string;
  };
}

export interface WorldlineDossierCheckpoint {
  run_id: string;
  created_at?: string;
  checkpoint_id: string;
  round_index: number;
  sandbox_run_id: string;
  major_event: string;
  stage: string;
  anchor_pressure?: string;
  causal_debt?: string;
  consequence_state?: WorldlineConsequenceState;
  who_remembered_what?: Array<{ character_id?: string; remembered?: string }>;
  next_story_possibilities?: Array<{
    id?: string;
    title?: string;
    brief?: string;
  }>;
}

export interface WorldlineDossierReport {
  version: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  worldline_state: WorldlineState;
  tianming_audit: {
    status: string;
    audit_status: string;
    requires_confirmation: boolean;
    root_tianming_mutated: boolean;
    artifact?: string;
  };
  task_count: number;
  tasks: Array<{
    task_id?: string;
    status?: string;
    latest_report_run_id?: string;
    created_at?: string;
    updated_at?: string;
    progress?: {
      current_round?: number;
      target_round?: number;
      percent?: number;
    };
    resume_from_checkpoint?: string;
    recovery?: WorldAutopilotRecovery;
    failure?: {
      message?: string;
      failed_round?: number;
      latest_checkpoint?: string;
      recoverable?: boolean;
    };
    recovered_from?: WorldAutopilotRecovery["resumed_from"];
  }>;
  checkpoint_count: number;
  checkpoints: WorldlineDossierCheckpoint[];
  next_actions: Array<{
    action: string;
    label: string;
    reason: string;
    worldline_id?: string;
    run_id?: string;
    checkpoint_id?: string;
  }>;
  boundaries: string[];
}

export interface DossierReadingVolumeTab {
  id:
    | "world_chronicle"
    | "anchor_volume"
    | "character_volume"
    | "faction_volume"
    | "event_multi_perspective"
    | string;
  label: string;
  title: string;
  body_md: string;
  character_id?: string;
  character_name?: string;
  faction_id?: string;
  faction_name?: string;
  cognitive_bias: string;
  evidence_refs: string[];
  evidence_chain?: Record<string, unknown>;
  information_gap?: Record<string, string>;
  novel_scene_plan?: CharacterLensNovelSceneBeat[];
  artifact: string;
  default_open: boolean;
}

export interface DossierReadingConfirmedChapter {
  artifact: string;
  markdown_artifact: string;
  chapter_title: string;
  body_md: string;
  edited: boolean;
  author_note: string;
  continuation_effect: Record<string, unknown>;
  evidence_chain: Record<string, unknown>;
}

export interface DossierReadingReport {
  version: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  status: "ready" | "partial" | "empty" | string;
  default_mode: "novel" | string;
  default_tab:
    | "continuous_reading"
    | "confirmed_chapter"
    | "world_chronicle"
    | "anchor_volume"
    | "character_volume"
    | "faction_volume"
    | "event_multi_perspective"
    | string;
  title: string;
  source_runs: {
    adoption_run_id?: string;
    draft_run_id?: string;
    confirmation_run_id?: string;
    lens_run_id?: string;
  };
  continuous_reading?: ContinuousReadingChapter;
  confirmed_chapter?: DossierReadingConfirmedChapter;
  reading_trail?: ConfirmedChapterReadingTrail;
  volume_tabs: DossierReadingVolumeTab[];
  perspective_biases: Array<{
    id: string;
    label: string;
    cognitive_bias: string;
    source: string;
  }>;
  evidence_panel: {
    default_open: boolean;
    label: string;
    description: string;
    ref_count: number;
    refs: string[];
  };
  worldline_dossier?: Partial<WorldlineDossierReport>;
  boundaries: string[];
}

export interface EventPerspectiveSceneBeat {
  id: string;
  beat_type: string;
  title: string;
  body: string;
  viewpoint: string;
  cognitive_bias?: string;
  evidence_refs: string[];
}

export interface EventPerspectiveReport {
  version: string;
  story_slug: string;
  worldline_id: string;
  event_id: string;
  status: "ready" | "partial" | "empty" | string;
  title: string;
  subtitle: string;
  source_runs: {
    adoption_run_id?: string;
    draft_run_id?: string;
    confirmation_run_id?: string;
    lens_run_id?: string;
    sandbox_run_id?: string;
  };
  event_volume: DossierReadingVolumeTab | Record<string, never>;
  scene_beats: EventPerspectiveSceneBeat[];
  information_gap: {
    canon_vs_character?: string;
    misbeliefs?: string;
    unknown_canon_facts?: string;
  };
  perspective_biases: Array<{
    id: string;
    label: string;
    source: string;
    cognitive_bias: string;
  }>;
  evidence_panel: {
    default_open: boolean;
    label: string;
    description: string;
    ref_count: number;
    refs: string[];
  };
  next_actions: Array<{
    id: string;
    label: string;
    route: string;
    reason: string;
  }>;
  boundaries: string[];
}

export interface LonglineTimelineEntry {
  id: string;
  sequence: number;
  phase: "scene" | "volume" | "confirmation" | "checkpoint" | string;
  label: string;
  title: string;
  body: string;
  source: string;
  route: string;
  evidence_refs: string[];
  affected_characters: string[];
  affected_factions: string[];
  consequence_hint: string;
}

export interface LonglineThread {
  id: string;
  label: string;
  status: "active" | "pending" | string;
  summary: string;
  source_count: number;
}

export interface LonglineReadingProgress {
  label: string;
  current_sequence: number;
  total_entries: number;
  percent: number;
  current_entry_id: string;
  current_title: string;
  next_entry_id: string;
  next_title: string;
  active_thread_count: number;
  unresolved_thread_count: number;
  summary: string;
}

export interface LonglineEventIndexItem {
  id: string;
  label: string;
  title: string;
  summary: string;
  phase: string;
  route: string;
  entry_ids: string[];
  thread_ids: string[];
  evidence_count: number;
  unresolved_count: number;
}

export interface LonglineEventIndex {
  label: string;
  description: string;
  event_count: number;
  items: LonglineEventIndexItem[];
}

export interface LonglineOpenThread extends LonglineThread {
  next_route: string;
  reason: string;
}

export interface LonglineMisbeliefRecoveryItem {
  id: string;
  status: "unresolved" | "recovered" | string;
  misunderstanding: string;
  origin_event_title: string;
  source: string;
  affected_characters: string[];
  evidence_refs: string[];
  recovery_steps: string[];
  next_route: string;
  author_prompt: string;
}

export interface LonglineMisbeliefRecovery {
  label: string;
  description: string;
  misbelief_count: number;
  items: LonglineMisbeliefRecoveryItem[];
  fallback_action: {
    label: string;
    route: string;
    reason: string;
  };
}

export interface LonglineReadingReport {
  version: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  status: "ready" | "partial" | "empty" | string;
  default_axis: "cause" | string;
  title: string;
  subtitle: string;
  source_runs: {
    adoption_run_id?: string;
    draft_run_id?: string;
    confirmation_run_id?: string;
    lens_run_id?: string;
  };
  current_tension: {
    summary: string;
    primary_misbelief?: string;
    next_chapter_hook?: string;
  };
  reading_progress: LonglineReadingProgress;
  event_index: LonglineEventIndex;
  misbelief_recovery: LonglineMisbeliefRecovery;
  timeline_entries: LonglineTimelineEntry[];
  longline_threads: LonglineThread[];
  open_threads: LonglineOpenThread[];
  evidence_panel: {
    default_open: boolean;
    label: string;
    description: string;
    ref_count: number;
    refs: string[];
  };
  next_actions: Array<{
    id: string;
    label: string;
    route: string;
    reason: string;
  }>;
  boundaries: string[];
}

export interface WorldAutopilotCheckpointReplayReport {
  version: string;
  run_id: string;
  checkpoint_id: string;
  checkpoint: WorldAutopilotCheckpoint;
  replay: {
    sandbox_run_id: string;
    major_event: string;
    can_resume_from_here: boolean;
    resume_hint?: string;
  };
  readable_entry?: WorldAutopilotReadableEntry;
}

export interface CharacterLensPerspective {
  character_id: string;
  character_name: string;
  stance: string;
  voice: string;
  evidence: {
    source: string;
    source_run_id?: string | null;
  };
}

export interface CharacterLensBrief {
  lens_type: string;
  title: string;
  body: string;
  character_id?: string;
  character_name?: string;
  perspectives?: CharacterLensPerspective[];
  evidence: Record<string, unknown>;
}

export interface CharacterLensNovelSceneBeat {
  beat_type: string;
  title: string;
  body: string;
  viewpoint: string;
  evidence_refs: string[];
}

export interface CharacterLensReport {
  version: string;
  artifact: string;
  run_id: string;
  story_slug: string;
  worldline_id: string;
  created_at: string;
  source: {
    source_event: string;
    sandbox_run_id: string;
    source_round_index: number;
  };
  brief_count: number;
  briefs: CharacterLensBrief[];
  volume_count?: number;
  volumes?: Array<{
    volume_type: string;
    title: string;
    prose: string;
    character_id?: string;
    character_name?: string;
    reading_mode?: {
      default: string;
      evidence_default_visible: boolean;
      guidance?: string;
    };
    novel_scene_plan?: CharacterLensNovelSceneBeat[];
    event_nodes?: Array<{
      id: string;
      title: string;
      body: string;
      evidence_refs: string[];
    }>;
    information_gap?: Record<string, string>;
    evidence_chain?: Record<string, unknown>;
  }>;
  artifacts: {
    character_lens_briefs: string;
    character_lens_volumes?: string;
  };
  boundaries: string[];
  next_steps: string[];
}

export interface AuthorAdoptionReport {
  version: string;
  artifact: string;
  run_id: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  created_at: string;
  decision: string;
  mode_label: string;
  comparison: {
    original_outline: string;
    sandbox_emergence: string;
    difference: string;
  };
  outline_diff?: {
    status: string;
    summary: string;
    original_outline: string;
    sandbox_emergence: string;
  };
  foreshadowing_adjustments?: Array<{ type: string; text: string }>;
  reviewer_suggestions?: string[];
  next_chapter_brief?: {
    opening_scene: string;
    chapter_goal: string;
    conflict_focus: string;
    sandbox_inputs: {
      major_event: string;
      worldline_id: string;
      author_note?: string;
    };
    materialized_consequences?: string[];
    must_preserve: string[];
    writing_plan?: {
      stance: string;
      next_chapter_brief_md: string;
      outline_delta: string;
      manual_review_points: string[];
      foreshadowing_moves: string[];
      materialized_consequences: string[];
    };
    feed_forward?: {
      chapter_generation_inputs: {
        decision: string;
        source_event?: string;
        original_outline: string;
        sandbox_emergence: string;
        opening_scene: string;
        conflict_focus: string;
        must_preserve: string[];
        unresolved_conflicts: string[];
      };
      sandbox_continuation_inputs: Record<string, string>;
      next_round_reads: string[];
      root_canon_policy: string;
      audit_note: string;
      author_note: string;
    };
    author_branch?: {
      branch_id?: string;
      source_worldline_id?: string;
      status?: string;
      root_canon_policy?: string;
    };
  };
  continuation_effect?: {
    affects_future_sandbox: boolean;
    worldline_state_artifact: string;
    next_sandbox_entry: Record<string, string>;
  };
  adoption_entry: {
    version: string;
    created_at: string;
    story_slug: string;
    source_kind: SourceKind | string;
    worldline_id: string;
    decision: string;
    mode_label: string;
    source_run_id: string;
    source_event: string;
    original_outline: string;
    sandbox_emergence: string;
    author_note: string;
  };
  artifacts: {
    author_adoption_record: string;
    author_adoption_brief: string;
    next_chapter_brief?: string;
    ledger: string;
  };
  boundaries: string[];
  next_steps: string[];
}

export interface AuthorChapterDraftReport {
  version: string;
  artifact: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  source_adoption_run_id: string;
  created_at: string;
  generated_by: string;
  fallback_reason?: string;
  chapter_title: string;
  chapter_text: string;
  chapter_text_with_accepted_rewrites?: string;
  draft_inputs: {
    decision?: string;
    mode_label?: string;
    opening_scene?: string;
    conflict_focus?: string;
    original_outline?: string;
    sandbox_emergence?: string;
  };
  evidence_chain: {
    adoption_record: string;
    next_chapter_brief: string;
    worldline_state_artifact: string;
    materialized_consequences: string[];
    must_preserve: string[];
    sandbox_inputs: Record<string, string>;
  };
  reviewer_checklist: Array<{
    item: string;
    passed: boolean;
  }>;
  revision_pack?: {
    version: string;
    artifact: string;
    status: "ready" | "needs_revision" | string;
    summary: string;
    semantic_reviewer?: {
      status: "ready" | "needs_revision" | string;
      diagnosis_summary: string;
      priority_order: string[];
      review_items: Array<{
        id: string;
        priority: "blocking" | "high" | "medium" | "low" | string;
        dimension: string;
        problem: string;
        evidence_text: string;
        recommendation: string;
      }>;
    };
    review_focus: string[];
    localized_rewrites: Array<{
      id: string;
      priority: "blocking" | "high" | "medium" | "low" | string;
      target_text: string;
      issue: string;
      rewrite_instruction: string;
      suggested_revision: string;
      original_problem?: string;
      revision_intent?: string;
      suggested_rewrite?: string;
      impact_on_characters?: string[];
      impact_on_world_state?: string;
      adoption_direction?: string;
      evidence_refs: string[];
    }>;
    editorial_revision_draft?: {
      status: string;
      preview_text_md: string;
      applied_rewrite_ids: string[];
      feeds: string[];
      does_not_overwrite: string[];
      adoption_direction?: string;
      evidence_refs?: string[];
    };
    adoption_feedback?: {
      surface: string;
      feeds: string[];
      confirmation_use: string;
      next_chapter_use: string;
    };
    confirmation_gate: {
      ready_for_confirmation: boolean;
      editorial_preview_available?: boolean;
      blocking_items: string[];
      author_action: string;
    };
    evidence_refs: string[];
    boundaries: string[];
  };
  continuous_reading_chapter?: ContinuousReadingChapter;
  accepted_local_rewrites?: {
    artifact: string;
    markdown_artifact: string;
    applied_rewrite_ids: string[];
    applied_rewrite_count: number;
    author_note?: string;
    updated_at?: string;
    feeds?: string[];
    does_not_overwrite?: string[];
  };
  edited_final_chapter?: {
    artifact: string;
    markdown_artifact: string;
    status: string;
    applied_rewrite_ids: string[];
    updated_at?: string;
    feeds?: string[];
    quality_gate?: {
      ready_for_confirmation: boolean;
      keeps_original_chapter_body?: boolean;
      applies_reviewer_rewrites?: boolean;
      not_a_review_appendix?: boolean;
    };
    preview_text?: string;
  };
  artifacts: {
    next_chapter_draft: string;
    next_chapter_markdown: string;
    draft_revision_pack?: string;
    continuous_reading_chapter?: string;
    continuous_reading_markdown?: string;
    accepted_local_rewrites?: string;
    next_chapter_draft_revised?: string;
    edited_final_chapter?: string;
    edited_final_chapter_markdown?: string;
  };
  boundaries: string[];
}

export interface EditedFinalChapter {
  version: string;
  artifact: string;
  markdown_artifact: string;
  status: "ready_for_confirmation" | "needs_author_review" | string;
  source_adoption_run_id: string;
  source_draft_artifact: string;
  source_revision_pack: string;
  worldline_id: string;
  created_at: string;
  author_note: string;
  applied_rewrite_ids: string[];
  applied_rewrites: Array<{
    id: string;
    mode: "targeted_replacement" | "continuation_insert" | string;
    original_problem: string;
    revision_intent: string;
    target_text: string;
    suggested_rewrite: string;
    impact_on_characters: string[];
    impact_on_world_state: string;
    adoption_direction: string;
  }>;
  final_chapter_text: string;
  quality_gate: {
    ready_for_confirmation: boolean;
    keeps_original_chapter_body: boolean;
    applies_reviewer_rewrites: boolean;
    not_a_review_appendix: boolean;
  };
  feeds: string[];
  does_not_overwrite: string[];
}

export interface AuthorChapterRewriteApplicationReport {
  version: string;
  artifact: string;
  markdown_artifact: string;
  story_slug: string;
  worldline_id: string;
  source_adoption_run_id: string;
  created_at: string;
  author_note: string;
  applied_rewrite_ids: string[];
  edited_final_chapter?: EditedFinalChapter;
  applied_rewrites: Array<{
    id: string;
    priority: "blocking" | "high" | "medium" | "low" | string;
    target_text: string;
    original_problem: string;
    revision_intent: string;
    suggested_rewrite: string;
    impact_on_characters: string[];
    impact_on_world_state: string;
    adoption_direction: string;
    evidence_refs: string[];
  }>;
  revised_chapter_text: string;
  evidence_chain: {
    next_chapter_draft: string;
    draft_revision_pack: string;
    localized_rewrites: string[];
  };
  feeds: string[];
  does_not_overwrite: string[];
  boundaries: string[];
}

export interface ContinuousReadingSection {
  id: string;
  title: string;
  body: string;
  source_beat_type?: string;
  viewpoint?: string;
  cognitive_bias?: string;
  conflict_turn?: string;
  narrative_role: string;
  evidence_refs: string[];
  evidence_mode?: {
    default_visible: boolean;
    refs: string[];
  };
}

export interface ContinuousReadingCrossVolumeRef {
  id: string;
  label: string;
  title: string;
  artifact: string;
  evidence_refs: string[];
  summary: string;
}

export interface ContinuousReadingChapter {
  version: string;
  artifact: string;
  markdown_artifact: string;
  status: "ready" | "partial" | string;
  default_mode?: "novel" | string;
  chapter_title: string;
  reading_body_md: string;
  reading_sections: ContinuousReadingSection[];
  story_beat_source?: {
    kind: string;
    source_lens_run_id: string;
    beat_count: number;
    artifact: string;
  };
  viewpoint_tabs?: Array<{
    id: string;
    label: string;
    artifact: string;
    summary: string;
  }>;
  evidence_toggle?: {
    default_visible: boolean;
    label: string;
    description: string;
  };
  continuity_threads?: {
    foreshadowing: string;
    payoff: string;
    misunderstanding: string;
  };
  chapter_cliffhanger?: string;
  reading_flow: {
    scene_count: number;
    opening_hook: string;
    turning_point: string;
    next_chapter_hook: string;
  };
  s8_source: {
    lens_run_id: string;
    source_sandbox_run_id: string;
    artifact: string;
  };
  cross_volume_refs: ContinuousReadingCrossVolumeRef[];
  reader_guidance: string[];
  boundaries: string[];
}

export interface ConfirmedChapterReadingTrailSection {
  id: string;
  label: string;
  title?: string;
  artifact: string;
  reason: string;
  evidence_refs: string[];
  character_id?: string;
  character_name?: string;
  event_node_count?: number;
}

export interface ConfirmedChapterReadingTrail {
  version: string;
  artifact: string;
  status: "ready" | "partial" | string;
  source_lens_run_id: string;
  source_sandbox_run_id: string;
  sections: ConfirmedChapterReadingTrailSection[];
  next_reader_actions: string[];
  boundaries: string[];
}

export interface AuthorChapterConfirmationReport {
  version: string;
  artifact: string;
  story_slug: string;
  source_kind: SourceKind | string;
  worldline_id: string;
  source_adoption_run_id: string;
  created_at: string;
  edited: boolean;
  edit_source?: "draft" | "author_manual_edit" | "auto_reviewer_final" | string;
  chapter_title: string;
  chapter_text: string;
  author_note: string;
  edited_final_chapter?: Partial<EditedFinalChapter>;
  evidence_chain: {
    adoption_record: string;
    next_chapter_brief: string;
    next_chapter_draft: string;
    edited_final_chapter?: string;
    worldline_state_artifact: string;
    sandbox_inputs: Record<string, string>;
    materialized_consequences: string[];
    reading_trail: string;
    accepted_local_rewrites?: string;
  };
  accepted_local_rewrites?: {
    artifact: string;
    markdown_artifact: string;
    applied_rewrite_ids: string[];
    applied_rewrite_count: number;
    applied_rewrites?: AuthorChapterRewriteApplicationReport["applied_rewrites"];
    author_note?: string;
    feeds?: string[];
  };
  continuation_effect: {
    affects_future_sandbox: boolean;
    worldline_state_artifact: string;
    next_sandbox_entry: {
      major_event: string;
      worldline_id: string;
      confirmed_chapter_artifact: string;
      confirmed_chapter_markdown: string;
      chapter_summary: string;
      accepted_local_rewrites?: string;
      accepted_rewrite_ids?: string;
      edited_final_chapter?: string;
    };
  };
  reading_trail: ConfirmedChapterReadingTrail;
  reviewer_checklist: Array<{
    item: string;
    passed: boolean;
  }>;
  artifacts: {
    confirmed_chapter_entry: string;
    confirmed_chapter_markdown: string;
    confirmed_chapter_reading_trail: string;
  };
  boundaries: string[];
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

export interface RuntimePreflightCheckpoint {
  id: string;
  label: string;
  status: "ready" | "attention" | "blocked" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
  detail: Record<string, unknown>;
}

export interface RuntimePreflightReport {
  version: string;
  mode: "read_only_runtime_preflight" | string;
  status: "ready" | "attention" | "blocked" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    checkpoint_count: number;
    ready_count: number;
    attention_count: number;
    blocked_count: number;
    external_services_required: boolean;
    writes_artifacts: boolean;
  };
  checkpoints: RuntimePreflightCheckpoint[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface VectorRetrievalReadinessSignal {
  id: string;
  label: string;
  status: "ready" | "attention" | "blocked" | string;
  evidence: string;
  next_step: string;
  detail: Record<string, unknown>;
}

export interface VectorRetrievalCandidateLayer {
  id: string;
  label: string;
  readiness: "evaluate" | "design_spike" | "monitor" | "deferred" | string;
  reason: string;
}

export interface VectorRetrievalFailureSample {
  query: string;
  expected_entities: string[];
  actual_top_sources: string[];
  reason: string;
}

export interface VectorRetrievalReadinessReport {
  version: string;
  mode: "read_only_vector_retrieval_readiness" | string;
  status: "ready" | "attention" | "monitor" | "triggered" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    chapter_count: number;
    character_count: number;
    corpus_item_count: number;
    canon_ledger_count: number;
    legacy_fact_count: number;
    chapter_brief_count: number;
    volume_brief_count: number;
    entity_alias_count: number;
    ledger_entity_count: number;
    alias_coverage_ratio: number;
    retrieval_probe_status: string;
    retrieval_probe_sample_count: number;
    retrieval_probe_hit_rate: number;
    saved_failure_sample_count: number;
    large_project: boolean;
    corpus_pressure: boolean;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    plaintext_key_returned: boolean;
  };
  signals: VectorRetrievalReadinessSignal[];
  candidate_layers: VectorRetrievalCandidateLayer[];
  retrieval_probe: {
    status: string;
    summary: string;
    metrics: Record<string, unknown>;
    failure_samples: Array<Record<string, unknown>>;
  };
  failure_samples: VectorRetrievalFailureSample[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface VectorRetrievalIndexReport {
  version: string;
  mode: "write_vector_retrieval_index" | string;
  status: "ready" | "empty" | "attention" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    document_count: number;
    indexed_count: number;
    embedding_model: string;
    embedding_dimension: number;
    vector_store_provider: string;
    collection: string;
    writes_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  documents: Array<{
    doc_id: string;
    source: string;
    chapter: number;
    text: string;
  }>;
  boundaries: string[];
}

export interface VectorRetrievalSearchItem {
  id: string;
  source: string;
  type?: string;
  score?: number;
  vector_score?: number;
  bm25_score?: number;
  rerank_score?: number;
  retrieval_path?: string;
  text: string;
  chapter: number;
  evidence?: string;
  entities?: string[];
  resolved_entities?: string[];
}

export interface VectorRetrievalSearchReport {
  version: string;
  mode: "hybrid_vector_retrieval_preview" | string;
  status: "ready" | "empty" | "fallback" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    item_count: number;
    retrieval_mode: string;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    writes_vector_store: boolean;
    default_retrieval_changed: boolean;
    plaintext_key_returned: boolean;
  };
  query: string;
  current_chapter: number;
  provider: Record<string, unknown>;
  items: VectorRetrievalSearchItem[];
  prompt_block: string;
  warnings: string[];
  boundaries: string[];
}

export interface GraphMemoryTriggerSignal {
  id: string;
  label: string;
  status: "ready" | "attention" | "deferred" | "triggered" | "monitor" | string;
  value: number;
  detail: string;
}

export interface GraphMemoryCandidateLayer {
  id: "graphrag" | "zep" | "temporal_memory" | string;
  label: string;
  status: "candidate" | "deferred" | string;
  reason: string;
}

export interface GraphMemoryTriggerEvidenceReport {
  version: string;
  mode: "read_only_graph_memory_trigger_evidence" | string;
  status: "not_triggered" | "monitor" | "triggered" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_kind: SourceKind | string;
    graph_memory_status: string;
    graph_memory_should_evaluate: boolean;
    graph_memory_reasons: string[];
    chapter_count: number;
    character_count: number;
    canon_ledger_count: number;
    canon_ledger_status: string;
    entity_alias_count: number;
    entity_alias_status: string;
    consistency_severe_issue_count: number;
    retrieval_probe_status: string;
    retrieval_probe_hit_rate: number;
    trend_project_count: number;
    trend_record_count: number;
    trend_lexical_gap_count: number;
    trend_empty_project_count: number;
    relation_signal_count: number;
    causal_signal_count: number;
    state_signal_count: number;
    relation_or_state_pressure: boolean;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    plaintext_key_returned: boolean;
  };
  trigger_gate: {
    id: string;
    status: "ready_for_spike_design" | "needs_more_evidence" | "deferred" | string;
    passed: boolean;
    reason: string;
    graph_memory_status: string;
    trend_record_count: number;
    trend_lexical_gap_count: number;
  };
  signals: GraphMemoryTriggerSignal[];
  candidate_layers: GraphMemoryCandidateLayer[];
  records: CrossProjectRetrievalSamplesIndexRecord[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemorySpikeLayerPlan {
  id: "graphrag" | "zep" | "temporal_memory" | string;
  label: string;
  status: "candidate" | "monitor" | "deferred" | string;
  source_status: string;
  reason: string;
  design_focus: string;
  trial_inputs: string[];
  acceptance_gate_ids: string[];
  risks: string[];
  rollback_strategy: string;
}

export interface GraphMemorySpikeExperimentInput {
  id: string;
  label: string;
  status: "required" | "optional" | "missing" | string;
  detail: string;
}

export interface GraphMemorySpikeAcceptanceGate {
  id: string;
  label: string;
  status: "required" | "optional" | "deferred" | string;
  target: string;
}

export interface GraphMemorySpikeDesignPackReport {
  version: string;
  mode: "read_only_graph_memory_spike_design_pack" | string;
  status: "ready_for_spike" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_kind: SourceKind | string;
    evidence_status: string;
    graph_memory_status: string;
    trigger_gate_status: string;
    candidate_layer_count: number;
    monitor_layer_count: number;
    experiment_input_count: number;
    acceptance_gate_count: number;
    no_go_condition_count: number;
    trend_record_count: number;
    trend_lexical_gap_count: number;
    relation_signal_count: number;
    causal_signal_count: number;
    state_signal_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    plaintext_key_returned: boolean;
  };
  design_gate: {
    id: string;
    status: "design_pack_ready" | "collect_more_evidence" | "deferred" | string;
    passed: boolean;
    reason: string;
    evidence_status: string;
    candidate_layer_count: number;
  };
  layer_plans: GraphMemorySpikeLayerPlan[];
  experiment_inputs: GraphMemorySpikeExperimentInput[];
  acceptance_gates: GraphMemorySpikeAcceptanceGate[];
  rollback_plan: Array<{ id: string; label: string; action: string }>;
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface EmbeddingEvaluationSample {
  query: string;
  expected_entities: string[];
  expected_item_id: string;
  expected_source: string;
  current_chapter: number;
  reason: string;
  bm25_hit: boolean;
  mock_embedding_hit: boolean;
  diagnosis: "lexical_gap" | "memory_gap" | "already_covered" | "invalid_sample" | string;
  target_item_id: string;
  target_statement: string;
  top_items: Array<{
    id: string;
    source: string;
    score: number;
    text: string;
    entities: string[];
  }>;
  actual_top_sources: string[];
}

export interface EmbeddingEvaluationSamplesReport {
  version: string;
  mode: "read_only_embedding_evaluation_samples" | string;
  status: "insufficient_samples" | "candidate" | "attention" | "blocked" | "covered" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    sample_status: string;
    sample_count: number;
    bm25_hit_count: number;
    mock_embedding_hit_count: number;
    lexical_gap_count: number;
    memory_gap_count: number;
    invalid_sample_count: number;
    bm25_hit_rate: number;
    mock_embedding_hit_rate: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  samples: EmbeddingEvaluationSample[];
  sample_schema: {
    path: string;
    required: string[];
    optional: string[];
  };
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalSampleExportPackSample {
  query: string;
  expected_entities: string[];
  expected_item_id: string;
  expected_source: string;
  current_chapter: number;
  reason: string;
  diagnosis: "lexical_gap" | "memory_gap" | "already_covered" | "invalid_sample" | string;
  bm25_hit: boolean;
  mock_embedding_hit: boolean;
  target_item_id: string;
  target_statement: string;
  actual_top_sources: string[];
}

export interface RetrievalSampleExportPackReport {
  version: string;
  mode: "read_only_retrieval_sample_export_pack" | string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  filename: string;
  content_type: string;
  summary: {
    sample_status: string;
    sample_count: number;
    bm25_hit_count: number;
    mock_embedding_hit_count: number;
    lexical_gap_count: number;
    memory_gap_count: number;
    already_covered_count: number;
    invalid_sample_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  manifest: {
    version: string;
    story_slug: string;
    generated_at: string;
    status: string;
    summary: RetrievalSampleExportPackReport["summary"];
    sample_schema: {
      path?: string;
      required?: string[];
      optional?: string[];
    };
    samples: RetrievalSampleExportPackSample[];
  };
  content_md: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface EmbeddingMockEvaluationReport {
  version: string;
  mode: "read_only_embedding_mock_evaluation_report" | string;
  status: "empty" | "candidate" | "attention" | "blocked" | "covered" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: RetrievalSampleExportPackReport["summary"] & {
    lexical_gap_rate: number;
    memory_gap_rate: number;
  };
  gate: {
    id: string;
    status: "candidate" | "needs_samples" | "needs_memory" | "blocked" | "covered" | string;
    passed: boolean;
    reason: string;
    min_candidates_required: number;
    sample_count: number;
    lexical_gap_count: number;
  };
  buckets: Record<
    "lexical_gap" | "memory_gap" | "already_covered" | "invalid_sample" | string,
    Array<{
      query: string;
      expected_entities: string[];
      target_item_id: string;
      target_statement: string;
      reason: string;
    }>
  >;
  report_md: string;
  export_pack: {
    status: string;
    filename: string;
    content_type: string;
  };
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalSampleReplayCase {
  case_id: string;
  query: string;
  expected_entities: string[];
  current_chapter: number;
  diagnosis: string;
  replay_status:
    | "still_failing_lexically"
    | "missing_memory_target"
    | "covered_by_current_retrieval"
    | "invalid_case"
    | "needs_review"
    | string;
  bm25_hit: boolean;
  mock_embedding_hit: boolean;
  target_item_id: string;
  target_statement: string;
  reason: string;
}

export interface RetrievalSampleReplayReport {
  version: string;
  mode: "read_only_retrieval_sample_replay_report" | string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    case_count: number;
    still_failing_lexically_count: number;
    missing_memory_target_count: number;
    covered_by_current_retrieval_count: number;
    invalid_case_count: number;
    needs_review_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  replay_gate: {
    id: string;
    status: "clean" | "needs_samples" | "needs_review" | "blocked" | string;
    passed: boolean;
    reason: string;
    case_count: number;
    invalid_case_count: number;
  };
  cases: RetrievalSampleReplayCase[];
  report_md: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalSampleMigrationRecord {
  eval_id: string;
  query: string;
  current_chapter: number;
  expected_entities: string[];
  expected_item_id: string;
  expected_source: string;
  target_statement: string;
  diagnosis: string;
  replay_status: string;
  labels: string[];
  assertions: {
    must_retrieve_item_id: string;
    should_include_entities: string[];
  };
  provenance: {
    story_slug: string;
    generated_at: string;
    original_case_id: string;
    source_report: string;
  };
}

export interface RetrievalSampleMigrationPackReport {
  version: string;
  mode: "read_only_retrieval_sample_migration_pack" | string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  filename: string;
  content_type: string;
  summary: {
    replay_case_count: number;
    record_count: number;
    migratable_count: number;
    skipped_count: number;
    still_failing_lexically_count: number;
    missing_memory_target_count: number;
    covered_by_current_retrieval_count: number;
    invalid_case_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  migration_gate: {
    id: string;
    status: "ready" | "needs_samples" | "needs_migratable_cases" | "blocked" | string;
    passed: boolean;
    reason: string;
    record_count: number;
    skipped_count: number;
  };
  manifest: {
    version: string;
    story_slug: string;
    generated_at: string;
    status: string;
    summary: Record<string, unknown>;
    migration_gate: Record<string, unknown>;
    record_schema: Record<string, unknown>;
    records: RetrievalSampleMigrationRecord[];
  };
  records: RetrievalSampleMigrationRecord[];
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryShadowComparison {
  id: "graphrag" | "zep" | "temporal_memory" | string;
  label: string;
  status: "candidate" | "monitor" | "deferred" | string;
  source_status: string;
  baseline: string;
  shadow_method: string;
  projected_gain_score: number;
  risk_score: number;
  decision: "shadow_compare" | "collect_samples" | "collect_foundation_evidence" | "defer" | string;
  sample_case_count: number;
  required_gate_ids: string[];
  missing_evidence: string[];
  notes: string[];
  rollback_strategy: string;
}

export interface GraphMemoryShadowSampleCase {
  eval_id: string;
  story_slug: string;
  display_name: string;
  query: string;
  expected_item_id: string;
  baseline_status: string;
  diagnosis: string;
  shadow_targets: string[];
}

export interface GraphMemoryShadowAcceptanceResult {
  gate_id: string;
  label: string;
  status: string;
  passed: boolean;
  result_status: "ready" | "needs_evidence" | string;
  target: string;
  evidence: string;
}

export interface GraphMemoryShadowComparePackReport {
  version: string;
  mode: "read_only_graph_memory_shadow_compare_pack" | string;
  status: "ready_for_shadow_compare" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_kind: SourceKind | string;
    design_status: string;
    evidence_status: string;
    design_gate_status: string;
    candidate_layer_count: number;
    monitor_layer_count: number;
    comparison_count: number;
    sample_case_count: number;
    acceptance_result_count: number;
    no_go_condition_count: number;
    best_projected_gain_score: number;
    best_candidate_layer: string;
    trend_record_count: number;
    trend_lexical_gap_count: number;
    relation_signal_count: number;
    causal_signal_count: number;
    state_signal_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  shadow_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    design_status: string;
    candidate_layer_count: number;
    sample_case_count: number;
  };
  comparisons: GraphMemoryShadowComparison[];
  sample_cases: GraphMemoryShadowSampleCase[];
  acceptance_results: GraphMemoryShadowAcceptanceResult[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryShadowCaseLayer {
  id: "graphrag" | "zep" | "temporal_memory" | string;
  label: string;
  status: "candidate" | "monitor" | "deferred" | string;
  decision: string;
  baseline: string;
  shadow_method: string;
  projected_gain_score: number;
  risk_score: number;
  missing_evidence: string[];
  rollback_strategy: string;
}

export interface GraphMemoryShadowCase {
  id: string;
  eval_id: string;
  story_slug: string;
  display_name: string;
  query: string;
  expected_item_id: string;
  baseline_status: string;
  diagnosis: string;
  shadow_targets: string[];
}

export interface GraphMemoryShadowCaseCell {
  case_id: string;
  layer_id: string;
  layer_label: string;
  status: "candidate" | "monitor" | "deferred" | string;
  decision: string;
  baseline_status: string;
  evidence_status: "local_evidence_ready" | "needs_local_evidence" | "deferred" | string;
  evidence_refs: string[];
  missing_evidence: string[];
  shadow_question: string;
  rollback_strategy: string;
  projected_gain_score: number;
  risk_score: number;
}

export interface GraphMemoryShadowCaseMatrixReport {
  version: string;
  mode: "read_only_graph_memory_shadow_case_matrix" | string;
  status: "ready" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_compare_status: string;
    status: string;
    case_count: number;
    layer_count: number;
    matrix_cell_count: number;
    candidate_cell_count: number;
    evidence_ready_cell_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  case_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    case_count: number;
    candidate_cell_count: number;
  };
  layers: GraphMemoryShadowCaseLayer[];
  cases: GraphMemoryShadowCase[];
  cells: GraphMemoryShadowCaseCell[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderBoundaryProvider {
  id: "graphrag" | "zep" | "temporal_memory" | string;
  label: string;
  service_target: string;
  provider_kind: string;
  status: "candidate" | "monitor" | "deferred" | string;
  source_layer_status: string;
  decision: string;
  opt_in_required: boolean;
  projected_gain_score: number;
  risk_score: number;
  recommended_for: string;
  local_baseline: string;
  rollback_strategy: string;
}

export interface GraphMemoryProviderBoundaryCategory {
  id: string;
  label: string;
  must_pass: boolean;
  base_requirement: string;
}

export interface GraphMemoryProviderBoundaryCell {
  provider_id: string;
  provider_label: string;
  category_id: string;
  category_label: string;
  status: "requires_opt_in" | "deferred" | string;
  must_pass: boolean;
  risk_level: "high" | "medium" | "low" | string;
  requirement: string;
  evidence_refs: string[];
  fallback: string;
}

export interface GraphMemoryProviderBoundaryMatrixReport {
  version: string;
  mode: "read_only_graph_memory_provider_boundary_matrix" | string;
  status: "ready_for_boundary_review" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_case_matrix_status: string;
    status: string;
    provider_count: number;
    candidate_provider_count: number;
    boundary_category_count: number;
    boundary_cell_count: number;
    requires_opt_in_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  boundary_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    candidate_provider_count: number;
    required_boundary_count: number;
  };
  providers: GraphMemoryProviderBoundaryProvider[];
  boundary_categories: GraphMemoryProviderBoundaryCategory[];
  boundary_cells: GraphMemoryProviderBoundaryCell[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryOfflineReplayProviderPlan {
  provider_id: string;
  provider_label: string;
  service_target: string;
  provider_kind: string;
  status: "planned" | "deferred" | string;
  opt_in_required: boolean;
  replay_scope: string;
  boundary_refs: string[];
  acceptance_summary: string;
  rollback_strategy: string;
  manual_review_required: boolean;
}

export interface GraphMemoryOfflineReplayCase {
  id: string;
  status: "planned" | "deferred" | string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  fixture_kind: string;
  eval_id: string;
  query: string;
  display_name: string;
  baseline_status: string;
  baseline_chain: string;
  replay_input: Record<string, unknown>;
  expected_delta: string;
  acceptance_criteria: string[];
  rollback_checklist: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
}

export interface GraphMemoryOfflineReplayStep {
  id: string;
  label: string;
  description: string;
}

export interface GraphMemoryOfflineShadowReplayPlanReport {
  version: string;
  mode: "read_only_graph_memory_offline_shadow_replay_plan" | string;
  status: "ready_for_offline_replay" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_provider_boundary_status: string;
    status: string;
    candidate_provider_count: number;
    provider_plan_count: number;
    replay_case_count: number;
    replay_step_count: number;
    manual_review_required_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  replay_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    provider_plan_count: number;
    replay_case_count: number;
  };
  provider_plans: GraphMemoryOfflineReplayProviderPlan[];
  replay_cases: GraphMemoryOfflineReplayCase[];
  replay_steps: GraphMemoryOfflineReplayStep[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryOfflineReplayProviderResult {
  provider_id: string;
  provider_label: string;
  service_target: string;
  status: "manual_review_required" | "collect_more_evidence" | string;
  case_result_count: number;
  candidate_gain_count: number;
  recommendation: string;
  rollback_strategy: string;
}

export interface GraphMemoryOfflineReplayCaseResult {
  id: string;
  source_case_id: string;
  status: "mock_candidate_gain" | "deferred" | string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  fixture_kind: string;
  eval_id: string;
  query: string;
  display_name: string;
  baseline_status: string;
  baseline_chain: string;
  mock_delta: Record<string, unknown>;
  gain_assessment: string;
  risk_assessment: string;
  acceptance_status: string;
  failure_mode: {
    fallback: string;
    reason: string;
    rollback_checklist: string[];
  };
  manual_review_result: {
    status: string;
    status_label: string;
    review_focus: string[];
  };
  no_go_conditions: string[];
}

export interface GraphMemoryOfflineShadowReplayReport {
  version: string;
  mode: "read_only_graph_memory_offline_shadow_replay_report" | string;
  status: "ready_for_review" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_replay_plan_status: string;
    status: string;
    provider_result_count: number;
    case_result_count: number;
    candidate_gain_count: number;
    manual_review_required_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  report_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    provider_result_count: number;
    case_result_count: number;
  };
  decision: {
    status: string;
    recommendation: string;
    candidate_gain_count: number;
    provider_result_count: number;
  };
  provider_results: GraphMemoryOfflineReplayProviderResult[];
  case_results: GraphMemoryOfflineReplayCaseResult[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeFixtureCase {
  eval_id: string;
  query: string;
  display_name: string;
  baseline_chain: string;
  mock_delta: Record<string, unknown>;
  gain_assessment: string;
  risk_assessment: string;
  manual_review_focus: string[];
  failure_fallback: string;
}

export interface GraphMemoryProviderSpikeFixture {
  id: string;
  dry_run_only: boolean;
  scope: string;
  project_slug: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_report_status: string;
  sample_case_count: number;
  source_case_ids: string[];
  cases: GraphMemoryProviderSpikeFixtureCase[];
  baseline_chain: string;
  expected_output: string;
}

export interface GraphMemoryProviderSpikeFixturePack {
  id: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  status: "dry_run_fixture_ready" | "deferred" | string;
  opt_in_required: boolean;
  fixture: GraphMemoryProviderSpikeFixture;
  cost_guardrails: string[];
  privacy_guardrails: string[];
  rollback_checklist: string[];
  manual_acceptance_checklist: string[];
  no_go_conditions: string[];
}

export interface GraphMemoryProviderSpikeFixturePackReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_fixture_pack" | string;
  status: "ready_for_fixture_pack" | "needs_more_evidence" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_replay_report_status: string;
    status: string;
    provider_fixture_count: number;
    selected_fixture_count: number;
    manual_review_required_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  fixture_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    provider_fixture_count: number;
    selected_fixture_count: number;
  };
  decision: {
    status: string;
    recommendation: string;
    provider_fixture_count: number;
    selected_fixture_count: number;
  };
  provider_fixture_packs: GraphMemoryProviderSpikeFixturePack[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeReadinessCheck {
  id: string;
  label: string;
  status: "passed" | "manual_review_required" | "blocked" | string;
  passed: boolean;
}

export interface GraphMemoryProviderSpikeReadiness {
  provider_id: string;
  provider_label: string;
  service_target: string;
  status: "manual_review_ready" | "blocked" | string;
  fixture_id: string;
  source_fixture_pack_status: string;
  sample_case_count: number;
  source_case_ids: string[];
  readiness_checks: GraphMemoryProviderSpikeReadinessCheck[];
  manual_review_items: string[];
  blockers: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeReadinessGateReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_readiness_gate" | string;
  status:
    | "ready_for_manual_opt_in_review"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_fixture_pack_status: string;
    status: string;
    provider_fixture_count: number;
    ready_for_manual_review_count: number;
    blocked_provider_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  readiness_gate: {
    id: string;
    status: string;
    passed: boolean;
    real_provider_config_allowed: boolean;
    reason: string;
    selected_provider_count: number;
  };
  decision: {
    status: string;
    recommendation: string;
    provider_count: number;
  };
  provider_readiness: GraphMemoryProviderSpikeReadiness[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeRunbookStep {
  id: string;
  phase: "prepare" | "dry_run" | "compare" | "review" | "rollback" | "stop" | string;
  title: string;
  description: string;
  expected_evidence: string[];
}

export interface GraphMemoryProviderSpikeRunbookProvider {
  provider_id: string;
  provider_label: string;
  service_target: string;
  status: "manual_dry_run_ready" | "blocked" | string;
  fixture_id: string;
  source_readiness_status: string;
  source_case_ids: string[];
  steps: GraphMemoryProviderSpikeRunbookStep[];
  acceptance_checks: string[];
  rollback_steps: string[];
  pause_conditions: string[];
  evidence_refs: string[];
  blockers: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeRunbookReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_runbook" | string;
  status: "ready_for_manual_dry_run" | "needs_more_evidence" | "blocked" | "deferred" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_readiness_gate_status: string;
    status: string;
    provider_runbook_count: number;
    ready_provider_count: number;
    blocked_provider_count: number;
    total_step_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  runbook: {
    id: string;
    title: string;
    status: string;
    manual_only: boolean;
    real_provider_config_allowed: boolean;
    provider_count: number;
    step_count: number;
    objective: string;
  };
  decision: {
    status: string;
    recommendation: string;
    provider_count: number;
  };
  provider_runbooks: GraphMemoryProviderSpikeRunbookProvider[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeDryRunResultField {
  id: string;
  label: string;
  description: string;
  input_kind: string;
  required: boolean;
  options: string[];
}

export interface GraphMemoryProviderSpikeDryRunDecisionOption {
  id: string;
  label: string;
  description: string;
}

export interface GraphMemoryProviderSpikeDryRunResultTemplateProvider {
  provider_id: string;
  provider_label: string;
  service_target: string;
  status: "manual_result_template_ready" | "blocked" | string;
  fixture_id: string;
  source_runbook_status: string;
  source_step_count: number;
  source_case_ids: string[];
  result_fields: GraphMemoryProviderSpikeDryRunResultField[];
  comparison_axes: GraphMemoryProviderSpikeDryRunDecisionOption[];
  acceptance_record: string[];
  pause_or_upgrade_decisions: GraphMemoryProviderSpikeDryRunDecisionOption[];
  rollback_confirmation: string[];
  evidence_refs: string[];
  blockers: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeDryRunResultTemplateReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_dry_run_result_template" | string;
  status:
    | "ready_for_manual_result_recording"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_runbook_status: string;
    status: string;
    provider_template_count: number;
    ready_provider_count: number;
    blocked_provider_count: number;
    required_result_field_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    result_write_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  template: {
    id: string;
    title: string;
    status: string;
    manual_only: boolean;
    result_write_allowed: boolean;
    real_provider_config_allowed: boolean;
    provider_count: number;
    required_result_field_count: number;
    objective: string;
  };
  decision: {
    status: string;
    recommendation: string;
    provider_count: number;
  };
  provider_result_templates: GraphMemoryProviderSpikeDryRunResultTemplateProvider[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeMockResultFieldValue {
  field_id: string;
  label: string;
  value: unknown;
  source: string;
}

export interface GraphMemoryProviderSpikeMockResultRecord {
  id: string;
  status: "mock_filled_result_ready" | string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  fixture_id: string;
  source_case_id: string;
  eval_id: string;
  template_field_count: number;
  field_values: GraphMemoryProviderSpikeMockResultFieldValue[];
  manual_decision: string;
  gain_summary: string;
  risk_summary: string;
  review_summary: string;
  pause_or_upgrade_decision: {
    id: string;
    label: string;
    description: string;
  };
  evidence_refs: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeMockResultReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_mock_result_report" | string;
  status:
    | "ready_for_manual_review"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_result_template_status: string;
    source_mock_replay_status: string;
    status: string;
    provider_result_count: number;
    filled_record_count: number;
    candidate_gain_count: number;
    manual_review_required_count: number;
    writes_artifacts: boolean;
    result_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  report_gate: {
    id: string;
    status: string;
    passed: boolean;
    reason: string;
    filled_record_count: number;
  };
  decision: {
    status: string;
    recommendation: string;
    filled_record_count: number;
  };
  mock_result_records: GraphMemoryProviderSpikeMockResultRecord[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeReviewGateItem {
  id: string;
  label: string;
  status: string;
  evidence: string;
}

export interface GraphMemoryProviderSpikeReviewGateProviderReview {
  id: string;
  status: "manual_review_required" | string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_record_id: string;
  fixture_id: string;
  source_case_id: string;
  eval_id: string;
  manual_decision: string;
  gate_decision: string;
  candidate_gain: boolean;
  review_item_count: number;
  review_items: GraphMemoryProviderSpikeReviewGateItem[];
  gain_summary: string;
  risk_summary: string;
  review_summary: string;
  pause_or_upgrade_decision: Record<string, unknown>;
  evidence_refs: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeReviewGateReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_review_gate" | string;
  status:
    | "ready_for_manual_review_gate"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_mock_result_status: string;
    status: string;
    mock_record_count: number;
    provider_review_count: number;
    candidate_gain_count: number;
    manual_review_required_count: number;
    pause_decision_count: number;
    manual_approval_required_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    result_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  review_gate: {
    id: string;
    status: string;
    passed: boolean;
    approval_required: boolean;
    automatic_upgrade_allowed: boolean;
    real_provider_config_allowed: boolean;
    reason: string;
    provider_review_count: number;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    provider_review_count: number;
  };
  provider_reviews: GraphMemoryProviderSpikeReviewGateProviderReview[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeManualApprovalPackEntry {
  id: string;
  label: string;
  status?: string;
  evidence?: string;
  value?: string;
}

export interface GraphMemoryProviderSpikeManualApprovalPackItem {
  id: string;
  status: "manual_approval_required" | string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_review_id: string;
  source_record_id: string;
  fixture_id: string;
  source_case_id: string;
  eval_id: string;
  manual_decision: string;
  gate_decision: string;
  approval_required: boolean;
  manual_signature_required: boolean;
  real_provider_config_allowed: boolean;
  risk_signoff_count: number;
  rollback_confirmation_count: number;
  opt_in_material_count: number;
  risk_signoffs: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  rollback_confirmations: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  opt_in_materials: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  gain_summary: string;
  risk_summary: string;
  evidence_refs: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeManualApprovalPackReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_manual_approval_pack" | string;
  status:
    | "ready_for_manual_approval_pack"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_review_gate_status: string;
    status: string;
    provider_review_count: number;
    approval_item_count: number;
    risk_signoff_count: number;
    rollback_confirmation_count: number;
    opt_in_material_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    approval_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  approval_pack: {
    id: string;
    status: string;
    ready: boolean;
    approval_required: boolean;
    manual_signature_required: boolean;
    automatic_upgrade_allowed: boolean;
    real_provider_config_allowed: boolean;
    approval_item_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    approval_item_count: number;
  };
  approval_items: GraphMemoryProviderSpikeManualApprovalPackItem[];
  manual_approval_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeManualApprovalEvidenceChecklistItem {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_approval_id: string;
  source_review_id: string;
  fixture_id: string;
  eval_id: string;
  gate_decision: string;
  evidence_status: string;
  pending_signoff_count: number;
  material_gap_count: number;
  rollback_material_gap_count: number;
  pending_signoffs: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  material_gaps: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  rollback_material_gaps: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  available_materials: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  rollback_confirmations: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  evidence_refs: string[];
  no_go_conditions: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeManualApprovalEvidenceChecklistReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_manual_approval_evidence_checklist"
    | string;
  status:
    | "ready_for_manual_approval_evidence_checklist"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_approval_pack_status: string;
    status: string;
    approval_item_count: number;
    checklist_item_count: number;
    pending_signoff_count: number;
    material_gap_count: number;
    rollback_material_gap_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    approval_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  evidence_checklist: {
    id: string;
    status: string;
    ready: boolean;
    manual_signoff_required: boolean;
    materials_complete: boolean;
    automatic_upgrade_allowed: boolean;
    real_provider_config_allowed: boolean;
    checklist_item_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    checklist_item_count: number;
  };
  checklist_items: GraphMemoryProviderSpikeManualApprovalEvidenceChecklistItem[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInEvidenceSnapshotItem {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_checklist_id: string;
  source_approval_id: string;
  source_review_id: string;
  fixture_id: string;
  eval_id: string;
  evidence_status: string;
  signoff_todo_count: number;
  material_gap_count: number;
  rollback_material_gap_count: number;
  blocker_count: number;
  signoff_todos: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  material_gaps: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  rollback_material_gaps: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  available_materials: GraphMemoryProviderSpikeManualApprovalPackEntry[];
  evidence_refs: string[];
  no_go_conditions: string[];
  blocker_reasons: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeOptInEvidenceSnapshotReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_evidence_snapshot"
    | string;
  status:
    | "ready_for_opt_in_evidence_snapshot"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_evidence_checklist_status: string;
    status: string;
    checklist_item_count: number;
    snapshot_item_count: number;
    signoff_todo_count: number;
    material_gap_count: number;
    rollback_material_gap_count: number;
    blocker_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    snapshot_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  opt_in_snapshot: {
    id: string;
    status: string;
    ready: boolean;
    opt_in_blocked: boolean;
    real_provider_config_allowed: boolean;
    snapshot_item_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    snapshot_item_count: number;
    blocker_count: number;
  };
  snapshot_items: GraphMemoryProviderSpikeOptInEvidenceSnapshotItem[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInNoGoCell {
  id: string;
  category: string;
  label: string;
  status: string;
  blocker_count: number;
  reason: string;
  evidence_ref_count: number;
}

export interface GraphMemoryProviderSpikeOptInNoGoMatrixRow {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_snapshot_id: string;
  source_checklist_id: string;
  fixture_id: string;
  eval_id: string;
  cell_count: number;
  blocked_cell_count: number;
  cells: GraphMemoryProviderSpikeOptInNoGoCell[];
  no_go_reasons: string[];
  evidence_refs: string[];
  source_blocker_reasons: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeOptInNoGoMatrixReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_opt_in_no_go_matrix" | string;
  status:
    | "ready_for_opt_in_no_go_matrix"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_opt_in_snapshot_status: string;
    status: string;
    provider_count: number;
    snapshot_item_count: number;
    matrix_row_count: number;
    matrix_cell_count: number;
    blocked_cell_count: number;
    signoff_blocker_count: number;
    material_blocker_count: number;
    rollback_blocker_count: number;
    real_config_blocker_count: number;
    external_account_or_key_blocker_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    matrix_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  no_go_matrix: {
    id: string;
    status: string;
    ready: boolean;
    opt_in_blocked: boolean;
    real_provider_config_allowed: boolean;
    matrix_row_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    matrix_row_count: number;
    blocked_cell_count: number;
  };
  matrix_rows: GraphMemoryProviderSpikeOptInNoGoMatrixRow[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInOperatorStep {
  id: string;
  category: string;
  label: string;
  status: string;
  action: string;
  source_cell_id: string;
  blocker_count: number;
  reason: string;
  evidence_refs: string[];
  pause_required: boolean;
  upgrade_allowed: boolean;
  real_provider_config_allowed: boolean;
}

export interface GraphMemoryProviderSpikeOptInOperatorChecklistSection {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_matrix_row_id: string;
  source_snapshot_id: string;
  fixture_id: string;
  eval_id: string;
  step_count: number;
  blocked_step_count: number;
  steps: GraphMemoryProviderSpikeOptInOperatorStep[];
  pause_reason: string;
  evidence_refs: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeOptInOperatorChecklistReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_operator_checklist"
    | string;
  status:
    | "ready_for_opt_in_operator_checklist"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_no_go_matrix_status: string;
    status: string;
    provider_count: number;
    matrix_row_count: number;
    checklist_section_count: number;
    operator_step_count: number;
    blocked_step_count: number;
    manual_signoff_step_count: number;
    real_config_step_count: number;
    external_account_or_key_step_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    checklist_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  operator_checklist: {
    id: string;
    status: string;
    ready: boolean;
    opt_in_blocked: boolean;
    real_provider_config_allowed: boolean;
    checklist_section_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    checklist_section_count: number;
    blocked_step_count: number;
  };
  checklist_sections: GraphMemoryProviderSpikeOptInOperatorChecklistSection[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInReviewPacketEvidenceItem {
  id: string;
  order: number;
  source_step_id: string;
  category: string;
  label: string;
  status: string;
  action: string;
  reason: string;
  blocker_count: number;
  evidence_refs: string[];
  pause_required: boolean;
  review_note: string;
  upgrade_allowed: boolean;
  real_provider_config_allowed: boolean;
}

export interface GraphMemoryProviderSpikeOptInReviewPacketSection {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_checklist_section_id: string;
  source_matrix_row_id: string;
  source_snapshot_id: string;
  fixture_id: string;
  eval_id: string;
  evidence_item_count: number;
  blocked_step_count: number;
  review_step_count: number;
  pause_required: boolean;
  evidence_sequence: GraphMemoryProviderSpikeOptInReviewPacketEvidenceItem[];
  pause_materials: string[];
  escalation_materials: string[];
  reviewer_todos: string[];
  evidence_refs: string[];
  recommendation: string;
}

export interface GraphMemoryProviderSpikeOptInReviewPacketReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_review_packet"
    | string;
  status:
    | "ready_for_opt_in_review_packet"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_operator_checklist_status: string;
    status: string;
    provider_count: number;
    source_checklist_section_count: number;
    packet_section_count: number;
    evidence_item_count: number;
    blocked_step_count: number;
    pause_material_count: number;
    escalation_material_count: number;
    manual_signoff_item_count: number;
    real_config_item_count: number;
    no_go_condition_count: number;
    writes_artifacts: boolean;
    review_packet_write_allowed: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  review_packet: {
    id: string;
    status: string;
    ready: boolean;
    opt_in_blocked: boolean;
    real_provider_config_allowed: boolean;
    packet_section_count: number;
    evidence_item_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    packet_section_count: number;
    blocked_step_count: number;
  };
  packet_sections: GraphMemoryProviderSpikeOptInReviewPacketSection[];
  review_packet_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInDecisionLedgerSignoffField {
  id: string;
  field: string;
  label: string;
  value: string | null;
  required: boolean;
  saved: boolean;
}

export interface GraphMemoryProviderSpikeOptInDecisionLedgerRow {
  id: string;
  status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_review_packet_section_id: string;
  source_checklist_section_id: string;
  fixture_id: string;
  eval_id: string;
  evidence_item_count: number;
  blocked_step_count: number;
  pause_material_count: number;
  escalation_material_count: number;
  pending_signoff_fields: GraphMemoryProviderSpikeOptInDecisionLedgerSignoffField[];
  decision_fields: Record<string, unknown>;
  preview_notes: string[];
  audit_refs: string[];
  approved: boolean;
  ledger_write_allowed: boolean;
  real_provider_config_allowed: boolean;
}

export interface GraphMemoryProviderSpikeOptInDecisionLedgerPreviewReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_decision_ledger_preview"
    | string;
  status:
    | "ready_for_opt_in_decision_ledger_preview"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_review_packet_status: string;
    status: string;
    provider_count: number;
    source_packet_section_count: number;
    ledger_row_count: number;
    pending_signoff_field_count: number;
    blocked_row_count: number;
    pause_material_count: number;
    escalation_material_count: number;
    writes_artifacts: boolean;
    ledger_write_allowed: boolean;
    approval_saved: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  decision_ledger_preview: {
    id: string;
    status: string;
    ready: boolean;
    ledger_row_count: number;
    pending_signoff_field_count: number;
    ledger_write_allowed: boolean;
    approval_saved: boolean;
    real_provider_config_allowed: boolean;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    ledger_row_count: number;
    blocked_row_count: number;
  };
  ledger_rows: GraphMemoryProviderSpikeOptInDecisionLedgerRow[];
  ledger_preview_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInFinalReadinessSignoffField {
  id: string;
  field: string;
  label: string;
  value: string | null;
  required: boolean;
  saved: boolean;
  provider_id: string;
  service_target: string;
  source_decision_ledger_row_id: string;
}

export interface GraphMemoryProviderSpikeOptInFinalReadinessRow {
  id: string;
  gate_status: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_decision_ledger_row_id: string;
  source_review_packet_section_id: string;
  fixture_id: string;
  eval_id: string;
  unresolved_signoff_fields: GraphMemoryProviderSpikeOptInFinalReadinessSignoffField[];
  unresolved_blockers: string[];
  readiness_notes: string[];
  audit_refs: string[];
  real_provider_ready: boolean;
  final_decision_saved: boolean;
  real_provider_config_allowed: boolean;
}

export interface GraphMemoryProviderSpikeOptInFinalReadinessSummaryReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_final_readiness_summary"
    | string;
  status:
    | "ready_for_opt_in_final_readiness_summary"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_decision_ledger_status: string;
    status: string;
    provider_count: number;
    source_ledger_row_count: number;
    readiness_row_count: number;
    unresolved_signoff_field_count: number;
    blocked_row_count: number;
    unresolved_blocker_count: number;
    writes_artifacts: boolean;
    final_decision_saved: boolean;
    approval_saved: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_ready: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  final_readiness_summary: {
    id: string;
    status: string;
    ready: boolean;
    real_provider_ready: boolean;
    readiness_label: string;
    readiness_row_count: number;
    unresolved_signoff_field_count: number;
    unresolved_blocker_count: number;
    final_decision_saved: boolean;
    real_provider_config_allowed: boolean;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    readiness_row_count: number;
    unresolved_blocker_count: number;
  };
  readiness_rows: GraphMemoryProviderSpikeOptInFinalReadinessRow[];
  unresolved_signoff_fields: GraphMemoryProviderSpikeOptInFinalReadinessSignoffField[];
  final_readiness_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInHumanSignoffSchemaField {
  id: string;
  provider_id: string;
  service_target: string;
  field: string;
  label: string;
  value: string | null;
  type: string;
  required: boolean;
  saved: boolean;
  input_storage: string;
  source_final_readiness_field_id: string;
  source_final_readiness_row_id: string;
  source_decision_ledger_row_id: string;
  validation_rule: {
    type: string;
    min_length: number;
    max_length: number;
    rejects_plaintext_keys: boolean;
  };
  review_prompt: string;
}

export interface GraphMemoryProviderSpikeOptInHumanSignoffSchemaSection {
  id: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_final_readiness_row_id: string;
  source_decision_ledger_row_id: string;
  fixture_id: string;
  eval_id: string;
  schema_fields: GraphMemoryProviderSpikeOptInHumanSignoffSchemaField[];
  required_field_count: number;
  save_allowed: boolean;
  signoff_saved: boolean;
  real_provider_config_allowed: boolean;
  section_notes: string[];
}

export interface GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_opt_in_human_signoff_schema_draft"
    | string;
  status:
    | "ready_for_human_signoff_schema_draft"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_final_readiness_status: string;
    source_final_readiness_summary_status: string;
    status: string;
    provider_count: number;
    schema_section_count: number;
    schema_field_count: number;
    required_field_count: number;
    unresolved_signoff_field_count: number;
    writes_artifacts: boolean;
    signoff_saved: boolean;
    approval_saved: boolean;
    final_decision_saved: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_ready: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  schema_draft: {
    id: string;
    status: string;
    ready: boolean;
    schema_version: string;
    save_allowed: boolean;
    signoff_saved: boolean;
    real_provider_config_allowed: boolean;
    field_count: number;
    required_field_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    schema_field_count: number;
  };
  schema_sections: GraphMemoryProviderSpikeOptInHumanSignoffSchemaSection[];
  schema_fields: GraphMemoryProviderSpikeOptInHumanSignoffSchemaField[];
  validation_rules: Array<Record<string, unknown>>;
  schema_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeOptInConfigEntry {
  id: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_schema_section_id: string;
  fixture_id: string;
  eval_id: string;
  config_key: string;
  config_format: string;
  storage_policy: string;
  save_allowed: boolean;
  config_saved: boolean;
  plaintext_key_required: boolean;
  plaintext_key_returned: boolean;
  real_provider_config_allowed: boolean;
  mock_compatible: boolean;
  field_mapping_count: number;
  required_signoff_count: number;
  draft_values: Record<string, unknown>;
  field_mappings: GraphMemoryProviderSpikeOptInConfigFieldMapping[];
}

export interface GraphMemoryProviderSpikeOptInConfigFieldMapping {
  id: string;
  provider_id: string;
  field: string;
  label: string;
  source_schema_field_id: string;
  source_decision_ledger_row_id: string;
  target_config_path: string;
  required: boolean;
  saved: boolean;
  storage_policy: string;
}

export interface GraphMemoryProviderSpikeOptInConfigDraftReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_opt_in_config_draft" | string;
  status:
    | "ready_for_opt_in_config_draft"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_human_signoff_schema_status: string;
    source_schema_draft_status: string;
    status: string;
    provider_count: number;
    config_entry_count: number;
    field_mapping_count: number;
    writes_artifacts: boolean;
    config_saved: boolean;
    signoff_saved: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    uses_graphrag: boolean;
    uses_zep: boolean;
    uses_vector_store: boolean;
    uses_reranker: boolean;
    uses_embedding_provider: boolean;
    plaintext_key_returned: boolean;
  };
  config_draft: {
    id: string;
    status: string;
    ready: boolean;
    draft_version: string;
    config_entry_count: number;
    field_mapping_count: number;
    save_allowed: boolean;
    config_saved: boolean;
    mock_compatible: boolean;
    real_provider_config_allowed: boolean;
    reason: string;
  };
  adapter_boundary: {
    id: string;
    status: string;
    provider_count: number;
    mock_adapter_allowed: boolean;
    real_provider_adapter_allowed: boolean;
    external_service_calls_allowed: boolean;
    plaintext_key_allowed: boolean;
    writes_artifacts: boolean;
    allowed_modes: string[];
    blocked_modes: string[];
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    config_entry_count: number;
  };
  config_entries: GraphMemoryProviderSpikeOptInConfigEntry[];
  field_mappings: GraphMemoryProviderSpikeOptInConfigFieldMapping[];
  draft_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeLocalProviderContractItem {
  id: string;
  provider_id: string;
  provider_label: string;
  service_target: string;
  source_config_entry_id: string;
  fixture_id: string;
  eval_id: string;
  contract_version: string;
  adapter_mode: string;
  mock_adapter_required: boolean;
  real_provider_calls_allowed: boolean;
  plaintext_key_allowed: boolean;
  writes_artifacts: boolean;
  implements_methods: string[];
  input_schema: Record<string, string>;
  output_schema: Record<string, string>;
}

export interface GraphMemoryProviderSpikeAdapterBoundary {
  id: string;
  provider_id: string;
  service_target: string;
  allowed_mode: string;
  blocked_modes: string[];
  plaintext_key_allowed: boolean;
  external_network_allowed: boolean;
  writes_artifacts: boolean;
  real_provider_adapter_allowed: boolean;
}

export interface GraphMemoryProviderSpikeContractMethod {
  name: string;
  description: string;
  external_services_required: boolean;
}

export interface GraphMemoryProviderSpikeLocalProviderContractReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_local_provider_contract" | string;
  status:
    | "ready_for_local_provider_contract"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_config_draft_status: string;
    status: string;
    provider_contract_count: number;
    adapter_boundary_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_config_allowed: boolean;
    real_provider_adapter_allowed: boolean;
    plaintext_key_returned: boolean;
  };
  local_provider_contract: {
    id: string;
    status: string;
    ready: boolean;
    contract_version: string;
    provider_contract_count: number;
    real_provider_adapter_allowed: boolean;
    mock_only: boolean;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    provider_contract_count: number;
  };
  provider_contracts: GraphMemoryProviderSpikeLocalProviderContractItem[];
  adapter_boundaries: GraphMemoryProviderSpikeAdapterBoundary[];
  contract_methods: GraphMemoryProviderSpikeContractMethod[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeFixtureHarness {
  id: string;
  provider_id: string;
  service_target: string;
  source_contract_id: string;
  fixture_id: string;
  eval_id: string;
  execution_mode: string;
  mock_execution_allowed: boolean;
  real_provider_execution_allowed: boolean;
  writes_artifacts: boolean;
  input_payload: Record<string, string>;
  expected_result_schema: Record<string, string>;
  validation_steps: string[];
}

export interface GraphMemoryProviderSpikeSingleFixtureDryRunHarnessReport {
  version: string;
  mode:
    | "read_only_graph_memory_provider_spike_single_fixture_dry_run_harness"
    | string;
  status:
    | "ready_for_single_fixture_dry_run_harness"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_local_provider_contract_status: string;
    status: string;
    fixture_harness_count: number;
    mock_execution_allowed: boolean;
    real_provider_execution_allowed: boolean;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    plaintext_key_returned: boolean;
  };
  dry_run_harness: {
    id: string;
    status: string;
    ready: boolean;
    mock_execution_allowed: boolean;
    real_provider_execution_allowed: boolean;
    fixture_harness_count: number;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    fixture_harness_count: number;
  };
  fixture_harnesses: GraphMemoryProviderSpikeFixtureHarness[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeMockCompatibleAdapterSpec {
  id: string;
  provider_id: string;
  service_target: string;
  source_fixture_harness_id: string;
  adapter_mode: string;
  implements_contract_methods: string[];
  fixture_bindings: string[];
  mock_result_template: Record<string, unknown>;
  real_provider_calls_allowed: boolean;
  external_network_allowed: boolean;
  plaintext_key_allowed: boolean;
  writes_artifacts: boolean;
}

export interface GraphMemoryProviderSpikeMockCompatibleAdapterReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_mock_compatible_adapter" | string;
  status:
    | "ready_for_mock_compatible_adapter"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_single_fixture_harness_status: string;
    status: string;
    adapter_count: number;
    mock_adapter_ready: boolean;
    real_provider_adapter_allowed: boolean;
    writes_artifacts: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    plaintext_key_returned: boolean;
  };
  mock_compatible_adapter: {
    id: string;
    status: string;
    ready: boolean;
    adapter_count: number;
    mock_adapter_ready: boolean;
    real_provider_adapter_allowed: boolean;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    adapter_count: number;
  };
  adapter_specs: GraphMemoryProviderSpikeMockCompatibleAdapterSpec[];
  validation_cases: Array<Record<string, unknown>>;
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface GraphMemoryProviderSpikeManualMockAdapterReviewRow {
  id: string;
  provider_id: string;
  service_target: string;
  source_adapter_spec_id: string;
  source_fixture_harness_id: string;
  adapter_mode: string;
  review_status: string;
  risk_level: string;
  required_methods: string[];
  missing_methods: string[];
  fixture_bindings: string[];
  review_prompts: string[];
  real_provider_calls_allowed: boolean;
  external_network_allowed: boolean;
  plaintext_key_allowed: boolean;
  writes_artifacts: boolean;
  manual_decision_saved: boolean;
}

export interface GraphMemoryProviderSpikeManualMockAdapterComplianceCheck {
  id: string;
  provider_id: string;
  service_target: string;
  check: string;
  status: string;
  external_services_required: boolean;
  real_provider_adapter_allowed: boolean;
  reason: string;
}

export interface GraphMemoryProviderSpikeManualMockAdapterReviewReport {
  version: string;
  mode: "read_only_graph_memory_provider_spike_manual_mock_adapter_review" | string;
  status:
    | "ready_for_manual_mock_adapter_review"
    | "needs_more_evidence"
    | "blocked"
    | "deferred"
    | string;
  story_slug: string;
  source_kind: SourceKind | string;
  generated_at: string;
  summary: {
    story_slug: string;
    source_mock_adapter_status: string;
    status: string;
    review_row_count: number;
    compliance_check_count: number;
    blocked_check_count: number;
    writes_artifacts: boolean;
    manual_decision_saved: boolean;
    external_services_required: boolean;
    provider_calls: boolean;
    real_provider_adapter_allowed: boolean;
    plaintext_key_returned: boolean;
    pause_after_this_slice: boolean;
  };
  manual_mock_adapter_review: {
    id: string;
    status: string;
    ready: boolean;
    review_row_count: number;
    compliance_check_count: number;
    blocked_check_count: number;
    save_allowed: boolean;
    manual_decision_saved: boolean;
    real_provider_adapter_allowed: boolean;
    pause_after_this_slice: boolean;
    reason: string;
  };
  decision: {
    status: string;
    recommendation: string;
    next_slice: string;
    review_row_count: number;
  };
  review_rows: GraphMemoryProviderSpikeManualMockAdapterReviewRow[];
  compliance_checks: GraphMemoryProviderSpikeManualMockAdapterComplianceCheck[];
  review_materials: string[];
  manual_review_checklist: string[];
  no_go_conditions: string[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalFailureSample {
  id: string;
  created_at: string;
  query: string;
  expected_entities: string[];
  expected_item_id: string;
  expected_source: string;
  reason: string;
  current_chapter: number;
  actual_top_sources: string[];
}

export interface RetrievalFailureSamplesReport {
  version: string;
  mode: "local_retrieval_failure_sample_authoring" | string;
  status: "missing" | "ready" | "damaged" | "builtin_sample" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  artifact_path: string;
  summary: {
    sample_count: number;
    invalid_sample_count: number;
    write_policy: string;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  samples: RetrievalFailureSample[];
  sample_schema: {
    path: string;
    required: string[];
    optional: string[];
  };
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalFailureSampleAppendRequest {
  query: string;
  expected_entities: string[];
  expected_item_id?: string;
  expected_source?: string;
  reason?: string;
  current_chapter?: number;
  actual_top_sources?: string[];
}

export interface RetrievalFailureSampleAppendResponse {
  version: string;
  mode: "local_append_retrieval_failure_sample" | string;
  status: "appended" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  artifact_path: string;
  sample: RetrievalFailureSample;
  summary: RetrievalFailureSamplesReport["summary"];
  boundaries: string[];
  next_steps: string[];
}

export interface ProjectionHealthCheck {
  id: string;
  label: string;
  status: "ready" | "attention" | "blocked" | string;
  status_label: string;
  source_artifact: string;
  evidence: string;
  next_step: string;
  detail: Record<string, unknown>;
}

export interface ProjectionHealthReport {
  version: string;
  mode: "read_only_projection_health" | string;
  status: "ready" | "attention" | "blocked" | string;
  run_id: string;
  branch_id: string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    check_count: number;
    ready_count: number;
    attention_count: number;
    blocked_count: number;
    writes_artifacts: boolean;
    mutates_state_snapshot: boolean;
    replaces_canon_ledger: boolean;
    external_services_required: boolean;
  };
  checks: ProjectionHealthCheck[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface ReaderPanelPersona {
  id: string;
  label: string;
  focus: string;
  status: "ready" | "attention" | "blocked" | string;
  issue_ids: string[];
  verdict: string;
}

export interface ReaderPanelIssue {
  id: string;
  label: string;
  severity: "low" | "medium" | "high" | string;
  severity_label: string;
  evidence: string[];
  persona_ids: string[];
  revision_brief: string;
}

export interface ReaderRevisionBrief {
  issue_id: string;
  label: string;
  severity: "low" | "medium" | "high" | string;
  revision_brief: string;
  keep: string;
  avoid: string;
}

export interface ReaderPanelReport {
  version: string;
  mode: "deterministic_reader_panel" | string;
  status: "ready" | "attention" | "blocked" | string;
  run_id: string;
  branch_id: string;
  summary: {
    issue_count: number;
    persona_count: number;
    revision_brief_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    llm_required: boolean;
  };
  personas: ReaderPanelPersona[];
  issues: ReaderPanelIssue[];
  revision_briefs: ReaderRevisionBrief[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface PromptBudgetItem {
  id: string;
  source: string;
  section_id: string;
  score: number;
  priority: number;
  text: string;
  char_count: number;
  estimated_tokens: number;
  evidence: string;
  included: boolean;
  reason: string;
}

export interface PromptBudgetSection {
  id: string;
  label: string;
  item_count: number;
  estimated_chars: number;
  items: PromptBudgetItem[];
}

export interface PromptBudgetPackReport {
  version: string;
  mode: "read_only_prompt_budget_pack" | string;
  status: "ready" | "attention" | "blocked" | string;
  run_id: string;
  branch_id: string;
  summary: {
    char_budget: number;
    source_item_count: number;
    deduped_item_count: number;
    included_item_count: number;
    excluded_item_count: number;
    estimated_prompt_chars: number;
    estimated_prompt_tokens: number;
    compression_ratio: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_vector_store: boolean;
  };
  sections: PromptBudgetSection[];
  packed_items: PromptBudgetItem[];
  excluded_items: PromptBudgetItem[];
  prompt_block: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
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

export interface ModelConfigurationSection {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  next_step: string;
}

export interface ModelConfigurationPreset {
  id: string;
  label: string;
  base_url: string;
  model_name: string;
  api_key_help: string;
  editable: boolean;
  enabled?: boolean;
}

export interface ModelConfigurationSummary {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    llm_configured: boolean;
    mock_enabled: boolean;
    visual_configured: boolean;
    visual_enabled: boolean;
    connectivity_check_available: boolean;
    plaintext_key_returned: boolean;
    ready_count: number;
    attention_count: number;
  };
  sections: ModelConfigurationSection[];
  text_model_presets: ModelConfigurationPreset[];
  visual_model_presets: ModelConfigurationPreset[];
  form_guidance: {
    save_scope: string;
    plaintext_key_returned: boolean;
    connection_test_note: string;
    secret_boundary: string;
  };
  warnings: string[];
  next_steps: string[];
}

export interface LLMProfileAssignmentProfile {
  id: string;
  label: string;
  task_kind: string;
  provider_id: string;
  mode: string;
  model: string;
  temperature: number | null;
  max_tokens: number | null;
  budget_tier: string;
  fallback: string;
  note: string;
}

export interface LLMProfileAssignmentReport {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    profile_count: number;
    provider_profile_count: number;
    mock_or_deterministic_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    plaintext_key_returned: boolean;
  };
  routing: {
    llm_route: string;
    visual_route: string;
    fallback_policy: string;
  };
  profiles: LLMProfileAssignmentProfile[];
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface ApiContractEndpoint {
  group: string;
  method: string;
  path: string;
  summary: string;
  operation_id: string;
  response_type: string;
  client_method: string | null;
  status_codes: number[];
}

export interface ApiContractGroup {
  id: string;
  label: string;
  endpoint_count: number;
}

export interface ApiContractTypedClientMethod {
  client_method: string;
  method: string;
  path: string;
  operation_id: string;
  response_type: string;
  group: string;
}

export interface ApiContractReport {
  version: string;
  mode: "read_only_api_contract" | string;
  status: "ready" | "attention" | string;
  summary: {
    endpoint_count: number;
    openapi_path_count: number;
    typed_client_method_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    plaintext_key_returned: boolean;
    generated_client_written: boolean;
  };
  openapi: Record<string, unknown>;
  groups: ApiContractGroup[];
  endpoints: ApiContractEndpoint[];
  typed_client: {
    status: string;
    client_source: string;
    types_source: string;
    methods: ApiContractTypedClientMethod[];
    generation: {
      mode: string;
      writes_files: boolean;
      generated_client_exists: boolean;
      recommendation: string;
    };
  };
  boundaries: string[];
  next_steps: string[];
}

export interface CrossProjectRetrievalSamplesProject {
  story_slug: string;
  display_name: string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  migration_gate_status: string;
  migration_gate_passed: boolean;
  record_count: number;
  replay_case_count: number;
  still_failing_lexically_count: number;
  covered_by_current_retrieval_count: number;
  skipped_count: number;
  filename: string;
  sample_records: Array<{
    eval_id: string;
    query: string;
    expected_item_id: string;
    replay_status: string;
  }>;
  reason?: string;
}

export interface CrossProjectRetrievalSamplesIndexRecord
  extends RetrievalSampleMigrationRecord {
  story_slug: string;
  display_name: string;
  indexed_at: string;
}

export interface CrossProjectRetrievalSamplesIndexReport {
  version: string;
  mode: "read_only_cross_project_retrieval_samples_index" | string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  generated_at: string;
  summary: {
    project_count: number;
    ready_project_count: number;
    empty_project_count: number;
    attention_project_count: number;
    blocked_project_count: number;
    record_count: number;
    replay_case_count: number;
    still_failing_lexically_count: number;
    covered_by_current_retrieval_count: number;
    skipped_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  index_gate: {
    id: string;
    status: "ready" | "needs_projects" | "needs_records" | "blocked" | string;
    passed: boolean;
    reason: string;
    project_count: number;
    record_count: number;
  };
  projects: CrossProjectRetrievalSamplesProject[];
  records: CrossProjectRetrievalSamplesIndexRecord[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface RetrievalSamplesTrendSignal {
  id: string;
  label: string;
  status: "ready" | "attention" | "blocked" | "deferred" | string;
  value: number;
  detail: string;
}

export interface RetrievalSamplesProjectTrend {
  story_slug: string;
  display_name: string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  record_count: number;
  replay_case_count: number;
  lexical_gap_count: number;
  covered_count: number;
  skipped_count: number;
  trend_bucket:
    | "has_samples"
    | "covered_samples"
    | "empty_samples"
    | "blocked"
    | string;
}

export interface RetrievalSamplesTrendSnapshotReport {
  version: string;
  mode: "read_only_retrieval_samples_trend_snapshot" | string;
  status: "empty" | "ready" | "attention" | "blocked" | string;
  generated_at: string;
  summary: {
    project_count: number;
    ready_project_count: number;
    empty_project_count: number;
    attention_project_count: number;
    blocked_project_count: number;
    record_count: number;
    replay_case_count: number;
    still_failing_lexically_count: number;
    covered_by_current_retrieval_count: number;
    skipped_count: number;
    sampled_project_ratio: number;
    lexical_gap_ratio: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    uses_embedding_provider: boolean;
    uses_vector_store: boolean;
    plaintext_key_returned: boolean;
  };
  trend_gate: {
    id: string;
    status: "ready" | "needs_projects" | "needs_records" | "blocked" | string;
    passed: boolean;
    reason: string;
    project_count: number;
    record_count: number;
  };
  signals: RetrievalSamplesTrendSignal[];
  project_trends: RetrievalSamplesProjectTrend[];
  records: CrossProjectRetrievalSamplesIndexRecord[];
  manifest: Record<string, unknown>;
  content_json: string;
  warnings: string[];
  boundaries: string[];
  next_steps: string[];
}

export interface BundledReleaseReadinessCheck {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_path: string;
  bytes?: number;
  next_step: string;
}

export interface BundledReleasePackageTarget {
  id: string;
  label: string;
  status: "deferred" | string;
  reason: string;
}

export interface BundledReleaseReadinessReport {
  version: string;
  mode: "read_only_packaging_readiness" | string;
  status: "ready" | "attention" | string;
  summary: {
    check_count: number;
    ready_count: number;
    attention_count: number;
    deferred_target_count: number;
    writes_artifacts: boolean;
    external_services_required: boolean;
    plaintext_key_returned: boolean;
    builds_package: boolean;
    bundles_runtime: boolean;
  };
  checks: BundledReleaseReadinessCheck[];
  package_targets: BundledReleasePackageTarget[];
  boundaries: string[];
  next_steps: string[];
  warnings: string[];
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

export interface RightsApprovalCheckpoint {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  next_step: string;
}

export interface RightsApprovalChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  story_slug: string;
  source_kind: SourceKind | string;
  summary: {
    checkpoint_count: number;
    ready_count: number;
    attention_count: number;
    public_publish_enabled: boolean;
    requires_export_confirmation: boolean;
  };
  checkpoints: RightsApprovalCheckpoint[];
  warnings: string[];
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

export interface DeploymentObservabilitySignal {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface DeploymentObservabilityChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  story_slug: string;
  summary: {
    signal_count: number;
    ready_count: number;
    attention_count: number;
    external_services_required: boolean;
    cloud_monitoring_enabled: boolean;
  };
  signals: DeploymentObservabilitySignal[];
  warnings: string[];
  next_steps: string[];
}

export interface AuthBoundaryCheckpoint {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface AuthBoundaryChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    checkpoint_count: number;
    ready_count: number;
    attention_count: number;
    auth_enforced: boolean;
    external_services_required: boolean;
  };
  checkpoints: AuthBoundaryCheckpoint[];
  warnings: string[];
  next_steps: string[];
}

export interface ObjectStorageBoundaryCheck {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface ObjectStorageBoundaryChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    check_count: number;
    ready_count: number;
    attention_count: number;
    adapter_implemented: boolean;
    remote_writes_enabled: boolean;
    external_services_required: boolean;
  };
  checks: ObjectStorageBoundaryCheck[];
  warnings: string[];
  next_steps: string[];
}

export interface QuotaEnforcementBoundaryCheck {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface QuotaEnforcementBoundaryChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    check_count: number;
    ready_count: number;
    attention_count: number;
    enforcement_enabled: boolean;
    hard_limits_enabled: boolean;
    external_billing_required: boolean;
  };
  checks: QuotaEnforcementBoundaryCheck[];
  warnings: string[];
  next_steps: string[];
}

export interface BillingAdapterBoundaryCheck {
  id: string;
  label: string;
  status: "ready" | "attention" | string;
  status_label: string;
  evidence: string;
  source_endpoint: string;
  next_step: string;
}

export interface BillingAdapterBoundaryChecklist {
  version: string;
  mode: string;
  status: "ready" | "attention" | string;
  summary: {
    check_count: number;
    ready_count: number;
    attention_count: number;
    adapter_implemented: boolean;
    billing_writes_enabled: boolean;
    external_billing_required: boolean;
  };
  checks: BillingAdapterBoundaryCheck[];
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

export interface RetrievalProviderConfigurationReport {
  version: string;
  mode: "read_only_retrieval_provider_configuration" | string;
  status: "ready" | "attention" | string;
  summary: {
    embedding_provider: string;
    embedding_configured: boolean;
    vector_store_provider: string;
    vector_store_configured: boolean;
    reranker_provider: string;
    reranker_configured: boolean;
    ready_count: number;
    attention_count: number;
    plaintext_key_returned: boolean;
    writes_artifacts: boolean;
    provider_calls: boolean;
    default_retrieval_changed: boolean;
  };
  providers: {
    embedding: {
      provider: string;
      base_url: string;
      model: string;
      dimension: number;
      batch_size: number;
      configured: boolean;
      masked_key: string;
      route: string;
    };
    vector_store: {
      provider: string;
      uri_configured: boolean;
      token_configured: boolean;
      configured: boolean;
      masked_token: string;
      collection: string;
      route: string;
    };
    reranker: {
      provider: string;
      endpoint: string;
      model: string;
      top_n: number;
      configured: boolean;
      masked_key: string;
      route: string;
    };
  };
  boundaries: string[];
  next_steps: string[];
  warnings: string[];
}

export interface RetrievalProviderConnectivityResult {
  version: string;
  mode: "mock" | "provider" | string;
  status: "ready" | "attention" | string;
  summary: {
    check_count: number;
    available_count: number;
    attention_count: number;
    provider_calls: boolean;
    writes_artifacts: boolean;
    default_retrieval_changed: boolean;
    elapsed_ms: number;
  };
  checks: {
    embedding: Record<string, unknown> & {
      available: boolean;
      model?: string;
      dimension?: number;
      provider_call?: boolean;
    };
    vector_store: Record<string, unknown> & {
      available: boolean;
      provider?: string;
      collection?: string;
      provider_call?: boolean;
    };
    reranker: Record<string, unknown> & {
      available: boolean;
      model?: string;
      result_count?: number;
      provider_call?: boolean;
    };
  };
  boundaries: string[];
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
