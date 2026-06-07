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
assert(
  page.includes("adoption-confirmation-handoff"),
  "confirmed chapter result should include a handoff rail before detailed artifacts",
);
assert(
  page.includes("确认入卷接力台"),
  "confirmation handoff should name the handoff moment in product language",
);
assert(page.includes("已成正史"), "confirmation handoff should explain the chapter is canon");
assert(page.includes("反哺下一轮"), "confirmation handoff should explain the next sandbox feed");
assert(page.includes("Reviewer 定稿"), "confirmation handoff should summarize reviewer finalization");
assert(page.includes("回到世界"), "confirmation handoff should keep the world continuation action visible");
assert(
  page.includes("confirmation.continuation_effect.next_sandbox_entry.major_event"),
  "confirmation handoff should use the next sandbox entry event",
);
assert(
  page.includes("confirmation.reading_trail.status"),
  "confirmation handoff should show reading trail readiness",
);
assert(
  page.includes("confirmation.accepted_local_rewrites?.applied_rewrite_count"),
  "confirmation handoff should show accepted local rewrite count",
);
assert(
  page.includes('confirmation.edit_source === "auto_reviewer_final"'),
  "confirmation handoff should distinguish automatic reviewer final text",
);
assert(
  page.indexOf("确认入卷接力台") < page.indexOf("<dt>正文</dt>"),
  "confirmation handoff should appear before artifact detail fields",
);
assert(css.includes(".adoption-confirmation-handoff"), "confirmation handoff should have styles");
assert(
  /\.adoption-confirmation-handoff__grid[\s\S]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "confirmation handoff should use a four-column desktop grid",
);
assert(
  /@media \(max-width: 620px\)[\s\S]*\.adoption-confirmation-handoff__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "confirmation handoff should collapse to one column on narrow mobile",
);

console.log("author adoption ux structure ok");
