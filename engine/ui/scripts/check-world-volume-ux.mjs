import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const routing = readFileSync("src/routing.ts", "utf8");
const app = readFileSync("src/App.tsx", "utf8");
const context = readFileSync("src/worldRouteContext.ts", "utf8");
const readingProgress = readFileSync("src/readingProgress.ts", "utf8");
const page = readFileSync("src/components/WorldVolumePage.tsx", "utf8");
const css = readFileSync("src/components/worldVolume.css", "utf8");

assert(
  routing.includes('name: "worldChronicle"') && routing.includes('name: "anchorVolume"'),
  "routing should define independent world chronicle and anchor volume routes",
);
assert(
  routing.includes('parts[4] === "chronicle"') && routing.includes('parts[4] === "anchors"'),
  "routing should parse /chronicle and /anchors world volume URLs",
);
assert(
  routing.includes('route.name === "worldChronicle"') &&
    routing.includes('route.name === "anchorVolume"'),
  "routing should navigate to independent world volume URLs",
);
assert(
  app.includes('import { WorldVolumePage } from "./components/WorldVolumePage"'),
  "App should import the shared world volume page",
);
assert(
  app.includes('route.name === "worldChronicle"') &&
    app.includes('volumeKind="chronicle"') &&
    app.includes('route.name === "anchorVolume"') &&
    app.includes('volumeKind="anchor"'),
  "App should render both world chronicle and anchor volume pages",
);

assert(
  context.includes('route.name === "worldChronicle"') &&
    context.includes('route.name === "anchorVolume"'),
  "world route context should understand independent world volume pages",
);
assert(
  context.includes('name: "worldChronicle"') &&
    context.includes('name: "anchorVolume"') &&
    !context.includes('tab: "world_chronicle",\n    },\n    {\n      key: "anchor"'),
  "global dossier links should route to independent world and anchor pages",
);
for (const label of ["正史卷", "主锚点卷", "世界正史卷", "主锚点卷"]) {
  assert(context.includes(label), `world route context should include ${label}`);
}

assert(
  readingProgress.includes('Extract<Route, { name: "worldChronicle" }>') &&
    readingProgress.includes('Extract<Route, { name: "anchorVolume" }>'),
  "recent reading should treat independent world volumes as readable routes",
);
assert(
  readingProgress.includes("继续读世界正史卷") &&
    readingProgress.includes("继续读主锚点卷"),
  "recent reading labels should describe independent world volumes",
);

assert(
  page.includes("export function WorldVolumePage") &&
    page.includes('type WorldVolumeKind = "chronicle" | "anchor"') &&
    page.includes("volumeKind: WorldVolumeKind"),
  "WorldVolumePage should expose one shared component for both volumes",
);
assert(
  page.includes("api.getDossierReading(slug, worldlineId)") &&
    page.includes("volumeId") &&
    page.includes("world_chronicle") &&
    page.includes("anchor_volume"),
  "WorldVolumePage should reuse existing dossier-reading data and volume tabs",
);
for (const label of [
  "世界正史卷",
  "主锚点卷",
  "正史接力台",
  "锚点接力台",
  "世界怎样记住",
  "锚点怎样承压",
  "回卷宗阅读",
  "继续沙盘",
  "作者台",
]) {
  assert(page.includes(label), `WorldVolumePage should include ${label}`);
}
for (const token of [
  "<WorldRunway",
  "renderProse(activeVolume.body_md)",
  "activeVolume?.evidence_refs",
  "report.evidence_panel.refs",
  "navigate({ name: \"worldChronicle\"",
  "navigate({ name: \"anchorVolume\"",
]) {
  assert(page.includes(token), `WorldVolumePage should preserve ${token}`);
}
assert(
  page.indexOf('className="world-volume-mobile-guide"') < page.indexOf("<WorldRunway"),
  "mobile world volume guide should appear before the explanatory runway",
);
assert(
  page.indexOf('className="world-volume-handoff"') < page.indexOf('className="world-volume-layout"'),
  "world volume handoff should appear before the long reading layout",
);

assert(
  css.includes(".world-volume-page") &&
    css.includes(".world-volume-mobile-guide") &&
    css.includes(".world-volume-handoff") &&
    css.includes(".world-volume-layout"),
  "world volume CSS should define page, mobile guide, handoff, and layout classes",
);
assert(
  css.includes("grid-template-columns: minmax(240px, 300px) minmax(0, 720px) minmax(240px, 300px)"),
  "world volume layout should use a stable three-column desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.world-volume-mobile-guide[\s\S]*display: grid/.test(css),
  "world volume mobile guide should be visible on mobile widths",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.world-volume-layout[\s\S]*display: flex/.test(css),
  "world volume layout should collapse for mobile without hiding sections",
);

console.log("world volume ux structure ok");
