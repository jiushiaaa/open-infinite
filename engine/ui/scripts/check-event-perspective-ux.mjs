import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/EventPerspectivePage.tsx", "utf8");
const css = readFileSync("src/components/eventPerspective.css", "utf8");

assert(
  page.includes("scrollToEventItem"),
  "event perspective page should expose direct scroll actions",
);
assert(
  page.includes('className="event-perspective-mobile-guide"'),
  "event perspective mobile guide should be present",
);
assert(
  page.indexOf('className="event-perspective-mobile-guide"') < page.indexOf("<WorldRunway"),
  "event perspective mobile guide should appear before the explanatory runway",
);
for (const label of ["读事件", "看信息差", "查证据", "作者台"]) {
  assert(page.includes(label), `event perspective mobile guide should include ${label}`);
}
assert(
  css.includes(".event-perspective-mobile-guide") && css.includes("display: none"),
  "event perspective mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.event-perspective-mobile-guide[\s\S]*display: grid/.test(css),
  "event perspective mobile guide should be visible on mobile widths",
);

console.log("event perspective ux structure ok");
