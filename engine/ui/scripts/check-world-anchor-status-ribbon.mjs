import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/WorldAnchorPage.tsx", "utf8");
const css = readFileSync("src/components/worldAnchor.css", "utf8");

assert(
  page.includes("anchor__status-ribbon"),
  "world anchor should expose a compact world status ribbon",
);
assert(
  page.includes("anchor__awakening") && page.includes("<WorldAwakeningFoyer"),
  "world anchor should expose a world awakening foyer",
);
assert(
  page.indexOf("<WorldAwakeningFoyer") < page.indexOf("<WorldDossierGateway data={data}"),
  "desktop world awakening foyer should appear before the full dossier gateway",
);
assert(
  page.includes("compactAwakening") && page.includes("anchor__awakening--compact"),
  "world anchor should include a compact mobile awakening foyer",
);
for (const label of ["世界苏醒台", "世界醒着吗", "谁会行动", "哪条伏笔牵引", "从哪里继续"]) {
  assert(page.includes(label), `world awakening foyer should include ${label}`);
}
for (const field of [
  "deriveWorldJourney",
  "deriveWorldPulse",
  "recentReading",
  "data.run_count",
  "data.characters[0]",
  "data.open_threads[0]",
]) {
  assert(page.includes(field), `world awakening foyer should use ${field}`);
}
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
  css.includes(".anchor__awakening") && css.includes(".anchor__awakening-grid"),
  "world awakening foyer should have dedicated styling",
);
assert(
  css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "world awakening foyer should use a stable four-column desktop grid",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.anchor__status-ribbon/.test(css),
  "world status ribbon should have mobile layout rules",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.anchor__awakening--full[\s\S]*display: none/.test(css),
  "full world awakening foyer should be hidden on mobile",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.anchor__awakening--compact[\s\S]*display: grid/.test(css),
  "compact world awakening foyer should appear on mobile",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.anchor__awakening-grid[\s\S]*grid-template-columns: 1fr/.test(css),
  "world awakening foyer should collapse to one column on mobile",
);

console.log("world anchor status ribbon structure ok");
