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
assert(page.includes("readingMode"), "dossier reading should track a reading mode");
assert(page.includes("dossier-reading-mode"), "dossier reading should expose a mode switch");
assert(page.includes("读小说"), "mode switch should include a novel reading option");
assert(page.includes("dossier-layout--"), "reading mode should affect the page layout");
assert(
  page.includes("setReadingMode(\"dossier\")"),
  "dossier mode should be reachable before opening archive controls",
);
assert(page.includes('className="dossier-carry"'), "reading carry section should be present");
assert(
  page.indexOf('className="dossier-carry"') < page.indexOf('className="dossier-evidence"'),
  "reading carry section should appear before the evidence appendix",
);
assert(
  page.includes('className="dossier-next-chapter-bridge"'),
  "continuous reading should include a next-chapter bridge after the prose",
);
assert(
  page.indexOf('className="dossier-section-stack"') <
    page.indexOf('className="dossier-next-chapter-bridge"') &&
    page.indexOf('className="dossier-next-chapter-bridge"') <
      page.indexOf('className="dossier-carry"'),
  "next-chapter bridge should sit after the prose and before the carry actions",
);
for (const label of [
  "下一章接力台",
  "本章留下什么",
  "下一章要追什么",
  "误会怎样发酵",
  "从这里续写",
]) {
  assert(page.includes(label), `next-chapter bridge should include ${label}`);
}
assert(
  page.includes("nextChapterBridgeItems") &&
    page.includes("continuity_threads") &&
    page.includes("reading_flow") &&
    page.includes("misbeliefNodes.length"),
  "next-chapter bridge should derive from reading flow, continuity and misbelief state",
);
assert(
  page.includes("navigate({ name: \"author\", slug })") &&
    page.includes("navigate({ name: \"sandbox\", slug })") &&
    page.includes("navigate({ name: \"longlineReading\", slug, worldlineId })"),
  "next-chapter bridge should route users to author, sandbox and longline continuations",
);
assert(
  page.includes("inline_evidence_anchors") &&
    page.includes("inlineEvidenceAnchorsForSection") &&
    page.includes("openInlineEvidenceAnchor"),
  "continuous reading should consume inline evidence anchors from the dossier packet",
);
assert(
  page.includes('className="dossier-inline-anchors"') &&
    page.includes('className="dossier-inline-anchor"'),
  "continuous prose should render clickable inline evidence anchors inside each section",
);
for (const label of ["角色记忆", "世界状态", "因果债", "事件视角", "作者证据"]) {
  assert(page.includes(label), `inline evidence anchors should include ${label}`);
}
assert(
  page.includes("setActiveTab(anchor.target.tab)") &&
    page.includes("navigate({ name: \"worldline\", slug, worldlineId })") &&
    page.includes('name: "eventPerspective"') &&
    page.includes("eventId: anchor.target.event_id || \"main\"") &&
    page.includes("navigate({ name: \"author\", slug })"),
  "inline evidence anchors should jump to tabs, worldline, event perspective, or author evidence",
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
assert(css.includes(".dossier-reading-mode"), "reading mode switch should have styles");
assert(css.includes(".dossier-layout--novel"), "novel reading mode should have layout styles");
assert(
  /\.dossier-layout--novel \.dossier-sidebar[\s\S]*display: none/.test(css),
  "novel reading mode should hide the dossier sidebar without removing it",
);
assert(
  page.includes('className="dossier-chapter-rail"'),
  "novel reading mode should keep a chapter scene rail inside the reader",
);
assert(page.includes("本卷场景"), "chapter scene rail should name the whole-volume scene map");
assert(
  page.includes("continuousSections.map((section, index)") &&
    page.includes("scrollToSection(section.id)"),
  "chapter scene rail should let readers jump between scenes without opening the dossier sidebar",
);
assert(
  page.indexOf('className="dossier-chapter-rail"') <
    page.indexOf('className="dossier-focus"'),
  "chapter scene rail should appear before the sticky current-scene guide",
);
assert(
  page.includes("currentReadingSection") && page.includes("nextReadingSection"),
  "continuous reading should derive current and next scene handoff state",
);
assert(
  page.includes('className="dossier-continuity-rail"'),
  "continuous reading should expose a continuity rail before the prose",
);
assert(
  page.indexOf('className="dossier-focus"') <
    page.indexOf('className="dossier-continuity-rail"') &&
    page.indexOf('className="dossier-continuity-rail"') <
      page.indexOf('className="dossier-section-stack"'),
  "continuity rail should sit between the sticky guide and the prose body",
);
for (const label of ["续读签", "正在读", "下一场", "本场误会", "承接线"]) {
  assert(page.includes(label), `continuity rail should include ${label}`);
}
assert(
  page.includes('className="dossier-reading-compass"'),
  "continuous reading should expose a pre-reading compass",
);
assert(
  page.indexOf('className="dossier-continuity-rail"') <
    page.indexOf('className="dossier-reading-compass"') &&
    page.indexOf('className="dossier-reading-compass"') <
      page.indexOf('className="dossier-section-stack"'),
  "pre-reading compass should sit between continuity context and the prose body",
);
for (const label of ["本章读感罗盘", "开场钩子", "转折压力", "误会燃料", "下一章悬念"]) {
  assert(page.includes(label), `pre-reading compass should include ${label}`);
}
assert(
  page.includes("readingCompassItems") &&
    page.includes("reading_flow") &&
    page.includes("currentReadingMisbelief"),
  "pre-reading compass should use real reading flow and misbelief state",
);
assert(
  page.includes("scrollToPageItem(\".dossier-flow\")") &&
    page.includes("scrollToSection(currentReadingSection.id)"),
  "pre-reading compass should let readers jump into prose or inspect rhythm details",
);
assert(
  page.includes("continuity_threads") && page.includes("chapter_cliffhanger"),
  "continuity rail should use real continuity and cliffhanger fields",
);
assert(
  page.includes("scrollToSection(nextReadingSection.id)") &&
    page.includes("scrollToPageItem(\".dossier-misbelief-map\")"),
  "continuity rail should let readers continue or inspect misbeliefs",
);
assert(css.includes(".dossier-chapter-rail"), "chapter scene rail should have styles");
assert(css.includes(".dossier-continuity-rail"), "continuity rail should have styles");
assert(css.includes(".dossier-reading-compass"), "pre-reading compass should have styles");
assert(css.includes(".dossier-next-chapter-bridge"), "next-chapter bridge should have styles");
assert(css.includes(".dossier-inline-anchors"), "inline evidence anchors should have styles");
assert(css.includes(".dossier-inline-anchor"), "inline evidence anchor buttons should have styles");
assert(
  css.includes(".dossier-next-chapter-bridge__grid") &&
    css.includes("grid-template-columns: repeat(4, minmax(0, 1fr))"),
  "next-chapter bridge should use a stable four-card desktop grid",
);
assert(
  css.includes(".dossier-next-chapter-bridge__actions"),
  "next-chapter bridge should style continuation actions",
);
assert(
  /@media \(max-width: 960px\)[\s\S]*\.dossier-continuity-rail__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "continuity rail should collapse cleanly on tablet widths",
);
assert(
  /@media \(max-width: 960px\)[\s\S]*\.dossier-reading-compass__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "pre-reading compass should collapse cleanly on tablet widths",
);
assert(
  /@media \(max-width: 640px\)[\s\S]*\.dossier-chapter-rail__list[\s\S]*overflow-x: auto/.test(
    css,
  ),
  "chapter scene rail should scroll horizontally on narrow mobile",
);
assert(
  /@media \(max-width: 640px\)[\s\S]*\.dossier-next-chapter-bridge__grid[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "next-chapter bridge should collapse on narrow mobile",
);
assert(
  /@media \(max-width: 640px\)[\s\S]*\.dossier-next-chapter-bridge__actions[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "next-chapter bridge actions should collapse on narrow mobile",
);
assert(css.includes(".dossier-carry"), "reading carry section should have styles");
assert(
  /@media \(max-width: 640px\)[\s\S]*\.dossier-carry__actions[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "reading carry actions should collapse on narrow mobile",
);

console.log("dossier reading ux structure ok");
