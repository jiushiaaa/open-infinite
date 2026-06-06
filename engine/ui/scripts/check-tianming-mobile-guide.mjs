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

console.log("tianming mobile guide structure ok");
