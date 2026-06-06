import assert from "node:assert/strict";
import { deriveWorldJourney, deriveWorldPulse } from "../.tmp-world-journey/worldJourney.js";

const base = {
  slug: "my-story",
  runCount: 0,
  characterCount: 3,
  openThreadCount: 2,
  factionCount: 1,
  currentChapter: 1,
  hasRecentReading: false,
};

const fresh = deriveWorldJourney(base);
assert.equal(fresh.phaseLabel, "待确认天命");
assert.equal(fresh.recommendedKey, "tianming");
assert.equal(fresh.recommendedAction, "确认天命");
assert.equal(fresh.steps[0].status, "next");
assert.equal(fresh.steps[1].status, "ready");
assert.equal(fresh.steps[2].status, "waiting");
assert.equal(fresh.steps[3].status, "waiting");

const running = deriveWorldJourney({ ...base, runCount: 2 });
assert.equal(running.phaseLabel, "已有沙盘结果");
assert.equal(running.recommendedKey, "reading");
assert.equal(running.recommendedAction, "进入卷宗阅读");
assert.equal(running.steps[0].status, "ready");
assert.equal(running.steps[1].status, "ready");
assert.equal(running.steps[2].status, "next");
assert.equal(running.steps[3].status, "ready");

const reading = deriveWorldJourney({ ...base, runCount: 2, hasRecentReading: true });
assert.equal(reading.phaseLabel, "可继续阅读");
assert.equal(reading.recommendedKey, "reading");
assert.equal(reading.recommendedAction, "继续阅读");
assert.match(reading.phaseDescription, /最近读到的卷宗/);

const sparse = deriveWorldJourney({
  ...base,
  characterCount: 0,
  openThreadCount: 0,
  currentChapter: null,
});
assert.equal(sparse.steps[0].summary, "0 条伏笔");
assert.equal(sparse.steps[1].status, "waiting");

const pulse = deriveWorldPulse({ ...base, runCount: 2 });
assert.equal(pulse.length, 4);
assert.deepEqual(
  pulse.map((item) => item.key),
  ["chapter", "characters", "threads", "runs"],
);
assert.equal(pulse[0].value, "第 1 章");
assert.match(pulse[3].hint, /沙盘/);

console.log("world journey helper ok");
