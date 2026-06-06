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
