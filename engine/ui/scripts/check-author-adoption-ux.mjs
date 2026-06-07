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
assert(
  page.includes("adoption-review-gate"),
  "draft review should include a reviewer quality gate before the rewrite list",
);
assert(
  page.includes('aria-label="Reviewer 质检门"'),
  "reviewer quality gate should have a clear accessible label",
);
assert(page.includes("Reviewer 质检门"), "reviewer quality gate should be named in product language");
assert(page.includes("urgentReviewerItems"), "reviewer quality gate should count blocking and high-priority items");
assert(
  page.includes("draft.revision_pack.semantic_reviewer?.review_items"),
  "reviewer quality gate should use semantic reviewer review items",
);
assert(
  page.includes("draft.revision_pack.editorial_revision_draft?.status"),
  "reviewer quality gate should use editorial revision draft readiness",
);
assert(
  page.includes("selectedRewriteCount"),
  "reviewer quality gate should show selected rewrite count",
);
assert(
  page.includes("localizedRewriteCount"),
  "reviewer quality gate should show total localized rewrite count",
);
assert(page.includes("阻断风险"), "reviewer quality gate should explain blocking risk");
assert(page.includes("已选改写"), "reviewer quality gate should explain selected rewrites");
assert(page.includes("自动定稿"), "reviewer quality gate should explain automatic final text readiness");
assert(page.includes("入卷判断"), "reviewer quality gate should explain confirmation readiness");
assert(
  page.includes('scrollToPageItem(".adoption-editor")'),
  "reviewer quality gate should keep a direct action to the editable chapter text",
);
assert(
  page.indexOf("Reviewer 质检门") < page.indexOf('className="adoption-rewrite-toolbar"'),
  "reviewer quality gate should appear before the rewrite toolbar and rewrite cards",
);
assert(
  page.includes("adoption-final-compare"),
  "draft review should include a final text comparison rail before confirmation",
);
assert(
  page.includes('aria-label="定稿对照台"'),
  "final comparison rail should have a clear accessible label",
);
assert(page.includes("定稿对照台"), "final comparison rail should be named in product language");
assert(page.includes("originalDraftPreview"), "final comparison rail should show original draft preview");
assert(page.includes("currentFinalPreview"), "final comparison rail should show current final preview");
assert(
  page.includes("rewriteApplication?.edited_final_chapter?.quality_gate"),
  "final comparison rail should use edited final chapter quality gate when available",
);
assert(
  page.includes("setEditedChapterText(draft.chapter_text)"),
  "final comparison rail should allow restoring the original draft text",
);
assert(page.includes("恢复原草稿"), "final comparison rail should expose a rollback action");
assert(page.includes("当前定稿"), "final comparison rail should label the current final text");
assert(page.includes("原始草稿"), "final comparison rail should label the original draft");
assert(page.includes("入卷质量门"), "final comparison rail should explain the quality gate");
assert(
  page.indexOf("定稿对照台") < page.indexOf('className="adoption-confirm"'),
  "final comparison rail should appear before the confirmation action",
);
assert(
  page.includes("chapterPolishSignals"),
  "draft review should derive chapter-level polish signals",
);
assert(
  page.includes("adoption-polish-radar"),
  "draft review should include a chapter polish radar before final comparison",
);
assert(
  page.includes('aria-label="章节质感雷达"'),
  "chapter polish radar should have a clear accessible label",
);
assert(page.includes("章节质感雷达"), "chapter polish radar should be named in product language");
assert(page.includes("读感节奏"), "chapter polish radar should explain reading rhythm");
assert(page.includes("角色动机"), "chapter polish radar should explain character motivation");
assert(page.includes("世界入文"), "chapter polish radar should explain world-state grounding");
assert(page.includes("入卷准备"), "chapter polish radar should explain confirmation readiness");
assert(
  page.includes("draft.reviewer_checklist"),
  "chapter polish radar should use the draft reviewer checklist",
);
assert(
  page.includes("semanticReviewItems.filter"),
  "chapter polish radar should summarize semantic reviewer dimensions",
);
assert(
  page.includes("finalTextSource"),
  "chapter polish radar should reflect the current final draft source",
);
assert(
  page.includes('scrollToPageItem(".adoption-review-gate")'),
  "chapter polish radar should link back to reviewer details",
);
assert(
  page.indexOf("章节质感雷达") < page.indexOf("定稿对照台"),
  "chapter polish radar should appear before the final comparison rail",
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
assert(css.includes(".adoption-review-gate"), "reviewer quality gate should have styles");
assert(
  /\.adoption-review-gate__grid[\s\S]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "reviewer quality gate should use a four-column desktop grid",
);
assert(
  /@media \(max-width: 620px\)[\s\S]*\.adoption-review-gate__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "reviewer quality gate should collapse to one column on narrow mobile",
);
assert(css.includes(".adoption-final-compare"), "final comparison rail should have styles");
assert(
  /\.adoption-final-compare__grid[\s\S]*grid-template-columns: minmax\(0, 1fr\) minmax\(0, 1fr\)/.test(
    css,
  ),
  "final comparison rail should compare original and current text in two desktop columns",
);
assert(
  /@media \(max-width: 620px\)[\s\S]*\.adoption-final-compare__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "final comparison rail should collapse to one column on narrow mobile",
);
assert(css.includes(".adoption-polish-radar"), "chapter polish radar should have styles");
assert(
  /\.adoption-polish-radar__grid[\s\S]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "chapter polish radar should use a four-column desktop grid",
);
assert(
  /@media \(max-width: 620px\)[\s\S]*\.adoption-polish-radar__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "chapter polish radar should collapse to one column on narrow mobile",
);

console.log("author adoption ux structure ok");
