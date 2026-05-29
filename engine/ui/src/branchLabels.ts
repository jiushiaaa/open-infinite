import type { BranchAxisItem, InterventionCompilation } from "./api/types";

// branch_a/b/c 只是目录 ID；用户看到的是 intervention_compilation.branch_axis 的动态 label。
// 映射契约（与 worldline_brancher.STABLE_BRANCH_IDS 一致）：
//   branch_a → axis[0], branch_b → axis[1], branch_c → axis[2], branch_d → axis[3]
const ORDER = ["branch_a", "branch_b", "branch_c", "branch_d"];

export interface BranchDisplay {
  label: string;
  outcome?: string;
  description?: string;
  lineageType?: string;
  isAxisDriven: boolean;
}

export function axisItemForBranch(
  branchId: string,
  compilation?: InterventionCompilation | null,
): BranchAxisItem | null {
  const axis = compilation?.branch_axis;
  if (!axis || axis.length === 0) return null;
  const idx = ORDER.indexOf(branchId);
  if (idx >= 0 && idx < axis.length) return axis[idx];
  return null;
}

const OUTCOME_LABELS: Record<string, string> = {
  complied: "顺应",
  delayed: "延迟",
  resisted: "抗拒",
  failed_but_aware: "未遂·觉察",
  believed: "采信",
  doubted: "存疑",
  rejected: "拒绝",
  absorbed: "吸收",
  downgraded: "降级转译",
  alternate: "另开界线",
};

export function outcomeLabel(outcome?: string): string {
  if (!outcome) return "";
  return OUTCOME_LABELS[outcome] ?? outcome;
}

export function branchDisplay(
  branchId: string,
  theme: string,
  compilation?: InterventionCompilation | null,
): BranchDisplay {
  const item = axisItemForBranch(branchId, compilation);
  if (item) {
    return {
      label: item.label || theme || branchId,
      outcome: item.outcome,
      description: item.description,
      lineageType: item.lineage_type,
      isAxisDriven: true,
    };
  }
  // 回退：linear（resume continue）或旧 run 无 compilation 时用 events.theme。
  const fallback = branchId === "linear" ? "顺势续写" : theme || branchId;
  return { label: fallback, isAxisDriven: false };
}

export function isAlternateNovel(lineageType?: string): boolean {
  return lineageType === "alternate_novel";
}
