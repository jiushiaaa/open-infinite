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
assert.deepEqual(character?.secondaryRoute, {
  name: "lens",
  slug: "my-story",
});
assert.equal(character?.stages.find((stage) => stage.key === "reading")?.status, "active");
assert.deepEqual(character?.stages.find((stage) => stage.key === "sandbox")?.route, {
  name: "sandbox",
  slug: "my-story",
});

const entry = getWorldRouteContext({ name: "entry" });
assert.equal(entry, null);

console.log("world route context helper ok");
