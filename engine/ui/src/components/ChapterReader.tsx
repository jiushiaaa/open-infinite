import { useEffect, useState } from "react";
import { api } from "../api/client";
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
  const [exporting, setExporting] = useState(false);
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [exportErr, setExportErr] = useState<string | null>(null);

  // 切换分支时若新分支无 diff，回到正文
  useEffect(() => {
    if (tab === "diff" && !branch.causal_diff) setTab("prose");
  }, [branch.causal_diff, tab]);

  const disp = branchDisplay(branch.branch_id, branch.theme, compilation);
  const diffCount = branch.causal_diff?.blocks?.length ?? 0;
  const auLineage =
    branch.causal_diff?.lineage_type ?? disp.lineageType ?? compilation?.lineage_type;
  const isAu = isAlternateNovel(auLineage);

  async function handleExport() {
    setExporting(true);
    setExportErr(null);
    setExportMsg(null);
    try {
      const payload = await api.getChapterExport(branch.run_id, branch.branch_id);
      const blob = new Blob([payload.content_md], {
        type: payload.content_type || "text/markdown;charset=utf-8",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = payload.filename || `${branch.run_id}_${branch.branch_id}.md`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setExportMsg("章节已生成下载文件，含来源与 AI 生成说明。");
    } catch (err) {
      setExportErr(err instanceof Error ? err.message : "导出失败，请稍后重试。");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="reader">
      <header className="reader__head">
        <div className="reader__topline">
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
          <button
            type="button"
            className="reader__export"
            onClick={handleExport}
            disabled={exporting || !branch.chapter_md?.trim()}
            title={
              branch.chapter_md?.trim()
                ? "导出当前世界线章节"
                : "该分支暂无正文可导出"
            }
          >
            {exporting ? "导出中…" : "导出章节"}
          </button>
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
        {(exportMsg || exportErr) && (
          <p className={`reader__export-note tiny ${exportErr ? "is-error" : ""}`}>
            {exportErr ?? exportMsg}
          </p>
        )}
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
