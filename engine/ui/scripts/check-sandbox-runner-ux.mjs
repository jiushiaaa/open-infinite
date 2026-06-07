import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const pagePath = resolve("src/components/WorldSandboxPage.tsx");
const cssPath = resolve("src/components/worldSandbox.css");
const page = readFileSync(pagePath, "utf8");
const css = readFileSync(cssPath, "utf8");

const failures = [];

const requiredPageMarkers = [
  ['className="sandbox-panel sandbox-runner"', "runner panel should have a dedicated product shell"],
  ["sandbox-runner__steps", "runner should explain event, optional intervention, and launch steps"],
  ["sandbox-runner__advanced", "optional intervention controls should be grouped separately"],
  ["sandbox-event-preview", "runner should preview how the major event enters the world"],
  ["事件入局预演台", "event preview should name the event entry rehearsal"],
  ["谁会先动", "event preview should explain which actors may move first"],
  ["世界怎样记账", "event preview should explain how the world will record consequences"],
  ["干预怎样入局", "event preview should connect optional intervention to the event"],
  ["跑完先看哪里", "event preview should tell users where to inspect the result"],
  ["majorEvent.trim()", "event preview should derive from the current event draft"],
  ["hasInterventionDraft", "event preview should react to whether an intervention is present"],
  ["sandbox-intervention-preview", "runner should preview how an intervention will enter the world"],
  ["干预后果预演台", "intervention preview should name the consequence rehearsal"],
  ["投放对象", "intervention preview should explain who will receive the intervention"],
  ["投放方式", "intervention preview should explain the projection mode"],
  ["世界会怎样吸收", "intervention preview should explain how the world absorbs the input"],
  ["后果观察点", "intervention preview should show where users can inspect consequences"],
  ["角色主观记忆", "intervention preview should route consequences to character memory"],
  ["世界线代偿", "intervention preview should route consequences to worldline compensation"],
  ["openInterventionControls", "intervention preview should have a control focus helper"],
  ["clearInterventionDraft", "intervention preview should let users clear stale intervention drafts"],
  ["启动一轮推演", "primary action should describe the product outcome"],
  ["sandbox-result-bridge", "completed round should open with a result bridge"],
  ["本轮已发生", "result bridge should tell users the round already changed the world"],
  ["读成正文", "result bridge should route the user to readable output"],
  ["看世界线", "result bridge should route the user to worldline consequences"],
  ["生成多视角", "result bridge should route the user to multi-perspective reading"],
  ["再推一轮", "result bridge should let the user continue the sandbox loop"],
  ["sandbox-strategy-board", "strategy board should surface character tactics after a round"],
  ["谁在算计谁", "strategy board should explain the relationship between actors and targets"],
  ["私下目的", "strategy board should explain each actor's private goal"],
  ["可能误判", "strategy board should show the misread that can move the world"],
  ["世界影响", "strategy board should connect tactics to world consequences"],
  ["sandbox-strategy-continuation", "strategy board should hand tactics into the next round"],
  ["下一轮暗线承接", "strategy continuation should name the next-round handoff"],
  ["作为下一轮暗线", "strategy continuation should let users queue a tactic as the next event"],
  ["queueStrategySeed", "strategy continuation should have a dedicated queue helper"],
  ["queuedStrategyTitle", "strategy continuation should give feedback after queuing a tactic"],
  ["setInterventionContent(\"\")", "strategy continuation should clear stale intervention text"],
  ["setInterventionTarget(\"\")", "strategy continuation should clear stale intervention targets"],
  ["item.misread", "strategy continuation should carry forward the possible misread"],
  ["item.effect", "strategy continuation should carry forward the expected world effect"],
  ["queueNextPossibility", "next story possibilities should be reusable as the next sandbox event"],
  ["作为下一轮事件", "possibility cards should let users continue the world loop"],
  ["不沿用上轮临时干预", "possibility continuation should avoid replaying stale intervention text"],
  ["已放入运行台", "possibility continuation should give feedback after queuing an event"],
  ["sandbox-overnight-brief", "autopilot report should open with a literary overnight brief"],
  ["昨夜世界醒来台", "overnight brief should frame the autopilot result as a readable wake report"],
  ["昨夜发生", "overnight brief should summarize what happened"],
  ["带着记忆醒来", "overnight brief should surface remembered character changes"],
  ["世界为什么变了", "overnight brief should explain why the world state changed"],
  ["从这里继续读", "overnight brief should route users back into reading"],
  ["overnightReport", "overnight brief should use the existing overnight_report payload"],
  ["overnightMemory", "overnight brief should use remembered character data"],
  ["overnightContinuation", "overnight brief should use continuation hints"],
  ["autopilotReport.readable_entry", "overnight brief should connect to the readable entry"],
];

for (const [marker, message] of requiredPageMarkers) {
  if (!page.includes(marker)) {
    failures.push(message);
  }
}

const runnerIndex = page.indexOf('className="sandbox-panel sandbox-runner"');
const runwayIndex = page.indexOf("<WorldRunway");
if (runnerIndex === -1 || runwayIndex === -1 || runnerIndex > runwayIndex) {
  failures.push("runner should be before the explanatory runway so mobile users can start in the first screen");
}

const resultBridgeIndex = page.indexOf("sandbox-result-bridge");
const eventPreviewIndex = page.indexOf("sandbox-event-preview");
const eventFieldIndex = page.indexOf("sandbox-runner__field--event");
const advancedInterventionIndex = page.indexOf("sandbox-runner__advanced");
const strategyBoardIndex = page.indexOf("sandbox-strategy-board");
const actionChainIndex = page.indexOf("角色行动链");
const possibilitiesIndex = page.indexOf("后续剧情可能性");
const queuePossibilityIndex = page.indexOf("queueNextPossibility");
const strategyContinuationIndex = page.indexOf("sandbox-strategy-continuation");
const interventionIndex = page.indexOf('className="sandbox-section sandbox-intervention"');
const autopilotReportIndex = page.indexOf('className="sandbox-section sandbox-autopilot-report"');
const overnightBriefIndex = page.indexOf("sandbox-overnight-brief");
const wakeEntryIndex = page.indexOf("<WakeReadingEntry");
const autopilotTimelineIndex = page.indexOf("sandbox-timeline");
if (
  eventFieldIndex === -1 ||
  eventPreviewIndex === -1 ||
  advancedInterventionIndex === -1 ||
  eventPreviewIndex < eventFieldIndex ||
  eventPreviewIndex > advancedInterventionIndex
) {
  failures.push(
    "event preview should sit between the major event input and optional intervention controls",
  );
}
if (resultBridgeIndex === -1 || actionChainIndex === -1 || resultBridgeIndex > actionChainIndex) {
  failures.push("completed round result bridge should appear before detailed action chains");
}
if (
  resultBridgeIndex === -1 ||
  strategyBoardIndex === -1 ||
  actionChainIndex === -1 ||
  strategyBoardIndex < resultBridgeIndex ||
  strategyBoardIndex > actionChainIndex
) {
  failures.push("strategy board should bridge from result summary to detailed action chains");
}
if (
  strategyBoardIndex === -1 ||
  strategyContinuationIndex === -1 ||
  interventionIndex === -1 ||
  strategyContinuationIndex < strategyBoardIndex ||
  strategyContinuationIndex > interventionIndex
) {
  failures.push("strategy continuation should sit after the strategy board before dense evidence panels");
}
if (
  actionChainIndex === -1 ||
  possibilitiesIndex === -1 ||
  queuePossibilityIndex === -1 ||
  possibilitiesIndex < actionChainIndex ||
  queuePossibilityIndex > possibilitiesIndex
) {
  failures.push("possibility continuation helper should power the post-action next-round cards");
}
if (
  autopilotReportIndex === -1 ||
  overnightBriefIndex === -1 ||
  wakeEntryIndex === -1 ||
  autopilotTimelineIndex === -1 ||
  overnightBriefIndex < autopilotReportIndex ||
  overnightBriefIndex > wakeEntryIndex ||
  overnightBriefIndex > autopilotTimelineIndex
) {
  failures.push(
    "overnight brief should sit inside the autopilot report before readable entry and timelines",
  );
}

const requiredCssMarkers = [
  [".sandbox-runner__head", "runner header styling is missing"],
  [".sandbox-runner__steps", "runner step track styling is missing"],
  [".sandbox-runner__advanced summary", "optional intervention summary styling is missing"],
  [".sandbox-event-preview", "event preview styling is missing"],
  [".sandbox-event-preview__head", "event preview header styling is missing"],
  [".sandbox-event-preview__grid", "event preview grid styling is missing"],
  [".sandbox-event-preview__actions", "event preview action styling is missing"],
  [".sandbox-intervention-preview", "intervention preview styling is missing"],
  [".sandbox-intervention-preview__head", "intervention preview header styling is missing"],
  [".sandbox-intervention-preview__grid", "intervention preview grid styling is missing"],
  [".sandbox-intervention-preview__map", "intervention preview consequence map styling is missing"],
  [".sandbox-intervention-preview__actions", "intervention preview action styling is missing"],
  [".sandbox-runner__submit", "runner primary action styling is missing"],
  [".sandbox-hero__control", "hero runner placement styling is missing"],
  [".sandbox-hero .sandbox-runner__field--event textarea", "mobile-first runner textarea override is missing"],
  [".sandbox-result-bridge", "result bridge styling is missing"],
  [".sandbox-result-bridge__signals", "result bridge signal styling is missing"],
  [".sandbox-result-bridge__actions", "result bridge action styling is missing"],
  [".sandbox-result-bridge__actions .btn", "result bridge action buttons should have stable sizing"],
  [".sandbox-strategy-board", "strategy board styling is missing"],
  [".sandbox-strategy-board__grid", "strategy board grid styling is missing"],
  [".sandbox-strategy-card__route", "strategy card route styling is missing"],
  [".sandbox-strategy-card dl", "strategy card detail grid styling is missing"],
  [".sandbox-strategy-card__effect", "strategy card consequence styling is missing"],
  [".sandbox-strategy-continuation", "strategy continuation styling is missing"],
  [".sandbox-strategy-continuation__grid", "strategy continuation grid styling is missing"],
  [".sandbox-strategy-continuation__event", "strategy continuation event styling is missing"],
  [".sandbox-strategy-continuation__actions", "strategy continuation action styling is missing"],
  [".sandbox-possibility__actions", "possibility continuation action styling is missing"],
  [".sandbox-possibility__actions .btn", "possibility continuation buttons should have stable sizing"],
  [".sandbox-overnight-brief", "overnight brief styling is missing"],
  [".sandbox-overnight-brief__intro", "overnight brief intro styling is missing"],
  [".sandbox-overnight-brief__grid", "overnight brief card grid styling is missing"],
  [".sandbox-overnight-brief article", "overnight brief card styling is missing"],
  [".sandbox-overnight-brief__actions", "overnight brief action styling is missing"],
];

for (const [marker, message] of requiredCssMarkers) {
  if (!css.includes(marker)) {
    failures.push(message);
  }
}

const mobileMediaIndex = css.indexOf("@media (max-width: 680px)");
const mobileActionsIndex = css.indexOf(".sandbox-result-bridge__actions", mobileMediaIndex);
const mobileEventGridIndex = css.indexOf(".sandbox-event-preview__grid", mobileMediaIndex);
const mobileEventActionsIndex = css.indexOf(".sandbox-event-preview__actions", mobileMediaIndex);
const mobilePreviewGridIndex = css.indexOf(".sandbox-intervention-preview__grid", mobileMediaIndex);
const mobilePreviewActionsIndex = css.indexOf(
  ".sandbox-intervention-preview__actions",
  mobileMediaIndex,
);
if (mobileMediaIndex === -1 || mobileActionsIndex === -1) {
  failures.push("result bridge actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileEventGridIndex === -1) {
  failures.push("event preview grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileEventActionsIndex === -1) {
  failures.push("event preview actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobilePreviewGridIndex === -1) {
  failures.push("intervention preview grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobilePreviewActionsIndex === -1) {
  failures.push("intervention preview actions should collapse in the mobile media query");
}
const tabletMediaIndex = css.indexOf("@media (max-width: 960px)");
const tabletStrategyIndex = css.indexOf(".sandbox-strategy-board__grid", tabletMediaIndex);
const tabletStrategyContinuationIndex = css.indexOf(
  ".sandbox-strategy-continuation__grid",
  tabletMediaIndex,
);
const mobileStrategyDetailIndex = css.indexOf(".sandbox-strategy-card dl", mobileMediaIndex);
const mobileStrategyContinuationActionsIndex = css.indexOf(
  ".sandbox-strategy-continuation__actions",
  mobileMediaIndex,
);
const mobilePossibilityActionsIndex = css.indexOf(".sandbox-possibility__actions", mobileMediaIndex);
const mobileOvernightGridIndex = css.indexOf(".sandbox-overnight-brief__grid", mobileMediaIndex);
if (tabletMediaIndex === -1 || tabletStrategyIndex === -1) {
  failures.push("strategy board should collapse to one column on tablet widths");
}
if (tabletMediaIndex === -1 || tabletStrategyContinuationIndex === -1) {
  failures.push("strategy continuation should collapse on tablet widths");
}
if (mobileMediaIndex === -1 || mobileStrategyDetailIndex === -1) {
  failures.push("strategy card details should collapse on narrow mobile widths");
}
if (mobileMediaIndex === -1 || mobileStrategyContinuationActionsIndex === -1) {
  failures.push("strategy continuation actions should collapse on narrow mobile widths");
}
if (mobileMediaIndex === -1 || mobilePossibilityActionsIndex === -1) {
  failures.push("possibility continuation actions should collapse on narrow mobile widths");
}
if (mobileMediaIndex === -1 || mobileOvernightGridIndex === -1) {
  failures.push("overnight brief should collapse on narrow mobile widths");
}

if (failures.length > 0) {
  console.error("Sandbox runner UX check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("sandbox runner ux structure ok");
