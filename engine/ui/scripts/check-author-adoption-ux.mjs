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
assert(page.includes("workspaceMode"), "author adoption page should track a workspace mode");
assert(page.includes("adoption-desk-switch"), "author adoption page should expose a desk mode switch");
assert(page.includes("写作台"), "desk mode switch should include a writing desk option");
assert(page.includes("审稿台"), "desk mode switch should include a review desk option");
assert(
  page.includes('className={`adoption-layout adoption-layout--${workspaceMode}`}'),
  "workspace mode should affect the adoption layout",
);
assert(
  page.includes("setWorkspaceMode(\"review\")"),
  "review desk should be opened after adoption, draft, rewrite, or confirmation progress",
);
assert(
  page.indexOf("调整材料") < page.indexOf("<WorldRunway"),
  "material adjustment action should appear before the explanatory runway",
);
assert(css.includes(".adoption-desk-switch"), "desk mode switch should have styles");
assert(css.includes(".adoption-layout--review"), "review desk should have layout styles");
assert(
  /\.adoption-layout--review \.adoption-panel,[\s\S]*\.adoption-layout--review \.adoption-note[\s\S]*display: none/.test(
    css,
  ),
  "review desk should hide writing material panels without removing them",
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
