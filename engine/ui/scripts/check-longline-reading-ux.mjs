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
for (const label of ["跨章回收台", "当前张力", "首要误会", "活跃线索", "下一章钩子", "送到作者台"]) {
  assert(page.includes(label), `longline recovery orchestrator should include ${label}`);
}
for (const field of ["misbelief_recovery", "open_threads", "current_tension", "next_chapter_hook"]) {
  assert(page.includes(field), `longline recovery orchestrator should use ${field}`);
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
  /@media \(max-width: 820px\)[\s\S]*\.longline-recovery-orchestrator[\s\S]*grid-template-columns: 1fr/.test(css),
  "longline recovery orchestrator should collapse to one column on mobile widths",
);

console.log("longline reading ux structure ok");
