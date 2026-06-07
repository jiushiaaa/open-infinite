import assert from "node:assert/strict";
import { readFileSync, rmSync } from "node:fs";
import { resolve } from "node:path";
import {
  deriveStoryShelfFocus,
  deriveStoryShelfSpotlight,
} from "../.tmp-story-shelf-focus/storyShelfFocus.js";

const freshImported = deriveStoryShelfFocus({
  sourceKind: "imported",
  runCount: 0,
});

assert.equal(freshImported.sourceLabel, "导入世界");
assert.equal(freshImported.stageLabel, "待确认天命");
assert.equal(freshImported.stageTone, "gold");
assert.equal(freshImported.recommendedKey, "tianming");
assert.equal(freshImported.recommendedAction, "确认天命");
assert.match(freshImported.stageDescription, /先确认天命书/);
assert.deepEqual(freshImported.metrics, [
  { label: "世界线运行", value: "0 条" },
  { label: "来源", value: "导入世界" },
]);
assert.deepEqual(
  freshImported.vitalitySignals.map((signal) => [
    signal.key,
    signal.label,
    signal.value,
    signal.detail,
  ]),
  [
    ["world_runs", "世界会运行", "待启动", "确认天命后启动第一轮角色行动"],
    ["memory", "角色会记得", "待写入", "沙盘结果会进入角色主观记忆"],
    ["intervention", "干预有后果", "待投放", "干预会被天命书转译并写成代偿"],
    ["chapter", "章节来自演化", "待生成", "跑出结果后进入卷宗阅读和作者采纳"],
  ],
);
assert.deepEqual(
  freshImported.journeyPulse.map((pulse) => [pulse.key, pulse.label, pulse.status]),
  [
    ["tianming", "下一步", "active"],
    ["sandbox", "待启动", "waiting"],
    ["reading", "待生成", "waiting"],
    ["author", "待素材", "waiting"],
  ],
);

const runningBuiltin = deriveStoryShelfFocus({
  sourceKind: "builtin",
  runCount: 3,
});

assert.equal(runningBuiltin.sourceLabel, "样例世界");
assert.equal(runningBuiltin.stageLabel, "已有沙盘结果");
assert.equal(runningBuiltin.stageTone, "jade");
assert.equal(runningBuiltin.recommendedKey, "reading");
assert.equal(runningBuiltin.recommendedAction, "进入卷宗阅读");
assert.match(runningBuiltin.stageDescription, /已经运行过沙盘/);
assert.equal(runningBuiltin.metrics[0].value, "3 条");
assert.deepEqual(
  runningBuiltin.vitalitySignals.map((signal) => [signal.key, signal.value]),
  [
    ["world_runs", "3 轮"],
    ["memory", "可回看"],
    ["intervention", "可追踪"],
    ["chapter", "可写下一章"],
  ],
);
assert.deepEqual(
  runningBuiltin.journeyPulse.map((pulse) => [pulse.key, pulse.label, pulse.status]),
  [
    ["tianming", "已定界", "ready"],
    ["sandbox", "3 轮", "ready"],
    ["reading", "现在读", "active"],
    ["author", "可整理", "ready"],
  ],
);

const defensive = deriveStoryShelfFocus({
  sourceKind: "imported",
  runCount: -2,
});

assert.equal(defensive.metrics[0].value, "0 条");
assert.equal(defensive.recommendedKey, "tianming");

const spotlightPrefersImported = deriveStoryShelfSpotlight([
  { slug: "sample", displayName: "样例世界", sourceKind: "builtin", runCount: 4 },
  { slug: "mine", displayName: "我的世界", sourceKind: "imported", runCount: 0 },
]);

assert.equal(spotlightPrefersImported?.slug, "mine");
assert.equal(spotlightPrefersImported?.seal, "我");
assert.equal(spotlightPrefersImported?.priorityLabel, "用户导入世界");
assert.equal(spotlightPrefersImported?.focus.recommendedKey, "tianming");
assert.match(spotlightPrefersImported?.spotlightReason ?? "", /你带进来的世界/);

const spotlightPrefersRunningWorld = deriveStoryShelfSpotlight([
  { slug: "fresh", displayName: "新样例", sourceKind: "builtin", runCount: 0 },
  { slug: "running", displayName: "旧王朝", sourceKind: "builtin", runCount: 2 },
]);

assert.equal(spotlightPrefersRunningWorld?.slug, "running");
assert.equal(spotlightPrefersRunningWorld?.priorityLabel, "已有沙盘结果");
assert.equal(spotlightPrefersRunningWorld?.focus.recommendedKey, "reading");
assert.equal(spotlightPrefersRunningWorld?.focus.journeyPulse[2]?.status, "active");
assert.equal(
  spotlightPrefersRunningWorld?.focus.vitalitySignals[0]?.detail,
  "已留下 2 轮角色行动、记忆和世界线变化",
);

const noSpotlight = deriveStoryShelfSpotlight([]);
assert.equal(noSpotlight, null);

const entryPage = readFileSync(resolve("src/components/StoryEntryPage.tsx"), "utf8");
assert.match(entryPage, /entry__spotlight-pulse/);
assert.match(entryPage, /entry__spotlight-vitality/);
assert.match(entryPage, /世界魅力前厅/);
assert.match(entryPage, /start-card__fit/);
assert.match(entryPage, /start-card__route/);
assert.match(entryPage, /适合：我想先确认产品手感/);
assert.match(entryPage, /适合：我已有小说章节/);
assert.match(entryPage, /适合：我只有题材和冲突/);
assert.match(entryPage, /样例世界[\s\S]*天命书[\s\S]*沙盘轮次[\s\S]*卷宗阅读/);
assert.match(entryPage, /章节文本[\s\S]*世界锚定[\s\S]*天命书[\s\S]*沙盘轮次/);
assert.match(entryPage, /主题念头[\s\S]*创世草案[\s\S]*世界锚定[\s\S]*天命书/);
assert.match(entryPage, /vitalitySignals\.map/);
assert.match(entryPage, /signal\.detail/);
assert.match(entryPage, /journeyPulse\.map/);
assert.match(entryPage, /navigateStoryJourney\(spotlight\.slug, pulse\.key\)/);
assert.match(
  entryPage,
  /className="story-card__journey"/,
  "story cards should expose their journey pulse, not only the spotlight card",
);
assert.match(
  entryPage,
  /focus\.journeyPulse\.map/,
  "story cards should reuse the same journey pulse state as the recommendation logic",
);
assert.match(
  entryPage,
  /navigateStoryJourney\(s\.slug, pulse\.key\)/,
  "story card journey pulses should navigate to the matching world stage",
);
assert.match(
  entryPage,
  /aria-label=\{`\$\{s\.display_name\} 的世界旅程`\}/,
  "story card journey pulse should have a per-story accessible label",
);
assert(
  entryPage.indexOf('className="story-card__open"') <
    entryPage.indexOf('className="story-card__journey"') &&
    entryPage.indexOf('className="story-card__journey"') <
      entryPage.indexOf('className="story-card__primary"'),
  "story card journey pulse should sit outside the main open button and before the primary action",
);

const entryCss = readFileSync(resolve("src/components/storyEntry.css"), "utf8");
assert.match(entryCss, /\.entry__spotlight-pulse/);
assert.match(entryCss, /\.entry__spotlight-vitality/);
assert.match(entryCss, /\.entry__spotlight-vitality-grid/);
assert.match(entryCss, /\.entry__spotlight-vitality-card/);
assert.match(entryCss, /\.entry__spotlight-vitality-card strong/);
assert.match(entryCss, /\.start-card__fit/);
assert.match(entryCss, /\.start-card__route/);
assert.match(
  entryCss,
  /\.start-card__route[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/,
  "start cards should show four stable route stages on desktop",
);
assert.match(
  entryCss,
  /@media \(max-width: 560px\)[\s\S]*\.start-card__route[\s\S]*repeat\(2,\s*minmax\(0,\s*1fr\)\)/,
  "start card routes should collapse to two columns on narrow mobile",
);
assert.match(entryCss, /grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/);
assert.match(entryCss, /@media \(max-width: 560px\)[\s\S]*\.entry__spotlight-pulse[\s\S]*repeat\(2,\s*minmax\(0,\s*1fr\)\)/);
assert.match(
  entryCss,
  /@media \(max-width: 560px\)[\s\S]*\.entry__spotlight-vitality-grid[\s\S]*grid-template-columns:\s*1fr/,
  "spotlight vitality signals should collapse to one column on narrow mobile",
);
assert.match(entryCss, /\.story-card__journey/);
assert.match(
  entryCss,
  /\.story-card__journey[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/,
  "story card journey pulse should scan as four stable stages on desktop",
);
assert.match(
  entryCss,
  /@media \(max-width: 560px\)[\s\S]*\.story-card__journey[\s\S]*repeat\(2,\s*minmax\(0,\s*1fr\)\)/,
  "story card journey pulse should collapse to two columns on narrow mobile",
);

rmSync(resolve(".tmp-story-shelf-focus"), { recursive: true, force: true });

console.log("story shelf focus helper ok");
