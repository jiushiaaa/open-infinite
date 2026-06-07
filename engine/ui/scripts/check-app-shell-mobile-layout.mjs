import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const cssPath = resolve("src/components/appShell.css");
const css = readFileSync(cssPath, "utf8");

const failures = [];

function findRule(selector, fromIndex = 0) {
  const selectorIndex = css.indexOf(selector, fromIndex);
  if (selectorIndex === -1) {
    return "";
  }

  const openIndex = css.indexOf("{", selectorIndex);
  if (openIndex === -1) {
    return "";
  }

  let depth = 0;
  for (let index = openIndex; index < css.length; index += 1) {
    const char = css[index];
    if (char === "{") {
      depth += 1;
    } else if (char === "}") {
      depth -= 1;
      if (depth === 0) {
        return css.slice(openIndex + 1, index);
      }
    }
  }

  return "";
}

const mobileIndex = css.indexOf("@media (max-width: 640px)");
if (mobileIndex === -1) {
  failures.push("missing @media (max-width: 640px) mobile shell rules");
}

const mobileWorldNavRule = findRule(".world-nav", mobileIndex);
if (!/grid-template-columns:\s*repeat\(5,\s*minmax\(0,\s*1fr\)\)/.test(mobileWorldNavRule)) {
  failures.push("mobile world nav should keep 9 entries within two dense rows at 390px");
}

const mobileStageRule = findRule(".shell-context__stages", mobileIndex);
if (!/grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/.test(mobileStageRule)) {
  failures.push("mobile stage switcher should stay in one row for the four world scenes");
}

const appShellPath = resolve("src/components/AppShell.tsx");
const appShell = readFileSync(appShellPath, "utf8");
const workspaceShellPath = resolve("src/components/WorldWorkspaceShell.tsx");
const workspaceShell = existsSync(workspaceShellPath)
  ? readFileSync(workspaceShellPath, "utf8")
  : "";
const contextPath = resolve("src/worldRouteContext.ts");
const context = readFileSync(contextPath, "utf8");

if (!appShell.includes("WorldWorkspaceShell")) {
  failures.push("AppShell should delegate world context to a shared WorldWorkspaceShell component");
}

if (!workspaceShell) {
  failures.push("WorldWorkspaceShell component should exist as the shared world workspace shell");
}

if (!workspaceShell.includes("世界工作区壳") || !workspaceShell.includes("世界旅程总线")) {
  failures.push("WorldWorkspaceShell should name the shared shell and expose a clear journey bus");
}

if (!workspaceShell.includes("routeContext.stages.map") || !workspaceShell.includes("routeContext.dossiers.map")) {
  failures.push("WorldWorkspaceShell should keep stage and dossier navigation in the shared shell");
}

if (!workspaceShell.includes("shell-context__handoffs")) {
  failures.push("WorldWorkspaceShell should render the shared state handoff preview row");
}

if (
  !workspaceShell.includes("routeContext.stateHandoffs.map") ||
  !workspaceShell.includes("navigate(handoff.route)")
) {
  failures.push("state handoff previews should be clickable and use semantic routes");
}

if (
  !context.includes("正在承接") ||
  !context.includes("会留下") ||
  !context.includes("下一处看见")
) {
  failures.push("state handoff previews should explain source, consequence and next receipt in Chinese");
}

if (!workspaceShell.includes("shell-context__workspace")) {
  failures.push("AppShell should render the world workspace summary inside the shared context bar");
}

if (!workspaceShell.includes("shell-context__workspace-card")) {
  failures.push("world workspace summary cards should be clickable journey pointers");
}

if (!workspaceShell.includes("shell-context__continuity")) {
  failures.push("AppShell should render the world pulse continuity row");
}

if (!workspaceShell.includes("shell-context__taskbar")) {
  failures.push("AppShell should render a dedicated current-task handoff row");
}

if (!workspaceShell.includes("当前任务") || !workspaceShell.includes("建议先做")) {
  failures.push("current-task row should use clear Chinese next-step copy");
}

if (
  !workspaceShell.includes("routeContext.workspaceSummary.why") ||
  !workspaceShell.includes("routeContext.primaryActionLabel")
) {
  failures.push("current-task row should pair the primary action with its rationale");
}

if (
  !workspaceShell.includes("routeContext.continuitySignals.map") ||
  !workspaceShell.includes("navigate(signal.route)")
) {
  failures.push("world pulse signals should be clickable and use semantic routes");
}

if (
  !workspaceShell.includes("当前环节") ||
  !workspaceShell.includes("承接世界线") ||
  !workspaceShell.includes("下一步为什么做")
) {
  failures.push("world workspace summary should explain stage, worldline and next-step rationale");
}

if (!workspaceShell.includes("navigate(routeContext.primaryRoute)")) {
  failures.push("next-step summary card should execute the primary route");
}

if (!workspaceShell.includes("worldlineDossierRoute")) {
  failures.push("worldline summary card should link to the worldline dossier");
}

if (!context.includes("workspaceSummary")) {
  failures.push("world route context should provide semantic summary data for AppShell");
}

if (!context.includes("continuitySignals")) {
  failures.push("world route context should provide continuity signals for AppShell");
}

if (
  !context.includes('"memory" | "consequence" | "reading" | "writing"') ||
  !context.includes("buildContinuitySignals")
) {
  failures.push("continuity signals should cover memory, consequence, reading and writing");
}

const workspaceRule = findRule(".shell-context__workspace");
if (!/grid-template-columns:\s*0\.75fr\s+0\.75fr\s+minmax\(0,\s*1\.5fr\)/.test(workspaceRule)) {
  failures.push("desktop workspace summary should keep stage, worldline and next-step rationale in one compact row");
}

const shellContextRule = findRule(".shell-context");
if (!/grid-template-areas:[^}]*taskbar/s.test(shellContextRule)) {
  failures.push("AppShell context grid should give the current-task row its own area");
}

const taskbarRule = findRule(".shell-context__taskbar");
if (
  !/display:\s*grid/.test(taskbarRule) ||
  !/grid-template-columns:\s*minmax\(0,\s*1fr\)\s+auto/.test(taskbarRule)
) {
  failures.push("desktop current-task row should keep explanation and actions in one scan row");
}

const handoffsRule = findRule(".shell-context__handoffs");
if (
  !/display:\s*grid/.test(handoffsRule) ||
  !/grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)/.test(handoffsRule)
) {
  failures.push("desktop state handoffs should present source, consequence and next receipt in one row");
}

const handoffRule = findRule(".shell-context__handoff-card");
if (!/display:\s*grid/.test(handoffRule) || !/text-align:\s*left/.test(handoffRule)) {
  failures.push("state handoff cards should keep the compact information-sign layout");
}

const journeyBusRule = findRule(".world-workspace-shell__journey");
if (
  !/display:\s*grid/.test(journeyBusRule) ||
  !/grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/.test(journeyBusRule)
) {
  failures.push("desktop journey bus should present the four world scenes as one stable scan row");
}

const journeyItemRule = findRule(".world-workspace-shell__journey-item");
if (
  !/display:\s*grid/.test(journeyItemRule) ||
  !/text-align:\s*left/.test(journeyItemRule)
) {
  failures.push("journey bus items should keep the compact information-sign layout");
}

const workspaceCardRule = findRule(".shell-context__workspace-card");
if (
  !/display:\s*grid/.test(workspaceCardRule) ||
  !/text-align:\s*left/.test(workspaceCardRule)
) {
  failures.push("workspace summary cards should keep the compact information-sign layout");
}

const mobileWorkspaceRule = findRule(".shell-context__workspace", mobileIndex);
if (!/grid-template-columns:\s*1fr/.test(mobileWorkspaceRule)) {
  failures.push("mobile workspace summary should stack into one column instead of squeezing text");
}

const mobileWorkspaceCardRule = findRule(".shell-context__workspace-card", mobileIndex);
if (!/min-height:\s*0/.test(mobileWorkspaceCardRule)) {
  failures.push("mobile workspace summary cards should not force tall rows");
}

const mobileTaskbarRule = findRule(".shell-context__taskbar", mobileIndex);
if (!/grid-template-columns:\s*1fr/.test(mobileTaskbarRule)) {
  failures.push("mobile current-task row should stack explanation above actions");
}

const mobileHandoffsRule = findRule(".shell-context__handoffs", mobileIndex);
if (!/grid-template-columns:\s*1fr/.test(mobileHandoffsRule)) {
  failures.push("mobile state handoffs should stack into one readable column");
}

const mobileJourneyRule = findRule(".world-workspace-shell__journey", mobileIndex);
if (!/grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/.test(mobileJourneyRule)) {
  failures.push("mobile journey bus should collapse into two readable columns");
}

const mobileActionsRule = findRule(".shell-context__actions", mobileIndex);
if (!/grid-template-columns:\s*repeat\(auto-fit,\s*minmax\(86px,\s*1fr\)\)/.test(mobileActionsRule)) {
  failures.push("mobile current-task actions should fit resume, primary and secondary controls without leaving empty columns");
}

const continuityRule = findRule(".shell-context__continuity");
if (!/grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/.test(continuityRule)) {
  failures.push("desktop world pulse row should keep four continuity signals in one scan row");
}

const pulseRule = findRule(".shell-context__pulse");
if (!/display:\s*grid/.test(pulseRule) || !/text-align:\s*left/.test(pulseRule)) {
  failures.push("world pulse cards should keep compact information-sign layout");
}

const mobileContinuityRule = findRule(".shell-context__continuity", mobileIndex);
if (!/grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/.test(mobileContinuityRule)) {
  failures.push("mobile world pulse row should collapse into two readable columns");
}

const mobilePulseRule = findRule(".shell-context__pulse", mobileIndex);
if (!/min-height:\s*0/.test(mobilePulseRule)) {
  failures.push("mobile world pulse cards should not force tall rows");
}

const narrowOverrides = css.slice(css.indexOf("@media (max-width: 520px)"));
if (/\.world-nav\s*\{[^}]*grid-template-columns:\s*repeat\((2|3),\s*minmax\(0,\s*1fr\)\)/s.test(narrowOverrides)) {
  failures.push("narrow mobile overrides should not expand the world nav back to 3+ rows");
}

if (failures.length > 0) {
  console.error("AppShell mobile layout check failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("AppShell mobile layout keeps world navigation compact and complete.");
