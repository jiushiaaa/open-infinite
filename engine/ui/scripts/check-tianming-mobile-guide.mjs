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

console.log("tianming mobile guide structure ok");
