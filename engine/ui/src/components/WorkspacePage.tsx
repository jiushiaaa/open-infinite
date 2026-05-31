import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { ApiError, api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import { useAsync } from "../hooks/useAsync";
import { navigate } from "../routing";
import type {
  ImportQualityRisk,
  ProjectWorkspace,
  ProjectWorkspaceAudit,
  ProjectWorkspaceCanonLedger,
  ProjectCreationLoop,
  ProjectCreationLoopAction,
  ProjectCreationLoopCandidate,
  ProjectCreationLoopEvidence,
  ProjectWorkspaceMemory,
  ProjectWorkspaceRetrieval,
  ResumeContinueResponse,
  RunTreeNode,
} from "../api/types";
import { ChapterReader } from "./ChapterReader";
import { RightPanel } from "./RightPanel";
import { WorldlineTree } from "./WorldlineTree";
import { InterventionComposer, type CharOption } from "./InterventionComposer";
import { EmptyState, ErrorState, Loading } from "./common/States";
import "./workspace.css";

export interface Selection {
  runId: string;
  branchId: string;
}

// 从 state_snapshot.characters（id→{name}）提取干预目标下拉选项。
function extractCharacters(snapshot: Record<string, unknown> | null): CharOption[] {
  const raw = snapshot?.characters;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return [];
  return Object.entries(raw as Record<string, { name?: string }>).map(([id, c]) => ({
    id,
    name: c?.name || id,
  }));
}

// 在树里找到第一个「有正文」的分支，作为默认选择。
function firstSelectable(nodes: RunTreeNode[]): Selection | null {
  for (const run of nodes) {
    for (const b of run.branches) {
      if (b.chapter_chars > 0) return { runId: run.run_id, branchId: b.branch_id };
    }
    for (const b of run.branches) {
      const child = firstSelectable(b.child_runs);
      if (child) return child;
    }
  }
  // 退而求其次：第一个分支即便空
  for (const run of nodes) {
    if (run.branches[0]) {
      return { runId: run.run_id, branchId: run.branches[0].branch_id };
    }
  }
  return null;
}

export function WorkspacePage({ slug }: { slug: string }) {
  const tree = useAsync(() => api.getTree(slug), [slug]);
  const project = useAsync(() => api.getProjectWorkspace(slug), [slug]);
  const [sel, setSel] = useState<Selection | null>(null);

  const nodes = useMemo(() => tree.data?.tree ?? [], [tree.data]);
  const firstSelection = useMemo(() => firstSelectable(nodes), [nodes]);

  // 切换故事时重置选择
  useEffect(() => {
    setSel(null);
  }, [slug]);

  const run = useAsync(
    () => (sel ? api.getRun(sel.runId) : Promise.resolve(null)),
    [sel?.runId],
  );
  const branch = useAsync(
    () =>
      sel ? api.getBranch(sel.runId, sel.branchId) : Promise.resolve(null),
    [sel?.runId, sel?.branchId],
  );

  const compilation = run.data?.intervention_compilation ?? null;
  const characters = extractCharacters(branch.data?.state_snapshot ?? null);

  const handleGenerated = (runId: string, branchId: string) => {
    setSel({ runId, branchId });
    tree.reload();
  };

  const handleResumeGenerated = (runId: string, branchId: string) => {
    setSel({ runId, branchId });
    tree.reload();
    project.reload();
  };

  const handleSelectionChanged = () => {
    project.reload();
  };

  return (
    <div className="workspace">
      <aside className="workspace__left">
        {tree.loading && <Loading label="正在绘制世界线树…" />}
        {tree.error && <ErrorState message={tree.error} onRetry={tree.reload} />}
        {!tree.loading && !tree.error && nodes.length === 0 && (
          <EmptyState
            title="尚无世界线"
            hint="这部故事还没有任何 run。先用 CLI 跑一次 intervene。"
          />
        )}
        {!tree.loading && !tree.error && nodes.length > 0 && (
          <WorldlineTree
            slug={slug}
            nodes={nodes}
            selection={sel}
            onSelect={setSel}
          />
        )}
      </aside>

      <section className="workspace__center">
        {!sel && project.loading && <Loading label="正在整理长篇项目…" />}
        {!sel && project.error && (
          <ErrorState message={project.error} onRetry={project.reload} />
        )}
        {!sel && !project.loading && !project.error && project.data && (
          <ProjectWorkspaceOverview
            data={project.data}
            firstSelection={firstSelection}
            onSelectFirst={(next) => setSel(next)}
            onResumeGenerated={handleResumeGenerated}
            onSelectionChanged={handleSelectionChanged}
          />
        )}
        {!sel && !project.loading && !project.error && !project.data && (
          <EmptyState title="项目工作台为空" hint="暂未读到可展示的长篇资料。" />
        )}
        {sel && branch.loading && <Loading />}
        {sel && branch.error && (
          <ErrorState message={branch.error} onRetry={branch.reload} />
        )}
        {sel && !branch.loading && !branch.error && branch.data && (
          <>
            <ChapterReader
              branch={branch.data}
              compilation={compilation}
              onBranchReload={branch.reload}
            />
            <InterventionComposer
              slug={slug}
              characters={characters}
              onGenerated={handleGenerated}
            />
          </>
        )}
      </section>

      <aside className="workspace__right">
        {sel && branch.data && (
          <RightPanel
            storySlug={slug}
            branch={branch.data}
            compilation={compilation}
            compilationLoading={run.loading}
          />
        )}
        {!sel && project.data && <ProjectWorkspaceSidePanel data={project.data} />}
        {!sel && !project.data && (
          <EmptyState title="解释面板" hint="选择世界线后展示状态与解释。" />
        )}
      </aside>
    </div>
  );
}

function ProjectWorkspaceOverview({
  data,
  firstSelection,
  onSelectFirst,
  onResumeGenerated,
  onSelectionChanged,
}: {
  data: ProjectWorkspace;
  firstSelection: Selection | null;
  onSelectFirst: (selection: Selection) => void;
  onResumeGenerated: (runId: string, branchId: string) => void;
  onSelectionChanged: () => void;
}) {
  const risks = data.import_review?.quality_risks ?? [];
  const issueCount = data.audit.summary.issue_count ?? 0;
  const sourceLabel = sourceTypeLabel(data.source.type || data.source_kind);
  const metrics = [
    { label: "章节", value: data.chapter_overview.total_chapters },
    { label: "记忆层", value: data.memory.layer_count },
    { label: "正史", value: data.canon_ledger.entry_count },
    { label: "审计", value: issueCount },
    { label: "检索", value: data.retrieval.hit_count },
  ];

  return (
    <div className="project-workspace">
      <header className="project-workspace__header">
        <div>
          <p className="tiny muted">长篇项目工作台</p>
          <h1>{data.display_name}</h1>
          <p className="project-workspace__meta">
            {sourceLabel} · {data.chapter_overview.total_characters} 字 ·{" "}
            {data.run_count} 条运行记录
          </p>
        </div>
        <div className="project-workspace__actions">
          <button
            type="button"
            className="workspace-btn"
            onClick={() => navigate({ name: "anchor", slug: data.slug })}
          >
            世界锚定
          </button>
          {firstSelection && (
            <button
              type="button"
              className="workspace-btn workspace-btn--primary"
              onClick={() => onSelectFirst(firstSelection)}
            >
              继续阅读
            </button>
          )}
        </div>
      </header>

      <div className="project-workspace__metrics">
        {metrics.map((m) => (
          <div className="project-workspace__metric" key={m.label}>
            <span>{m.label}</span>
            <strong>{m.value}</strong>
          </div>
        ))}
      </div>

      <section className="project-workspace__section">
        <SectionTitle title="导入检查" status={data.import_review?.status ?? "missing"} />
        <RiskStrip risks={risks} warnings={data.import_review?.warnings ?? []} />
        <div className="project-workspace__steps">
          {data.actions.next_steps.map((step) => (
            <span key={step}>{step}</span>
          ))}
        </div>
      </section>

      {data.creation_loop && (
        <CreationLoopPanel
          storySlug={data.slug}
          loop={data.creation_loop}
          onOpen={(candidate) =>
            onSelectFirst({
              runId: candidate.run_id,
              branchId: candidate.branch_id,
            })
          }
          onGenerated={onResumeGenerated}
          onSelectionChanged={onSelectionChanged}
        />
      )}

      <section className="project-workspace__section">
        <SectionTitle title="章节片段" status={`${data.chapter_overview.playable_chapter_limit} 章可先读`} />
        {data.chapter_overview.previews.length === 0 ? (
          <EmptyState title="尚无章节片段" hint="导入报告缺失时会尝试从 source 目录降级生成。" />
        ) : (
          <div className="chapter-preview-list">
            {data.chapter_overview.previews.map((chapter) => (
              <article className="chapter-preview" key={`${chapter.index}-${chapter.title}`}>
                <div className="chapter-preview__head">
                  <strong>第 {chapter.index} 章</strong>
                  <span>{chapter.characters} 字</span>
                </div>
                <h3>{chapter.title || "未命名章节"}</h3>
                <p>{chapter.preview || "暂无片段。"}</p>
              </article>
            ))}
          </div>
        )}
      </section>

      <ProjectArtifactGrid
        memory={data.memory}
        ledger={data.canon_ledger}
        retrieval={data.retrieval}
        audit={data.audit}
      />
    </div>
  );
}

function ProjectWorkspaceSidePanel({ data }: { data: ProjectWorkspace }) {
  return (
    <div className="project-side">
      <h2>项目资产</h2>
      <SideLine label="来源" value={sourceTypeLabel(data.source.type || data.source_kind)} />
      <SideLine label="章节" value={`${data.chapter_overview.total_chapters} 章`} />
      <SideLine label="记忆层" value={`${data.memory.layer_count} 层`} />
      <SideLine label="别名实体" value={`${data.entity_aliases.count} 个`} />
      <SideLine label="正史记录" value={`${data.canon_ledger.entry_count} 条`} />
      <SideLine label="检索命中" value={`${data.retrieval.hit_count} 条`} />
      <SideLine label="审计风险" value={`${data.audit.summary.issue_count ?? 0} 项`} />
      <button
        type="button"
        className="workspace-btn workspace-btn--full"
        onClick={() => navigate({ name: "anchor", slug: data.slug })}
      >
        进入世界锚定
      </button>
    </div>
  );
}

function CreationLoopPanel({
  storySlug,
  loop,
  onOpen,
  onGenerated,
  onSelectionChanged,
}: {
  storySlug: string;
  loop: ProjectCreationLoop;
  onOpen: (candidate: ProjectCreationLoopCandidate) => void;
  onGenerated: (runId: string, branchId: string) => void;
  onSelectionChanged: () => void;
}) {
  const recommended = loop.recommended;
  const selected = loop.selected ?? null;
  const postAudit = loop.post_run_audit ?? null;
  const completion = loop.completion ?? null;
  const closeout = loop.closeout ?? null;
  let loopStatus = loop.status === "ready" ? "可继续" : "待生成";
  if (closeout?.can_close_alpha || completion?.can_mark_alpha_complete) {
    loopStatus = "可收口";
  }
  const [busy, setBusy] = useState(false);
  const [selecting, setSelecting] = useState(false);
  const [quickAction, setQuickAction] = useState<string | null>(null);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [mock, setMock] = useState(true);
  const stoppedRef = useRef(false);

  useEffect(() => {
    let alive = true;
    api
      .getRuntimeSettings()
      .then((s) => alive && setMock(s.default_mock))
      .catch(() => {});
    return () => {
      alive = false;
      stoppedRef.current = true;
    };
  }, []);

  async function resumeContinue(candidate: ProjectCreationLoopCandidate) {
    if (busy) return;
    setBusy(true);
    setError(null);
    setStage("排队中…");
    try {
      const { job_id } = await api.postJobResumeContinue({
        run_id: candidate.run_id,
        branch_id: candidate.branch_id,
        mock,
      });
      const result = await pollJob<ResumeContinueResponse>(
        job_id,
        (p) => setStage(p.stage ? `${p.stage}…` : "续写中…"),
        () => stoppedRef.current,
      );
      if (!result.branch_id) throw new ApiError("续写成功但未返回分支", 0);
      onGenerated(result.run_id, result.branch_id);
    } catch (err) {
      if (err instanceof JobCancelled) return;
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function selectCandidate(candidate: ProjectCreationLoopCandidate) {
    if (busy || selecting) return;
    setSelecting(true);
    setError(null);
    setStage("正在记录选择…");
    try {
      await api.selectWorldline(storySlug, {
        run_id: candidate.run_id,
        branch_id: candidate.branch_id,
        note: "从创作闭环设为下一章起点",
      });
      setStage("已设为下一章起点。");
      onSelectionChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSelecting(false);
    }
  }

  async function runCompletionAction(action: ProjectCreationLoopAction) {
    if (!recommended || busy || selecting || quickAction) return;
    if (action.id === "replay_audit") {
      navigate({ name: "anchor", slug: storySlug });
      return;
    }
    if (action.id === "select_worldline") {
      await selectCandidate(recommended);
      return;
    }
    if (action.id === "run_replay_range") {
      if (!action.payload) {
        setError("缺少范围回放参数。");
        return;
      }
      setQuickAction(action.id);
      setError(null);
      setStage("正在运行范围回放…");
      try {
        await api.runCanonReplayRange(storySlug, action.payload);
        setStage("范围回放已完成。");
        onSelectionChanged();
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setQuickAction(null);
      }
      return;
    }
    if (action.id !== "worldline_judgement") return;
    setQuickAction(action.id);
    setError(null);
    setStage("正在生成世界线评审…");
    try {
      await api.generateWorldlineJudgement(recommended.run_id, recommended.branch_id, {
        story_slug: storySlug,
      });
      setStage("世界线评审已生成。");
      onSelectionChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setQuickAction(null);
    }
  }

  return (
    <section className="project-workspace__section creation-loop">
      <SectionTitle
        title="创作闭环"
        status={loopStatus}
      />
      {completion && (
        <div className={`creation-loop__completion is-${completion.status}`}>
          <div>
            <p className="tiny muted">闭环完成度</p>
            <strong>
              {completion.done_count}/{completion.total_count}
            </strong>
            <p>{completion.summary}</p>
          </div>
          {completion.blocking_labels.length > 0 && (
            <span>
              待处理：{completion.blocking_labels.slice(0, 3).join("、")}
            </span>
          )}
          {completion.actions.length > 0 && (
            <div className="creation-loop__completion-actions">
              {completion.actions.slice(0, 3).map((action) => (
                <button
                  type="button"
                  className="workspace-btn"
                  key={action.id}
                  onClick={() => runCompletionAction(action)}
                  disabled={busy || selecting || quickAction !== null}
                  title={action.detail}
                >
                  {quickAction === action.id ? "处理中…" : action.label}
                </button>
              ))}
            </div>
          )}
          {completion.evidence.length > 0 && (
            <div className="creation-loop__evidence">
              <p className="tiny muted">判定依据</p>
              {completion.evidence.slice(0, 4).map((item) => (
                <span key={item.id} title={item.ref}>
                  {item.label}：{evidenceSourceLabel(item)}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
      {closeout && (
        <div className={`creation-loop__closeout is-${closeout.status}`}>
          <div>
            <p className="tiny muted">Alpha 收口</p>
            <strong>{closeout.can_close_alpha ? "可收口" : "待补齐"}</strong>
            <p>{closeout.summary}</p>
          </div>
          <span>
            {closeout.ready_count}/{closeout.required_count}
            {closeout.remaining_blockers.length > 0
              ? ` · 阻塞：${closeout.remaining_blockers.slice(0, 3).join("、")}`
              : " · 无阻塞"}
          </span>
          <p className="creation-loop__closeout-next">{closeout.next_step}</p>
        </div>
      )}
      {recommended ? (
        <div className="creation-loop__focus">
          <div>
            <p className="tiny muted">推荐继续世界线</p>
            <h3>{recommended.branch_label}</h3>
            <p>
              {recommended.recommendation}
              {typeof recommended.overall_score === "number"
                ? ` · 评审 ${(recommended.overall_score * 100).toFixed(0)}`
                : ""}
              {recommended.has_causal_diff ? " · 已有时空 Diff" : ""}
              {recommended.state_overlay_applied ? " · 已应用状态覆盖" : ""}
            </p>
            {recommended.continue_hint && (
              <div className="creation-loop__command">
                <span>续写入口</span>
                <code>{recommended.continue_hint}</code>
              </div>
            )}
            {selected && (
              <div className="creation-loop__selected">
                <span>已选起点</span>
                <strong>{selected.branch_label}</strong>
              </div>
            )}
          </div>
          <div className="creation-loop__actions">
            <button
              type="button"
              className="workspace-btn"
              onClick={() => onOpen(recommended)}
              disabled={busy}
            >
              打开世界线
            </button>
            <button
              type="button"
              className="workspace-btn"
              onClick={() => selectCandidate(recommended)}
              disabled={busy || selecting || recommended.is_selected}
            >
              {recommended.is_selected ? "已设为起点" : selecting ? "记录中…" : "设为起点"}
            </button>
            <button
              type="button"
              className="workspace-btn workspace-btn--primary"
              onClick={() => resumeContinue(recommended)}
              disabled={busy || selecting}
            >
              {busy ? "正在续写…" : "生成下一章"}
            </button>
          </div>
        </div>
      ) : (
        <EmptyState
          title="尚无候选世界线"
          hint="先从项目工作台发起基线或干预，生成可阅读分支。"
        />
      )}

      {(stage || error) && (
        <div className={`creation-loop__status ${error ? "is-error" : ""}`}>
          {error || stage}
        </div>
      )}

      {postAudit && (
        <div className={`creation-loop__audit is-${postAudit.status}`}>
          <div>
            <p className="tiny muted">选择后审计</p>
            <strong>{postAudit.selected_label || "尚未选择世界线"}</strong>
            <p>{postAudit.summary}</p>
          </div>
          <div className="creation-loop__audit-metrics">
            <span>静态风险 {postAudit.static_issue_count} 项</span>
            <span>{postAudit.has_range_replay ? "已跑范围回放" : "未跑范围回放"}</span>
            <span>{riskLevelLabel(postAudit.risk_level)}</span>
          </div>
          {postAudit.missing_entities.length > 0 && (
            <p className="tiny muted">
              缺失实体：{postAudit.missing_entities.slice(0, 4).join("、")}
            </p>
          )}
          {postAudit.next_actions.length > 0 && (
            <div className="creation-loop__audit-actions">
              {postAudit.next_actions.slice(0, 2).map((action) => (
                <span key={action}>{action}</span>
              ))}
            </div>
          )}
          <button
            type="button"
            className="workspace-btn"
            onClick={() => navigate({ name: "anchor", slug: storySlug })}
          >
            查看回放与审计
          </button>
        </div>
      )}

      <div className="creation-loop__checklist">
        {loop.checklist.map((item) => (
          <div
            className={`creation-loop__step is-${item.status}`}
            key={item.id}
          >
            <strong>{item.label}</strong>
            <span>{stepStatusLabel(item.status)}</span>
            <p>{item.detail}</p>
          </div>
        ))}
      </div>

      {loop.next_steps.length > 0 && (
        <div className="project-workspace__steps creation-loop__next">
          {loop.next_steps.map((step) => (
            <span key={step}>{step}</span>
          ))}
        </div>
      )}

      {loop.candidates.length > 1 && (
        <ul className="creation-loop__candidates">
          {loop.candidates.slice(0, 3).map((candidate) => (
            <li key={`${candidate.run_id}-${candidate.branch_id}`}>
              <span>{candidate.branch_label}</span>
              <strong>
                {candidate.recommendation}
                {typeof candidate.overall_score === "number"
                  ? ` · ${(candidate.overall_score * 100).toFixed(0)}`
                  : ""}
              </strong>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function ProjectArtifactGrid({
  memory,
  ledger,
  retrieval,
  audit,
}: {
  memory: ProjectWorkspaceMemory;
  ledger: ProjectWorkspaceCanonLedger;
  retrieval: ProjectWorkspaceRetrieval;
  audit: ProjectWorkspaceAudit;
}) {
  return (
    <section className="project-workspace__grid">
      <ArtifactBlock title="分层记忆" status={memory.status}>
        {memory.layers.length === 0 ? (
          <p className="muted tiny">{firstWarning(memory.warnings, "暂无记忆层。")}</p>
        ) : (
          <ul className="asset-list">
            {memory.layers.slice(0, 8).map((layer) => (
              <li key={layer.name}>
                <span>{memoryLayerLabel(layer.name)}</span>
                <strong>{layer.count}</strong>
              </li>
            ))}
          </ul>
        )}
      </ArtifactBlock>

      <ArtifactBlock title="正史账本" status={ledger.status}>
        {ledger.samples.length === 0 ? (
          <p className="muted tiny">{firstWarning(ledger.warnings, "暂无正史样例。")}</p>
        ) : (
          <ul className="sample-list">
            {ledger.samples.slice(0, 4).map((sample) => (
              <li key={sample.id}>
                <strong>{canonTypeLabel(sample.type)}</strong>
                <span>{sample.statement}</span>
              </li>
            ))}
          </ul>
        )}
      </ArtifactBlock>

      <ArtifactBlock title="检索命中" status={retrieval.status}>
        {retrieval.samples.length === 0 ? (
          <p className="muted tiny">{firstWarning(retrieval.warnings, "暂无检索命中。")}</p>
        ) : (
          <ul className="sample-list">
            {retrieval.samples.slice(0, 4).map((hit) => (
              <li key={`${hit.run_id}-${hit.branch_id}-${hit.source_ref}`}>
                <strong>{hit.branch_id}</strong>
                <span>{hit.preview || hit.source_ref || "未记录片段"}</span>
              </li>
            ))}
          </ul>
        )}
      </ArtifactBlock>

      <ArtifactBlock title="一致性审计" status={audit.status}>
        {audit.issues.length === 0 ? (
          <p className="muted tiny">
            {firstWarning(audit.warnings, audit.repair_suggestions[0] || "暂无审计风险。")}
          </p>
        ) : (
          <ul className="sample-list">
            {audit.issues.slice(0, 4).map((issue) => (
              <li key={`${issue.category}-${issue.kind}-${issue.detail}`}>
                <strong>{severityLabel(issue.severity)}</strong>
                <span>{issue.detail}</span>
              </li>
            ))}
          </ul>
        )}
      </ArtifactBlock>
    </section>
  );
}

function ArtifactBlock({
  title,
  status,
  children,
}: {
  title: string;
  status: string;
  children: ReactNode;
}) {
  return (
    <article className="artifact-block">
      <SectionTitle title={title} status={statusLabel(status)} />
      {children}
    </article>
  );
}

function SectionTitle({ title, status }: { title: string; status: string }) {
  return (
    <div className="project-workspace__section-title">
      <h2>{title}</h2>
      <span>{status}</span>
    </div>
  );
}

function RiskStrip({
  risks,
  warnings,
}: {
  risks: ImportQualityRisk[];
  warnings: string[];
}) {
  const items = risks.length > 0 ? risks.map((r) => r.message) : warnings;
  if (items.length === 0) {
    return <p className="project-workspace__ok">未发现导入级质量风险。</p>;
  }
  return (
    <div className="risk-strip">
      {items.slice(0, 4).map((item) => (
        <span key={item}>{item}</span>
      ))}
    </div>
  );
}

function SideLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="project-side__line">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function sourceTypeLabel(value: string): string {
  const map: Record<string, string> = {
    manual: "手动章节",
    txt: "TXT",
    md: "Markdown",
    zip: "ZIP",
    epub: "EPUB",
    imported: "导入项目",
    builtin: "内置样例",
    unknown: "未知来源",
  };
  return map[value] ?? value;
}

function statusLabel(value: string): string {
  const map: Record<string, string> = {
    ready: "已就绪",
    missing: "未生成",
    damaged: "需修复",
  };
  return map[value] ?? value;
}

function stepStatusLabel(value: string): string {
  const map: Record<string, string> = {
    done: "已完成",
    todo: "待处理",
    warn: "需核对",
  };
  return map[value] ?? value;
}

function evidenceSourceLabel(item: ProjectCreationLoopEvidence): string {
  const map: Record<string, string> = {
    artifact: "已有产物",
    api: "可执行接口",
    route: "可查看页面",
    state: "当前状态",
  };
  return map[item.source] ?? "当前依据";
}

function memoryLayerLabel(value: string): string {
  const map: Record<string, string> = {
    contract: "设定",
    volumes: "卷记忆",
    chapters: "章记忆",
    character_states: "角色状态",
    timeline: "时间线",
    plot_threads: "伏笔",
    propagation_debts: "传播债",
    canon_ledger: "正史",
    entity_aliases: "实体别名",
    consistency_report: "审计",
  };
  return map[value] ?? value;
}

function canonTypeLabel(value: string): string {
  const map: Record<string, string> = {
    event: "事件",
    state: "状态",
    relationship: "关系",
    foreshadowing: "伏笔",
  };
  return map[value] ?? value;
}

function severityLabel(value: string): string {
  const map: Record<string, string> = {
    high: "高",
    medium: "中",
    low: "低",
    info: "记",
  };
  return map[value] ?? (value || "记");
}

function riskLevelLabel(value: string): string {
  const map: Record<string, string> = {
    high: "高风险",
    medium: "中风险",
    low: "低风险",
    unknown: "风险未知",
  };
  return map[value] ?? (value || "风险未知");
}

function firstWarning(warnings: string[], fallback: string): string {
  return warnings[0] || fallback;
}
