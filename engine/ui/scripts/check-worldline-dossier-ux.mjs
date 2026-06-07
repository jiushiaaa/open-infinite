import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/WorldlineDossierPage.tsx", "utf8");
const css = readFileSync("src/components/worldlineDossier.css", "utf8");

assert(
  page.includes("scrollToWorldlineItem"),
  "worldline dossier page should expose direct scroll actions",
);
assert(
  page.includes('className="worldline-mobile-guide"'),
  "worldline mobile guide should be present",
);
assert(
  page.indexOf('className="worldline-mobile-guide"') <
    page.indexOf('className="worldline-command"'),
  "worldline mobile guide should appear before the full workflow summary",
);
assert(
  page.indexOf('className="worldline-mobile-guide"') < page.indexOf("<WorldRunway"),
  "worldline mobile guide should appear before the explanatory runway",
);
assert(
  page.includes('className="worldline-continuity-rail"'),
  "worldline dossier page should include a state continuity rail",
);
assert(
  page.indexOf('className="worldline-command"') <
    page.indexOf('className="worldline-continuity-rail"'),
  "worldline continuity rail should appear after the workflow summary",
);
assert(
  page.indexOf('className="worldline-continuity-rail"') < page.indexOf("<WorldRunway"),
  "worldline continuity rail should appear before the explanatory runway",
);
assert(
  page.includes('className="worldline-compensation-compass"'),
  "worldline dossier page should include a compensation compass",
);
assert(
  page.indexOf('className="worldline-continuity-rail"') <
    page.indexOf('className="worldline-compensation-compass"'),
  "worldline compensation compass should appear after the continuity rail",
);
assert(
  page.indexOf('className="worldline-compensation-compass"') < page.indexOf("<WorldRunway"),
  "worldline compensation compass should appear before the explanatory runway",
);
assert(
  page.includes('className="worldline-fermentation-ledger"'),
  "worldline dossier page should include a world fermentation ledger",
);
assert(
  page.indexOf('className="worldline-compensation-compass"') <
    page.indexOf('className="worldline-fermentation-ledger"'),
  "worldline fermentation ledger should appear after the compensation compass",
);
assert(
  page.indexOf('className="worldline-fermentation-ledger"') < page.indexOf("<WorldRunway"),
  "worldline fermentation ledger should appear before the explanatory runway",
);
for (const label of ["代偿罗盘", "最近代价", "承压领域", "下一轮提示", "从这里继续看"]) {
  assert(page.includes(label), `worldline compensation compass should include ${label}`);
}
for (const label of ["世界发酵账", "最近写入", "承压域", "下一轮会消费", "去长线卷"]) {
  assert(page.includes(label), `worldline fermentation ledger should include ${label}`);
}
for (const field of [
  "state?.consequence_state?.summary",
  "state?.consequence_state?.ledger",
  "state?.consequence_state?.next_round_hint",
  "consequenceDomains",
]) {
  assert(page.includes(field), `worldline compensation compass should use ${field}`);
}
for (const label of ["状态接力", "角色记忆", "因果代偿", "检查点", "下一轮入口"]) {
  assert(page.includes(label), `worldline continuity rail should include ${label}`);
}
for (const field of ["nextRoundReads", "consequenceDomains", "latestCheckpoint"]) {
  assert(page.includes(field), `worldline continuity rail should use ${field}`);
}
for (const field of ["fermentationLedgerItems", "fermentationDomainItems"]) {
  assert(page.includes(field), `worldline fermentation ledger should use ${field}`);
}
for (const label of ["回放", "看代偿", "看任务", "长线卷"]) {
  assert(page.includes(label), `worldline mobile guide should include ${label}`);
}
for (const targetClass of [
  "worldline-actions-section",
  "worldline-consequence-section",
  "worldline-task-section",
]) {
  assert(page.includes(targetClass), `worldline dossier page should keep ${targetClass}`);
}
assert(
  css.includes(".worldline-mobile-guide") && css.includes("display: none"),
  "worldline mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.worldline-mobile-guide[\s\S]*display: grid/.test(css),
  "worldline mobile guide should be visible on mobile widths",
);
assert(
  css.includes(".worldline-continuity-rail") &&
    css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "worldline continuity rail should use a stable four-column desktop grid",
);
assert(
  css.includes(".worldline-compensation-compass") &&
    css.includes(".worldline-compensation-compass__grid"),
  "worldline compensation compass styling should be present",
);
assert(
  css.includes(".worldline-fermentation-ledger") &&
    css.includes(".worldline-fermentation-ledger__timeline"),
  "worldline fermentation ledger styling should be present",
);
assert(
  css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "worldline compensation compass should use a stable desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.worldline-continuity-rail[\s\S]*grid-template-columns: 1fr/.test(css),
  "worldline continuity rail should collapse to one column on mobile widths",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.worldline-compensation-compass__grid[\s\S]*grid-template-columns: 1fr/.test(css),
  "worldline compensation compass should collapse to one column on mobile widths",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.worldline-fermentation-ledger__body[\s\S]*grid-template-columns: 1fr/.test(css),
  "worldline fermentation ledger should collapse to one column on mobile widths",
);

console.log("worldline dossier ux structure ok");
