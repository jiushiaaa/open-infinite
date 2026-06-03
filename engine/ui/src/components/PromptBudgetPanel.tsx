import { useEffect, useState } from "react";
import type { BranchDetail, PromptBudgetPackReport } from "../api/types";
import { ApiError, api } from "../api/client";
import { EmptyState, ErrorState, Loading } from "./common/States";

type LoadState =
  | { status: "loading"; report: null; error: null }
  | { status: "ready"; report: PromptBudgetPackReport; error: null }
  | { status: "error"; report: null; error: string };

export function PromptBudgetPanel({ branch }: { branch: BranchDetail }) {
  const [state, setState] = useState<LoadState>({
    status: "loading",
    report: null,
    error: null,
  });

  useEffect(() => {
    let alive = true;
    setState({ status: "loading", report: null, error: null });
    api
      .getPromptBudgetPack(branch.run_id, branch.branch_id)
      .then((report) => {
        if (alive) setState({ status: "ready", report, error: null });
      })
      .catch((err: unknown) => {
        if (!alive) return;
        const message =
          err instanceof ApiError ? err.message : "上下文包读取失败。";
        setState({ status: "error", report: null, error: message });
      });
    return () => {
      alive = false;
    };
  }, [branch.run_id, branch.branch_id]);

  if (state.status === "loading") {
    return <Loading label="正在整理上下文包…" />;
  }
  if (state.status === "error") {
    return <ErrorState message={state.error} />;
  }
  if (!state.report) {
    return <EmptyState title="暂无上下文包" hint="旧 run 或缺失检索记忆会保持空态。" />;
  }
  return <PromptBudgetReportView report={state.report} />;
}

function PromptBudgetReportView({ report }: { report: PromptBudgetPackReport }) {
  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">上下文包</h3>
        <div className="chip-row" style={{ marginBottom: 10 }}>
          <span className={statusChipClass(report.status)}>
            {statusLabel(report.status)}
          </span>
          <span className="memory-chip">预算 {report.summary.char_budget}</span>
          <span className="memory-chip">纳入 {report.summary.included_item_count}</span>
          <span className="memory-chip">排除 {report.summary.excluded_item_count}</span>
        </div>
        <Row k="字符" v={`${report.summary.estimated_prompt_chars}`} />
        <Row k="估算 token" v={`${report.summary.estimated_prompt_tokens}`} />
        <Row k="压缩比" v={`${Math.round(report.summary.compression_ratio * 100)}%`} />
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
        <h3 className="expl-section__title">分组</h3>
        {report.sections.map((section) => (
          <div key={section.id} className="artifact-item">
            <div className="artifact-item__title">
              {section.label}
              <span className="memory-chip" style={{ marginLeft: 8 }}>
                {section.item_count}
              </span>
            </div>
            {section.items.slice(0, 3).map((item) => (
              <div key={item.id} className="retr-item">
                <div className="retr-item__src">
                  {item.source} · {item.char_count} 字
                </div>
                <div className="retr-item__text">{item.text}</div>
              </div>
            ))}
          </div>
        ))}
      </section>

      {report.excluded_items.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">未纳入</h3>
          {report.excluded_items.slice(0, 5).map((item) => (
            <div key={item.id} className="artifact-item">
              <div className="artifact-item__title">{item.source}</div>
              <div className="muted tiny">{item.reason}</div>
              <div className="artifact-item__text">{item.text}</div>
            </div>
          ))}
        </section>
      )}

      {report.prompt_block && (
        <section className="expl-section">
          <h3 className="expl-section__title">Prompt Block</h3>
          <div className="artifact-item">
            <div className="artifact-item__text">{report.prompt_block}</div>
          </div>
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
