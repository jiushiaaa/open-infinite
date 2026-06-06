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

console.log("longline reading ux structure ok");
