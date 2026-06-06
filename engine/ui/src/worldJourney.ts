export type WorldJourneyStepKey = "tianming" | "sandbox" | "reading" | "author";
export type WorldJourneyStatus = "ready" | "next" | "waiting";

export interface WorldJourneyInput {
  slug: string;
  runCount: number;
  characterCount: number;
  openThreadCount: number;
  factionCount: number;
  currentChapter?: number | null;
  hasRecentReading: boolean;
}

export interface WorldJourneyStep {
  key: WorldJourneyStepKey;
  label: string;
  title: string;
  summary: string;
  status: WorldJourneyStatus;
  statusLabel: string;
}

export interface WorldJourney {
  phaseLabel: string;
  phaseDescription: string;
  recommendedKey: WorldJourneyStepKey;
  recommendedAction: string;
  steps: WorldJourneyStep[];
}

function statusLabel(status: WorldJourneyStatus): string {
  if (status === "next") return "下一步";
  if (status === "ready") return "可用";
  return "待生成";
}

export function deriveWorldJourney(input: WorldJourneyInput): WorldJourney {
  const hasAnchoredWorld = input.characterCount > 0 || input.openThreadCount > 0;
  const hasRun = input.runCount > 0;
  const hasReading = hasRun || input.hasRecentReading;

  const recommendedKey: WorldJourneyStepKey = input.hasRecentReading
    ? "reading"
    : hasRun
      ? "reading"
      : "tianming";
  const recommendedAction = input.hasRecentReading
    ? "继续阅读"
    : hasRun
      ? "进入卷宗阅读"
      : "确认天命";
  const phaseLabel = input.hasRecentReading
    ? "可继续阅读"
    : hasRun
      ? "已有沙盘结果"
      : "待确认天命";
  const phaseDescription = input.hasRecentReading
    ? "最近读到的卷宗已经记住；可以先续读，再决定是否运行沙盘或写下一章。"
    : hasRun
      ? "这个世界已经运行过沙盘；最短路径是进入卷宗阅读，看看角色行动留下了什么后果。"
      : "世界素材已经锚定；先确认天命书，再让角色按欲望、记忆和利益行动。";

  const steps: WorldJourneyStep[] = [
    {
      key: "tianming",
      label: "定界",
      title: "天命书",
      summary: `${input.openThreadCount} 条伏笔`,
      status: recommendedKey === "tianming" ? "next" : "ready",
      statusLabel: "",
    },
    {
      key: "sandbox",
      label: "运行",
      title: "世界沙盘",
      summary: `${input.characterCount} 个角色`,
      status: hasAnchoredWorld ? "ready" : "waiting",
      statusLabel: "",
    },
    {
      key: "reading",
      label: "阅读",
      title: "卷宗阅读",
      summary: input.currentChapter != null ? `第 ${input.currentChapter} 章` : "主线卷",
      status: recommendedKey === "reading" ? "next" : hasReading ? "ready" : "waiting",
      statusLabel: "",
    },
    {
      key: "author",
      label: "采纳",
      title: "作者台",
      summary: `${input.runCount} 次运行`,
      status: hasRun ? "ready" : "waiting",
      statusLabel: "",
    },
  ];

  return {
    phaseLabel,
    phaseDescription,
    recommendedKey,
    recommendedAction,
    steps: steps.map((step) => ({ ...step, statusLabel: statusLabel(step.status) })),
  };
}
