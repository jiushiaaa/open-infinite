import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { BranchSummaryNode, InterventionCompilation, RunTreeNode } from "../api/types";
import { branchDisplay, isAlternateNovel, outcomeLabel } from "../branchLabels";
import type { Selection } from "./WorkspacePage";
import "./worldlineTree.css";

const KIND_LABEL: Record<string, string> = {
  intervene: "干预",
  resume_continue: "续写",
  resume_intervene: "再干预",
};

export function WorldlineTree({
  slug,
  nodes,
  selection,
  onSelect,
}: {
  slug: string;
  nodes: RunTreeNode[];
  selection: Selection | null;
  onSelect: (s: Selection) => void;
}) {
  return (
    <nav className="wtree" aria-label="世界线树">
      <div className="wtree__head">
        <h2 className="wtree__title">世界线</h2>
        <span className="muted tiny mono">{slug}</span>
      </div>
      <ul className="wtree__list">
        {nodes.map((run) => (
          <RunRow
            key={run.run_id}
            run={run}
            depth={0}
            selection={selection}
            onSelect={onSelect}
          />
        ))}
      </ul>
    </nav>
  );
}

function RunRow({
  run,
  depth,
  selection,
  onSelect,
}: {
  run: RunTreeNode;
  depth: number;
  selection: Selection | null;
  onSelect: (s: Selection) => void;
}) {
  // 仅当此 run 被选中（其某分支被选中）时才取 compilation，做动态 label。
  const isActiveRun = selection?.runId === run.run_id;
  const [comp, setComp] = useState<InterventionCompilation | null>(null);

  useEffect(() => {
    let alive = true;
    if (run.kind === "resume_continue") return; // linear 续写无 axis
    api
      .getRun(run.run_id)
      .then((d) => {
        if (alive) setComp(d.intervention_compilation ?? null);
      })
      .catch(() => {
        if (alive) setComp(null);
      });
    return () => {
      alive = false;
    };
  }, [run.run_id, run.kind]);

  return (
    <li className="wtree__run" style={{ ["--depth" as string]: depth }}>
      <div className={`wtree__run-head ${isActiveRun ? "is-active-run" : ""}`}>
        <span className={`badge tiny ${run.kind === "intervene" ? "badge--cinnabar" : "badge--gold"}`}>
          {KIND_LABEL[run.kind] ?? run.kind}
        </span>
        {run.current_chapter != null && (
          <span className="muted tiny">第{run.current_chapter}章</span>
        )}
        {run.is_orphan && (
          <span className="badge badge--indigo tiny" title="父运行已不在索引中">
            游离
          </span>
        )}
      </div>
      {run.intervention_preview && (
        <p className="wtree__preview muted tiny">{run.intervention_preview}</p>
      )}
      <ul className="wtree__branches">
        {run.branches.map((b) => (
          <BranchRow
            key={b.branch_id}
            runId={run.run_id}
            branch={b}
            comp={comp}
            selected={
              selection?.runId === run.run_id &&
              selection?.branchId === b.branch_id
            }
            onSelect={onSelect}
          />
        ))}
      </ul>
      {run.branches.flatMap((b) => b.child_runs).length > 0 && (
        <ul className="wtree__children">
          {run.branches.flatMap((b) =>
            b.child_runs.map((child) => (
              <RunRow
                key={child.run_id}
                run={child}
                depth={depth + 1}
                selection={selection}
                onSelect={onSelect}
              />
            )),
          )}
        </ul>
      )}
    </li>
  );
}

function BranchRow({
  runId,
  branch,
  comp,
  selected,
  onSelect,
}: {
  runId: string;
  branch: BranchSummaryNode;
  comp: InterventionCompilation | null;
  selected: boolean;
  onSelect: (s: Selection) => void;
}) {
  const disp = branchDisplay(branch.branch_id, branch.theme, comp);
  const au = isAlternateNovel(disp.lineageType);
  return (
    <li>
      <button
        className={`wtree__branch ${selected ? "is-selected" : ""} ${au ? "is-au" : ""}`}
        onClick={() => onSelect({ runId, branchId: branch.branch_id })}
        title={disp.description || disp.label}
      >
        <span className="wtree__branch-dot" aria-hidden />
        <span className="wtree__branch-main">
          <span className="wtree__branch-label">{disp.label}</span>
          <span className="wtree__branch-sub muted tiny">
            <span className="mono">{branch.branch_id}</span>
            {disp.outcome && <span> · {outcomeLabel(disp.outcome)}</span>}
          </span>
        </span>
        <span className="wtree__branch-marks">
          {au && (
            <span className="badge badge--indigo tiny" title="Alternate Novel / AU 世界线">
              AU
            </span>
          )}
          {branch.has_causal_diff && (
            <span className="mark mark--diff" title={`时空 Diff · ${branch.causal_diff_count} 块`}>
              Δ
            </span>
          )}
          {branch.has_multi_agent_trace && (
            <span className="mark mark--trace" title="Agent 轨迹">
              ◇
            </span>
          )}
          {branch.retrieval_count > 0 && (
            <span className="mark mark--mem" title={`检索记忆 · ${branch.retrieval_count}`}>
              ❖
            </span>
          )}
        </span>
      </button>
    </li>
  );
}
