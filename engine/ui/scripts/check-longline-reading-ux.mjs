import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/LonglineReadingPage.tsx", "utf8");
const css = readFileSync("src/components/longlineReading.css", "utf8");

assert(
  page.includes("scrollToPageItem"),
  "longline page should expose direct scroll actions",
);
assert(
  page.includes('className="longline-mobile-guide"'),
  "longline mobile guide should be present",
);
assert(
  page.indexOf('className="longline-mobile-guide"') < page.indexOf("<WorldRunway"),
  "longline mobile guide should appear before the explanatory runway",
);
assert(
  page.includes('className="longline-recovery-orchestrator"'),
  "longline page should include a cross-chapter recovery orchestrator",
);
assert(
  page.indexOf("<WorldRunway") < page.indexOf('className="longline-recovery-orchestrator"'),
  "longline recovery orchestrator should appear after the explanatory runway",
);
assert(
  page.indexOf('className="longline-recovery-orchestrator"') <
    page.indexOf('className="longline-briefing"'),
  "longline recovery orchestrator should appear before the reading briefing grid",
);
assert(
  page.includes('className="longline-continuation-map"'),
  "longline page should include a cross-chapter continuation map",
);
assert(
  page.indexOf('className="longline-recovery-orchestrator"') <
    page.indexOf('className="longline-continuation-map"'),
  "longline continuation map should appear after the recovery orchestrator",
);
assert(
  page.indexOf('className="longline-continuation-map"') <
    page.indexOf('className="longline-briefing"'),
  "longline continuation map should appear before the reading briefing grid",
);
assert(
  page.includes("interface LonglineEntityLane") &&
    page.includes("buildLonglineEntityLanes") &&
    page.includes("longlineEntityLanes"),
  "longline page should derive character and faction tracking lanes from existing timeline data",
);
assert(
  page.includes('className="longline-entity-lanes"') &&
    page.includes('aria-label="角色与势力追踪带"') &&
    page.includes("longlineEntityLanes.map"),
  "longline page should render character and faction tracking lanes",
);
assert(
  page.indexOf('className="longline-continuation-map"') <
    page.indexOf('className="longline-entity-lanes"') &&
    page.indexOf('className="longline-entity-lanes"') <
      page.indexOf('className="longline-briefing"'),
  "longline entity lanes should sit between continuation map and briefing grid",
);
for (const label of ["跨章回收台", "当前张力", "首要误会", "活跃线索", "下一章钩子", "送到作者台"]) {
  assert(page.includes(label), `longline recovery orchestrator should include ${label}`);
}
for (const label of ["跨章承接地图", "现在读到", "来源事件", "误会余波", "下一轮去向", "世界线怎样继续"]) {
  assert(page.includes(label), `longline continuation map should include ${label}`);
}
for (const label of ["角色与势力追踪带", "按角色追", "按势力追", "看这条长线", "谁还带着后果往前走"]) {
  assert(page.includes(label), `longline entity lanes should include ${label}`);
}
for (const field of ["misbelief_recovery", "open_threads", "current_tension", "next_chapter_hook"]) {
  assert(page.includes(field), `longline recovery orchestrator should use ${field}`);
}
for (const field of ["activeEntry", "activeEvent", "primaryMisbelief", "next_actions"]) {
  assert(page.includes(field), `longline continuation map should use ${field}`);
}
for (const field of [
  "timeline_entries",
  "affected_characters",
  "affected_factions",
  "misbelief_recovery.items",
  "focusEntry(lane.primaryEntryId)",
]) {
  assert(page.includes(field), `longline entity lanes should use ${field}`);
}
for (const label of ["读长线", "按事件追", "回收误会", "作者台"]) {
  assert(page.includes(label), `longline mobile guide should include ${label}`);
}
assert(
  css.includes(".longline-mobile-guide") && css.includes("display: none"),
  "longline mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.longline-mobile-guide[\s\S]*display: grid/.test(css),
  "longline mobile guide should be visible on mobile widths",
);
assert(
  css.includes(".longline-recovery-orchestrator") &&
    css.includes("grid-template-columns: minmax(220px, 0.8fr) repeat(3, minmax(0, 1fr))"),
  "longline recovery orchestrator should use a stable desktop grid",
);
assert(
  css.includes(".longline-continuation-map") &&
    css.includes("grid-template-columns: minmax(220px, 0.9fr) repeat(4, minmax(0, 1fr))"),
  "longline continuation map should use a stable desktop grid",
);
assert(
  css.includes(".longline-entity-lanes") &&
    css.includes(".longline-entity-lanes__grid") &&
    css.includes(".longline-entity-lane") &&
    css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "longline entity lanes should use a stable four-card desktop grid",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.longline-recovery-orchestrator[\s\S]*grid-template-columns: 1fr/.test(css),
  "longline recovery orchestrator should collapse to one column on mobile widths",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.longline-continuation-map[\s\S]*grid-template-columns: 1fr/.test(css),
  "longline continuation map should collapse to one column on mobile widths",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.longline-entity-lanes__grid[\s\S]*grid-template-columns: 1fr/.test(css),
  "longline entity lanes should collapse to one column on mobile widths",
);

console.log("longline reading ux structure ok");
