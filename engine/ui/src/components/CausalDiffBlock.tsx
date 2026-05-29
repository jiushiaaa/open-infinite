import { useState } from "react";
import { api } from "../api/client";
import type {
  CausalDiffArtifact,
  CausalDiffBlock as Block,
  DiffActionKind,
  InterventionCompilation,
} from "../api/types";
import { isAlternateNovel } from "../branchLabels";
import { EmptyState } from "./common/States";
import "./causalDiff.css";

const DIFF_MODE_LABEL: Record<string, string> = {
  local_divergence: "局部偏离",
  broad_rewrite: "大范围改写",
  alternate_novel_seed: "AU 世界线种子",
};

const OP_LABEL: Record<string, string> = {
  replace: "改写",
  insert: "新增",
  delete: "抹去",
};

const ACTIONS: { kind: DiffActionKind; label: string; tone: string }[] = [
  { kind: "accept", label: "确立此界线", tone: "btn--primary" },
  { kind: "reject", label: "抹除这次改写", tone: "" },
  { kind: "revert", label: "回滚到干预前", tone: "" },
];

export function CausalDiffView({
  diff,
  compilation,
  runId,
  branchId,
  onChanged,
}: {
  diff: CausalDiffArtifact | null;
  compilation: InterventionCompilation | null;
  runId: string;
  branchId: string;
  onChanged: () => void;
}) {
  const [busy, setBusy] = useState<DiffActionKind | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!diff) {
    return (
      <EmptyState
        title="该分支尚未生成时空 Diff"
        hint="causal_diff.json 不存在或该 run 在 v0.7.1-C 之前生成。"
      />
    );
  }

  const blocks = diff.blocks ?? [];
  const scope = diff.affected_scope ?? compilation?.affected_scope ?? {};
  const au = isAlternateNovel(diff.lineage_type);
  const settled = diff.status === "accepted" || diff.status === "rejected" || diff.status === "reverted";

  async function act(kind: DiffActionKind) {
    setBusy(kind);
    setError(null);
    try {
      await api.postDiffAction({ run_id: runId, branch_id: branchId, action: kind });
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="cdiff">
      <div className="cdiff__lede">
        <p className="cdiff__question">我刚刚那句话，到底改变了哪里？</p>
        <div className="cdiff__tags">
          <span className={`badge ${au ? "badge--indigo" : "badge--jade"}`}>
            {DIFF_MODE_LABEL[diff.diff_mode ?? ""] ?? diff.diff_mode ?? "差异"}
          </span>
          <span className={`badge ${statusTone(diff.status)}`}>
            状态 · {statusLabel(diff.status ?? "proposed")}
          </span>
          {diff.lineage_type && (
            <span className="badge badge--gold">{diff.lineage_type}</span>
          )}
        </div>

        <div className="cdiff__actions">
          {ACTIONS.map((a) => (
            <button
              key={a.kind}
              className={`btn tiny ${a.tone}`}
              disabled={busy !== null}
              onClick={() => act(a.kind)}
            >
              {busy === a.kind ? "处理中…" : a.label}
            </button>
          ))}
          {settled && (
            <span className="muted tiny cdiff__settled">
              已记录为「{statusLabel(diff.status ?? "proposed")}」，可再次更改
            </span>
          )}
        </div>
        {error && <p className="cdiff__error">{error}</p>}
        <p className="muted tiny cdiff__note">
          仅记录世界线取舍，不改写正文，也不删除其他世界线。
        </p>
      </div>

      {blocks.length === 0 ? (
        <div className="cdiff__empty">
          <p className="muted">
            {diff.reason || "未产生可视差异块。"}
          </p>
        </div>
      ) : (
        <ol className="cdiff__list">
          {blocks.map((b, i) => (
            <DiffBlock key={b.id || i} block={b} index={i} scope={scope} />
          ))}
        </ol>
      )}
    </div>
  );
}

function statusTone(status?: string): string {
  if (status === "accepted") return "badge--jade";
  if (status === "rejected") return "badge--cinnabar";
  if (status === "reverted") return "badge--indigo";
  return "";
}

function statusLabel(s: string): string {
  return (
    { proposed: "待定", accepted: "已确立", rejected: "已抹除", reverted: "已回滚" }[s] ??
    s
  );
}

function DiffBlock({
  block,
  index,
  scope,
}: {
  block: Block;
  index: number;
  scope: NonNullable<CausalDiffArtifact["affected_scope"]>;
}) {
  const chars = [...(scope.characters ?? [])];
  const locs = [...(scope.locations ?? [])];

  return (
    <li className="cblock">
      <div className="cblock__op">
        <span className="cblock__index mono">#{index + 1}</span>
        <span className={`badge badge--${opTone(block.op)}`}>
          {OP_LABEL[block.op] ?? block.op}
        </span>
        {block.anchor?.chapter ? (
          <span className="muted tiny">第{block.anchor.chapter}章</span>
        ) : null}
      </div>

      {block.old_text && (
        <div className="cblock__old">
          <span className="cblock__tag">被抹去的旧现实</span>
          <p className="cblock__text">{block.old_text}</p>
        </div>
      )}
      {block.new_text && (
        <div className="cblock__new">
          <span className="cblock__tag">新凝聚的世界线</span>
          <p className="cblock__text cblock__text--type">{block.new_text}</p>
        </div>
      )}

      {(chars.length > 0 || locs.length > 0 || block.note) && (
        <div className="cblock__explain">
          {chars.length > 0 && (
            <span className="muted tiny">影响角色：{chars.join("、")}</span>
          )}
          {locs.length > 0 && (
            <span className="muted tiny">影响地点：{locs.join("、")}</span>
          )}
          {block.note && <span className="muted tiny">{block.note}</span>}
        </div>
      )}
    </li>
  );
}

function opTone(op: string): "cinnabar" | "jade" | "gold" {
  if (op === "delete") return "cinnabar";
  if (op === "insert") return "jade";
  return "gold";
}
