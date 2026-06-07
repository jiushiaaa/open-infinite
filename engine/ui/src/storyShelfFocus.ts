export type StoryShelfSourceKind = "builtin" | "imported" | string;
export type StoryShelfActionKey = "tianming" | "reading";
export type StoryShelfStageTone = "gold" | "jade";
export type StoryShelfJourneyKey = "tianming" | "sandbox" | "reading" | "author";
export type StoryShelfJourneyStatus = "active" | "ready" | "waiting";

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
  vitalitySignals: StoryShelfVitalitySignal[];
  journeyPulse: StoryShelfJourneyPulse[];
}

export interface StoryShelfVitalitySignal {
  key: "world_runs" | "memory" | "intervention" | "chapter";
  label: string;
  value: string;
  detail: string;
}

export interface StoryShelfJourneyPulse {
  key: StoryShelfJourneyKey;
  label: string;
  title: string;
  status: StoryShelfJourneyStatus;
  hint: string;
}

export interface StoryShelfSpotlightInput {
  slug: string;
  displayName: string;
  sourceKind: StoryShelfSourceKind;
  runCount: number;
}

export interface StoryShelfSpotlight extends StoryShelfSpotlightInput {
  seal: string;
  priorityLabel: string;
  spotlightReason: string;
  focus: StoryShelfFocus;
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
    vitalitySignals: hasSandboxResult
      ? [
          {
            key: "world_runs",
            label: "世界会运行",
            value: `${runCount} 轮`,
            detail: `已留下 ${runCount} 轮角色行动、记忆和世界线变化`,
          },
          {
            key: "memory",
            label: "角色会记得",
            value: "可回看",
            detail: "主观记忆会继续影响下一轮行动",
          },
          {
            key: "intervention",
            label: "干预有后果",
            value: "可追踪",
            detail: "干预会进入因果债、锚点压力和多视角正文",
          },
          {
            key: "chapter",
            label: "章节来自演化",
            value: "可写下一章",
            detail: "沙盘涌现剧情可送入作者采纳台",
          },
        ]
      : [
          {
            key: "world_runs",
            label: "世界会运行",
            value: "待启动",
            detail: "确认天命后启动第一轮角色行动",
          },
          {
            key: "memory",
            label: "角色会记得",
            value: "待写入",
            detail: "沙盘结果会进入角色主观记忆",
          },
          {
            key: "intervention",
            label: "干预有后果",
            value: "待投放",
            detail: "干预会被天命书转译并写成代偿",
          },
          {
            key: "chapter",
            label: "章节来自演化",
            value: "待生成",
            detail: "跑出结果后进入卷宗阅读和作者采纳",
          },
        ],
    journeyPulse: hasSandboxResult
      ? [
          {
            key: "tianming",
            label: "已定界",
            title: "天命",
            status: "ready",
            hint: "回看锚点",
          },
          {
            key: "sandbox",
            label: `${runCount} 轮`,
            title: "沙盘",
            status: "ready",
            hint: "继续推演",
          },
          {
            key: "reading",
            label: "现在读",
            title: "阅读",
            status: "active",
            hint: "看后果",
          },
          {
            key: "author",
            label: "可整理",
            title: "采纳",
            status: "ready",
            hint: "写下一章",
          },
        ]
      : [
          {
            key: "tianming",
            label: "下一步",
            title: "天命",
            status: "active",
            hint: "确认边界",
          },
          {
            key: "sandbox",
            label: "待启动",
            title: "沙盘",
            status: "waiting",
            hint: "先定界",
          },
          {
            key: "reading",
            label: "待生成",
            title: "阅读",
            status: "waiting",
            hint: "跑一轮后读",
          },
          {
            key: "author",
            label: "待素材",
            title: "采纳",
            status: "waiting",
            hint: "先有涌现",
          },
        ],
  };
}

export function deriveStoryShelfSpotlight(
  stories: StoryShelfSpotlightInput[],
): StoryShelfSpotlight | null {
  if (stories.length === 0) return null;

  const best = stories
    .map((story, index) => ({ story, index, score: spotlightScore(story) }))
    .sort((a, b) => b.score - a.score || a.index - b.index)[0]?.story;

  if (!best) return null;

  const runCount = Math.max(0, best.runCount);
  const focus = deriveStoryShelfFocus({
    sourceKind: best.sourceKind,
    runCount,
  });
  const isImported = best.sourceKind === "imported";
  const hasSandboxResult = runCount > 0;

  return {
    ...best,
    runCount,
    seal: best.displayName.trim().slice(0, 1) || "书",
    priorityLabel: isImported
      ? "用户导入世界"
      : hasSandboxResult
        ? "已有沙盘结果"
        : "推荐样例世界",
    spotlightReason: isImported
      ? "这是你带进来的世界；从它开始，最容易看到干预如何改变熟悉剧情。"
      : hasSandboxResult
        ? "这个世界已经运行过沙盘；适合直接进入卷宗，阅读角色行动留下的后果。"
        : "从天命书开始最稳，先理解世界锚点，再启动第一轮角色行动。",
    focus,
  };
}

function spotlightScore(story: StoryShelfSpotlightInput): number {
  const runCount = Math.max(0, story.runCount);
  const sourceScore = story.sourceKind === "imported" ? 100 : 0;
  const runningScore = runCount > 0 ? 30 : 0;
  return sourceScore + runningScore + Math.min(runCount, 10);
}
