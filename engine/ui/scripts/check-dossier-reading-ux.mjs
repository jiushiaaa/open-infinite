import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/DossierReadingPage.tsx", "utf8");
const css = readFileSync("src/components/dossierReading.css", "utf8");

assert(
  page.includes('className="dossier-mobile-guide"'),
  "mobile reading guide should be present",
);
assert(
  page.indexOf('className="dossier-mobile-guide"') < page.indexOf("<WorldRunway"),
  "mobile reading guide should appear before the explanatory runway",
);
for (const label of ["开始读正文", "查卷宗", "作者台"]) {
  assert(page.includes(label), `mobile reading guide should include ${label}`);
}
assert(page.includes('className="dossier-carry"'), "reading carry section should be present");
assert(
  page.indexOf('className="dossier-carry"') < page.indexOf('className="dossier-evidence"'),
  "reading carry section should appear before the evidence appendix",
);
for (const label of ["回看误会图谱", "追踪跨事件余波", "继续一轮沙盘", "写成下一章材料"]) {
  assert(page.includes(label), `reading carry section should include ${label}`);
}
assert(
  css.includes(".dossier-mobile-guide") && css.includes("display: none"),
  "mobile reading guide should be hidden by default",
);
assert(
  /@media \(max-width: 960px\)[\s\S]*\.dossier-mobile-guide[\s\S]*display: grid/.test(css),
  "mobile reading guide should be visible on mobile/tablet widths",
);
assert(css.includes(".dossier-carry"), "reading carry section should have styles");
assert(
  /@media \(max-width: 640px\)[\s\S]*\.dossier-carry__actions[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "reading carry actions should collapse on narrow mobile",
);

console.log("dossier reading ux structure ok");
