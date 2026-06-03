import { useEffect, useState } from "react";
import type { BranchDetail, ProjectionHealthReport } from "../api/types";
import { ApiError, api } from "../api/client";
import { EmptyState, ErrorState, Loading } from "./common/States";

type LoadState =
  | { status: "loading"; report: null; error: null }
  | { status: "ready"; report: ProjectionHealthReport; error: null }
  | { status: "error"; report: null; error: string };

export function ProjectionHealthPanel({ branch }: { branch: BranchDetail }) {
  const [state, setState] = useState<LoadState>({
    status: "loading",
    report: null,
    error: null,
  });

  useEffect(() => {
    let alive = true;
    setState({ status: "loading", report: null, error: null });
    api
      .getProjectionHealth(branch.run_id, branch.branch_id)
      .then((report) => {
        if (alive) setState({ status: "ready", report, error: null });
      })
      .catch((err: unknown) => {
        if (!alive) return;
        const message =
          err instanceof ApiError ? err.message : "投影健康报告读取失败。";
        setState({ status: "error", report: null, error: message });
      });
    return () => {
      alive = false;
    };
  }, [branch.run_id, branch.branch_id]);

  if (state.status === "loading") {
    return <Loading label="正在读取投影健康…" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.error} />;
  }
  const report = state.report;
  if (!report) {
    return (
      <EmptyState
        title="暂无投影健康报告"
        hint="旧 run 或缺失分支会保持空态。"
      />
    );
  }

  return <ProjectionHealthReportView report={report} />;
}

function ProjectionHealthReportView({ report }: { report: ProjectionHealthReport }) {
  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">投影健康</h3>
        <div className="chip-row" style={{ marginBottom: 10 }}>
          <span className={statusChipClass(report.status)}>
            {statusLabel(report.status)}
          </span>
          <span className="memory-chip">已具备 {report.summary.ready_count}</span>
          <span className="memory-chip">需留意 {report.summary.attention_count}</span>
          <span className="memory-chip">需修复 {report.summary.blocked_count}</span>
        </div>
        <Row k="运行" v={`${report.run_id} / ${report.branch_id}`} />
        <Row k="故事" v={report.story_slug || "未定位"} />
        <Row k="边界" v={boundaryText(report)} />
      </section>

      {report.warnings.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">提醒</h3>
          {report.warnings.slice(0, 5).map((warning, index) => (
            <div key={index} className="runtime-warning">
              {warning}
            </div>
          ))}
        </section>
      )}

      <section className="expl-section">
        <h3 className="expl-section__title">检查项</h3>
        {report.checks.map((check) => (
          <div key={check.id} className="artifact-item">
            <div className="artifact-item__title">
              {check.label}
              <span className={statusChipClass(check.status)} style={{ marginLeft: 8 }}>
                {check.status_label || statusLabel(check.status)}
              </span>
            </div>
            <div className="muted tiny">{check.source_artifact}</div>
            <div className="artifact-item__text">{check.evidence}</div>
            <div className="muted tiny">{check.next_step}</div>
          </div>
        ))}
      </section>

      <section className="expl-section">
        <h3 className="expl-section__title">下一步</h3>
        {report.next_steps.map((step, index) => (
          <div key={index} className="artifact-item">
            <div className="artifact-item__text">{step}</div>
          </div>
        ))}
      </section>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="kv">
      <span className="kv__k">{k}</span>
      <span className="kv__v">{v}</span>
    </div>
  );
}

function statusLabel(status: string): string {
  if (status === "ready") return "已具备";
  if (status === "attention") return "需留意";
  if (status === "blocked") return "需修复";
  return status || "未知";
}

function statusChipClass(status: string): string {
  if (status === "blocked") return "memory-chip projection-chip--blocked";
  if (status === "attention") return "memory-chip projection-chip--attention";
  return "memory-chip memory-chip--entity";
}

function boundaryText(report: ProjectionHealthReport): string {
  const parts: string[] = [];
  if (!report.summary.writes_artifacts) parts.push("不写文件");
  if (!report.summary.mutates_state_snapshot) parts.push("不覆盖状态");
  if (!report.summary.replaces_canon_ledger) parts.push("不替换正史账本");
  if (!report.summary.external_services_required) parts.push("不打外网");
  return parts.join(" · ");
}
