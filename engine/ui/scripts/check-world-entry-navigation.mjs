import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const appShell = readFileSync("src/components/AppShell.tsx", "utf8");
const storyEntry = readFileSync("src/components/StoryEntryPage.tsx", "utf8");
const worldAnchor = readFileSync("src/components/WorldAnchorPage.tsx", "utf8");
const context = readFileSync("src/worldRouteContext.ts", "utf8");

assert(
  /function worldSlug[\s\S]*route\.name === "worldChronicle"[\s\S]*route\.name === "anchorVolume"/.test(
    appShell,
  ),
  "AppShell should treat independent world volume pages as world routes.",
);
assert(
  /function worldlineId[\s\S]*route\.name === "worldChronicle"[\s\S]*route\.name === "anchorVolume"/.test(
    appShell,
  ),
  "AppShell should preserve worldline ids for world chronicle and anchor volume pages.",
);
assert(
  appShell.includes("正史卷") && appShell.includes("锚点卷"),
  "AppShell top navigation should expose world chronicle and anchor volume as first-class dossier rooms.",
);
const worldNavStart = appShell.indexOf('className="world-nav"');
const worldNavEnd = appShell.indexOf('title="切换强反馈动效', worldNavStart);
const worldNav = appShell.slice(worldNavStart, worldNavEnd);
assert(
  worldNav.indexOf("正史卷") < worldNav.indexOf("世界线") &&
    worldNav.indexOf("锚点卷") < worldNav.indexOf("世界线"),
  "World volume entries should appear before worldline/mechanism tracing in the top navigation.",
);

assert(
  storyEntry.includes("openWorldRoom") &&
    storyEntry.includes('navigate({ name: "anchor", slug })'),
  "Story shelf cards should open the world room before pushing users into feature panels.",
);
assert(
  storyEntry.includes("进入世界") &&
    storyEntry.includes("世界正史卷") &&
    storyEntry.includes("主锚点卷") &&
    storyEntry.includes("长线卷"),
  "Story shelf should offer world-room and dossier exits, not only sandbox/workspace actions.",
);
assert(
  !/className="story-card__link"[\s\S]{0,160}navigate\(\{ name: "workspace"/.test(storyEntry),
  "Story cards should not keep mechanism archive as a default footer action.",
);
assert(
  !/className="entry__spotlight-links"[\s\S]*navigate\(\{ name: "workspace"/.test(storyEntry),
  "Spotlight card should not advertise mechanism archive as a default action.",
);

for (const label of [
  "世界正史卷",
  "主锚点卷",
  "角色个人卷",
  "势力卷",
  "事件多视角",
  "跨事件长线卷",
]) {
  assert(worldAnchor.includes(label), `World anchor gateway should expose ${label}.`);
}
for (const routeName of [
  'name: "worldChronicle"',
  'name: "anchorVolume"',
  'name: "characterVolume"',
  'name: "factionVolume"',
  'name: "dossierReading"',
  'name: "longlineReading"',
]) {
  assert(worldAnchor.includes(routeName), `World anchor gateway should route through ${routeName}.`);
}
assert(
  worldAnchor.includes("firstCharacterId") && worldAnchor.includes("firstFactionId"),
  "World anchor gateway should use real story characters/factions for first dossier jumps.",
);
assert(
  /className="anchor__archive-link"[\s\S]*机制档案/.test(worldAnchor),
  "Mechanism archive should be demoted to a trace/archive link on the world anchor page.",
);

assert(
  context.includes("世界内部卷宗") && context.includes("主场景页"),
  "World route context should describe the default navigation as world dossiers and scene pages.",
);

console.log("world entry navigation structure ok");
