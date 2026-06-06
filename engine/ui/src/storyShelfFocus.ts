export type StoryShelfSourceKind = "builtin" | "imported" | string;
export type StoryShelfActionKey = "tianming" | "reading";
export type StoryShelfStageTone = "gold" | "jade";

export interface StoryShelfFocusInput {
  sourceKind: StoryShelfSourceKind;
  runCount: number;
}

export interface StoryShelfMetric {
  label: string;
  value: string;
}

export interface StoryShelfFocus {
  sourceLabel: string;
  stageLabel: string;
  stageTone: StoryShelfStageTone;
  stageDescription: string;
  recommendedKey: StoryShelfActionKey;
  recommendedAction: string;
  metrics: StoryShelfMetric[];
}

export function deriveStoryShelfFocus(input: StoryShelfFocusInput): StoryShelfFocus {
  const runCount = Math.max(0, input.runCount);
  const sourceLabel = input.sourceKind === "imported" ? "导入世界" : "样例世界";
  const hasSandboxResult = runCount > 0;

  return {
    sourceLabel,
    stageLabel: hasSandboxResult ? "已有沙盘结果" : "待确认天命",
    stageTone: hasSandboxResult ? "jade" : "gold",
    stageDescription: hasSandboxResult
      ? "这个世界已经运行过沙盘；先进入卷宗阅读，看角色行动留下的后果和下一章材料。"
      : "先确认天命书，理解世界锚点、吸引子和干预边界，再启动角色行动。",
    recommendedKey: hasSandboxResult ? "reading" : "tianming",
    recommendedAction: hasSandboxResult ? "进入卷宗阅读" : "确认天命",
    metrics: [
      { label: "世界线运行", value: `${runCount} 条` },
      { label: "来源", value: sourceLabel },
    ],
  };
}
