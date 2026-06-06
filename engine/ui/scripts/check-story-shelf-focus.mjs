import assert from "node:assert/strict";
import { deriveStoryShelfFocus } from "../.tmp-story-shelf-focus/storyShelfFocus.js";

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

const defensive = deriveStoryShelfFocus({
  sourceKind: "imported",
  runCount: -2,
});

assert.equal(defensive.metrics[0].value, "0 条");
assert.equal(defensive.recommendedKey, "tianming");

console.log("story shelf focus helper ok");
