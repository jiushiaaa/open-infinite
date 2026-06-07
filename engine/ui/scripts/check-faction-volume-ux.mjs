import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/FactionVolumePage.tsx", "utf8");
const css = readFileSync("src/components/factionVolume.css", "utf8");

assert(
  page.includes("scrollToFactionItem"),
  "faction volume page should expose direct scroll actions",
);
assert(
  page.includes('className="faction-volume-mobile-guide"'),
  "faction volume mobile guide should be present",
);
assert(
  page.indexOf('className="faction-volume-mobile-guide"') < page.indexOf("<WorldRunway"),
  "faction volume mobile guide should appear before the explanatory runway",
);
assert(
  page.includes('className="faction-pressure-handoff"'),
  "faction volume should expose a pressure handoff rail",
);
assert(
  page.indexOf("<WorldRunway") < page.indexOf('className="faction-pressure-handoff"') &&
    page.indexOf('className="faction-pressure-handoff"') < page.indexOf('className="faction-volume-layout"'),
  "faction pressure handoff should bridge the runway and the detailed reading layout",
);
for (const label of ["看站位", "查代偿", "换势力", "作者台"]) {
  assert(page.includes(label), `faction volume mobile guide should include ${label}`);
}
for (const label of ["势力压力接力台", "当前站位", "代偿压力", "最近记录", "下一轮秩序", "把势力压力送到作者台"]) {
  assert(page.includes(label), `faction pressure handoff should include ${label}`);
}
for (const field of ["primaryImpact", "activeVolume", "domain", "latestLedger", "consequence"]) {
  assert(page.includes(field), `faction pressure handoff should use ${field}`);
}
assert(
  css.includes(".faction-volume-mobile-guide") && css.includes("display: none"),
  "faction volume mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.faction-volume-mobile-guide[\s\S]*display: grid/.test(css),
  "faction volume mobile guide should be visible on mobile widths",
);
assert(
  css.includes(".faction-pressure-handoff") &&
    css.includes("grid-template-columns: minmax(220px, 0.8fr) repeat(3, minmax(0, 1fr))"),
  "faction pressure handoff should use a stable desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.faction-pressure-handoff[\s\S]*grid-template-columns: 1fr/.test(css),
  "faction pressure handoff should collapse to one column on mobile",
);

console.log("faction volume ux structure ok");
