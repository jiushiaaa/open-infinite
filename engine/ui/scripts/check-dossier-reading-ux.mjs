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
assert(
  css.includes(".dossier-mobile-guide") && css.includes("display: none"),
  "mobile reading guide should be hidden by default",
);
assert(
  /@media \(max-width: 960px\)[\s\S]*\.dossier-mobile-guide[\s\S]*display: grid/.test(css),
  "mobile reading guide should be visible on mobile/tablet widths",
);

console.log("dossier reading ux structure ok");
