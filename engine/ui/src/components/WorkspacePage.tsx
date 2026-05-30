import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import type { RunTreeNode } from "../api/types";
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
  const [sel, setSel] = useState<Selection | null>(null);

  const nodes = useMemo(() => tree.data?.tree ?? [], [tree.data]);

  useEffect(() => {
    if (!sel && nodes.length > 0) {
      setSel(firstSelectable(nodes));
    }
  }, [nodes, sel]);

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
        {!sel && !tree.loading && (
          <EmptyState title="选择左侧的一条世界线开始阅读" />
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
        {!sel && <EmptyState title="解释面板" hint="选择世界线后展示状态与解释。" />}
      </aside>
    </div>
  );
}
