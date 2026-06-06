import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/WorldAnchorPage.tsx", "utf8");
const css = readFileSync("src/components/worldAnchor.css", "utf8");

assert(
  page.includes("anchor__status-ribbon"),
  "world anchor should expose a compact world status ribbon",
);
assert(
  page.indexOf("<WorldStatusRibbon") <
    page.indexOf("<WorldDossierGateway data={data} recentReading={recentReading} compact />"),
  "mobile world status ribbon should appear before the compact dossier gateway",
);
assert(
  page.includes("!compact &&") && page.includes("<WorldStatusRibbon journey={journey}"),
  "desktop world status ribbon should appear inside the full dossier gateway",
);
for (const marker of ["当前阶段", "下一步", "世界脉搏"]) {
  assert(page.includes(marker), `world status ribbon should include ${marker}`);
}
assert(
  page.includes("journey.phaseLabel") && page.includes("journey.recommendedAction"),
  "world status ribbon should reuse journey phase and recommended action",
);
assert(
  page.includes("pulse.slice(0, 3)"),
  "world status ribbon should reuse compact pulse data",
);
assert(
  css.includes(".anchor__status-ribbon"),
  "world status ribbon should have dedicated styling",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.anchor__status-ribbon/.test(css),
  "world status ribbon should have mobile layout rules",
);

console.log("world anchor status ribbon structure ok");
