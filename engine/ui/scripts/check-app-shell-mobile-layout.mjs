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

if (
  !appShell.includes('className="skip-link"') ||
  !appShell.includes('href="#main-content"') ||
  !appShell.includes("跳到当前页面内容")
) {
  failures.push("AppShell should expose a keyboard skip link before dense world navigation");
}

if (!appShell.includes('id="main-content"') || !appShell.includes('className="shell__body"')) {
  failures.push("AppShell main content should expose a stable #main-content target");
}

if (!appShell.includes('id="main-content"') || !appShell.includes("tabIndex={-1}")) {
  failures.push("main content skip target should be programmatically focusable");
}

if (!appShell.includes('aria-label="当前页面内容"')) {
  failures.push("main content skip target should expose a clear Chinese accessible name");
}

const skipLinkRule = findRule(".skip-link");
if (
  !/position:\s*fixed/.test(skipLinkRule) ||
  !/transform:\s*translateY\(calc\(-100%\s*-\s*var\(--space-3\)\)\)/.test(skipLinkRule) ||
  !/z-index:\s*100/.test(skipLinkRule)
) {
  failures.push("skip link should stay offscreen until focused while remaining above the app shell");
}

const skipLinkFocusRule = findRule(".skip-link:focus-visible");
if (!/transform:\s*translateY\(0\)/.test(skipLinkFocusRule)) {
  failures.push("skip link should return onscreen on keyboard focus");
}

const brandFocusRule = findRule(".brand:focus-visible");
if (!/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.48\)/.test(brandFocusRule) || !/outline-offset:\s*3px/.test(brandFocusRule)) {
  failures.push("brand button should expose a clear keyboard focus ring");
}

const worldNavFocusRule = findRule(".world-nav button:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.48\)/.test(worldNavFocusRule) ||
  !/outline-offset:\s*2px/.test(worldNavFocusRule) ||
  !/background:\s*var\(--paper-sunken\)/.test(worldNavFocusRule)
) {
  failures.push("world navigation buttons should expose a visible keyboard focus state");
}

const topbarButtonFocusRule = findRule(".topbar__right > .btn:focus-visible");
if (!/outline:\s*2px solid rgba\(74,\s*124,\s*99,\s*0\.44\)/.test(topbarButtonFocusRule) || !/outline-offset:\s*2px/.test(topbarButtonFocusRule)) {
  failures.push("topbar utility buttons should expose a visible keyboard focus state");
}

const journeyItemFocusRule = findRule(".world-workspace-shell__journey-item:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.46\)/.test(journeyItemFocusRule) ||
  !/outline-offset:\s*2px/.test(journeyItemFocusRule) ||
  !/background:\s*var\(--paper-sunken\)/.test(journeyItemFocusRule)
) {
  failures.push("WorldWorkspaceShell journey buttons should expose a visible keyboard focus state");
}

const dossierButtonFocusRule = findRule(".shell-context__dossiers button:focus-visible");
if (
  !/outline:\s*2px solid rgba\(74,\s*124,\s*99,\s*0\.44\)/.test(dossierButtonFocusRule) ||
  !/outline-offset:\s*2px/.test(dossierButtonFocusRule) ||
  !/background:\s*var\(--jade-wash\)/.test(dossierButtonFocusRule)
) {
  failures.push("WorldWorkspaceShell dossier buttons should expose a visible keyboard focus state");
}

const stageButtonFocusRule = findRule(".shell-context__stages button:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.44\)/.test(stageButtonFocusRule) ||
  !/outline-offset:\s*2px/.test(stageButtonFocusRule) ||
  !/background:\s*rgba\(255,\s*252,\s*244,\s*0\.9\)/.test(stageButtonFocusRule) ||
  !/color:\s*var\(--ink\)/.test(stageButtonFocusRule)
) {
  failures.push("world experience stage rail buttons should expose a visible keyboard focus state");
}

const mobileSummaryFocusRule = findRule(".world-workspace-shell__mobile-nav summary:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.46\)/.test(mobileSummaryFocusRule) ||
  !/outline-offset:\s*2px/.test(mobileSummaryFocusRule) ||
  !/background:\s*rgba\(255,\s*252,\s*244,\s*0\.9\)/.test(mobileSummaryFocusRule)
) {
  failures.push("mobile world navigation summary should expose a visible keyboard focus state");
}

const focusChipFocusRule = findRule(".world-workspace-shell__focus-chip:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.42\)/.test(focusChipFocusRule) ||
  !/outline-offset:\s*2px/.test(focusChipFocusRule) ||
  !/border-color:\s*rgba\(141,\s*50,\s*37,\s*0\.28\)/.test(focusChipFocusRule) ||
  !/background:\s*rgba\(255,\s*252,\s*244,\s*0\.86\)/.test(focusChipFocusRule)
) {
  failures.push("focused scan band chips should match the paper hover affordance on keyboard focus");
}

const workspaceCardFocusRule = findRule(".shell-context__workspace-card:focus-visible");
if (
  !/outline:\s*2px solid rgba\(141,\s*50,\s*37,\s*0\.48\)/.test(workspaceCardFocusRule) ||
  !/outline-offset:\s*2px/.test(workspaceCardFocusRule) ||
  !/border-color:\s*rgba\(141,\s*50,\s*37,\s*0\.28\)/.test(workspaceCardFocusRule) ||
  !/background:[\s\S]*rgba\(255,\s*252,\s*244,\s*0\.88\)/.test(workspaceCardFocusRule)
) {
  failures.push("workspace pointer cards should keep the paper hover affordance on keyboard focus");
}

const handoffCardFocusRule = findRule(".shell-context__handoff-card:focus-visible");
if (
  !/outline:\s*2px solid rgba\(181,\s*131,\s*58,\s*0\.42\)/.test(handoffCardFocusRule) ||
  !/outline-offset:\s*2px/.test(handoffCardFocusRule) ||
  !/border-color:\s*rgba\(141,\s*50,\s*37,\s*0\.24\)/.test(handoffCardFocusRule) ||
  !/background:[\s\S]*rgba\(255,\s*252,\s*244,\s*0\.86\)/.test(handoffCardFocusRule)
) {
  failures.push("state handoff cards should keep the paper hover affordance on keyboard focus");
}

const pulseFocusRule = findRule(".shell-context__pulse:focus-visible");
if (
  !/outline:\s*2px solid rgba\(74,\s*124,\s*99,\s*0\.44\)/.test(pulseFocusRule) ||
  !/outline-offset:\s*2px/.test(pulseFocusRule) ||
  !/border-color:\s*rgba\(74,\s*124,\s*99,\s*0\.34\)/.test(pulseFocusRule) ||
  !/background:\s*var\(--jade-wash\)/.test(pulseFocusRule)
) {
  failures.push("world pulse cards should keep the jade hover affordance on keyboard focus");
}

for (const activeKey of [
  "anchor",
  "tianming",
  "sandbox",
  "reading",
  "longline",
  "worldline",
  "lens",
  "author",
  "workspace",
]) {
  if (!appShell.includes(`aria-current={active === "${activeKey}" ? "page" : undefined}`)) {
    failures.push(`topbar ${activeKey} navigation should expose aria-current for the active world route`);
  }
}

for (const activeRoute of ["characterVolume", "factionVolume", "eventPerspective"]) {
  if (!appShell.includes(`route.name === "${activeRoute}"`) || !appShell.includes('aria-current="page"')) {
    failures.push(`topbar ${activeRoute} route chip should expose aria-current when shown as active`);
  }
}

if (!workspaceShell) {
  failures.push("WorldWorkspaceShell component should exist as the shared world workspace shell");
}

if (!workspaceShell.includes("世界工作区壳") || !workspaceShell.includes("世界旅程总线")) {
  failures.push("WorldWorkspaceShell should name the shared shell and expose a clear journey bus");
}

if (
  !workspaceShell.includes("world-workspace-shell__desktop-nav-top") ||
  !workspaceShell.includes("world-workspace-shell__desktop-nav-rest")
) {
  failures.push("WorldWorkspaceShell should keep the full desktop navigation outside the mobile drawer");
}

if (
  !workspaceShell.includes("<details className=\"world-workspace-shell__mobile-nav\"") ||
  !workspaceShell.includes("world-workspace-shell__mobile-nav-body") ||
  !workspaceShell.includes("展开世界导航")
) {
  failures.push("WorldWorkspaceShell should collapse the global world navigation behind a mobile details drawer");
}

for (const [selector, message] of [
  [
    '<nav className="world-workspace-shell__journey" aria-label="世界旅程总线"',
    "WorldWorkspaceShell journey bus should be a named navigation landmark",
  ],
  [
    '<nav className="shell-context__workspace" aria-label="世界工作区总览"',
    "WorldWorkspaceShell workspace summary should be a named navigation landmark",
  ],
  [
    '<nav className="shell-context__handoffs" aria-label="世界状态预告"',
    "WorldWorkspaceShell state handoffs should be a named navigation landmark",
  ],
  [
    '<nav className="shell-context__continuity" aria-label="世界脉搏"',
    "WorldWorkspaceShell pulse row should be a named navigation landmark",
  ],
  [
    '<nav className="shell-context__stages" aria-label="世界体验轨道"',
    "WorldWorkspaceShell stage rail should be a named navigation landmark",
  ],
  [
    '<nav className="shell-context__dossiers" aria-label="世界卷宗速览"',
    "WorldWorkspaceShell dossier rail should stay a named navigation landmark",
  ],
]) {
  if (!workspaceShell.includes(selector)) {
    failures.push(message);
  }
}

if (
  !workspaceShell.includes(
    '<details className="world-workspace-shell__mobile-nav" aria-label="移动端世界导航"',
  )
) {
  failures.push("mobile world navigation drawer should expose an accessible navigation label");
}

if (
  workspaceShell.indexOf("shell-context__taskbar") === -1 ||
  workspaceShell.indexOf("world-workspace-shell__desktop-nav-top") === -1 ||
  workspaceShell.indexOf("shell-context__taskbar") > workspaceShell.indexOf("world-workspace-shell__desktop-nav-top")
) {
  failures.push("shared shell should promote the current-task scan band before dense world navigation");
}

if (
  !workspaceShell.includes("world-workspace-shell__focus-band") ||
  !workspaceShell.includes("world-workspace-shell__focus-map") ||
  !workspaceShell.includes("世界扫读带") ||
  !workspaceShell.includes("现在先看这一条")
) {
  failures.push("WorldWorkspaceShell should promote a focused scan band before secondary navigation");
}

if (
  workspaceShell.indexOf("world-workspace-shell__focus-band") === -1 ||
  workspaceShell.indexOf("world-workspace-shell__desktop-nav-top") === -1 ||
  workspaceShell.indexOf("world-workspace-shell__focus-band") > workspaceShell.indexOf("world-workspace-shell__desktop-nav-top")
) {
  failures.push("the focused scan band should appear before the dense desktop navigation deck");
}

if (
  !workspaceShell.includes("旅程入口") ||
  !workspaceShell.includes("世界线档案") ||
  !workspaceShell.includes("为什么建议这步")
) {
  failures.push("workspace pointer cards should read as secondary journey pointers, not another primary task row");
}

if (!workspaceShell.includes("routeContext.stages.map") || !workspaceShell.includes("routeContext.dossiers.map")) {
  failures.push("WorldWorkspaceShell should keep stage and dossier navigation in the shared shell");
}

if (!workspaceShell.includes('aria-current={stage.status === "active" ? "step" : undefined}')) {
  failures.push("WorldWorkspaceShell stage navigation should expose aria-current=step for the active journey stage");
}

if (!workspaceShell.includes('aria-current={dossier.status === "active" ? "page" : undefined}')) {
  failures.push("WorldWorkspaceShell dossier navigation should expose aria-current=page for the active dossier");
}

if (!workspaceShell.includes("import { preloadRoutePage } from \"../routePagePreload\";")) {
  failures.push("WorldWorkspaceShell should reuse route page preloading for global shell navigation");
}

if (!workspaceShell.includes("const routeIntent = (target?: Route) => ({")) {
  failures.push("WorldWorkspaceShell should centralize optional route prefetch handlers");
}

for (const handler of ["onMouseEnter", "onFocus", "onPointerDown"]) {
  if (!workspaceShell.includes(`${handler}: () => target && preloadRoutePage(target)`)) {
    failures.push(`WorldWorkspaceShell routeIntent should preload on ${handler}`);
  }
}

for (const routeSource of [
  "stage.route",
  "activeStageRoute",
  "worldlineDossierRoute",
  "routeContext.primaryRoute",
  "routeContext.secondaryRoute",
  "handoff.route",
  "signal.route",
  "dossier.route",
]) {
  if (!workspaceShell.includes(`...routeIntent(${routeSource})`)) {
    failures.push(`WorldWorkspaceShell should prefetch ${routeSource} before click`);
  }
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
  !workspaceShell.includes("为什么建议这步")
) {
  failures.push("world workspace summary should explain stage, worldline and next-step rationale");
}

if (!workspaceShell.includes("navigate(routeContext.primaryRoute)")) {
  failures.push("next-step summary card should execute the primary route");
}

if (
  !workspaceShell.includes("activateShellAction") ||
  !workspaceShell.includes("findScrollableParent") ||
  !workspaceShell.includes("routeContext.primaryTargetId") ||
  !workspaceShell.includes("scrollIntoView({ behavior: \"smooth\", block: \"start\" })") ||
  !workspaceShell.includes("scrollTo({") ||
  !workspaceShell.includes("window.requestAnimationFrame")
) {
  failures.push("primary shell actions should support same-route anchors inside scrollable page containers like the sandbox runner");
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
if (!/grid-template-areas:[^}]*taskbar[^}]*mobile-nav/s.test(shellContextRule)) {
  failures.push("AppShell context grid should give the current-task row and mobile drawer their own areas");
}

const desktopNavTopRule = findRule(".world-workspace-shell__desktop-nav-top");
if (!/display:\s*contents/.test(desktopNavTopRule)) {
  failures.push("desktop navigation wrappers should use display: contents so existing grid areas stay intact");
}

const desktopNavRestRule = findRule(".world-workspace-shell__desktop-nav-rest");
if (!/display:\s*contents/.test(desktopNavRestRule)) {
  failures.push("desktop rest navigation wrapper should use display: contents so existing grid areas stay intact");
}

const mobileNavRule = findRule(".world-workspace-shell__mobile-nav");
if (!/display:\s*none/.test(mobileNavRule)) {
  failures.push("desktop layout should hide the mobile world navigation drawer");
}

const mobileNavBodyRule = findRule(".world-workspace-shell__mobile-nav-body");
if (!/display:\s*grid/.test(mobileNavBodyRule)) {
  failures.push("mobile drawer body should be ready to stack preserved world navigation sections");
}

const taskbarRule = findRule(".shell-context__taskbar");
if (
  !/display:\s*grid/.test(taskbarRule) ||
  !/grid-template-columns:\s*minmax\(170px,\s*0\.55fr\)\s+minmax\(0,\s*1fr\)\s+auto/.test(taskbarRule)
) {
  failures.push("desktop current-task row should combine orientation, explanation and actions in one scan band");
}

const focusBandRule = findRule(".world-workspace-shell__focus-band");
if (
  !/background:[^}]*rgba\(255,\s*252,\s*244,\s*0\.9\)/s.test(focusBandRule) ||
  !/box-shadow:\s*var\(--shadow-card\)/.test(focusBandRule)
) {
  failures.push("focused scan band should be visually promoted with restrained paper contrast");
}

const focusMapRule = findRule(".world-workspace-shell__focus-map");
if (!/display:\s*grid/.test(focusMapRule) || !/grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/.test(focusMapRule)) {
  failures.push("focus map should keep current stage and worldline in a compact two-item row");
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

const mobileDesktopNavTopRule = findRule(".world-workspace-shell__desktop-nav-top", mobileIndex);
if (!/display:\s*none/.test(mobileDesktopNavTopRule)) {
  failures.push("mobile layout should hide the expanded desktop navigation before showing the drawer");
}

const mobileDesktopNavRestRule = findRule(".world-workspace-shell__desktop-nav-rest", mobileIndex);
if (!/display:\s*none/.test(mobileDesktopNavRestRule)) {
  failures.push("mobile layout should hide the desktop navigation remainder before showing the drawer");
}

const mobileDrawerRule = findRule(".world-workspace-shell__mobile-nav", mobileIndex);
if (!/display:\s*grid/.test(mobileDrawerRule) || !/grid-area:\s*mobile-nav/.test(mobileDrawerRule)) {
  failures.push("mobile world navigation drawer should appear as its own grid area after the current task");
}

const mobileSummaryRule = findRule(".world-workspace-shell__mobile-nav summary", mobileIndex);
if (!/cursor:\s*pointer/.test(mobileSummaryRule) || !/display:\s*grid/.test(mobileSummaryRule)) {
  failures.push("mobile drawer summary should be a clear tappable control");
}

const mobileNavBodyMobileRule = findRule(".world-workspace-shell__mobile-nav-body", mobileIndex);
if (!/display:\s*grid/.test(mobileNavBodyMobileRule) || !/gap:\s*var\(--space-2\)/.test(mobileNavBodyMobileRule)) {
  failures.push("mobile drawer body should stack every preserved world navigation section with readable spacing");
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
