import assert from "node:assert/strict";
import { getWorldRouteContext } from "../.tmp-world-route-context/worldRouteContext.js";

const context = getWorldRouteContext({
  name: "sandbox",
  slug: "my-story",
});

assert.equal(context?.sectionLabel, "运行");
assert.equal(context?.title, "世界沙盘");
assert.match(context?.description ?? "", /让角色行动/);
assert.deepEqual(context?.primaryRoute, {
  name: "dossierReading",
  slug: "my-story",
  worldlineId: "main",
});
assert.equal(context?.primaryActionLabel, "进入卷宗阅读");
assert.deepEqual(context?.workspaceSummary, {
  stageLabel: "运行",
  stageTitle: "世界沙盘",
  worldlineLabel: "世界线 main",
  nextStepLabel: "进入卷宗阅读",
  why: "本轮行动会进入记忆、代偿和下一章材料。",
});
assert.deepEqual(
  context?.stateHandoffs.map((item) => [item.key, item.label, item.title]),
  [
    ["source", "正在承接", "事件与干预"],
    ["effect", "会留下", "记忆与代偿"],
    ["receipt", "下一处看见", "进入卷宗阅读"],
  ],
);
assert.deepEqual(context?.stateHandoffs[1].route, {
  name: "worldline",
  slug: "my-story",
  worldlineId: "main",
});
assert.deepEqual(
  context?.stages.map((stage) => [stage.key, stage.label, stage.status]),
  [
    ["tianming", "定界", "ready"],
    ["sandbox", "运行", "active"],
    ["reading", "阅读", "ready"],
    ["author", "采纳", "ready"],
  ],
);
assert.deepEqual(context?.stages[2].route, {
  name: "dossierReading",
  slug: "my-story",
  worldlineId: "main",
});
assert.deepEqual(
  context?.dossiers.map((item) => [item.key, item.label, item.status]),
  [
    ["continuous", "正文", "ready"],
    ["world", "正史", "ready"],
    ["anchor", "锚点", "ready"],
    ["character", "角色", "ready"],
    ["faction", "势力", "ready"],
    ["event", "事件", "ready"],
    ["longline", "长线", "ready"],
    ["worldline", "世界线", "ready"],
  ],
);
assert.deepEqual(context?.dossiers[1].route, {
  name: "worldChronicle",
  slug: "my-story",
  worldlineId: "main",
});
assert.deepEqual(context?.dossiers[2].route, {
  name: "anchorVolume",
  slug: "my-story",
  worldlineId: "main",
});

const character = getWorldRouteContext({
  name: "characterVolume",
  slug: "my-story",
  worldlineId: "branch-a",
  characterId: "zhao_xuan",
});

assert.equal(character?.sectionLabel, "角色卷");
assert.equal(character?.title, "角色个人卷");
assert.deepEqual(character?.primaryRoute, {
  name: "sandbox",
  slug: "my-story",
});
assert.equal(character?.secondaryActionLabel, "去多视角");
assert.equal(character?.workspaceSummary.stageLabel, "阅读");
assert.equal(character?.workspaceSummary.worldlineLabel, "世界线 branch-a");
assert.match(character?.workspaceSummary.why ?? "", /记忆、误会和秘密/);
assert.match(character?.stateHandoffs[0].detail ?? "", /主观记忆/);
assert.deepEqual(character?.stateHandoffs[2].route, {
  name: "sandbox",
  slug: "my-story",
});
assert.deepEqual(character?.secondaryRoute, {
  name: "lens",
  slug: "my-story",
});
assert.equal(character?.stages.find((stage) => stage.key === "reading")?.status, "active");
assert.deepEqual(character?.stages.find((stage) => stage.key === "sandbox")?.route, {
  name: "sandbox",
  slug: "my-story",
});
assert.equal(character?.dossiers.find((item) => item.key === "character")?.status, "active");

const chronicle = getWorldRouteContext({
  name: "worldChronicle",
  slug: "my-story",
  worldlineId: "branch-a",
});

assert.equal(chronicle?.sectionLabel, "正史卷");
assert.equal(chronicle?.title, "世界正史卷");
assert.equal(chronicle?.dossiers.find((item) => item.key === "world")?.status, "active");
assert.deepEqual(chronicle?.primaryRoute, {
  name: "anchorVolume",
  slug: "my-story",
  worldlineId: "branch-a",
});
assert.match(chronicle?.workspaceSummary.why ?? "", /世界承认的事实/);

const anchor = getWorldRouteContext({
  name: "anchorVolume",
  slug: "my-story",
  worldlineId: "branch-a",
});

assert.equal(anchor?.sectionLabel, "锚点卷");
assert.equal(anchor?.title, "主锚点卷");
assert.equal(anchor?.dossiers.find((item) => item.key === "anchor")?.status, "active");
assert.deepEqual(anchor?.secondaryRoute, {
  name: "worldChronicle",
  slug: "my-story",
  worldlineId: "branch-a",
});
assert.match(anchor?.workspaceSummary.why ?? "", /锚点压力/);

const longline = getWorldRouteContext({
  name: "longlineReading",
  slug: "my-story",
  worldlineId: "branch-a",
});

assert.equal(longline?.dossiers.find((item) => item.key === "longline")?.status, "active");
assert.deepEqual(longline?.dossiers.find((item) => item.key === "world")?.route, {
  name: "worldChronicle",
  slug: "my-story",
  worldlineId: "branch-a",
});

const entry = getWorldRouteContext({ name: "entry" });
assert.equal(entry, null);

console.log("world route context helper ok");
