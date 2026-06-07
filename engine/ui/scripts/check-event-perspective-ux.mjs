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
assert(
  page.includes('className="event-gap-handoff"'),
  "event perspective page should expose an information-gap handoff rail",
);
assert(
  page.indexOf("<WorldRunway") < page.indexOf('className="event-gap-handoff"') &&
    page.indexOf('className="event-gap-handoff"') < page.indexOf('className="event-perspective-layout"'),
  "event gap handoff should bridge the runway and detailed reading layout",
);
assert(
  page.includes("eventMisreadArcSignals"),
  "event perspective page should derive a concise misread arc",
);
assert(
  page.includes('className="event-misread-arc"') &&
    page.includes('aria-label="事件误读弧线"'),
  "event perspective page should include an event misread arc section",
);
assert(
  page.indexOf('className="event-gap-handoff"') <
    page.indexOf('className="event-misread-arc"') &&
    page.indexOf('className="event-misread-arc"') <
      page.indexOf('className="event-perspective-layout"'),
  "event misread arc should bridge the handoff and detailed reading layout",
);
for (const label of ["读事件", "看信息差", "查证据", "作者台"]) {
  assert(page.includes(label), `event perspective mobile guide should include ${label}`);
}
for (const label of ["事件信息差接力台", "事件现场", "信息差", "首要误读", "送入下一章", "把信息差送到作者台"]) {
  assert(page.includes(label), `event gap handoff should include ${label}`);
}
for (const field of ["primaryBias", "activeBeat", "gap", "report.evidence_panel", "report.next_actions"]) {
  assert(page.includes(field), `event gap handoff should use ${field}`);
}
for (const label of ["事件误读弧线", "谁看错了", "正史裂缝", "偏差怎样发酵", "下一步回收"]) {
  assert(page.includes(label), `event misread arc should include ${label}`);
}
for (const field of ["perspective_biases", "information_gap", "misbeliefs", "unknown_canon_facts", "next_actions"]) {
  assert(page.includes(field), `event misread arc should use ${field}`);
}
assert(
  css.includes(".event-perspective-mobile-guide") && css.includes("display: none"),
  "event perspective mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.event-perspective-mobile-guide[\s\S]*display: grid/.test(css),
  "event perspective mobile guide should be visible on mobile widths",
);
assert(
  css.includes(".event-gap-handoff") &&
    css.includes("grid-template-columns: minmax(220px, 0.82fr) repeat(3, minmax(0, 1fr))"),
  "event gap handoff should use a stable desktop grid",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.event-gap-handoff[\s\S]*grid-template-columns: 1fr/.test(css),
  "event gap handoff should collapse to one column on narrow widths",
);
assert(
  css.includes(".event-misread-arc") &&
    css.includes(".event-misread-arc__grid") &&
    css.includes(".event-misread-arc__step"),
  "event misread arc should have dedicated layout styles",
);
assert(
  css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "event misread arc should use a stable four-column desktop grid",
);
assert(
  /@media \(max-width: 820px\)[\s\S]*\.event-misread-arc__grid[\s\S]*grid-template-columns: 1fr/.test(css),
  "event misread arc should collapse to one column on narrow widths",
);

console.log("event perspective ux structure ok");
