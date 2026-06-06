import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/AuthorAdoptionPage.tsx", "utf8");
const css = readFileSync("src/components/authorAdoption.css", "utf8");

assert(
  page.includes("scrollToPageItem") && page.includes('".adoption-layout"'),
  "author adoption page should expose a scroll target for editing materials",
);
assert(
  page.includes("调整材料"),
  "author adoption command should include a material adjustment action",
);
assert(
  page.indexOf("调整材料") < page.indexOf("<WorldRunway"),
  "material adjustment action should appear before the explanatory runway",
);
assert(
  css.includes(".adoption-command__step p") && css.includes("display: none"),
  "mobile command cards should hide long step details",
);
assert(
  /@media \(max-width: 620px\)[\s\S]*\.adoption-command__actions[\s\S]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "mobile command actions should use a compact two-column grid",
);

console.log("author adoption ux structure ok");
