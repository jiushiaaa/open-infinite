import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const pagePath = resolve("src/components/WorldSandboxPage.tsx");
const cssPath = resolve("src/components/worldSandbox.css");
const page = readFileSync(pagePath, "utf8");
const css = readFileSync(cssPath, "utf8");

const failures = [];

const requiredPageMarkers = [
  ['className="sandbox-panel sandbox-runner"', "runner panel should have a dedicated product shell"],
  ['id="sandbox-runner"', "runner panel should expose a stable product anchor for the shell primary action"],
  ["sandbox-runner__steps", "runner should explain event, optional intervention, and launch steps"],
  ["sandbox-runner__advanced", "optional intervention controls should be grouped separately"],
  ["sandbox-event-seeds", "runner should provide world-pressure event seeds before the blank draft"],
  ["事件种子台", "event seed deck should name the pre-run seed surface"],
  ["不知道写什么", "event seed deck should reduce blank-page friction"],
  ["放入事件", "event seed cards should let users place a seed into the runner"],
  ["eventSeedDeck", "event seeds should be derived in one readable model"],
  ["queuedEventSeedTitle", "event seeds should give feedback after queuing"],
  ["chooseEventSeed", "event seeds should have a dedicated queue helper"],
  ["setMajorEvent(seed.event)", "event seeds should update the major event draft"],
  ["firstPossibility", "event seeds should reuse post-round possibilities when available"],
  ["latestConsequence", "event seeds should read worldline consequence pressure when available"],
  ["strategyInteractions[0]", "event seeds should reuse the leading strategy pressure when available"],
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
  ["sandbox-preflight-map", "empty sandbox should expose a pre-run product map"],
  ["开跑前路标", "pre-run product map should name the next-start guide"],
  ["去写事件", "pre-run product map should let users jump to the event draft"],
  ["添加干预", "pre-run product map should let users open optional intervention"],
  ["跑完先看本轮已发生", "pre-run product map should explain the first result destination"],
  ["从这里启动推演", "pre-run product map should let users start the round in place"],
  ["sandbox-result-bridge", "completed round should open with a result bridge"],
  ["本轮已发生", "result bridge should tell users the round already changed the world"],
  ["读成正文", "result bridge should route the user to readable output"],
  ["看世界线", "result bridge should route the user to worldline consequences"],
  ["生成多视角", "result bridge should route the user to multi-perspective reading"],
  ["再推一轮", "result bridge should let the user continue the sandbox loop"],
  ["sandbox-result-reading-guide", "completed round should provide a result reading order"],
  ["结果阅读顺序", "result reading guide should name the post-run reading order"],
  ["先读总览", "result reading guide should start with the summary"],
  ["再看暗线", "result reading guide should direct users to strategy when present"],
  ["然后追角色行动", "result reading guide should direct users to the action chain"],
  ["最后选择出口", "result reading guide should end with reading and continuation exits"],
  ["focusStrategyBoard", "result reading guide should scroll to the strategy board"],
  ["focusActionChain", "result reading guide should scroll to the action chain"],
  ["sandbox-action-focus", "completed round should provide a scannable character action focus before dense action chains"],
  ["角色行动焦点", "action focus should name the post-round character focus surface"],
  ["最值得追的角色", "action focus should tell users which characters to inspect first"],
  ["行动背后的真实意图", "action focus should expose intent before detailed evidence"],
  ["风险与结果", "action focus should surface consequence and risk"],
  ["回填为下一轮事件", "action focus should let users continue a character action into the next round"],
  ["actionFocusDeck", "action focus should derive a readable deck from character actions"],
  ["queueActionFocusSeed", "action focus should have a dedicated next-round queue helper"],
  ["queuedActionFocusTitle", "action focus should give feedback after queuing a character action"],
  ["setMajorEvent(card.event)", "action focus should update the major event draft"],
  ["定位行动链", "action focus should let users jump to detailed action evidence"],
  ["追角色卷", "action focus should route users to the character volume"],
  ["sandbox-action-trail", "completed round should expose a cross-round character trail before dense action chains"],
  ["角色跨轮追踪", "action trail should name the cross-round character reading surface"],
  ["上一轮记忆", "action trail should start from the character's previous memory"],
  ["本轮行动", "action trail should show the current round action"],
  ["结果压力", "action trail should explain how the action pressures the world"],
  ["下一轮推力", "action trail should hand the character arc into the next round"],
  ["actionTrailDeck", "action trail should derive a readable deck from character actions"],
  ["queueActionTrailSeed", "action trail should have a dedicated next-round queue helper"],
  ["追这条弧线", "action trail should let users jump to detailed action evidence"],
  ["带入下一轮", "action trail should let users reuse the character arc as the next event"],
  ["读角色卷", "action trail should route users to the character volume"],
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
const runnerStepsIndex = page.indexOf("sandbox-runner__steps");
const eventSeedsIndex = page.indexOf("sandbox-event-seeds");
const eventPreviewIndex = page.indexOf("sandbox-event-preview");
const eventFieldIndex = page.indexOf("sandbox-runner__field--event");
const advancedInterventionIndex = page.indexOf("sandbox-runner__advanced");
const strategyBoardIndex = page.indexOf("sandbox-strategy-board");
const resultReadingGuideIndex = page.indexOf("sandbox-result-reading-guide");
const actionFocusIndex = page.indexOf("sandbox-action-focus");
const actionTrailIndex = page.indexOf("sandbox-action-trail");
const actionChainIndex = page.indexOf("<h2>角色行动链</h2>");
const possibilitiesIndex = page.indexOf("后续剧情可能性");
const queuePossibilityIndex = page.indexOf("queueNextPossibility");
const strategyContinuationIndex = page.indexOf("sandbox-strategy-continuation");
const interventionIndex = page.indexOf('className="sandbox-section sandbox-intervention"');
const autopilotReportIndex = page.indexOf('className="sandbox-section sandbox-autopilot-report"');
const overnightBriefIndex = page.indexOf("sandbox-overnight-brief");
const wakeEntryIndex = page.indexOf("<WakeReadingEntry");
const autopilotTimelineIndex = page.indexOf("sandbox-timeline");
if (
  runnerStepsIndex === -1 ||
  eventSeedsIndex === -1 ||
  eventFieldIndex === -1 ||
  eventSeedsIndex < runnerStepsIndex ||
  eventSeedsIndex > eventFieldIndex
) {
  failures.push("event seed deck should sit after runner steps and before the event textarea");
}
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
  resultReadingGuideIndex === -1 ||
  actionChainIndex === -1 ||
  resultReadingGuideIndex < resultBridgeIndex ||
  resultReadingGuideIndex > actionChainIndex
) {
  failures.push("result reading guide should bridge from result summary to detailed evidence");
}
if (
  resultReadingGuideIndex === -1 ||
  actionFocusIndex === -1 ||
  actionChainIndex === -1 ||
  actionFocusIndex < resultReadingGuideIndex ||
  actionFocusIndex > actionChainIndex
) {
  failures.push("action focus should bridge from reading order to detailed character action chains");
}
if (
  actionFocusIndex === -1 ||
  actionTrailIndex === -1 ||
  actionChainIndex === -1 ||
  actionTrailIndex < actionFocusIndex ||
  actionTrailIndex > actionChainIndex
) {
  failures.push("action trail should sit after action focus and before detailed character action chains");
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
  [".sandbox-event-seeds", "event seed deck styling is missing"],
  [".sandbox-event-seeds__head", "event seed header styling is missing"],
  [".sandbox-event-seeds__grid", "event seed grid styling is missing"],
  [".sandbox-event-seeds__actions", "event seed action styling is missing"],
  [".sandbox-event-seeds__feedback", "event seed queued feedback styling is missing"],
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
  [".sandbox-preflight-map", "pre-run product map styling is missing"],
  [".sandbox-preflight-map__intro", "pre-run product map intro styling is missing"],
  [".sandbox-preflight-map__grid", "pre-run product map grid styling is missing"],
  [".sandbox-preflight-map__actions", "pre-run product map action styling is missing"],
  [".sandbox-hero__control", "hero runner placement styling is missing"],
  [".sandbox-hero .sandbox-runner__field--event textarea", "mobile-first runner textarea override is missing"],
  [".sandbox-result-bridge", "result bridge styling is missing"],
  [".sandbox-result-bridge__signals", "result bridge signal styling is missing"],
  [".sandbox-result-bridge__actions", "result bridge action styling is missing"],
  [".sandbox-result-bridge__actions .btn", "result bridge action buttons should have stable sizing"],
  [".sandbox-result-reading-guide", "result reading guide styling is missing"],
  [".sandbox-result-reading-guide__grid", "result reading guide grid styling is missing"],
  [".sandbox-result-reading-guide__actions", "result reading guide action styling is missing"],
  [".sandbox-action-focus", "action focus styling is missing"],
  [".sandbox-action-focus__grid", "action focus grid styling is missing"],
  [".sandbox-action-focus-card", "action focus card styling is missing"],
  [".sandbox-action-focus-card__meta", "action focus metadata styling is missing"],
  [".sandbox-action-focus-card__signals", "action focus signal styling is missing"],
  [".sandbox-action-focus-card__actions", "action focus action styling is missing"],
  [".sandbox-action-trail", "action trail styling is missing"],
  [".sandbox-action-trail__grid", "action trail grid styling is missing"],
  [".sandbox-action-trail-card", "action trail card styling is missing"],
  [".sandbox-action-trail-card__steps", "action trail step styling is missing"],
  [".sandbox-action-trail-card__actions", "action trail action styling is missing"],
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
const mobileReadingGuideGridIndex = css.indexOf(
  ".sandbox-result-reading-guide__grid",
  mobileMediaIndex,
);
const mobileReadingGuideActionsIndex = css.indexOf(
  ".sandbox-result-reading-guide__actions",
  mobileMediaIndex,
);
const mobileActionFocusGridIndex = css.indexOf(".sandbox-action-focus__grid", mobileMediaIndex);
const mobileActionFocusActionsIndex = css.indexOf(
  ".sandbox-action-focus-card__actions",
  mobileMediaIndex,
);
const mobileActionTrailGridIndex = css.indexOf(".sandbox-action-trail__grid", mobileMediaIndex);
const mobileActionTrailActionsIndex = css.indexOf(
  ".sandbox-action-trail-card__actions",
  mobileMediaIndex,
);
const mobilePreflightGridIndex = css.indexOf(".sandbox-preflight-map__grid", mobileMediaIndex);
const mobilePreflightActionsIndex = css.indexOf(
  ".sandbox-preflight-map__actions",
  mobileMediaIndex,
);
const mobileSeedGridIndex = css.indexOf(".sandbox-event-seeds__grid", mobileMediaIndex);
const mobileSeedActionsIndex = css.indexOf(".sandbox-event-seeds__actions", mobileMediaIndex);
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
if (mobileMediaIndex === -1 || mobileReadingGuideGridIndex === -1) {
  failures.push("result reading guide grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileReadingGuideActionsIndex === -1) {
  failures.push("result reading guide actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileActionFocusGridIndex === -1) {
  failures.push("action focus grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileActionFocusActionsIndex === -1) {
  failures.push("action focus actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileActionTrailGridIndex === -1) {
  failures.push("action trail grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileActionTrailActionsIndex === -1) {
  failures.push("action trail actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobilePreflightGridIndex === -1) {
  failures.push("pre-run product map grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobilePreflightActionsIndex === -1) {
  failures.push("pre-run product map actions should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileSeedGridIndex === -1) {
  failures.push("event seed grid should collapse in the mobile media query");
}
if (mobileMediaIndex === -1 || mobileSeedActionsIndex === -1) {
  failures.push("event seed actions should collapse in the mobile media query");
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
