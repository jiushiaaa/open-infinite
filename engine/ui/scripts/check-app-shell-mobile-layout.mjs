import { readFileSync } from "node:fs";
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

if (!appShell.includes("shell-context__workspace")) {
  failures.push("AppShell should render the world workspace summary inside the shared context bar");
}

if (
  !appShell.includes("当前环节") ||
  !appShell.includes("承接世界线") ||
  !appShell.includes("下一步为什么做")
) {
  failures.push("world workspace summary should explain stage, worldline and next-step rationale");
}

const contextPath = resolve("src/worldRouteContext.ts");
const context = readFileSync(contextPath, "utf8");
if (!context.includes("workspaceSummary")) {
  failures.push("world route context should provide semantic summary data for AppShell");
}

const workspaceRule = findRule(".shell-context__workspace");
if (!/grid-template-columns:\s*0\.75fr\s+0\.75fr\s+minmax\(0,\s*1\.5fr\)/.test(workspaceRule)) {
  failures.push("desktop workspace summary should keep stage, worldline and next-step rationale in one compact row");
}

const mobileWorkspaceRule = findRule(".shell-context__workspace", mobileIndex);
if (!/grid-template-columns:\s*1fr/.test(mobileWorkspaceRule)) {
  failures.push("mobile workspace summary should stack into one column instead of squeezing text");
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
