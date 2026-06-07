import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/TianmingPage.tsx", "utf8");
const css = readFileSync("src/components/tianming.css", "utf8");

assert(
  page.includes("scrollToTianmingItem"),
  "tianming page should expose direct mobile scroll actions",
);
assert(
  page.includes('className="tianming-mobile-guide"'),
  "tianming mobile guide should be present",
);
assert(
  page.indexOf('className="tianming-mobile-guide"') <
    page.indexOf('className="tianming-command"'),
  "tianming mobile guide should appear before the full workflow summary",
);
for (const label of ["生成", "确认", "沙盘", "看锚点", "投干预"]) {
  assert(page.includes(label), `tianming mobile guide should include ${label}`);
}
for (const targetClass of [
  "tianming-anchor-section",
  "tianming-compiler",
  "tianming-compensation",
]) {
  assert(page.includes(targetClass), `tianming page should keep ${targetClass}`);
}
assert(
  css.includes(".tianming-mobile-guide") && css.includes("display: none"),
  "tianming mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.tianming-mobile-guide[\s\S]*display: grid/.test(css),
  "tianming mobile guide should be visible on mobile widths",
);
assert(
  page.includes("tianming-confirmation-handoff"),
  "confirmed tianming page should include a handoff rail before detailed panels",
);
assert(
  page.includes("天命生效接力台"),
  "confirmed tianming handoff should name the handoff moment in product language",
);
for (const label of ["世界宪法已生效", "锚点承压", "干预边界", "沙盘就绪"]) {
  assert(page.includes(label), `tianming handoff should include ${label}`);
}
assert(
  page.includes("book.anchor_status.current_anchor_name"),
  "tianming handoff should use the current anchor name",
);
assert(
  page.includes("book.anchor_status.risk"),
  "tianming handoff should show anchor risk",
);
assert(
  page.includes("book.mutation_policy.ordinary_intervention"),
  "tianming handoff should explain ordinary intervention policy",
);
assert(
  page.includes("book.contract_pressure.pressure_tiers"),
  "tianming handoff should use contract pressure tiers",
);
assert(
  page.indexOf("天命生效接力台") < page.indexOf('className="tianming-layout"'),
  "tianming handoff should appear before the detailed tianming panels",
);
assert(
  page.includes("tianming-next-round-brief"),
  "confirmed tianming page should include a next-round launch brief",
);
assert(
  page.includes("下一轮启动简报"),
  "next-round launch brief should name the operational handoff",
);
assert(
  page.indexOf("天命生效接力台") < page.indexOf('className="tianming-next-round-brief"') &&
    page.indexOf('className="tianming-next-round-brief"') <
      page.indexOf('className="tianming-layout"'),
  "next-round launch brief should sit between the handoff rail and detailed panels",
);
for (const label of ["会被消费的锚点", "当前压力档", "牵引吸引子", "候选承载者"]) {
  assert(page.includes(label), `next-round launch brief should include ${label}`);
}
for (const field of [
  "book.narrative_attractors[0]",
  "book.replacement_anchor_candidates[0]",
  "activeTier?.drivers",
  "book.mutation_policy.ordinary_intervention",
]) {
  assert(page.includes(field), `next-round launch brief should use ${field}`);
}
for (const actionLabel of ["启动世界沙盘", "先投放干预", "看锚点压力"]) {
  assert(page.includes(actionLabel), `next-round launch brief should include ${actionLabel}`);
}
assert(css.includes(".tianming-confirmation-handoff"), "tianming handoff should have styles");
assert(
  /\.tianming-confirmation-handoff__grid[\s\S]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "tianming handoff should use a four-column desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.tianming-confirmation-handoff__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "tianming handoff should collapse to one column on mobile",
);
assert(css.includes(".tianming-next-round-brief"), "next-round launch brief should have styles");
assert(
  /\.tianming-next-round-brief[\s\S]*grid-template-columns: minmax\(0, 0.78fr\) minmax\(0, 1.22fr\)/.test(
    css,
  ),
  "next-round launch brief should have a desktop summary/detail split",
);
assert(
  /\.tianming-next-round-brief__grid[\s\S]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "next-round launch brief should use a two-column detail grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.tianming-next-round-brief[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "next-round launch brief should collapse to one column on mobile",
);

console.log("tianming mobile guide structure ok");
