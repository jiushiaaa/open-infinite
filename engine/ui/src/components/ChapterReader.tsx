import { useEffect, useState } from "react";
import type { BranchDetail, InterventionCompilation } from "../api/types";
import { branchDisplay, isAlternateNovel, outcomeLabel } from "../branchLabels";
import { renderProse } from "../markdown";
import { CausalDiffView } from "./CausalDiffBlock";
import { EmptyState } from "./common/States";
import "./chapterReader.css";

type Tab = "prose" | "diff";

export function ChapterReader({
  branch,
  compilation,
  onBranchReload,
}: {
  branch: BranchDetail;
  compilation: InterventionCompilation | null;
  onBranchReload: () => void;
}) {
  const [tab, setTab] = useState<Tab>("prose");

  // 切换分支时若新分支无 diff，回到正文
  useEffect(() => {
    if (tab === "diff" && !branch.causal_diff) setTab("prose");
  }, [branch.causal_diff, tab]);

  const disp = branchDisplay(branch.branch_id, branch.theme, compilation);
  const diffCount = branch.causal_diff?.blocks?.length ?? 0;
  const auLineage =
    branch.causal_diff?.lineage_type ?? disp.lineageType ?? compilation?.lineage_type;
  const isAu = isAlternateNovel(auLineage);

  return (
    <div className="reader">
      <header className="reader__head">
        <div className="reader__titleline">
          <h1 className="reader__title">{disp.label}</h1>
          {disp.outcome && (
            <span className="badge badge--jade">{outcomeLabel(disp.outcome)}</span>
          )}
          {isAu && (
            <span className="badge badge--indigo" title="Alternate Novel / AU 世界线">
              另开界线 · AU
            </span>
          )}
        </div>
        <div className="reader__tabs">
          <button
            className={`reader__tab ${tab === "prose" ? "is-active" : ""}`}
            onClick={() => setTab("prose")}
          >
            正文
          </button>
          <button
            className={`reader__tab ${tab === "diff" ? "is-active" : ""}`}
            onClick={() => setTab("diff")}
            disabled={!branch.causal_diff}
            title={branch.causal_diff ? "" : "该分支尚未生成时空 Diff"}
          >
            时空 Diff{diffCount > 0 ? ` · ${diffCount}` : ""}
          </button>
        </div>
      </header>

      {isAu && tab === "prose" && (
        <div className="reader__au-note">
          这不是普通分支，而是 Alternate Novel / AU 世界线。原世界线不会被静默污染。
        </div>
      )}

      <div className="reader__scroll">
        {tab === "prose" ? (
          <article className="prose">
            {branch.chapter_md?.trim() ? (
              renderProse(branch.chapter_md)
            ) : (
              <EmptyState
                title="这条世界线还没有正文"
                hint="该分支可能尚未生成 chapter.md。"
              />
            )}
          </article>
        ) : (
          <CausalDiffView
            diff={branch.causal_diff}
            compilation={compilation}
            runId={branch.run_id}
            branchId={branch.branch_id}
            onChanged={onBranchReload}
          />
        )}
      </div>
    </div>
  );
}
