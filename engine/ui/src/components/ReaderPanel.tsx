import { useEffect, useState } from "react";
import type { BranchDetail, ReaderPanelReport } from "../api/types";
import { ApiError, api } from "../api/client";
import { EmptyState, ErrorState, Loading } from "./common/States";

type LoadState =
  | { status: "loading"; report: null; error: null }
  | { status: "ready"; report: ReaderPanelReport; error: null }
  | { status: "error"; report: null; error: string };

export function ReaderPanel({ branch }: { branch: BranchDetail }) {
  const [state, setState] = useState<LoadState>({
    status: "loading",
    report: null,
    error: null,
  });

  useEffect(() => {
    let alive = true;
    setState({ status: "loading", report: null, error: null });
    api
      .getReaderPanel(branch.run_id, branch.branch_id)
      .then((report) => {
        if (alive) setState({ status: "ready", report, error: null });
      })
      .catch((err: unknown) => {
        if (!alive) return;
        const message =
          err instanceof ApiError ? err.message : "读者评审读取失败。";
        setState({ status: "error", report: null, error: message });
      });
    return () => {
      alive = false;
    };
  }, [branch.run_id, branch.branch_id]);

  if (state.status === "loading") {
    return <Loading label="正在读取读者评审…" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.error} />;
  }
  if (!state.report) {
    return (
      <EmptyState
        title="暂无读者评审"
        hint="旧 run 或缺失正文会保持空态。"
      />
    );
  }
  return <ReaderPanelReportView report={state.report} />;
}

function ReaderPanelReportView({ report }: { report: ReaderPanelReport }) {
  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">读者评审</h3>
        <div className="chip-row" style={{ marginBottom: 10 }}>
          <span className={statusChipClass(report.status)}>
            {statusLabel(report.status)}
          </span>
          <span className="memory-chip">问题 {report.summary.issue_count}</span>
          <span className="memory-chip">修订 {report.summary.revision_brief_count}</span>
        </div>
        <Row k="运行" v={`${report.run_id} / ${report.branch_id}`} />
        <Row k="边界" v={boundaryText(report)} />
      </section>

      {report.warnings.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">提醒</h3>
          {report.warnings.slice(0, 4).map((warning, index) => (
            <div key={index} className="runtime-warning">
              {warning}
            </div>
          ))}
        </section>
      )}

      <section className="expl-section">
        <h3 className="expl-section__title">读者</h3>
        {report.personas.map((persona) => (
          <div key={persona.id} className="artifact-item">
            <div className="artifact-item__title">
              {persona.label}
              <span className={statusChipClass(persona.status)} style={{ marginLeft: 8 }}>
                {statusLabel(persona.status)}
              </span>
            </div>
            <div className="muted tiny">{persona.focus}</div>
            <div className="artifact-item__text">{persona.verdict}</div>
          </div>
        ))}
      </section>

      <section className="expl-section">
        <h3 className="expl-section__title">命中问题</h3>
        {report.issues.length === 0 ? (
          <EmptyState title="没有命中明显问题" />
        ) : (
          report.issues.map((issue) => (
            <div key={issue.id} className="artifact-item">
              <div className="artifact-item__title">
                {issue.label}
                <span className={severityChipClass(issue.severity)} style={{ marginLeft: 8 }}>
                  {issue.severity_label}
                </span>
              </div>
              {issue.evidence.slice(0, 3).map((item, index) => (
                <div key={index} className="artifact-item__text">
                  {item}
                </div>
              ))}
              <div className="muted tiny">{issue.revision_brief}</div>
            </div>
          ))
        )}
      </section>

      {report.revision_briefs.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">修订 Brief</h3>
          {report.revision_briefs.map((brief) => (
            <div key={brief.issue_id} className="artifact-item">
              <div className="artifact-item__title">{brief.label}</div>
              <div className="artifact-item__text">{brief.revision_brief}</div>
              <Row k="保留" v={brief.keep} />
              <Row k="避免" v={brief.avoid} />
            </div>
          ))}
        </section>
      )}
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

function severityChipClass(severity: string): string {
  if (severity === "high") return "memory-chip projection-chip--blocked";
  if (severity === "medium") return "memory-chip projection-chip--attention";
  return "memory-chip";
}

function boundaryText(report: ReaderPanelReport): string {
  const parts: string[] = [];
  if (!report.summary.writes_artifacts) parts.push("不写文件");
  if (!report.summary.external_services_required) parts.push("不打外网");
  if (!report.summary.llm_required) parts.push("不调模型");
  return parts.join(" · ");
}
