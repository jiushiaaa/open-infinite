import { useEffect, useMemo, useRef, useState, type FormEvent, type ReactNode } from "react";
import { ApiError, api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import { useAsync } from "../hooks/useAsync";
import { navigate } from "../routing";
import type {
  ImportQualityRisk,
  CardsWorkspaceCard,
  CardsWorkspaceReport,
  ProjectWorkspace,
  ProjectWorkspaceAudit,
  ProjectWorkspaceCanonLedger,
  RuntimePreflightReport,
  VectorRetrievalReadinessReport,
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
  CanonReplayRangeRequest,
  ProjectCreationLoop,
  ProjectCreationLoopAction,
  ProjectCreationLoopCandidate,
  ProjectCreationLoopEvidence,
  ProjectCreationLoopActionRequirement,
  MasterSettingPatch,
  EmbeddingEvaluationSamplesReport,
  EmbeddingMockEvaluationReport,
  RetrievalSampleMigrationPackReport,
  RetrievalSampleReplayReport,
  RetrievalSampleExportPackReport,
  RetrievalFailureSampleAppendRequest,
  ProjectAuditLog,
  ProjectAuditLogEvent,
  ProjectMasterSettingWorkspace,
  ProjectWorkspaceMemory,
  ProjectWorkspaceRetrieval,
  RightsApprovalChecklist,
  ResumeContinueResponse,
  RunTreeNode,
  WorldlineJudgementRequest,
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

      <RuntimePreflightPanel storySlug={data.slug} />

      <VectorRetrievalReadinessPanel storySlug={data.slug} />

      <GraphMemoryTriggerEvidencePanel storySlug={data.slug} />

      <GraphMemorySpikeDesignPackPanel storySlug={data.slug} />

      <GraphMemoryShadowComparePackPanel storySlug={data.slug} />

      <GraphMemoryShadowCaseMatrixPanel storySlug={data.slug} />

      <GraphMemoryProviderBoundaryMatrixPanel storySlug={data.slug} />

      <GraphMemoryOfflineShadowReplayPlanPanel storySlug={data.slug} />

      <GraphMemoryOfflineShadowReplayReportPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeFixturePackPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeReadinessGatePanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeRunbookPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeDryRunResultTemplatePanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeMockResultReportPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeReviewGatePanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeManualApprovalPackPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeManualApprovalEvidenceChecklistPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInEvidenceSnapshotPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInNoGoMatrixPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInOperatorChecklistPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInReviewPacketPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInDecisionLedgerPreviewPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInFinalReadinessSummaryPanel storySlug={data.slug} />

      <GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftPanel storySlug={data.slug} />

      <EmbeddingEvaluationSamplesPanel storySlug={data.slug} />

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

      <MasterSettingPanel
        storySlug={data.slug}
        master={data.master_setting_workspace}
        onSaved={onSelectionChanged}
      />

      <CardsWorkspacePanel storySlug={data.slug} />

      <ProjectAuditLogPanel storySlug={data.slug} />

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

function ProjectAuditLogPanel({ storySlug }: { storySlug: string }) {
  const audit = useAsync(() => api.getProjectAuditLog(storySlug), [storySlug]);
  const rights = useAsync(() => api.getRightsApprovalChecklist(storySlug), [storySlug]);
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [exportErr, setExportErr] = useState<string | null>(null);
  const report = audit.data;
  const events = report?.events ?? [];
  const warnings = report?.warnings ?? [];

  function downloadMarkdown(payload: {
    filename: string;
    content_type: string;
    content_md: string;
    share_guard?: {
      requires_rights_confirmation?: boolean;
      notice?: string;
      warnings?: string[];
    };
  }) {
    if (payload.share_guard?.requires_rights_confirmation) {
      const confirmed = window.confirm(
        [
          payload.share_guard.notice || "请确认审计日志的分享边界。",
          ...(payload.share_guard.warnings ?? []),
        ].join("\n"),
      );
      if (!confirmed) {
        setExportMsg("已取消导出，未生成下载文件。");
        return false;
      }
    }
    const blob = new Blob([payload.content_md], {
      type: payload.content_type || "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = payload.filename || `${storySlug}-audit-log.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return true;
  }

  async function handleExport() {
    setExporting(true);
    setExportErr(null);
    setExportMsg(null);
    try {
      const payload = await api.getProjectAuditLogExport(storySlug);
      if (downloadMarkdown(payload)) {
        setExportMsg(
          `审计日志已生成下载文件，共 ${payload.metadata.event_count} 条事件。`,
        );
      }
    } catch (err) {
      setExportErr(err instanceof Error ? err.message : "导出审计日志失败。");
    } finally {
      setExporting(false);
    }
  }

  return (
    <section className="project-workspace__section audit-log">
      <SectionTitle
        title="项目审计日志"
        status={
          audit.loading
            ? "读取中"
            : report
              ? `${report.summary.event_count} 条`
              : "未读取"
        }
      />
      {audit.loading && <Loading label="正在读取审计时间线…" />}
      {audit.error && <ErrorState message={audit.error} onRetry={audit.reload} />}
      {!audit.loading && !audit.error && report && (
        <>
          <RightsApprovalPanel
            data={rights.data}
            loading={rights.loading}
            error={rights.error}
            onRetry={rights.reload}
          />
          <div className="audit-log__toolbar">
            <div>
              <p className="tiny muted">本地项目时间线</p>
              <strong>{auditStatusText(report)}</strong>
              <span>
                {report.summary.source_count} 个来源产物 ·{" "}
                {Object.keys(report.summary.action_counts).length} 类动作
              </span>
            </div>
            <button
              type="button"
              className="workspace-btn"
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? "导出中…" : "导出 Markdown"}
            </button>
          </div>
          {warnings.length > 0 && (
            <div className="risk-strip audit-log__warnings">
              {warnings.slice(0, 3).map((warning) => (
                <span key={`${warning.code}-${warning.message}`}>
                  {warning.message || warning.code}
                </span>
              ))}
            </div>
          )}
          {exportMsg && <p className="project-workspace__ok">{exportMsg}</p>}
          {exportErr && <p className="master-setting__error">{exportErr}</p>}
          {events.length === 0 ? (
            <EmptyState title="暂无审计事件" hint="关键写操作完成后会追加到本地审计日志。" />
          ) : (
            <ul className="audit-log__list">
              {events.slice(-6).reverse().map((event) => (
                <AuditLogEventItem event={event} key={event.event_id} />
              ))}
            </ul>
          )}
          {report.next_steps.length > 0 && (
            <div className="project-workspace__steps audit-log__steps">
              {report.next_steps.slice(0, 3).map((step) => (
                <span key={step}>{step}</span>
              ))}
            </div>
          )}
        </>
      )}
    </section>
  );
}

function RuntimePreflightPanel({ storySlug }: { storySlug: string }) {
  const preflight = useAsync(() => api.getRuntimePreflight(storySlug), [storySlug]);
  const report = preflight.data;
  const statusText = preflight.loading
    ? "读取中"
    : report
      ? `${report.summary.ready_count} / ${report.summary.checkpoint_count} 已具备`
      : "未读取";

  return (
    <section className="project-workspace__section runtime-preflight">
      <SectionTitle title="运行前体检" status={statusText} />
      {preflight.loading && <Loading label="正在核对运行前证据…" />}
      {preflight.error && (
        <ErrorState message={preflight.error} onRetry={preflight.reload} />
      )}
      {!preflight.loading && !preflight.error && report && (
        <RuntimePreflightReportView report={report} />
      )}
    </section>
  );
}

function RuntimePreflightReportView({ report }: { report: RuntimePreflightReport }) {
  const blocked = report.checkpoints.filter((item) => item.status === "blocked");
  const attention = report.checkpoints.filter((item) => item.status === "attention");
  const visible = [...blocked, ...attention, ...report.checkpoints].filter(
    (item, index, arr) => arr.findIndex((other) => other.id === item.id) === index,
  );

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>已具备</span>
          <strong>{report.summary.ready_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>需留意</span>
          <strong>{report.summary.attention_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>需修复</span>
          <strong>{report.summary.blocked_count}</strong>
        </div>
      </div>

      {report.warnings.length === 0 ? (
        <p className="project-workspace__ok">运行前证据已聚合，未发现阻断项。</p>
      ) : (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      <div className="audit-log__rights-list">
        {visible.slice(0, 11).map((checkpoint) => (
          <span key={checkpoint.id}>
            {checkpoint.label}：{checkpoint.status_label} · {checkpoint.evidence}
          </span>
        ))}
      </div>

      {report.next_steps.length > 0 && (
        <div className="project-workspace__steps">
          {report.next_steps.slice(0, 3).map((step) => (
            <span key={step}>{step}</span>
          ))}
        </div>
      )}
    </>
  );
}

function VectorRetrievalReadinessPanel({ storySlug }: { storySlug: string }) {
  const readiness = useAsync(
    () => api.getVectorRetrievalReadiness(storySlug),
    [storySlug],
  );
  const report = readiness.data;
  const statusText = readiness.loading
    ? "读取中"
    : report
      ? vectorReadinessStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="向量检索就绪" status={statusText} />
      {readiness.loading && <Loading label="正在评估检索召回压力…" />}
      {readiness.error && (
        <ErrorState message={readiness.error} onRetry={readiness.reload} />
      )}
      {!readiness.loading && !readiness.error && report && (
        <VectorRetrievalReadinessView report={report} />
      )}
    </section>
  );
}

function VectorRetrievalReadinessView({
  report,
}: {
  report: VectorRetrievalReadinessReport;
}) {
  const attentionSignals = report.signals.filter(
    (signal) => signal.status !== "ready",
  );
  const visibleSignals = [...attentionSignals, ...report.signals].filter(
    (signal, index, arr) => arr.findIndex((item) => item.id === signal.id) === index,
  );

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>章节</span>
          <strong>{report.summary.chapter_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>语料</span>
          <strong>{report.summary.corpus_item_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>探针命中</span>
          <strong>{Math.round(report.summary.retrieval_probe_hit_rate * 100)}%</strong>
        </div>
        <div className="master-setting__metric">
          <span>失败样本</span>
          <strong>{report.summary.saved_failure_sample_count}</strong>
        </div>
      </div>

      {report.warnings.length > 0 ? (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : (
        <p className="project-workspace__ok">当前评估未调用外部服务，也未生成向量索引。</p>
      )}

      <div className="audit-log__rights-list">
        {visibleSignals.slice(0, 5).map((signal) => (
          <span key={signal.id}>
            {signal.label}：{signal.evidence} · {signal.next_step}
          </span>
        ))}
      </div>

      <div className="audit-log__rights-list">
        {report.candidate_layers.slice(0, 4).map((layer) => (
          <span key={layer.id}>
            {layer.label}：{vectorLayerReadinessLabel(layer.readiness)} · {layer.reason}
          </span>
        ))}
      </div>

      {report.failure_samples.length > 0 && (
        <ul className="sample-list">
          {report.failure_samples.slice(0, 3).map((sample) => (
            <li key={sample.query}>
              <strong>召回失败</strong>
              <span>{sample.query}：{sample.reason}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="project-workspace__steps">
        {report.next_steps.slice(0, 3).map((step) => (
          <span key={step}>{step}</span>
        ))}
      </div>
      <p className="master-setting__note">{report.boundaries[1]}</p>
    </>
  );
}

function GraphMemoryTriggerEvidencePanel({ storySlug }: { storySlug: string }) {
  const evidence = useAsync(
    () => api.getGraphMemoryTriggerEvidence(storySlug),
    [storySlug],
  );
  const report = evidence.data;
  const statusText = evidence.loading
    ? "读取中"
    : report
      ? graphTriggerStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="GraphRAG / Zep 触发证据" status={statusText} />
      {evidence.loading && <Loading label="正在整理重型记忆触发证据…" />}
      {evidence.error && <ErrorState message={evidence.error} onRetry={evidence.reload} />}
      {!evidence.loading && !evidence.error && report && (
        <GraphMemoryTriggerEvidenceView report={report} />
      )}
    </section>
  );
}

function GraphMemoryTriggerEvidenceView({
  report,
}: {
  report: GraphMemoryTriggerEvidenceReport;
}) {
  const attentionSignals = report.signals.filter(
    (signal) => signal.status !== "ready",
  );
  const visibleSignals = [...attentionSignals, ...report.signals].filter(
    (signal, index, arr) => arr.findIndex((item) => item.id === signal.id) === index,
  );

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>Graph 状态</span>
          <strong>{graphTriggerStatusLabel(report.summary.graph_memory_status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>趋势样本</span>
          <strong>{report.summary.trend_record_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>词面缺口</span>
          <strong>{report.summary.trend_lexical_gap_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>关系/状态</span>
          <strong>
            {report.summary.relation_signal_count + report.summary.state_signal_count}
          </strong>
        </div>
      </div>

      {report.warnings.length > 0 ? (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : (
        <p className="project-workspace__ok">这里只输出触发证据，不接外部记忆服务。</p>
      )}

      <div className="audit-log__rights-list">
        {visibleSignals.slice(0, 5).map((signal) => (
          <span key={signal.id}>
            {signal.label}：{graphTriggerStatusLabel(signal.status)} · {signal.detail}
          </span>
        ))}
      </div>

      <div className="audit-log__rights-list">
        {report.candidate_layers.map((layer) => (
          <span key={layer.id}>
            {layer.label}：{graphCandidateStatusLabel(layer.status)} · {layer.reason}
          </span>
        ))}
      </div>

      {report.records.length > 0 && (
        <ul className="sample-list">
          {report.records.slice(0, 3).map((record) => (
            <li key={`${record.story_slug}:${record.eval_id}`}>
              <strong>{record.display_name}</strong>
              <span>{record.eval_id}：{record.expected_item_id || record.replay_status}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="project-workspace__steps">
        {report.next_steps.slice(0, 3).map((step) => (
          <span key={step}>{step}</span>
        ))}
      </div>
      <p className="master-setting__note">{report.boundaries[2]}</p>
    </>
  );
}

function GraphMemorySpikeDesignPackPanel({ storySlug }: { storySlug: string }) {
  const designPack = useAsync(
    () => api.getGraphMemorySpikeDesignPack(storySlug),
    [storySlug],
  );
  const report = designPack.data;
  const statusText = designPack.loading
    ? "读取中"
    : report
      ? graphDesignStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆设计包" status={statusText} />
      {designPack.loading && <Loading label="正在整理 Graph 记忆 spike 设计包…" />}
      {designPack.error && <ErrorState message={designPack.error} onRetry={designPack.reload} />}
      {!designPack.loading && !designPack.error && report && (
        <GraphMemorySpikeDesignPackView report={report} />
      )}
    </section>
  );
}

function GraphMemorySpikeDesignPackView({
  report,
}: {
  report: GraphMemorySpikeDesignPackReport;
}) {
  const candidateLayers = report.layer_plans.filter((layer) => layer.status !== "deferred");
  const visibleLayers = candidateLayers.length > 0 ? candidateLayers : report.layer_plans;

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>设计状态</span>
          <strong>{graphDesignGateStatusLabel(report.design_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选层</span>
          <strong>{report.summary.candidate_layer_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>试验输入</span>
          <strong>{report.summary.experiment_input_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>验收门槛</span>
          <strong>{report.summary.acceptance_gate_count}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.design_gate.reason}</p>

      <div className="audit-log__rights-list">
        {visibleLayers.slice(0, 3).map((layer) => (
          <span key={layer.id}>
            {layer.label}：{graphCandidateStatusLabel(layer.status)} · {layer.design_focus}
          </span>
        ))}
      </div>

      <ul className="sample-list">
        {report.experiment_inputs.slice(0, 4).map((input) => (
          <li key={input.id}>
            <strong>{input.label}</strong>
            <span>{graphDesignInputStatusLabel(input.status)}：{input.detail}</span>
          </li>
        ))}
      </ul>

      <div className="audit-log__rights-list">
        {report.acceptance_gates.slice(0, 5).map((gate) => (
          <span key={gate.id}>
            {gate.label}：{graphDesignInputStatusLabel(gate.status)} · {gate.target}
          </span>
        ))}
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">{report.boundaries[1]}</p>
    </>
  );
}

function GraphMemoryShadowComparePackPanel({ storySlug }: { storySlug: string }) {
  const shadowPack = useAsync(
    () => api.getGraphMemoryShadowComparePack(storySlug),
    [storySlug],
  );
  const report = shadowPack.data;
  const statusText = shadowPack.loading
    ? "读取中"
    : report
      ? graphShadowStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Shadow 对照" status={statusText} />
      {shadowPack.loading && <Loading label="正在整理 Graph 记忆 shadow 对照…" />}
      {shadowPack.error && <ErrorState message={shadowPack.error} onRetry={shadowPack.reload} />}
      {!shadowPack.loading && !shadowPack.error && report && (
        <GraphMemoryShadowComparePackView report={report} />
      )}
    </section>
  );
}

function GraphMemoryShadowComparePackView({
  report,
}: {
  report: GraphMemoryShadowComparePackReport;
}) {
  const activeComparisons = report.comparisons.filter(
    (item) => item.status !== "deferred",
  );
  const visibleComparisons =
    activeComparisons.length > 0 ? activeComparisons : report.comparisons;

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>对照状态</span>
          <strong>{graphShadowGateStatusLabel(report.shadow_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选层</span>
          <strong>{report.summary.candidate_layer_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>样本</span>
          <strong>{report.summary.sample_case_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>最高收益</span>
          <strong>{report.summary.best_projected_gain_score}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.shadow_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      <div className="audit-log__rights-list">
        {visibleComparisons.slice(0, 3).map((item) => (
          <span key={item.id}>
            {item.label}：{graphCandidateStatusLabel(item.status)} ·
            {" "}{graphShadowDecisionLabel(item.decision)} · 收益 {item.projected_gain_score}
          </span>
        ))}
      </div>

      {report.sample_cases.length > 0 && (
        <ul className="sample-list">
          {report.sample_cases.slice(0, 3).map((sample) => (
            <li key={sample.eval_id}>
              <strong>{sample.display_name}</strong>
              <span>{sample.query || sample.eval_id}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="audit-log__rights-list">
        {report.acceptance_results.slice(0, 5).map((result) => (
          <span key={result.gate_id}>
            {result.label}：{graphShadowResultLabel(result.result_status)} · {result.evidence}
          </span>
        ))}
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryShadowCaseMatrixPanel({ storySlug }: { storySlug: string }) {
  const matrixState = useAsync(
    () => api.getGraphMemoryShadowCaseMatrix(storySlug),
    [storySlug],
  );
  const report = matrixState.data;
  const statusText = matrixState.loading
    ? "读取中"
    : report
      ? graphCaseStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Case 矩阵" status={statusText} />
      {matrixState.loading && <Loading label="正在展开 Graph 记忆 case 矩阵…" />}
      {matrixState.error && <ErrorState message={matrixState.error} onRetry={matrixState.reload} />}
      {!matrixState.loading && !matrixState.error && report && (
        <GraphMemoryShadowCaseMatrixView report={report} />
      )}
    </section>
  );
}

function GraphMemoryShadowCaseMatrixView({
  report,
}: {
  report: GraphMemoryShadowCaseMatrixReport;
}) {
  const activeCells = report.cells.filter((cell) => cell.status !== "deferred");
  const visibleCells = activeCells.length > 0 ? activeCells : report.cells;

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>矩阵状态</span>
          <strong>{graphCaseGateStatusLabel(report.case_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>样本</span>
          <strong>{report.summary.case_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选格</span>
          <strong>{report.summary.candidate_cell_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>证据格</span>
          <strong>{report.summary.evidence_ready_cell_count}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.case_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      <div className="audit-log__rights-list">
        {visibleCells.slice(0, 5).map((cell) => (
          <span key={`${cell.case_id}-${cell.layer_id}`}>
            {cell.layer_label}：{graphCandidateStatusLabel(cell.status)} ·{" "}
            {graphCaseEvidenceStatusLabel(cell.evidence_status)} · {cell.shadow_question}
          </span>
        ))}
      </div>

      {report.cases.length > 0 && (
        <ul className="sample-list">
          {report.cases.slice(0, 3).map((item) => (
            <li key={item.eval_id}>
              <strong>{item.display_name || item.eval_id}</strong>
              <span>{item.query || item.baseline_status}</span>
            </li>
          ))}
        </ul>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderBoundaryMatrixPanel({ storySlug }: { storySlug: string }) {
  const boundaryState = useAsync(
    () => api.getGraphMemoryProviderBoundaryMatrix(storySlug),
    [storySlug],
  );
  const report = boundaryState.data;
  const statusText = boundaryState.loading
    ? "读取中"
    : report
      ? graphProviderBoundaryStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider 边界" status={statusText} />
      {boundaryState.loading && <Loading label="正在整理 Graph 记忆 provider 边界…" />}
      {boundaryState.error && (
        <ErrorState message={boundaryState.error} onRetry={boundaryState.reload} />
      )}
      {!boundaryState.loading && !boundaryState.error && report && (
        <GraphMemoryProviderBoundaryMatrixView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderBoundaryMatrixView({
  report,
}: {
  report: GraphMemoryProviderBoundaryMatrixReport;
}) {
  const activeProviders = report.providers.filter((item) => item.status !== "deferred");
  const visibleProviders = activeProviders.length > 0 ? activeProviders : report.providers;
  const highRiskCells = report.boundary_cells.filter(
    (cell) => cell.status !== "deferred" && cell.risk_level === "high",
  );
  const visibleCells = report.boundary_cells.filter((cell) => cell.status !== "deferred");

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>边界状态</span>
          <strong>{graphProviderBoundaryGateLabel(report.boundary_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选服务</span>
          <strong>{report.summary.candidate_provider_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>边界格</span>
          <strong>{report.summary.requires_opt_in_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>高风险</span>
          <strong>{highRiskCells.length}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.boundary_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      <div className="audit-log__rights-list">
        {visibleProviders.slice(0, 3).map((provider) => (
          <span key={provider.id}>
            {provider.service_target}：{graphCandidateStatusLabel(provider.status)} ·{" "}
            {provider.opt_in_required ? "必须显式开启" : "只读观察"} · {provider.recommended_for}
          </span>
        ))}
      </div>

      {visibleCells.length > 0 && (
        <div className="audit-log__rights-list">
          {visibleCells.slice(0, 5).map((cell) => (
            <span key={`${cell.provider_id}-${cell.category_id}`}>
              {cell.provider_label} / {cell.category_label}：
              {graphProviderBoundaryCellLabel(cell.status)} · {cell.requirement}
            </span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryOfflineShadowReplayPlanPanel({ storySlug }: { storySlug: string }) {
  const replayPlanState = useAsync(
    () => api.getGraphMemoryOfflineShadowReplayPlan(storySlug),
    [storySlug],
  );
  const report = replayPlanState.data;
  const statusText = replayPlanState.loading
    ? "读取中"
    : report
      ? graphOfflineReplayStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆离线 Replay 计划" status={statusText} />
      {replayPlanState.loading && <Loading label="正在整理 Graph 记忆离线 replay 计划…" />}
      {replayPlanState.error && (
        <ErrorState message={replayPlanState.error} onRetry={replayPlanState.reload} />
      )}
      {!replayPlanState.loading && !replayPlanState.error && report && (
        <GraphMemoryOfflineShadowReplayPlanView report={report} />
      )}
    </section>
  );
}

function GraphMemoryOfflineShadowReplayPlanView({
  report,
}: {
  report: GraphMemoryOfflineShadowReplayPlanReport;
}) {
  const visibleCases = report.replay_cases.filter((item) => item.status !== "deferred");

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>Replay 状态</span>
          <strong>{graphOfflineReplayGateLabel(report.replay_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>计划服务</span>
          <strong>{report.summary.provider_plan_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>复跑样本</span>
          <strong>{report.summary.replay_case_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>人工复核</span>
          <strong>{report.summary.manual_review_required_count}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.replay_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {report.provider_plans.length > 0 && (
        <div className="audit-log__rights-list">
          {report.provider_plans.slice(0, 3).map((plan) => (
            <span key={plan.provider_id}>
              {plan.service_target}：{graphOfflineReplayItemLabel(plan.status)} ·{" "}
              {plan.replay_scope} · {plan.acceptance_summary}
            </span>
          ))}
        </div>
      )}

      {visibleCases.length > 0 && (
        <ul className="sample-list">
          {visibleCases.slice(0, 4).map((item) => (
            <li key={item.id}>
              <strong>{item.provider_label} / {item.display_name || item.eval_id}</strong>
              <span>{item.query || item.expected_delta}</span>
            </li>
          ))}
        </ul>
      )}

      {report.replay_steps.length > 0 && (
        <div className="project-workspace__steps">
          {report.replay_steps.slice(0, 5).map((step) => (
            <span key={step.id}>
              {step.label}：{step.description}
            </span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryOfflineShadowReplayReportPanel({ storySlug }: { storySlug: string }) {
  const replayReportState = useAsync(
    () => api.getGraphMemoryOfflineShadowReplayReport(storySlug),
    [storySlug],
  );
  const report = replayReportState.data;
  const statusText = replayReportState.loading
    ? "读取中"
    : report
      ? graphOfflineReplayReportStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆离线 Replay 报告" status={statusText} />
      {replayReportState.loading && <Loading label="正在整理 Graph 记忆离线 replay 报告…" />}
      {replayReportState.error && (
        <ErrorState message={replayReportState.error} onRetry={replayReportState.reload} />
      )}
      {!replayReportState.loading && !replayReportState.error && report && (
        <GraphMemoryOfflineShadowReplayReportView report={report} />
      )}
    </section>
  );
}

function GraphMemoryOfflineShadowReplayReportView({
  report,
}: {
  report: GraphMemoryOfflineShadowReplayReport;
}) {
  const visibleCases = report.case_results.filter((item) => item.status !== "deferred");

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>报告状态</span>
          <strong>{graphOfflineReplayGateLabel(report.report_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>服务结果</span>
          <strong>{report.summary.provider_result_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>Case 结果</span>
          <strong>{report.summary.case_result_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>待复核</span>
          <strong>{report.summary.manual_review_required_count}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.report_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {report.provider_results.length > 0 && (
        <div className="audit-log__rights-list">
          {report.provider_results.slice(0, 3).map((item) => (
            <span key={item.provider_id}>
              {item.service_target}：{graphOfflineReplayItemLabel(item.status)} ·{" "}
              {item.case_result_count} 个 case · {item.recommendation}
            </span>
          ))}
        </div>
      )}

      {visibleCases.length > 0 && (
        <ul className="sample-list">
          {visibleCases.slice(0, 4).map((item) => (
            <li key={item.id}>
              <strong>{item.provider_label} / {item.display_name || item.eval_id}</strong>
              <span>{item.gain_assessment || item.query}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="project-workspace__steps">
        <span>{graphOfflineReplayItemLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeFixturePackPanel({ storySlug }: { storySlug: string }) {
  const fixturePackState = useAsync(
    () => api.getGraphMemoryProviderSpikeFixturePack(storySlug),
    [storySlug],
  );
  const report = fixturePackState.data;
  const statusText = fixturePackState.loading
    ? "读取中"
    : report
      ? graphProviderFixturePackStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 前置包" status={statusText} />
      {fixturePackState.loading && <Loading label="正在整理 Provider spike 前置包…" />}
      {fixturePackState.error && (
        <ErrorState message={fixturePackState.error} onRetry={fixturePackState.reload} />
      )}
      {!fixturePackState.loading && !fixturePackState.error && report && (
        <GraphMemoryProviderSpikeFixturePackView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeFixturePackView({
  report,
}: {
  report: GraphMemoryProviderSpikeFixturePackReport;
}) {
  const selectedPacks = report.provider_fixture_packs.filter(
    (pack) => pack.status !== "deferred",
  );
  const visibleCases = selectedPacks.flatMap((pack) =>
    pack.fixture.cases.map((item) => ({
      ...item,
      providerLabel: pack.provider_label,
    })),
  );

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>前置包状态</span>
          <strong>{graphOfflineReplayGateLabel(report.fixture_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选服务</span>
          <strong>{report.summary.provider_fixture_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>选中 fixture</span>
          <strong>{report.summary.selected_fixture_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>待复核</span>
          <strong>{report.summary.manual_review_required_count}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.fixture_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {selectedPacks.length > 0 && (
        <div className="audit-log__rights-list">
          {selectedPacks.slice(0, 3).map((pack) => (
            <span key={pack.id}>
              {pack.service_target}：{graphOfflineReplayItemLabel(pack.status)} ·{" "}
              {pack.fixture.sample_case_count} 个 case ·{" "}
              {pack.opt_in_required ? "显式 opt-in" : "未要求 opt-in"}
            </span>
          ))}
        </div>
      )}

      {visibleCases.length > 0 && (
        <ul className="sample-list">
          {visibleCases.slice(0, 4).map((item) => (
            <li key={`${item.providerLabel}-${item.eval_id}`}>
              <strong>
                {item.providerLabel} / {item.display_name || item.eval_id}
              </strong>
              <span>{item.gain_assessment || item.query}</span>
            </li>
          ))}
        </ul>
      )}

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 4).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphOfflineReplayItemLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeReadinessGatePanel({ storySlug }: { storySlug: string }) {
  const readinessGateState = useAsync(
    () => api.getGraphMemoryProviderSpikeReadinessGate(storySlug),
    [storySlug],
  );
  const report = readinessGateState.data;
  const statusText = readinessGateState.loading
    ? "读取中"
    : report
      ? graphProviderReadinessGateStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 就绪门禁" status={statusText} />
      {readinessGateState.loading && <Loading label="正在整理 Provider spike 就绪门禁…" />}
      {readinessGateState.error && (
        <ErrorState message={readinessGateState.error} onRetry={readinessGateState.reload} />
      )}
      {!readinessGateState.loading && !readinessGateState.error && report && (
        <GraphMemoryProviderSpikeReadinessGateView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeReadinessGateView({
  report,
}: {
  report: GraphMemoryProviderSpikeReadinessGateReport;
}) {
  const visibleProviders = report.provider_readiness.filter(
    (item) => item.status !== "deferred",
  );

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>门禁状态</span>
          <strong>{graphProviderReadinessGateStatusLabel(report.readiness_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>可人工复核</span>
          <strong>{report.summary.ready_for_manual_review_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>阻塞服务</span>
          <strong>{report.summary.blocked_provider_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>{report.readiness_gate.real_provider_config_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.readiness_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {visibleProviders.length > 0 && (
        <div className="audit-log__rights-list">
          {visibleProviders.slice(0, 3).map((provider) => (
            <span key={provider.provider_id}>
              {provider.service_target}：
              {graphProviderReadinessItemLabel(provider.status)} ·{" "}
              {provider.sample_case_count} 个 case · {provider.recommendation}
            </span>
          ))}
        </div>
      )}

      {visibleProviders.length > 0 && (
        <ul className="sample-list">
          {visibleProviders.slice(0, 3).map((provider) => (
            <li key={provider.provider_id}>
              <strong>{provider.provider_label} / {provider.fixture_id}</strong>
              <span>
                {provider.readiness_checks
                  .slice(0, 4)
                  .map((check) => `${check.label}：${graphProviderReadinessItemLabel(check.status)}`)
                  .join("；")}
              </span>
            </li>
          ))}
        </ul>
      )}

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 4).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderReadinessItemLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeRunbookPanel({ storySlug }: { storySlug: string }) {
  const runbookState = useAsync(
    () => api.getGraphMemoryProviderSpikeRunbook(storySlug),
    [storySlug],
  );
  const report = runbookState.data;
  const statusText = runbookState.loading
    ? "读取中"
    : report
      ? graphProviderRunbookStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Runbook" status={statusText} />
      {runbookState.loading && <Loading label="正在整理 Provider spike 人工 SOP…" />}
      {runbookState.error && (
        <ErrorState message={runbookState.error} onRetry={runbookState.reload} />
      )}
      {!runbookState.loading && !runbookState.error && report && (
        <GraphMemoryProviderSpikeRunbookView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeRunbookView({
  report,
}: {
  report: GraphMemoryProviderSpikeRunbookReport;
}) {
  const visibleProviders = report.provider_runbooks.filter(
    (item) => item.status !== "deferred",
  );
  const firstProvider = visibleProviders[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>SOP 状态</span>
          <strong>{graphProviderRunbookStatusLabel(report.runbook.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>可 dry-run</span>
          <strong>{report.summary.ready_provider_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>SOP 步骤</span>
          <strong>{report.summary.total_step_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>{report.runbook.real_provider_config_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.runbook.objective}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {visibleProviders.length > 0 && (
        <div className="audit-log__rights-list">
          {visibleProviders.slice(0, 3).map((provider) => (
            <span key={provider.provider_id}>
              {provider.service_target}：
              {graphProviderRunbookStatusLabel(provider.status)} ·{" "}
              {provider.steps.length} 步 · {provider.recommendation}
            </span>
          ))}
        </div>
      )}

      {firstProvider && firstProvider.steps.length > 0 && (
        <ul className="sample-list">
          {firstProvider.steps.slice(0, 6).map((step) => (
            <li key={step.id}>
              <strong>{step.title}</strong>
              <span>{step.description}</span>
            </li>
          ))}
        </ul>
      )}

      {firstProvider && (
        <div className="project-workspace__steps">
          {firstProvider.acceptance_checks.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {firstProvider && (
        <div className="project-workspace__steps">
          {firstProvider.rollback_steps.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderRunbookStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeDryRunResultTemplatePanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const templateState = useAsync(
    () => api.getGraphMemoryProviderSpikeDryRunResultTemplate(storySlug),
    [storySlug],
  );
  const report = templateState.data;
  const statusText = templateState.loading
    ? "读取中"
    : report
      ? graphProviderResultTemplateStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 结果模板" status={statusText} />
      {templateState.loading && <Loading label="正在整理 dry-run 结果模板…" />}
      {templateState.error && (
        <ErrorState message={templateState.error} onRetry={templateState.reload} />
      )}
      {!templateState.loading && !templateState.error && report && (
        <GraphMemoryProviderSpikeDryRunResultTemplateView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeDryRunResultTemplateView({
  report,
}: {
  report: GraphMemoryProviderSpikeDryRunResultTemplateReport;
}) {
  const visibleProviders = report.provider_result_templates.filter(
    (item) => item.status !== "deferred",
  );
  const firstProvider = visibleProviders[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>模板状态</span>
          <strong>{graphProviderResultTemplateStatusLabel(report.template.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>可记录</span>
          <strong>{report.summary.ready_provider_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>结果字段</span>
          <strong>{report.summary.required_result_field_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>写入结果</span>
          <strong>{report.template.result_write_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.template.objective}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {visibleProviders.length > 0 && (
        <div className="audit-log__rights-list">
          {visibleProviders.slice(0, 3).map((provider) => (
            <span key={provider.provider_id}>
              {provider.service_target}：
              {graphProviderResultTemplateStatusLabel(provider.status)} ·{" "}
              {provider.result_fields.length} 字段 · {provider.recommendation}
            </span>
          ))}
        </div>
      )}

      {firstProvider && firstProvider.result_fields.length > 0 && (
        <ul className="sample-list">
          {firstProvider.result_fields.slice(0, 6).map((field) => (
            <li key={field.id}>
              <strong>{field.label}</strong>
              <span>{field.description}</span>
            </li>
          ))}
        </ul>
      )}

      {firstProvider && (
        <div className="project-workspace__steps">
          {firstProvider.pause_or_upgrade_decisions.slice(0, 4).map((item) => (
            <span key={item.id}>{item.label}</span>
          ))}
        </div>
      )}

      {firstProvider && (
        <div className="project-workspace__steps">
          {firstProvider.acceptance_record.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderResultTemplateStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeMockResultReportPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const mockResultState = useAsync(
    () => api.getGraphMemoryProviderSpikeMockResultReport(storySlug),
    [storySlug],
  );
  const report = mockResultState.data;
  const statusText = mockResultState.loading
    ? "读取中"
    : report
      ? graphProviderMockResultStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Mock 结果" status={statusText} />
      {mockResultState.loading && <Loading label="正在整理 mock 结果报告…" />}
      {mockResultState.error && (
        <ErrorState message={mockResultState.error} onRetry={mockResultState.reload} />
      )}
      {!mockResultState.loading && !mockResultState.error && report && (
        <GraphMemoryProviderSpikeMockResultReportView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeMockResultReportView({
  report,
}: {
  report: GraphMemoryProviderSpikeMockResultReport;
}) {
  const records = report.mock_result_records ?? [];
  const firstRecord = records[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>报告状态</span>
          <strong>{graphProviderMockResultStatusLabel(report.report_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>填充记录</span>
          <strong>{report.summary.filled_record_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选收益</span>
          <strong>{report.summary.candidate_gain_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>写入结果</span>
          <strong>{report.summary.result_write_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.report_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {records.length > 0 && (
        <div className="audit-log__rights-list">
          {records.slice(0, 3).map((record) => (
            <span key={record.id}>
              {record.service_target}：
              {graphProviderMockResultStatusLabel(record.status)} ·{" "}
              {graphProviderMockResultStatusLabel(record.manual_decision)}
            </span>
          ))}
        </div>
      )}

      {firstRecord && (
        <ul className="sample-list">
          {firstRecord.field_values.slice(0, 6).map((field) => (
            <li key={field.field_id}>
              <strong>{field.label}</strong>
              <span>{String(field.value)}</span>
            </li>
          ))}
        </ul>
      )}

      {firstRecord && (
        <div className="project-workspace__steps">
          <span>{firstRecord.gain_summary}</span>
          <span>{firstRecord.risk_summary}</span>
          <span>{firstRecord.review_summary}</span>
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderMockResultStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeReviewGatePanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const reviewGateState = useAsync(
    () => api.getGraphMemoryProviderSpikeReviewGate(storySlug),
    [storySlug],
  );
  const report = reviewGateState.data;
  const statusText = reviewGateState.loading
    ? "读取中"
    : report
      ? graphProviderReviewGateStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 复核门禁" status={statusText} />
      {reviewGateState.loading && <Loading label="正在整理复核门禁…" />}
      {reviewGateState.error && (
        <ErrorState message={reviewGateState.error} onRetry={reviewGateState.reload} />
      )}
      {!reviewGateState.loading && !reviewGateState.error && report && (
        <GraphMemoryProviderSpikeReviewGateView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeReviewGateView({
  report,
}: {
  report: GraphMemoryProviderSpikeReviewGateReport;
}) {
  const reviews = report.provider_reviews ?? [];
  const firstReview = reviews[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>门禁状态</span>
          <strong>{graphProviderReviewGateStatusLabel(report.review_gate.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>复核行</span>
          <strong>{report.summary.provider_review_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>候选收益</span>
          <strong>{report.summary.candidate_gain_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>{report.review_gate.real_provider_config_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.review_gate.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {reviews.length > 0 && (
        <div className="audit-log__rights-list">
          {reviews.slice(0, 3).map((review) => (
            <span key={review.id}>
              {review.service_target}：
              {graphProviderReviewGateStatusLabel(review.status)} ·{" "}
              {graphProviderReviewGateStatusLabel(review.gate_decision)}
            </span>
          ))}
        </div>
      )}

      {firstReview && (
        <ul className="sample-list">
          {firstReview.review_items.slice(0, 6).map((item) => (
            <li key={item.id}>
              <strong>{item.label}</strong>
              <span>{item.evidence}</span>
            </li>
          ))}
        </ul>
      )}

      {firstReview && (
        <div className="project-workspace__steps">
          <span>{firstReview.gain_summary}</span>
          <span>{firstReview.risk_summary}</span>
          <span>{firstReview.recommendation}</span>
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderReviewGateStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeManualApprovalPackPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const approvalState = useAsync(
    () => api.getGraphMemoryProviderSpikeManualApprovalPack(storySlug),
    [storySlug],
  );
  const report = approvalState.data;
  const statusText = approvalState.loading
    ? "读取中"
    : report
      ? graphProviderManualApprovalStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 人工审批包" status={statusText} />
      {approvalState.loading && <Loading label="正在整理人工审批包…" />}
      {approvalState.error && (
        <ErrorState message={approvalState.error} onRetry={approvalState.reload} />
      )}
      {!approvalState.loading && !approvalState.error && report && (
        <GraphMemoryProviderSpikeManualApprovalPackView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeManualApprovalPackView({
  report,
}: {
  report: GraphMemoryProviderSpikeManualApprovalPackReport;
}) {
  const items = report.approval_items ?? [];
  const firstItem = items[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>审批包</span>
          <strong>{graphProviderManualApprovalStatusLabel(report.approval_pack.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>审批项</span>
          <strong>{report.summary.approval_item_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>风险签收</span>
          <strong>{report.summary.risk_signoff_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>{report.approval_pack.real_provider_config_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.approval_pack.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="audit-log__rights-list">
          {items.slice(0, 3).map((item) => (
            <span key={item.id}>
              {item.service_target}：
              {graphProviderManualApprovalStatusLabel(item.status)} ·{" "}
              {graphProviderManualApprovalStatusLabel(item.gate_decision)}
            </span>
          ))}
        </div>
      )}

      {firstItem && (
        <ul className="sample-list">
          {firstItem.risk_signoffs.slice(0, 5).map((item) => (
            <li key={item.id}>
              <strong>{item.label}</strong>
              <span>{item.evidence ?? item.value ?? ""}</span>
            </li>
          ))}
        </ul>
      )}

      {firstItem && (
        <div className="project-workspace__steps">
          {firstItem.rollback_confirmations.slice(0, 3).map((item) => (
            <span key={item.id}>{item.label}</span>
          ))}
        </div>
      )}

      {firstItem && (
        <div className="project-workspace__steps">
          {firstItem.opt_in_materials.slice(0, 4).map((item) => (
            <span key={item.id}>
              {item.label}：{item.value}
            </span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderManualApprovalStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_approval_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_approval_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeManualApprovalEvidenceChecklistPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const checklistState = useAsync(
    () => api.getGraphMemoryProviderSpikeManualApprovalEvidenceChecklist(storySlug),
    [storySlug],
  );
  const report = checklistState.data;
  const statusText = checklistState.loading
    ? "读取中"
    : report
      ? graphProviderApprovalEvidenceStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike 审批证据核对表" status={statusText} />
      {checklistState.loading && <Loading label="正在整理审批证据核对表…" />}
      {checklistState.error && (
        <ErrorState message={checklistState.error} onRetry={checklistState.reload} />
      )}
      {!checklistState.loading && !checklistState.error && report && (
        <GraphMemoryProviderSpikeManualApprovalEvidenceChecklistView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeManualApprovalEvidenceChecklistView({
  report,
}: {
  report: GraphMemoryProviderSpikeManualApprovalEvidenceChecklistReport;
}) {
  const items = report.checklist_items ?? [];
  const firstItem = items[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>核对表</span>
          <strong>{graphProviderApprovalEvidenceStatusLabel(report.evidence_checklist.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>待签收</span>
          <strong>{report.summary.pending_signoff_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>材料缺口</span>
          <strong>{report.summary.material_gap_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.evidence_checklist.real_provider_config_allowed ? "允许" : "禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.evidence_checklist.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="audit-log__rights-list">
          {items.slice(0, 3).map((item) => (
            <span key={item.id}>
              {item.service_target}：
              {graphProviderApprovalEvidenceStatusLabel(item.status)} ·{" "}
              {graphProviderApprovalEvidenceStatusLabel(item.evidence_status)}
            </span>
          ))}
        </div>
      )}

      {firstItem && (
        <ul className="sample-list">
          {firstItem.pending_signoffs.slice(0, 5).map((item) => (
            <li key={item.id}>
              <strong>{item.label}</strong>
              <span>{item.evidence ?? item.value ?? ""}</span>
            </li>
          ))}
        </ul>
      )}

      {firstItem && firstItem.available_materials.length > 0 && (
        <div className="project-workspace__steps">
          {firstItem.available_materials.slice(0, 4).map((item) => (
            <span key={item.id}>
              {item.label}：{item.value}
            </span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderApprovalEvidenceStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInEvidenceSnapshotPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const snapshotState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInEvidenceSnapshot(storySlug),
    [storySlug],
  );
  const report = snapshotState.data;
  const statusText = snapshotState.loading
    ? "读取中"
    : report
      ? graphProviderOptInSnapshotStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 证据快照" status={statusText} />
      {snapshotState.loading && <Loading label="正在整理 opt-in 证据快照…" />}
      {snapshotState.error && (
        <ErrorState message={snapshotState.error} onRetry={snapshotState.reload} />
      )}
      {!snapshotState.loading && !snapshotState.error && report && (
        <GraphMemoryProviderSpikeOptInEvidenceSnapshotView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInEvidenceSnapshotView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInEvidenceSnapshotReport;
}) {
  const items = report.snapshot_items ?? [];
  const firstItem = items[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>快照</span>
          <strong>{graphProviderOptInSnapshotStatusLabel(report.opt_in_snapshot.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>阻塞项</span>
          <strong>{report.summary.blocker_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>待签收</span>
          <strong>{report.summary.signoff_todo_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.opt_in_snapshot.real_provider_config_allowed ? "允许" : "禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.opt_in_snapshot.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="audit-log__rights-list">
          {items.slice(0, 3).map((item) => (
            <span key={item.id}>
              {item.service_target}：
              {graphProviderOptInSnapshotStatusLabel(item.status)} · 阻塞{" "}
              {item.blocker_count} 项
            </span>
          ))}
        </div>
      )}

      {firstItem && (
        <ul className="sample-list">
          {firstItem.signoff_todos.slice(0, 5).map((item) => (
            <li key={item.id}>
              <strong>{item.label}</strong>
              <span>{item.evidence ?? item.value ?? ""}</span>
            </li>
          ))}
        </ul>
      )}

      {firstItem && firstItem.blocker_reasons.length > 0 && (
        <div className="project-workspace__steps">
          {firstItem.blocker_reasons.slice(0, 4).map((reason) => (
            <span key={reason}>{reason}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderOptInSnapshotStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInNoGoMatrixPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const matrixState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInNoGoMatrix(storySlug),
    [storySlug],
  );
  const report = matrixState.data;
  const statusText = matrixState.loading
    ? "读取中"
    : report
      ? graphProviderNoGoMatrixStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in No-go 矩阵" status={statusText} />
      {matrixState.loading && <Loading label="正在整理 opt-in no-go 矩阵…" />}
      {matrixState.error && (
        <ErrorState message={matrixState.error} onRetry={matrixState.reload} />
      )}
      {!matrixState.loading && !matrixState.error && report && (
        <GraphMemoryProviderSpikeOptInNoGoMatrixView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInNoGoMatrixView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInNoGoMatrixReport;
}) {
  const rows = report.matrix_rows ?? [];
  const firstRow = rows[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>矩阵</span>
          <strong>{graphProviderNoGoMatrixStatusLabel(report.no_go_matrix.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>阻塞格</span>
          <strong>{report.summary.blocked_cell_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>签收阻塞</span>
          <strong>{report.summary.signoff_blocker_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.no_go_matrix.real_provider_config_allowed ? "允许" : "禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.no_go_matrix.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {rows.length > 0 && (
        <div className="audit-log__rights-list">
          {rows.slice(0, 3).map((row) => (
            <span key={row.id}>
              {row.service_target}：{graphProviderNoGoMatrixStatusLabel(row.status)} ·{" "}
              阻塞格 {row.blocked_cell_count}
            </span>
          ))}
        </div>
      )}

      {firstRow && (
        <ul className="sample-list">
          {firstRow.cells.slice(0, 5).map((cell) => (
            <li key={cell.id}>
              <strong>{cell.label}</strong>
              <span>
                {graphProviderNoGoMatrixStatusLabel(cell.status)} · {cell.reason}
              </span>
            </li>
          ))}
        </ul>
      )}

      {firstRow && firstRow.no_go_reasons.length > 0 && (
        <div className="project-workspace__steps">
          {firstRow.no_go_reasons.slice(0, 4).map((reason) => (
            <span key={reason}>{reason}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderNoGoMatrixStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInOperatorChecklistPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const checklistState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInOperatorChecklist(storySlug),
    [storySlug],
  );
  const report = checklistState.data;
  const statusText = checklistState.loading
    ? "读取中"
    : report
      ? graphProviderOperatorChecklistStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 操作清单" status={statusText} />
      {checklistState.loading && <Loading label="正在整理 opt-in 操作清单…" />}
      {checklistState.error && (
        <ErrorState message={checklistState.error} onRetry={checklistState.reload} />
      )}
      {!checklistState.loading && !checklistState.error && report && (
        <GraphMemoryProviderSpikeOptInOperatorChecklistView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInOperatorChecklistView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInOperatorChecklistReport;
}) {
  const sections = report.checklist_sections ?? [];
  const firstSection = sections[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>清单</span>
          <strong>
            {graphProviderOperatorChecklistStatusLabel(report.operator_checklist.status)}
          </strong>
        </div>
        <div className="master-setting__metric">
          <span>阻塞步骤</span>
          <strong>{report.summary.blocked_step_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>签收步骤</span>
          <strong>{report.summary.manual_signoff_step_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.operator_checklist.real_provider_config_allowed ? "允许" : "禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.operator_checklist.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {sections.length > 0 && (
        <div className="audit-log__rights-list">
          {sections.slice(0, 3).map((section) => (
            <span key={section.id}>
              {section.service_target}：
              {graphProviderOperatorChecklistStatusLabel(section.status)} · 阻塞步骤{" "}
              {section.blocked_step_count}
            </span>
          ))}
        </div>
      )}

      {firstSection && (
        <ul className="sample-list">
          {firstSection.steps.slice(0, 5).map((step) => (
            <li key={step.id}>
              <strong>{step.label}</strong>
              <span>
                {graphProviderOperatorChecklistStatusLabel(step.status)} ·{" "}
                {step.action}
              </span>
            </li>
          ))}
        </ul>
      )}

      {firstSection && (
        <div className="project-workspace__steps">
          <span>{firstSection.pause_reason}</span>
          <span>{firstSection.recommendation}</span>
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderOperatorChecklistStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.manual_review_checklist.length > 0 && (
        <div className="project-workspace__steps">
          {report.manual_review_checklist.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      {report.no_go_conditions.length > 0 && (
        <div className="project-workspace__steps">
          {report.no_go_conditions.slice(0, 3).map((condition) => (
            <span key={condition}>{condition}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInReviewPacketPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const packetState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInReviewPacket(storySlug),
    [storySlug],
  );
  const report = packetState.data;
  const statusText = packetState.loading
    ? "读取中"
    : report
      ? graphProviderReviewPacketStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 复核包" status={statusText} />
      {packetState.loading && <Loading label="正在整理 opt-in 复核包…" />}
      {packetState.error && (
        <ErrorState message={packetState.error} onRetry={packetState.reload} />
      )}
      {!packetState.loading && !packetState.error && report && (
        <GraphMemoryProviderSpikeOptInReviewPacketView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInReviewPacketView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInReviewPacketReport;
}) {
  const sections = report.packet_sections ?? [];
  const firstSection = sections[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>复核包</span>
          <strong>{graphProviderReviewPacketStatusLabel(report.review_packet.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>证据项</span>
          <strong>{report.summary.evidence_item_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>暂停材料</span>
          <strong>{report.summary.pause_material_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.review_packet.real_provider_config_allowed ? "允许" : "禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.review_packet.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {sections.length > 0 && (
        <div className="audit-log__rights-list">
          {sections.slice(0, 3).map((section) => (
            <span key={section.id}>
              {section.service_target}：
              {graphProviderReviewPacketStatusLabel(section.status)} · 证据项{" "}
              {section.evidence_item_count}
            </span>
          ))}
        </div>
      )}

      {firstSection && (
        <ul className="sample-list">
          {firstSection.evidence_sequence.slice(0, 5).map((item) => (
            <li key={item.id}>
              <strong>{item.label}</strong>
              <span>
                {graphProviderReviewPacketStatusLabel(item.status)} ·{" "}
                {item.review_note}
              </span>
            </li>
          ))}
        </ul>
      )}

      {firstSection && (
        <div className="project-workspace__steps">
          {firstSection.pause_materials.slice(0, 2).map((item) => (
            <span key={item}>{item}</span>
          ))}
          {firstSection.escalation_materials.slice(0, 2).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderReviewPacketStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.review_packet_materials.length > 0 && (
        <div className="project-workspace__steps">
          {report.review_packet_materials.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInDecisionLedgerPreviewPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const ledgerState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInDecisionLedgerPreview(storySlug),
    [storySlug],
  );
  const report = ledgerState.data;
  const statusText = ledgerState.loading
    ? "读取中"
    : report
      ? graphProviderDecisionLedgerStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 决策账本预览" status={statusText} />
      {ledgerState.loading && <Loading label="正在整理 opt-in 决策账本预览…" />}
      {ledgerState.error && (
        <ErrorState message={ledgerState.error} onRetry={ledgerState.reload} />
      )}
      {!ledgerState.loading && !ledgerState.error && report && (
        <GraphMemoryProviderSpikeOptInDecisionLedgerPreviewView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInDecisionLedgerPreviewView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInDecisionLedgerPreviewReport;
}) {
  const rows = report.ledger_rows ?? [];
  const firstRow = rows[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>账本预览</span>
          <strong>
            {graphProviderDecisionLedgerStatusLabel(report.decision_ledger_preview.status)}
          </strong>
        </div>
        <div className="master-setting__metric">
          <span>预览行</span>
          <strong>{report.summary.ledger_row_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>签收字段</span>
          <strong>{report.summary.pending_signoff_field_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>保存状态</span>
          <strong>{report.decision_ledger_preview.approval_saved ? "已保存" : "未保存"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.decision_ledger_preview.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {rows.length > 0 && (
        <div className="audit-log__rights-list">
          {rows.slice(0, 3).map((row) => (
            <span key={row.id}>
              {row.service_target}：
              {graphProviderDecisionLedgerStatusLabel(row.status)} · 签收字段{" "}
              {row.pending_signoff_fields.length}
            </span>
          ))}
        </div>
      )}

      {firstRow && (
        <ul className="sample-list">
          {firstRow.pending_signoff_fields.slice(0, 5).map((field) => (
            <li key={field.id}>
              <strong>{field.label}</strong>
              <span>{field.saved ? "已保存" : "未保存"} · 值为空</span>
            </li>
          ))}
        </ul>
      )}

      {firstRow && (
        <div className="project-workspace__steps">
          {firstRow.preview_notes.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderDecisionLedgerStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.ledger_preview_materials.length > 0 && (
        <div className="project-workspace__steps">
          {report.ledger_preview_materials.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInFinalReadinessSummaryPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const summaryState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInFinalReadinessSummary(storySlug),
    [storySlug],
  );
  const report = summaryState.data;
  const statusText = summaryState.loading
    ? "读取中"
    : report
      ? graphProviderFinalReadinessStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 最终就绪摘要" status={statusText} />
      {summaryState.loading && <Loading label="正在整理 opt-in 最终就绪摘要…" />}
      {summaryState.error && (
        <ErrorState message={summaryState.error} onRetry={summaryState.reload} />
      )}
      {!summaryState.loading && !summaryState.error && report && (
        <GraphMemoryProviderSpikeOptInFinalReadinessSummaryView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInFinalReadinessSummaryView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInFinalReadinessSummaryReport;
}) {
  const rows = report.readiness_rows ?? [];
  const firstRow = rows[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>最终摘要</span>
          <strong>
            {graphProviderFinalReadinessStatusLabel(report.final_readiness_summary.status)}
          </strong>
        </div>
        <div className="master-setting__metric">
          <span>就绪行</span>
          <strong>{report.summary.readiness_row_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>未签收</span>
          <strong>{report.summary.unresolved_signoff_field_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>真实配置</span>
          <strong>
            {report.final_readiness_summary.real_provider_ready ? "可继续" : "仍禁止"}
          </strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.final_readiness_summary.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {rows.length > 0 && (
        <div className="audit-log__rights-list">
          {rows.slice(0, 3).map((row) => (
            <span key={row.id}>
              {row.service_target}：
              {graphProviderFinalReadinessStatusLabel(row.gate_status)} · 阻塞{" "}
              {row.unresolved_blockers.length}
            </span>
          ))}
        </div>
      )}

      {firstRow && (
        <ul className="sample-list">
          {firstRow.unresolved_signoff_fields.slice(0, 5).map((field) => (
            <li key={field.id}>
              <strong>{field.label}</strong>
              <span>{field.saved ? "已保存" : "未保存"} · 仍需人工确认</span>
            </li>
          ))}
        </ul>
      )}

      {firstRow && (
        <div className="project-workspace__steps">
          {firstRow.unresolved_blockers.slice(0, 4).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderFinalReadinessStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.final_readiness_materials.length > 0 && (
        <div className="project-workspace__steps">
          {report.final_readiness_materials.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftPanel({
  storySlug,
}: {
  storySlug: string;
}) {
  const schemaState = useAsync(
    () => api.getGraphMemoryProviderSpikeOptInHumanSignoffSchemaDraft(storySlug),
    [storySlug],
  );
  const report = schemaState.data;
  const statusText = schemaState.loading
    ? "读取中"
    : report
      ? graphProviderHumanSignoffSchemaStatusLabel(report.status)
      : "未读取";

  return (
    <section className="project-workspace__section vector-readiness">
      <SectionTitle title="Graph 记忆 Provider Spike Opt-in 人工签收 Schema" status={statusText} />
      {schemaState.loading && <Loading label="正在整理人工签收 schema 草案…" />}
      {schemaState.error && <ErrorState message={schemaState.error} onRetry={schemaState.reload} />}
      {!schemaState.loading && !schemaState.error && report && (
        <GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftView report={report} />
      )}
    </section>
  );
}

function GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftView({
  report,
}: {
  report: GraphMemoryProviderSpikeOptInHumanSignoffSchemaDraftReport;
}) {
  const sections = report.schema_sections ?? [];
  const firstSection = sections[0];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>Schema 草案</span>
          <strong>{graphProviderHumanSignoffSchemaStatusLabel(report.schema_draft.status)}</strong>
        </div>
        <div className="master-setting__metric">
          <span>字段</span>
          <strong>{report.summary.schema_field_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>必填</span>
          <strong>{report.summary.required_field_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>保存签收</span>
          <strong>{report.schema_draft.save_allowed ? "允许" : "禁止"}</strong>
        </div>
      </div>

      <p className="project-workspace__ok">{report.schema_draft.reason}</p>

      {report.warnings.length > 0 && (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      )}

      {sections.length > 0 && (
        <div className="audit-log__rights-list">
          {sections.slice(0, 3).map((section) => (
            <span key={section.id}>
              {section.service_target}：必填 {section.required_field_count} ·{" "}
              {section.save_allowed ? "可保存" : "只读草案"}
            </span>
          ))}
        </div>
      )}

      {firstSection && (
        <ul className="sample-list">
          {firstSection.schema_fields.slice(0, 5).map((field) => (
            <li key={field.id}>
              <strong>{field.label}</strong>
              <span>
                {field.validation_rule.type === "required_non_empty_text"
                  ? "必填文本"
                  : field.validation_rule.type}{" "}
                · {field.input_storage === "not_saved" ? "不保存输入" : field.input_storage}
              </span>
            </li>
          ))}
        </ul>
      )}

      <div className="project-workspace__steps">
        <span>{graphProviderHumanSignoffSchemaStatusLabel(report.decision.status)}</span>
        <span>{report.decision.recommendation}</span>
      </div>

      {report.schema_materials.length > 0 && (
        <div className="project-workspace__steps">
          {report.schema_materials.slice(0, 3).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      )}

      <p className="master-setting__note">
        {report.boundaries[1] ?? report.boundaries[0]}
      </p>
    </>
  );
}

function EmbeddingEvaluationSamplesPanel({ storySlug }: { storySlug: string }) {
  const samplesState = useAsync(
    () => api.getEmbeddingEvaluationSamples(storySlug),
    [storySlug],
  );
  const [draft, setDraft] = useState({
    query: "",
    expectedEntities: "",
    reason: "",
    currentChapter: "1",
  });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [exportPack, setExportPack] = useState<RetrievalSampleExportPackReport | null>(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [mockReport, setMockReport] = useState<EmbeddingMockEvaluationReport | null>(null);
  const [mockReportLoading, setMockReportLoading] = useState(false);
  const [mockReportError, setMockReportError] = useState<string | null>(null);
  const [replayReport, setReplayReport] = useState<RetrievalSampleReplayReport | null>(null);
  const [replayReportLoading, setReplayReportLoading] = useState(false);
  const [replayReportError, setReplayReportError] = useState<string | null>(null);
  const [migrationPack, setMigrationPack] = useState<RetrievalSampleMigrationPackReport | null>(
    null,
  );
  const [migrationPackLoading, setMigrationPackLoading] = useState(false);
  const [migrationPackError, setMigrationPackError] = useState<string | null>(null);
  const report = samplesState.data;
  const statusText = samplesState.loading
    ? "读取中"
    : report
      ? embeddingSamplesStatusLabel(report.status)
      : "未读取";
  const canSubmit = draft.query.trim() && parseExpectedEntities(draft.expectedEntities).length;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit || saving) return;
    const payload: RetrievalFailureSampleAppendRequest = {
      query: draft.query.trim(),
      expected_entities: parseExpectedEntities(draft.expectedEntities),
      reason: draft.reason.trim(),
      current_chapter: Number(draft.currentChapter) || 1,
    };
    setSaving(true);
    setSaveError(null);
    try {
      await api.addRetrievalFailureSample(storySlug, payload);
      setDraft({ query: "", expectedEntities: "", reason: "", currentChapter: "1" });
      setExportPack(null);
      setMockReport(null);
      setReplayReport(null);
      setMigrationPack(null);
      samplesState.reload();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "记录失败");
    } finally {
      setSaving(false);
    }
  }

  async function handleExportPreview() {
    if (exportLoading) return;
    setExportLoading(true);
    setExportError(null);
    try {
      setExportPack(await api.getRetrievalSampleExportPack(storySlug));
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "导出包读取失败");
    } finally {
      setExportLoading(false);
    }
  }

  async function handleMockReportPreview() {
    if (mockReportLoading) return;
    setMockReportLoading(true);
    setMockReportError(null);
    try {
      setMockReport(await api.getEmbeddingMockEvaluationReport(storySlug));
    } catch (err) {
      setMockReportError(err instanceof Error ? err.message : "对照报告读取失败");
    } finally {
      setMockReportLoading(false);
    }
  }

  async function handleReplayReportPreview() {
    if (replayReportLoading) return;
    setReplayReportLoading(true);
    setReplayReportError(null);
    try {
      setReplayReport(await api.getRetrievalSampleReplayReport(storySlug));
    } catch (err) {
      setReplayReportError(err instanceof Error ? err.message : "复跑报告读取失败");
    } finally {
      setReplayReportLoading(false);
    }
  }

  async function handleMigrationPackPreview() {
    if (migrationPackLoading) return;
    setMigrationPackLoading(true);
    setMigrationPackError(null);
    try {
      setMigrationPack(await api.getRetrievalSampleMigrationPack(storySlug));
    } catch (err) {
      setMigrationPackError(err instanceof Error ? err.message : "迁移包读取失败");
    } finally {
      setMigrationPackLoading(false);
    }
  }

  return (
    <section className="project-workspace__section embedding-samples">
      <SectionTitle title="Embedding 样本评估" status={statusText} />
      {samplesState.loading && <Loading label="正在评估失败样本…" />}
      {samplesState.error && (
        <ErrorState message={samplesState.error} onRetry={samplesState.reload} />
      )}
      {!samplesState.loading && !samplesState.error && report && (
        <EmbeddingEvaluationSamplesView
          report={report}
          draft={draft}
          onDraftChange={setDraft}
          onSubmit={handleSubmit}
          canSubmit={Boolean(canSubmit)}
          saving={saving}
          saveError={saveError}
          exportPack={exportPack}
          exportLoading={exportLoading}
          exportError={exportError}
          onExportPreview={handleExportPreview}
          mockReport={mockReport}
          mockReportLoading={mockReportLoading}
          mockReportError={mockReportError}
          onMockReportPreview={handleMockReportPreview}
          replayReport={replayReport}
          replayReportLoading={replayReportLoading}
          replayReportError={replayReportError}
          onReplayReportPreview={handleReplayReportPreview}
          migrationPack={migrationPack}
          migrationPackLoading={migrationPackLoading}
          migrationPackError={migrationPackError}
          onMigrationPackPreview={handleMigrationPackPreview}
        />
      )}
    </section>
  );
}

function EmbeddingEvaluationSamplesView({
  report,
  draft,
  onDraftChange,
  onSubmit,
  canSubmit,
  saving,
  saveError,
  exportPack,
  exportLoading,
  exportError,
  onExportPreview,
  mockReport,
  mockReportLoading,
  mockReportError,
  onMockReportPreview,
  replayReport,
  replayReportLoading,
  replayReportError,
  onReplayReportPreview,
  migrationPack,
  migrationPackLoading,
  migrationPackError,
  onMigrationPackPreview,
}: {
  report: EmbeddingEvaluationSamplesReport;
  draft: {
    query: string;
    expectedEntities: string;
    reason: string;
    currentChapter: string;
  };
  onDraftChange: (draft: {
    query: string;
    expectedEntities: string;
    reason: string;
    currentChapter: string;
  }) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  canSubmit: boolean;
  saving: boolean;
  saveError: string | null;
  exportPack: RetrievalSampleExportPackReport | null;
  exportLoading: boolean;
  exportError: string | null;
  onExportPreview: () => void;
  mockReport: EmbeddingMockEvaluationReport | null;
  mockReportLoading: boolean;
  mockReportError: string | null;
  onMockReportPreview: () => void;
  replayReport: RetrievalSampleReplayReport | null;
  replayReportLoading: boolean;
  replayReportError: string | null;
  onReplayReportPreview: () => void;
  migrationPack: RetrievalSampleMigrationPackReport | null;
  migrationPackLoading: boolean;
  migrationPackError: string | null;
  onMigrationPackPreview: () => void;
}) {
  const visibleSamples = [
    ...report.samples.filter((sample) => sample.diagnosis === "lexical_gap"),
    ...report.samples.filter((sample) => sample.diagnosis !== "lexical_gap"),
  ];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>样本</span>
          <strong>{report.summary.sample_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>BM25 命中</span>
          <strong>{report.summary.bm25_hit_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>Mock 命中</span>
          <strong>{report.summary.mock_embedding_hit_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>词面缺口</span>
          <strong>{report.summary.lexical_gap_count}</strong>
        </div>
      </div>

      {report.warnings.length > 0 ? (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : (
        <p className="project-workspace__ok">样本评估未调用真实 embedding provider。</p>
      )}

      {visibleSamples.length === 0 ? (
        <EmptyState
          title="暂无失败样本"
          hint="先记录换说法召回失败样本，再比较 BM25 与 mock 语义命中。"
        />
      ) : (
        <ul className="sample-list">
          {visibleSamples.slice(0, 4).map((sample) => (
            <li key={sample.query}>
              <strong>{embeddingDiagnosisLabel(sample.diagnosis)}</strong>
              <span>
                {sample.query}
                {sample.target_item_id ? ` · ${sample.target_item_id}` : ""}
              </span>
            </li>
          ))}
        </ul>
      )}

      <div className="audit-log__rights-list">
        <span>
          样本文件：{report.sample_schema.path} · 必填：
          {report.sample_schema.required.join("、")}
        </span>
        <span>
          对照口径：BM25 走当前检索链路，mock 命中只检查期望实体能否定位到账本目标。
        </span>
      </div>

      {report.source_kind !== "builtin" && (
        <form className="master-setting__editor embedding-samples__form" onSubmit={onSubmit}>
          <label className="master-setting__field master-setting__field--wide">
            <span>失败查询</span>
            <textarea
              value={draft.query}
              onChange={(event) =>
                onDraftChange({ ...draft, query: event.target.value })
              }
              maxLength={180}
            />
          </label>
          <label className="master-setting__field">
            <span>期望实体</span>
            <input
              value={draft.expectedEntities}
              onChange={(event) =>
                onDraftChange({ ...draft, expectedEntities: event.target.value })
              }
              maxLength={240}
            />
          </label>
          <label className="master-setting__field">
            <span>当前章节</span>
            <input
              value={draft.currentChapter}
              onChange={(event) =>
                onDraftChange({ ...draft, currentChapter: event.target.value })
              }
              inputMode="numeric"
              maxLength={4}
            />
          </label>
          <label className="master-setting__field master-setting__field--wide">
            <span>失败原因</span>
            <input
              value={draft.reason}
              onChange={(event) =>
                onDraftChange({ ...draft, reason: event.target.value })
              }
              maxLength={220}
            />
          </label>
          <div className="master-setting__field master-setting__field--wide embedding-samples__actions">
            <button
              type="submit"
              className="workspace-btn workspace-btn--primary"
              disabled={!canSubmit || saving}
            >
              {saving ? "记录中" : "记录样本"}
            </button>
            {saveError && <span className="error-text">{saveError}</span>}
          </div>
        </form>
      )}

      <div className="embedding-samples__export">
        <div className="embedding-samples__actions">
          <button
            type="button"
            className="workspace-btn"
            onClick={onExportPreview}
            disabled={exportLoading}
          >
            {exportLoading ? "整理中" : "预览导出包"}
          </button>
          <button
            type="button"
            className="workspace-btn"
            onClick={onMockReportPreview}
            disabled={mockReportLoading}
          >
            {mockReportLoading ? "生成中" : "生成对照报告"}
          </button>
          <button
            type="button"
            className="workspace-btn"
            onClick={onReplayReportPreview}
            disabled={replayReportLoading}
          >
            {replayReportLoading ? "复跑中" : "生成复跑报告"}
          </button>
          <button
            type="button"
            className="workspace-btn"
            onClick={onMigrationPackPreview}
            disabled={migrationPackLoading}
          >
            {migrationPackLoading ? "整理中" : "生成迁移包"}
          </button>
        </div>
        {exportError && <span className="error-text">{exportError}</span>}
        {mockReportError && <span className="error-text">{mockReportError}</span>}
        {replayReportError && <span className="error-text">{replayReportError}</span>}
        {migrationPackError && <span className="error-text">{migrationPackError}</span>}
        {exportPack && (
          <div className="embedding-samples__export-preview">
            <div className="audit-log__rights-list">
              <span>
                文件：{exportPack.filename} · 状态：
                {retrievalExportPackStatusLabel(exportPack.status)}
              </span>
              <span>
                样本：{exportPack.summary.sample_count} · 词面缺口：
                {exportPack.summary.lexical_gap_count}
              </span>
            </div>
            <pre>{exportPack.content_md.slice(0, 1800)}</pre>
          </div>
        )}
        {mockReport && (
          <div className="embedding-samples__export-preview">
            <div className="audit-log__rights-list">
              <span>
                对照报告：{embeddingMockReportStatusLabel(mockReport.status)} · Gate：
                {mockReport.gate.passed ? "通过" : "未通过"}
              </span>
              <span>
                样本：{mockReport.summary.sample_count} · 词面缺口：
                {mockReport.summary.lexical_gap_count}
              </span>
            </div>
            <pre>{mockReport.report_md.slice(0, 1800)}</pre>
          </div>
        )}
        {replayReport && (
          <div className="embedding-samples__export-preview">
            <div className="audit-log__rights-list">
              <span>
                复跑报告：{retrievalReplayReportStatusLabel(replayReport.status)} · Gate：
                {replayReport.replay_gate.passed ? "通过" : "未通过"}
              </span>
              <span>
                Cases：{replayReport.summary.case_count} · 仍是词面缺口：
                {replayReport.summary.still_failing_lexically_count}
              </span>
            </div>
            <pre>{replayReport.report_md.slice(0, 1800)}</pre>
          </div>
        )}
        {migrationPack && (
          <div className="embedding-samples__export-preview">
            <div className="audit-log__rights-list">
              <span>
                迁移包：{retrievalMigrationPackStatusLabel(migrationPack.status)} · Gate：
                {migrationPack.migration_gate.passed ? "通过" : "未通过"}
              </span>
              <span>
                Records：{migrationPack.summary.record_count} · 跳过：
                {migrationPack.summary.skipped_count}
              </span>
            </div>
            <pre>{migrationPack.content_json.slice(0, 1800)}</pre>
          </div>
        )}
      </div>

      <div className="project-workspace__steps">
        {report.next_steps.slice(0, 3).map((step) => (
          <span key={step}>{step}</span>
        ))}
      </div>
      <p className="master-setting__note">{report.boundaries[2]}</p>
    </>
  );
}

function parseExpectedEntities(value: string): string[] {
  return value
    .split(/[,，;；\s]+/)
    .map((item) => item.trim())
    .filter((item, index, arr) => item && arr.indexOf(item) === index)
    .slice(0, 10);
}

function RightsApprovalPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: RightsApprovalChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  const summary = data?.summary;
  const statusText = loading
    ? "读取中"
    : summary
      ? `${summary.ready_count} / ${summary.checkpoint_count} 已具备`
      : "未读取";

  return (
    <div className="audit-log__rights">
      <div className="audit-log__rights-head">
        <div>
          <p className="tiny muted">版权审批检查</p>
          <strong>{statusText}</strong>
        </div>
        {error && (
          <button type="button" className="workspace-btn workspace-btn--ghost" onClick={onRetry}>
            重试
          </button>
        )}
      </div>
      {error && <p className="master-setting__error">{error}</p>}
      {data && (
        <>
          <div className="audit-log__rights-list">
            {data.checkpoints.slice(0, 4).map((checkpoint) => (
              <span key={checkpoint.id}>
                {checkpoint.label}：{checkpoint.status_label}
              </span>
            ))}
          </div>
          {data.next_steps[0] && (
            <p className="audit-log__rights-note">{data.next_steps[0]}</p>
          )}
        </>
      )}
    </div>
  );
}

function AuditLogEventItem({ event }: { event: ProjectAuditLogEvent }) {
  return (
    <li>
      <div>
        <strong>{auditActionLabel(event.action, event.label)}</strong>
        <span>{event.summary || event.label}</span>
      </div>
      <div>
        <span>{event.created_at || "未记录时间"}</span>
        <em>{severityLabel(event.severity)}</em>
      </div>
    </li>
  );
}

function auditStatusText(report: ProjectAuditLog): string {
  if (report.status === "empty") return "尚无事件";
  return "已聚合审计事件";
}

function ProjectWorkspaceSidePanel({ data }: { data: ProjectWorkspace }) {
  return (
    <div className="project-side">
      <h2>项目资产</h2>
      <SideLine label="来源" value={sourceTypeLabel(data.source.type || data.source_kind)} />
      <SideLine label="章节" value={`${data.chapter_overview.total_chapters} 章`} />
      <SideLine label="记忆层" value={`${data.memory.layer_count} 层`} />
      <SideLine label="设定状态" value={statusLabel(data.master_setting_workspace.status)} />
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
  const actionRequirements = completion
    ? collectActionRequirements(completion.actions)
    : [];
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
      if (!isCanonReplayRangePayload(action.payload)) {
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
      const payload = isWorldlineJudgementPayload(action.payload)
        ? action.payload
        : { story_slug: storySlug };
      await api.generateWorldlineJudgement(
        recommended.run_id,
        recommended.branch_id,
        payload,
      );
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
          {actionRequirements.length > 0 && (
            <div className="creation-loop__requirements">
              <p className="tiny muted">审计前置</p>
              {actionRequirements.slice(0, 3).map((item) => (
                <span key={item.id} title={item.detail}>
                  {item.label}
                </span>
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

interface MasterSettingDraft {
  displayName: string;
  genre: string;
  worldRules: string;
  powerLimits: string;
  forbiddenAdditions: string;
}

function MasterSettingPanel({
  storySlug,
  master,
  onSaved,
}: {
  storySlug: string;
  master: ProjectMasterSettingWorkspace;
  onSaved: () => void;
}) {
  const [currentMaster, setCurrentMaster] = useState(master);
  const summary = currentMaster.summary;
  const metrics = [
    { label: "世界规则", value: summary.world_rule_count },
    { label: "人物", value: summary.character_count },
    { label: "时间线", value: summary.timeline_event_count },
    { label: "伏笔", value: summary.plot_thread_count },
    { label: "章节摘要", value: summary.chapter_brief_count },
  ];
  const worldRules = unknownList(currentMaster.world.world_rules, 4);
  const limits = unknownList(currentMaster.world.power_system_limits, 3);
  const locations = unknownList(currentMaster.world.locations, 3);
  const factions = unknownList(currentMaster.world.factions, 3);
  const hasWorldFacts =
    worldRules.length > 0 || limits.length > 0 || locations.length > 0 || factions.length > 0;
  const canEdit = currentMaster.capabilities.can_edit && currentMaster.status === "ready";
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<MasterSettingDraft>(() => initMasterDraft(master));
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  useEffect(() => {
    setCurrentMaster(master);
    setDraft(initMasterDraft(master));
  }, [master]);

  async function saveMasterSetting() {
    if (!canEdit || saving) return;
    setSaving(true);
    setSaveError(null);
    setSavedMsg(null);
    const patch: MasterSettingPatch = {
      display_name: draft.displayName.trim(),
      genre: draft.genre.trim(),
      world_rules: linesToList(draft.worldRules),
      power_system_limits: linesToList(draft.powerLimits),
      forbidden_additions: linesToList(draft.forbiddenAdditions),
    };
    try {
      const result = await api.updateMasterSetting(storySlug, patch);
      setEditing(false);
      setCurrentMaster(result.master_setting_workspace);
      setDraft(initMasterDraft(result.master_setting_workspace));
      setSavedMsg(result.backup ? `设定已保存，备份 ${result.backup}` : "设定已保存");
      window.setTimeout(onSaved, 2500);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="project-workspace__section master-setting">
      <SectionTitle
        title="设定工作台"
        status={`${statusLabel(currentMaster.status)} · ${
          currentMaster.capabilities.read_only ? "只读" : "可编辑"
        }`}
      />
      {currentMaster.warnings.length > 0 ? (
        <div className="risk-strip">
          {currentMaster.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : (
        <p className="project-workspace__ok">已聚合世界设定、人物状态、时间线和章节记忆。</p>
      )}

      <div className="master-setting__metrics">
        {metrics.map((metric) => (
          <div className="master-setting__metric" key={metric.label}>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </div>

      <div className="master-setting__editbar">
        {canEdit ? (
          editing ? (
            <>
              <button
                type="button"
                className="workspace-btn workspace-btn--primary"
                onClick={saveMasterSetting}
                disabled={saving}
              >
                {saving ? "保存中…" : "保存设定"}
              </button>
              <button
                type="button"
                className="workspace-btn"
                onClick={() => {
                  setEditing(false);
                  setSaveError(null);
                  setDraft(initMasterDraft(currentMaster));
                }}
                disabled={saving}
              >
                放弃修改
              </button>
            </>
          ) : (
            <button
              type="button"
              className="workspace-btn"
              onClick={() => {
                setEditing(true);
                setSaveError(null);
                setSavedMsg(null);
                setDraft(initMasterDraft(currentMaster));
              }}
            >
              编辑设定
            </button>
          )
        ) : (
          <span>{currentMaster.capabilities.edit_note}</span>
        )}
        {savedMsg && <strong>{savedMsg}</strong>}
      </div>
      {saveError && <p className="master-setting__error">{saveError}</p>}

      {editing && (
        <div className="master-setting__editor">
          <label className="master-setting__field">
            <span>作品名</span>
            <input
              value={draft.displayName}
              onChange={(event) =>
                setDraft((prev) => ({ ...prev, displayName: event.target.value }))
              }
              disabled={saving}
            />
          </label>
          <label className="master-setting__field">
            <span>题材</span>
            <input
              value={draft.genre}
              onChange={(event) =>
                setDraft((prev) => ({ ...prev, genre: event.target.value }))
              }
              disabled={saving}
            />
          </label>
          <label className="master-setting__field master-setting__field--wide">
            <span>世界规则</span>
            <textarea
              value={draft.worldRules}
              onChange={(event) =>
                setDraft((prev) => ({ ...prev, worldRules: event.target.value }))
              }
              disabled={saving}
            />
          </label>
          <label className="master-setting__field">
            <span>力量限制</span>
            <textarea
              value={draft.powerLimits}
              onChange={(event) =>
                setDraft((prev) => ({ ...prev, powerLimits: event.target.value }))
              }
              disabled={saving}
            />
          </label>
          <label className="master-setting__field">
            <span>禁用设定</span>
            <textarea
              value={draft.forbiddenAdditions}
              onChange={(event) =>
                setDraft((prev) => ({
                  ...prev,
                  forbiddenAdditions: event.target.value,
                }))
              }
              disabled={saving}
            />
          </label>
        </div>
      )}

      <div className="master-setting__layout">
        <article className="master-setting__block master-setting__block--wide">
          <div className="master-setting__block-head">
            <h3>{currentMaster.world.display_name || "世界设定"}</h3>
            <span>{currentMaster.world.genre || "题材未标注"}</span>
          </div>
          {!hasWorldFacts ? (
            <p className="muted tiny">暂无可展示的世界规则。</p>
          ) : (
            <div className="master-setting__facts">
              <FactList label="规则" items={worldRules} empty="暂无规则" />
              <FactList label="限制" items={limits} empty="暂无限制" />
              <FactList label="地点" items={locations} empty="暂无地点" />
              <FactList label="势力" items={factions} empty="暂无势力" />
            </div>
          )}
        </article>

        <article className="master-setting__block">
          <SectionTitle title="人物状态" status={`${currentMaster.characters.length} 人`} />
          {currentMaster.characters.length === 0 ? (
            <p className="muted tiny">暂无人物状态样例。</p>
          ) : (
            <ul className="master-setting__list">
              {currentMaster.characters.slice(0, 4).map((character) => (
                <li key={character.character_id || character.name}>
                  <strong>{character.name || character.character_id}</strong>
                  <span>
                    {character.narrative_role || "角色"} ·{" "}
                    {character.current_state.location || "位置未明"} ·{" "}
                    {character.current_state.emotion || "状态未明"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="master-setting__block">
          <SectionTitle title="时间线" status={`${currentMaster.timeline.event_count} 件`} />
          {currentMaster.timeline.samples.length === 0 ? (
            <p className="muted tiny">暂无时间线样例。</p>
          ) : (
            <ul className="master-setting__list">
              {currentMaster.timeline.samples.slice(0, 3).map((event) => (
                <li key={`${event.chapter ?? "x"}-${event.title}-${event.source_ref}`}>
                  <strong>{event.chapter ? `第 ${event.chapter} 章` : "未标章节"}</strong>
                  <span>{event.title || event.summary || "未记录事件"}</span>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="master-setting__block">
          <SectionTitle title="伏笔线" status={`${currentMaster.plot_threads.thread_count} 条`} />
          {currentMaster.plot_threads.active_threads.length === 0 ? (
            <p className="muted tiny">暂无活跃伏笔。</p>
          ) : (
            <ul className="master-setting__list">
              {currentMaster.plot_threads.active_threads.slice(0, 3).map((thread) => (
                <li key={thread.id || thread.title}>
                  <strong>{thread.status || "未标状态"}</strong>
                  <span>{thread.title || thread.id}</span>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="master-setting__block">
          <SectionTitle title="章节摘要" status={`${currentMaster.chapter_briefs.chapter_count} 章`} />
          {currentMaster.chapter_briefs.samples.length === 0 ? (
            <p className="muted tiny">暂无章节摘要。</p>
          ) : (
            <ul className="master-setting__list">
              {currentMaster.chapter_briefs.samples.slice(0, 3).map((chapter) => (
                <li key={`${chapter.chapter ?? "x"}-${chapter.title}-${chapter.source_ref}`}>
                  <strong>{chapter.chapter ? `第 ${chapter.chapter} 章` : "未标章节"}</strong>
                  <span>{chapter.summary || chapter.title || "未记录摘要"}</span>
                </li>
              ))}
            </ul>
          )}
        </article>
      </div>

      {currentMaster.next_steps.length > 0 && (
        <div className="project-workspace__steps master-setting__steps">
          {currentMaster.next_steps.slice(0, 4).map((step) => (
            <span key={step}>{step}</span>
          ))}
        </div>
      )}
      <p className="master-setting__note">{currentMaster.capabilities.edit_note}</p>
    </section>
  );
}

function FactList({ label, items, empty }: { label: string; items: string[]; empty: string }) {
  return (
    <div className="master-setting__fact-list">
      <strong>{label}</strong>
      <span>{items.length > 0 ? items.join("、") : empty}</span>
    </div>
  );
}

function CardsWorkspacePanel({ storySlug }: { storySlug: string }) {
  const cardsState = useAsync(() => api.getCardsWorkspace(storySlug), [storySlug]);
  const report = cardsState.data;
  const statusText = cardsState.loading
    ? "读取中"
    : report
      ? `${report.summary.card_count} 张卡片`
      : "未读取";

  return (
    <section className="project-workspace__section cards-workspace">
      <SectionTitle title="设定卡片" status={statusText} />
      {cardsState.loading && <Loading label="正在整理设定卡片…" />}
      {cardsState.error && (
        <ErrorState message={cardsState.error} onRetry={cardsState.reload} />
      )}
      {!cardsState.loading && !cardsState.error && report && (
        <CardsWorkspaceReportView report={report} />
      )}
    </section>
  );
}

function CardsWorkspaceReportView({ report }: { report: CardsWorkspaceReport }) {
  const visibleCards = [
    ...report.cards.filter((card) => card.type === "world"),
    ...report.cards.filter((card) => card.type === "style"),
    ...report.cards.filter((card) => card.type === "character"),
  ];

  return (
    <>
      <div className="master-setting__metrics">
        <div className="master-setting__metric">
          <span>世界卡</span>
          <strong>{report.summary.world_card_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>角色卡</span>
          <strong>{report.summary.character_card_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>风格卡</span>
          <strong>{report.summary.style_card_count}</strong>
        </div>
        <div className="master-setting__metric">
          <span>可轻编辑</span>
          <strong>{report.summary.editable_card_count}</strong>
        </div>
      </div>

      {report.warnings.length > 0 ? (
        <div className="risk-strip">
          {report.warnings.slice(0, 4).map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : (
        <p className="project-workspace__ok">设定卡片已从本地记忆资产整理完成。</p>
      )}

      <div className="cards-workspace__grid">
        {visibleCards.slice(0, 10).map((card) => (
          <CardsWorkspaceCardView card={card} key={card.id} />
        ))}
      </div>

      <div className="project-workspace__steps">
        {report.next_steps.slice(0, 3).map((step) => (
          <span key={step}>{step}</span>
        ))}
      </div>
      <p className="master-setting__note">{report.boundaries[0]}</p>
    </>
  );
}

function CardsWorkspaceCardView({ card }: { card: CardsWorkspaceCard }) {
  const readyFields = card.fields.filter((field) => field.status === "ready");
  return (
    <article className="cards-workspace__card">
      <div className="cards-workspace__head">
        <div>
          <strong>{card.title}</strong>
          <span>{card.subtitle || cardTypeLabel(card.type)}</span>
        </div>
        <em>{card.status_label}</em>
      </div>
      {readyFields.length === 0 ? (
        <p className="muted tiny">暂无可展示字段。</p>
      ) : (
        <div className="cards-workspace__fields">
          {readyFields.slice(0, 4).map((field) => (
            <div className="cards-workspace__field" key={field.label}>
              <span>{field.label}</span>
              <strong>{field.items.slice(0, 3).join("、")}</strong>
            </div>
          ))}
        </div>
      )}
      {card.editable_fields.length > 0 && (
        <p className="cards-workspace__edit-note">可通过上方设定工作台轻编辑。</p>
      )}
    </article>
  );
}

function cardTypeLabel(type: string): string {
  if (type === "world") return "世界卡";
  if (type === "character") return "角色卡";
  if (type === "style") return "风格卡";
  return "设定卡";
}

function initMasterDraft(master: ProjectMasterSettingWorkspace): MasterSettingDraft {
  return {
    displayName: master.world.display_name,
    genre: master.world.genre,
    worldRules: unknownList(master.world.world_rules, 20).join("\n"),
    powerLimits: unknownList(master.world.power_system_limits, 12).join("\n"),
    forbiddenAdditions: unknownList(master.world.forbidden_additions, 20).join("\n"),
  };
}

function linesToList(value: string): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const line of value.split(/\r?\n/)) {
    const text = line.trim();
    if (!text || seen.has(text)) continue;
    seen.add(text);
    out.push(text);
  }
  return out;
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
            {retrieval.samples.slice(0, 4).map((hit, index) => (
              <li key={`${hit.run_id}-${hit.branch_id}-${hit.source_ref || index}`}>
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
    attention: "需留意",
    blocked: "需修复",
  };
  return map[value] ?? value;
}

function vectorReadinessStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready: "继续现状",
    attention: "先补底座",
    monitor: "进入监控",
    triggered: "可做探针",
  };
  return map[value] ?? statusLabel(value);
}

function vectorLayerReadinessLabel(value: string): string {
  const map: Record<string, string> = {
    evaluate: "可评估",
    design_spike: "先做探针",
    monitor: "监控中",
    deferred: "暂缓",
  };
  return map[value] ?? value;
}

function graphTriggerStatusLabel(value: string): string {
  const map: Record<string, string> = {
    not_triggered: "暂不触发",
    monitor: "继续观察",
    triggered: "可做探针",
    ready_for_spike: "可做设计",
    ready_for_spike_design: "可设计探针",
    needs_more_evidence: "需更多证据",
    deferred: "暂缓",
    ready: "正常",
    attention: "需关注",
  };
  return map[value] ?? statusLabel(value);
}

function graphCandidateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    candidate: "候选",
    monitor: "观察",
    deferred: "暂缓",
  };
  return map[value] ?? value;
}

function graphDesignStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_spike: "可做设计",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphTriggerStatusLabel(value);
}

function graphDesignGateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    design_pack_ready: "设计包就绪",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphTriggerStatusLabel(value);
}

function graphDesignInputStatusLabel(value: string): string {
  const map: Record<string, string> = {
    required: "必需",
    optional: "可选",
    missing: "缺失",
    deferred: "暂缓",
  };
  return map[value] ?? value;
}

function graphShadowStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_shadow_compare: "可做对照",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphDesignStatusLabel(value);
}

function graphShadowGateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    shadow_compare_ready: "对照就绪",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphShadowStatusLabel(value);
}

function graphShadowDecisionLabel(value: string): string {
  const map: Record<string, string> = {
    shadow_compare: "进入对照",
    collect_samples: "补样本",
    collect_foundation_evidence: "补基础证据",
    defer: "暂缓",
  };
  return map[value] ?? value;
}

function graphShadowResultLabel(value: string): string {
  const map: Record<string, string> = {
    ready: "可验证",
    needs_evidence: "需证据",
  };
  return map[value] ?? graphDesignInputStatusLabel(value);
}

function graphCaseStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready: "可展开",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphShadowStatusLabel(value);
}

function graphCaseGateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    case_matrix_ready: "矩阵就绪",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphCaseStatusLabel(value);
}

function graphCaseEvidenceStatusLabel(value: string): string {
  const map: Record<string, string> = {
    local_evidence_ready: "本地证据就绪",
    needs_local_evidence: "需本地证据",
    deferred: "暂缓",
  };
  return map[value] ?? value;
}

function graphProviderBoundaryStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_boundary_review: "可审查",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphCaseStatusLabel(value);
}

function graphProviderBoundaryGateLabel(value: string): string {
  const map: Record<string, string> = {
    boundary_matrix_ready: "边界就绪",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderBoundaryStatusLabel(value);
}

function graphProviderBoundaryCellLabel(value: string): string {
  const map: Record<string, string> = {
    requires_opt_in: "需显式开启",
    deferred: "暂缓",
  };
  return map[value] ?? value;
}

function graphOfflineReplayStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_offline_replay: "Replay 就绪",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderBoundaryStatusLabel(value);
}

function graphOfflineReplayReportStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_review: "待人工复核",
  };
  return map[value] ?? graphOfflineReplayStatusLabel(value);
}

function graphOfflineReplayGateLabel(value: string): string {
  const map: Record<string, string> = {
    offline_replay_ready: "Replay 就绪",
    offline_replay_report_ready: "报告就绪",
    fixture_pack_ready: "前置包就绪",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphOfflineReplayStatusLabel(value);
}

function graphOfflineReplayItemLabel(value: string): string {
  const map: Record<string, string> = {
    planned: "已计划",
    mock_candidate_gain: "候选收益",
    manual_review_required: "待人工复核",
    dry_run_fixture_ready: "dry-run 就绪",
    manual_review_before_real_provider_config: "先人工复核",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphOfflineReplayStatusLabel(value);
}

function graphProviderFixturePackStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_fixture_pack: "前置包就绪",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphOfflineReplayReportStatusLabel(value);
}

function graphProviderReadinessGateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_opt_in_review: "可人工复核",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    collect_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderFixturePackStatusLabel(value);
}

function graphProviderReadinessItemLabel(value: string): string {
  const map: Record<string, string> = {
    manual_review_ready: "可人工复核",
    manual_review_required: "需人工确认",
    manual_review_ready_no_real_config: "只可人工复核",
    passed: "通过",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderReadinessGateStatusLabel(value);
}

function graphProviderRunbookStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_dry_run: "可人工 dry-run",
    manual_dry_run_ready: "可人工 dry-run",
    manual_runbook_ready_no_real_config: "SOP 就绪",
    blocked_before_manual_dry_run: "dry-run 前阻塞",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderReadinessItemLabel(value);
}

function graphProviderResultTemplateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_result_recording: "可人工记录",
    manual_result_template_ready: "模板就绪",
    result_template_ready_no_real_config: "记录模板就绪",
    blocked_before_result_recording: "记录前阻塞",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderRunbookStatusLabel(value);
}

function graphProviderMockResultStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_review: "待人工复核",
    mock_result_report_ready: "报告就绪",
    mock_filled_result_ready: "填充就绪",
    mock_result_review_required_no_real_config: "仅可人工复核",
    collect_more_evidence: "继续补证据",
    pause_no_stable_gain: "暂停：收益不稳定",
    upgrade_manual_opt_in_spike: "另开真实 opt-in spike",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderResultTemplateStatusLabel(value);
}

function graphProviderReviewGateStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_review_gate: "可人工复核",
    manual_review_gate_ready: "门禁就绪",
    manual_review_required: "需人工复核",
    review_required_no_real_provider_config: "仅可人工复核",
    collect_more_evidence: "继续补证据",
    manual_approval_required: "需人工审批",
    pause_no_stable_gain: "暂停：收益不稳定",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderMockResultStatusLabel(value);
}

function graphProviderManualApprovalStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_approval_pack: "审批包就绪",
    manual_approval_pack_ready: "审批包就绪",
    manual_approval_required: "需人工审批",
    approval_pack_ready_no_real_provider_config: "仅可人工审批",
    signature_required: "需签收",
    confirmation_required: "需确认",
    collect_more_evidence: "继续补证据",
    manual_approval_required_gate: "需人工审批",
    pause_no_stable_gain: "暂停：收益不稳定",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderReviewGateStatusLabel(value);
}

function graphProviderApprovalEvidenceStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_manual_approval_evidence_checklist: "核对表就绪",
    evidence_checklist_ready: "核对表就绪",
    manual_signoff_required: "待人工签收",
    materials_ready_signoff_pending: "材料齐，待签收",
    materials_gap: "材料缺口",
    materials_ready: "材料齐备",
    checklist_ready_no_real_provider_config: "仅可核对证据",
    complete_no_real_config: "证据齐备",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderManualApprovalStatusLabel(value);
}

function graphProviderOptInSnapshotStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_evidence_snapshot: "快照就绪",
    opt_in_evidence_snapshot_ready: "快照就绪",
    blocked_by_pending_signoff: "签收阻塞",
    blocked_by_material_gap: "材料阻塞",
    materials_ready_real_config_still_blocked: "材料齐，仍禁真实配置",
    snapshot_ready_real_provider_still_blocked: "仍禁止真实配置",
    needs_more_evidence: "补证据",
    blocked: "已阻塞",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderApprovalEvidenceStatusLabel(value);
}

function graphProviderNoGoMatrixStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_no_go_matrix: "矩阵就绪",
    no_go_matrix_ready: "矩阵就绪",
    no_go_matrix_ready_real_provider_still_blocked: "仍禁止真实配置",
    blocked: "已阻塞",
    clear: "无阻塞",
    clear_no_real_config: "仅证据无阻塞",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderOptInSnapshotStatusLabel(value);
}

function graphProviderOperatorChecklistStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_operator_checklist: "清单就绪",
    operator_checklist_ready: "清单就绪",
    operator_checklist_ready_real_provider_still_blocked: "仍禁止真实配置",
    blocked: "已阻塞",
    review: "待复核",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderNoGoMatrixStatusLabel(value);
}

function graphProviderReviewPacketStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_review_packet: "复核包就绪",
    review_packet_ready: "复核包就绪",
    review_packet_ready_real_provider_still_blocked: "仍禁止真实配置",
    blocked: "已阻塞",
    review: "待复核",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderOperatorChecklistStatusLabel(value);
}

function graphProviderDecisionLedgerStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_decision_ledger_preview: "账本预览就绪",
    decision_ledger_preview_ready: "账本预览就绪",
    decision_ledger_preview_ready_real_provider_still_blocked: "仍禁止真实配置",
    blocked: "已阻塞",
    review: "待复核",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderReviewPacketStatusLabel(value);
}

function graphProviderFinalReadinessStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_opt_in_final_readiness_summary: "最终摘要就绪",
    final_readiness_summary_ready: "最终摘要就绪",
    final_readiness_summary_ready_real_provider_still_blocked: "仍禁止真实配置",
    not_ready_for_real_provider: "未就绪",
    blocked: "已阻塞",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderDecisionLedgerStatusLabel(value);
}

function graphProviderHumanSignoffSchemaStatusLabel(value: string): string {
  const map: Record<string, string> = {
    ready_for_human_signoff_schema_draft: "签收 Schema 就绪",
    human_signoff_schema_draft_ready: "签收 Schema 就绪",
    human_signoff_schema_draft_ready_real_provider_still_blocked: "仍禁止真实配置",
    blocked: "已阻塞",
    needs_more_evidence: "补证据",
    deferred: "暂缓",
  };
  return map[value] ?? graphProviderFinalReadinessStatusLabel(value);
}

function embeddingSamplesStatusLabel(value: string): string {
  const map: Record<string, string> = {
    insufficient_samples: "待收集",
    candidate: "可对照",
    attention: "先补记忆",
    blocked: "需修复",
    covered: "已覆盖",
  };
  return map[value] ?? value;
}

function embeddingDiagnosisLabel(value: string): string {
  const map: Record<string, string> = {
    lexical_gap: "词面缺口",
    memory_gap: "记忆缺口",
    already_covered: "已命中",
    invalid_sample: "样本需修复",
  };
  return map[value] ?? value;
}

function retrievalExportPackStatusLabel(value: string): string {
  const map: Record<string, string> = {
    empty: "暂无样本",
    ready: "可导出",
    attention: "需复核",
    blocked: "需修复",
  };
  return map[value] ?? value;
}

function embeddingMockReportStatusLabel(value: string): string {
  const map: Record<string, string> = {
    empty: "暂无样本",
    candidate: "可继续评估",
    attention: "先补记忆",
    blocked: "需修复",
    covered: "已覆盖",
  };
  return map[value] ?? value;
}

function retrievalReplayReportStatusLabel(value: string): string {
  const map: Record<string, string> = {
    empty: "暂无样本",
    ready: "可复跑",
    attention: "需复核",
    blocked: "需修复",
  };
  return map[value] ?? value;
}

function retrievalMigrationPackStatusLabel(value: string): string {
  const map: Record<string, string> = {
    empty: "暂无样本",
    ready: "可迁移",
    attention: "需补目标",
    blocked: "需修复",
  };
  return map[value] ?? value;
}

function unknownList(items: unknown[], limit: number): string[] {
  return items.map(unknownText).filter(Boolean).slice(0, limit);
}

function unknownText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) {
    return value.map(unknownText).filter(Boolean).slice(0, 3).join("、");
  }
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    const preferred = [
      "name",
      "title",
      "label",
      "rule",
      "summary",
      "description",
      "value",
    ];
    const parts = preferred.map((key) => unknownText(record[key])).filter(Boolean);
    if (parts.length > 0) return parts.slice(0, 2).join("：");
    return Object.values(record).map(unknownText).filter(Boolean).slice(0, 2).join("：");
  }
  return "";
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

function isCanonReplayRangePayload(
  payload: ProjectCreationLoopAction["payload"],
): payload is CanonReplayRangeRequest {
  return Boolean(
    payload &&
      "baseline_run_id" in payload &&
      "chapter_start" in payload &&
      "chapter_end" in payload,
  );
}

function isWorldlineJudgementPayload(
  payload: ProjectCreationLoopAction["payload"],
): payload is WorldlineJudgementRequest {
  return Boolean(payload && "story_slug" in payload);
}

function collectActionRequirements(
  actions: ProjectCreationLoopAction[],
): ProjectCreationLoopActionRequirement[] {
  const seen = new Set<string>();
  const items: ProjectCreationLoopActionRequirement[] = [];
  for (const action of actions) {
    for (const requirement of action.requirements ?? []) {
      if (seen.has(requirement.id)) continue;
      seen.add(requirement.id);
      items.push(requirement);
    }
  }
  return items;
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

function auditActionLabel(action: string, fallback: string): string {
  const map: Record<string, string> = {
    import_review_generated: "导入检查",
    worldline_selected: "选择世界线",
    state_execution_applied: "应用状态覆盖",
    state_execution_rolled_back: "回滚状态覆盖",
    master_setting_updated: "设定更新",
    creation_loop_closed: "闭环收口",
    manual_note: "人工备注",
    rights_reviewed: "版权声明",
    retention_policy_reviewed: "保留策略",
    project_space_reviewed: "项目空间",
    audit_reviewed: "审计复核",
  };
  return map[action] ?? fallback ?? action;
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
