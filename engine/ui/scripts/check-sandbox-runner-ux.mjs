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
const strategyBoardIndex = page.indexOf("sandbox-strategy-board");
const actionChainIndex = page.indexOf("角色行动链");
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

const requiredCssMarkers = [
  [".sandbox-runner__head", "runner header styling is missing"],
  [".sandbox-runner__steps", "runner step track styling is missing"],
  [".sandbox-runner__advanced summary", "optional intervention summary styling is missing"],
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
];

for (const [marker, message] of requiredCssMarkers) {
  if (!css.includes(marker)) {
    failures.push(message);
  }
}

const mobileMediaIndex = css.indexOf("@media (max-width: 680px)");
const mobileActionsIndex = css.indexOf(".sandbox-result-bridge__actions", mobileMediaIndex);
if (mobileMediaIndex === -1 || mobileActionsIndex === -1) {
  failures.push("result bridge actions should collapse in the mobile media query");
}
const tabletMediaIndex = css.indexOf("@media (max-width: 960px)");
const tabletStrategyIndex = css.indexOf(".sandbox-strategy-board__grid", tabletMediaIndex);
const mobileStrategyDetailIndex = css.indexOf(".sandbox-strategy-card dl", mobileMediaIndex);
if (tabletMediaIndex === -1 || tabletStrategyIndex === -1) {
  failures.push("strategy board should collapse to one column on tablet widths");
}
if (mobileMediaIndex === -1 || mobileStrategyDetailIndex === -1) {
  failures.push("strategy card details should collapse on narrow mobile widths");
}

if (failures.length > 0) {
  console.error("Sandbox runner UX check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("sandbox runner ux structure ok");
