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
assert(
  page.includes("factionPressureArcSignals"),
  "faction volume page should derive a concise pressure arc",
);
assert(
  page.includes('className="faction-pressure-arc"') &&
    page.includes('aria-label="势力代偿弧线"'),
  "faction volume page should include a faction pressure arc section",
);
assert(
  page.indexOf('className="faction-pressure-handoff"') <
    page.indexOf('className="faction-pressure-arc"') &&
    page.indexOf('className="faction-pressure-arc"') <
      page.indexOf('className="faction-volume-layout"'),
  "faction pressure arc should bridge the handoff and the detailed reading layout",
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
for (const label of ["势力代偿弧线", "最近写入", "承压领域", "资源/秘密", "下一轮秩序"]) {
  assert(page.includes(label), `faction pressure arc should include ${label}`);
}
for (const field of ["source_run_id", "major_event", "debt_score", "impacts", "next_round_hint"]) {
  assert(page.includes(field), `faction pressure arc should use ${field}`);
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
assert(
  css.includes(".faction-pressure-arc") &&
    css.includes(".faction-pressure-arc__grid") &&
    css.includes(".faction-pressure-arc__step"),
  "faction pressure arc should have dedicated layout styles",
);
assert(
  css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "faction pressure arc should use a stable four-column desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.faction-pressure-arc__grid[\s\S]*grid-template-columns: 1fr/.test(css),
  "faction pressure arc should collapse to one column on mobile",
);

console.log("faction volume ux structure ok");
