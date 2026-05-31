import { useEffect, useState } from "react";
import type {
  BranchDetail,
  DynamicActionRegistry,
  EmergenceReport,
  NarrativeDiagnostics,
  RunnerStateExecutionReport,
  RuntimeMemoryContext,
} from "../api/types";
import { ApiError, api } from "../api/client";
import { EmptyState } from "./common/States";

export function ArtifactPanel({ branch }: { branch: BranchDetail }) {
  const hasAny =
    hasRuntimeMemory(branch.runtime_memory_context) ||
    hasObject(branch.act_director_plan) ||
    hasRegistry(branch.dynamic_action_registry) ||
    hasDiagnostics(branch.narrative_diagnostics) ||
    hasEmergence(branch.emergence_nodes) ||
    hasStateExecution(branch.runner_state_execution_report);

  if (!hasAny) {
    return (
      <EmptyState
        title="该分支暂无机制档案"
        hint="旧 run 或对应 artifact 尚未生成时，会保持空态。"
      />
    );
  }

  return (
    <div>
      <RuntimeMemorySection memory={branch.runtime_memory_context} />
      <ActionPlanSection plan={branch.act_director_plan} />
      <ActionRegistrySection registry={branch.dynamic_action_registry} />
      <NarrativeDiagnosticsSection diagnostics={branch.narrative_diagnostics} />
      <EmergenceSection report={branch.emergence_nodes} branchId={branch.branch_id} />
      <StateExecutionSection
        runId={branch.run_id}
        initialReport={branch.runner_state_execution_report}
      />
    </div>
  );
}

function RuntimeMemorySection({
  memory,
}: {
  memory: RuntimeMemoryContext | null | undefined;
}) {
  if (!hasRuntimeMemory(memory)) {
    return <MissingSection title="运行记忆" hint="未找到 runtime_memory_context.json。" />;
  }
  const layers = memory.consumed_layers || [];
  const resolved = memory.resolved_query_entities || [];
  const aliases = memory.entity_aliases;

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">运行记忆</h3>
      <Row k="查询" v={memory.query || "未记录"} />
      <Row k="章节" v={`第 ${memory.current_chapter || 1} 章`} />
      <div className="chip-row" style={{ marginBottom: 8 }}>
        {layers.length > 0 ? (
          layers.map((layer) => (
            <span key={layer} className="memory-chip">
              {labelLayer(layer)}
            </span>
          ))
        ) : (
          <span className="muted tiny">没有消费到记忆层。</span>
        )}
      </div>
      <Row
        k="别名"
        v={`${labelAliasStatus(aliases?.status)} · ${aliases?.count ?? 0} 个实体`}
      />
      {resolved.length > 0 && (
        <div className="chip-row">
          {resolved.map((entity) => (
            <span key={entity} className="memory-chip memory-chip--entity">
              {entity}
            </span>
          ))}
        </div>
      )}
      <Warnings warnings={memory.warnings} />
    </section>
  );
}

function ActionPlanSection({ plan }: { plan: BranchDetail["act_director_plan"] }) {
  if (!hasObject(plan)) {
    return <MissingSection title="动作计划" hint="未找到 act_director_plan.json。" />;
  }
  const steps = Array.isArray(plan.steps) ? plan.steps : [];

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">动作计划</h3>
      <Row k="世系" v={plan.lineage_type || "未记录"} />
      <Row k="动作数" v={`${steps.length}`} />
      {steps.length === 0 ? (
        <p className="muted tiny">没有可展示的角色动作。</p>
      ) : (
        steps.slice(0, 4).map((step, index) => (
          <div key={step.action_id || index} className="artifact-item">
            <div className="artifact-item__title">
              {step.character_name || step.character_id || "角色"}
              {step.action_label ? ` · ${step.action_label}` : ""}
            </div>
            <div className="muted tiny">
              {step.branch_label || step.branch_axis_id || "分支动作"}
              {step.risk ? ` · 风险 ${riskLabel(step.risk)}` : ""}
            </div>
            <InlineList label="前置" items={step.preconditions} />
            <InlineList label="效果" items={step.effects} />
            {step.failure_reason && (
              <div className="muted tiny">失败原因：{step.failure_reason}</div>
            )}
          </div>
        ))
      )}
      <Warnings warnings={plan.warnings} />
    </section>
  );
}

function ActionRegistrySection({
  registry,
}: {
  registry: DynamicActionRegistry | null | undefined;
}) {
  if (!hasRegistry(registry)) {
    return <MissingSection title="动作注册表" hint="未找到 dynamic_action_registry.yaml。" />;
  }
  const actions = Array.isArray(registry.actions) ? registry.actions : [];
  const aliasCount = registry.aliases ? Object.keys(registry.aliases).length : 0;
  const count =
    typeof registry.summary?.action_count === "number"
      ? registry.summary.action_count
      : actions.length;

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">动作注册表</h3>
      <Row k="动作" v={`${count}`} />
      <Row k="别名" v={`${aliasCount}`} />
      {actions.slice(0, 4).map((action, index) => (
        <div key={action.action_type || index} className="artifact-item">
          <div className="artifact-item__title">
            {action.action_label || action.action_type || "未命名动作"}
          </div>
          <InlineList label="别名" items={action.aliases} />
          <InlineList label="效果" items={action.effects} />
        </div>
      ))}
      <Warnings warnings={registry.warnings} />
    </section>
  );
}

function NarrativeDiagnosticsSection({
  diagnostics,
}: {
  diagnostics: NarrativeDiagnostics | null | undefined;
}) {
  if (!hasDiagnostics(diagnostics)) {
    return <MissingSection title="叙事诊断" hint="未找到 narrative_diagnostics.json。" />;
  }
  const metrics = diagnostics.metrics || {};
  const curve = Array.isArray(diagnostics.tension_curve)
    ? diagnostics.tension_curve
    : [];

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">叙事诊断</h3>
      <Row k="字数" v={numText(metrics.char_count)} />
      <Row k="句段" v={`${metrics.sentence_count ?? 0} 句 · ${metrics.paragraph_count ?? 0} 段`} />
      <Row k="节奏" v={numText(metrics.pacing)} />
      {curve.length > 0 && (
        <div className="artifact-curve" aria-label="张力曲线">
          {curve.slice(0, 8).map((point) => (
            <span
              key={point.index}
              className="artifact-curve__bar"
              style={{ height: `${Math.max(8, Math.min(48, point.tension * 48))}px` }}
              title={`第 ${point.index} 段：${formatScore(point.tension)}`}
            />
          ))}
        </div>
      )}
      <Warnings warnings={diagnostics.warnings} />
      <InlineList label="建议" items={diagnostics.suggestions} />
    </section>
  );
}

function EmergenceSection({
  report,
  branchId,
}: {
  report: EmergenceReport | null | undefined;
  branchId: string;
}) {
  if (!hasEmergence(report)) {
    return <MissingSection title="涌现节点" hint="未找到 emergence_nodes.json。" />;
  }
  const allNodes = Array.isArray(report.nodes) ? report.nodes : [];
  const nodes = allNodes.filter((node) => !node.branch_id || node.branch_id === branchId);
  const visibleNodes = nodes.length > 0 ? nodes : allNodes;
  const nodeCount =
    typeof report.summary?.node_count === "number"
      ? report.summary.node_count
      : allNodes.length;

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">涌现节点</h3>
      <Row k="节点" v={`${nodeCount}`} />
      {visibleNodes.length === 0 ? (
        <p className="muted tiny">没有可展示的涌现节点。</p>
      ) : (
        visibleNodes.slice(0, 4).map((node, index) => (
          <div key={node.node_id || index} className="artifact-item">
            <div className="artifact-item__title">
              {node.title || node.node_id || "未命名节点"}
            </div>
            <div className="muted tiny">
              {node.status ? statusLabel(node.status) : "未分级"}
              {typeof node.score === "number" ? ` · ${formatScore(node.score)}` : ""}
            </div>
            {node.description && (
              <div className="artifact-item__text">{node.description}</div>
            )}
            {node.recommendation && (
              <div className="muted tiny">建议：{node.recommendation}</div>
            )}
          </div>
        ))
      )}
      <Warnings warnings={report.warnings} />
    </section>
  );
}

function StateExecutionSection({
  runId,
  initialReport,
}: {
  runId: string;
  initialReport: RunnerStateExecutionReport | null | undefined;
}) {
  const [report, setReport] = useState(initialReport);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setReport(initialReport);
    setError("");
  }, [initialReport, runId]);

  async function evaluate() {
    setWorking(true);
    setError("");
    try {
      setReport(await api.evaluateRunnerStateExecution(runId));
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "状态执行评估失败");
    } finally {
      setWorking(false);
    }
  }

  const hasReport = hasStateExecution(report);
  const summary = report?.summary;
  const candidates = report?.candidates || [];

  return (
    <section className="expl-section">
      <h3 className="expl-section__title">状态执行评估</h3>
      {!hasReport ? (
        <>
          <p className="muted tiny">
            尚未生成 runner_state_execution_report.json。评估只做干运行，不写回状态。
          </p>
          <button className="btn btn--ghost" onClick={evaluate} disabled={working}>
            {working ? "评估中..." : "生成评估"}
          </button>
        </>
      ) : (
        <>
          <Row k="模式" v={report.mode === "dry_run" ? "干运行" : report.mode} />
          <Row
            k="候选"
            v={`${summary?.candidate_count ?? candidates.length} 个 · 可执行 ${
              summary?.executable_count ?? 0
            } · 需复核 ${summary?.review_required_count ?? 0} · 阻断 ${
              summary?.blocked_count ?? 0
            }`}
          />
          <Row
            k="安全"
            v={
              report.safety?.writes_state_snapshot
                ? "会写状态"
                : "不写 state_snapshot，只生成报告"
            }
          />
          {candidates.slice(0, 4).map((candidate) => (
            <div key={candidate.candidate_id} className="artifact-item">
              <div className="artifact-item__title">
                {candidate.character_name || candidate.character_id || "角色"}
                {candidate.action_label ? ` · ${candidate.action_label}` : ""}
              </div>
              <div className="muted tiny">
                {gateLabel(candidate.gate_status)}
                {candidate.risk ? ` · 风险 ${riskLabel(candidate.risk)}` : ""}
              </div>
              {candidate.state_deltas.slice(0, 2).map((delta, index) => (
                <div key={`${candidate.candidate_id}-${index}`} className="muted tiny">
                  {delta.field}：{formatUnknown(delta.old_value)}
                  {" -> "}
                  {formatUnknown(delta.new_value)}
                </div>
              ))}
              <InlineList label="阻断" items={candidate.blockers} />
              <InlineList label="提示" items={candidate.warnings} />
            </div>
          ))}
          <InlineList label="MVP 前置" items={report.safety?.required_before_mvp} />
          <Warnings warnings={report.warnings} />
          <button className="btn btn--ghost" onClick={evaluate} disabled={working}>
            {working ? "评估中..." : "重新评估"}
          </button>
        </>
      )}
      {error && <div className="runtime-warning">{error}</div>}
    </section>
  );
}

function MissingSection({ title, hint }: { title: string; hint: string }) {
  return (
    <section className="expl-section">
      <h3 className="expl-section__title">{title}</h3>
      <p className="muted tiny">{hint}</p>
    </section>
  );
}

function Row({ k, v }: { k: string; v?: string | null }) {
  if (!v) return null;
  return (
    <div className="kv">
      <span className="kv__k">{k}</span>
      <span className="kv__v">{v}</span>
    </div>
  );
}

function InlineList({
  label,
  items,
}: {
  label: string;
  items?: string[] | null;
}) {
  if (!items || items.length === 0) return null;
  return <div className="muted tiny">{label}：{items.join("、")}</div>;
}

function Warnings({ warnings }: { warnings?: string[] | null }) {
  if (!warnings || warnings.length === 0) return null;
  return (
    <div style={{ marginTop: 8 }}>
      {warnings.slice(0, 3).map((warning, index) => (
        <div key={index} className="runtime-warning">
          {warning}
        </div>
      ))}
    </div>
  );
}

function hasObject(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && Object.keys(value).length > 0;
}

function hasRuntimeMemory(
  value: RuntimeMemoryContext | null | undefined,
): value is RuntimeMemoryContext {
  return hasObject(value);
}

function hasRegistry(
  value: DynamicActionRegistry | null | undefined,
): value is DynamicActionRegistry {
  return hasObject(value);
}

function hasDiagnostics(
  value: NarrativeDiagnostics | null | undefined,
): value is NarrativeDiagnostics {
  return hasObject(value);
}

function hasEmergence(
  value: EmergenceReport | null | undefined,
): value is EmergenceReport {
  return hasObject(value);
}

function hasStateExecution(
  value: RunnerStateExecutionReport | null | undefined,
): value is RunnerStateExecutionReport {
  return hasObject(value);
}

function numText(value?: number) {
  return typeof value === "number" ? `${Number.isInteger(value) ? value : value.toFixed(2)}` : "0";
}

function formatScore(value: number) {
  return value.toFixed(2);
}

function labelLayer(layer: string) {
  const labels: Record<string, string> = {
    entity_aliases: "实体别名",
    canon_ledger: "正史账本",
    chapter_brief: "章节摘要",
    volume_brief: "卷摘要",
    contract: "故事合约",
    fact: "正史事实",
  };
  return labels[layer] || layer;
}

function labelAliasStatus(status: string | undefined) {
  if (status === "ready") return "已就绪";
  if (status === "damaged") return "文件损坏，已降级";
  if (status === "missing") return "未生成";
  return status || "未知";
}

function riskLabel(risk: string) {
  if (risk === "low") return "低";
  if (risk === "medium") return "中";
  if (risk === "high") return "高";
  return risk;
}

function statusLabel(status: string) {
  if (status === "high_value") return "高价值";
  if (status === "candidate") return "候选";
  if (status === "archive") return "归档";
  return status;
}

function gateLabel(status: string) {
  if (status === "executable") return "可进入 MVP 白名单";
  if (status === "review_required") return "需人工复核";
  if (status === "blocked") return "已阻断";
  return status;
}

function formatUnknown(value: unknown) {
  if (Array.isArray(value)) return value.join("、") || "空";
  if (typeof value === "string") return value || "空";
  if (value == null) return "空";
  return JSON.stringify(value);
}
