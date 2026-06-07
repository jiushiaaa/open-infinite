import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const component = readFileSync(resolve("src/components/WorldRunway.tsx"), "utf8");
const css = readFileSync(resolve("src/components/worldRunway.css"), "utf8");

const failures = [];

function findRule(selector, fromIndex = 0) {
  const selectorIndex = css.indexOf(selector, fromIndex);
  if (selectorIndex === -1) return "";

  const openIndex = css.indexOf("{", selectorIndex);
  if (openIndex === -1) return "";

  let depth = 0;
  for (let index = openIndex; index < css.length; index += 1) {
    const char = css[index];
    if (char === "{") depth += 1;
    else if (char === "}") {
      depth -= 1;
      if (depth === 0) return css.slice(openIndex + 1, index);
    }
  }

  return "";
}

if (!component.includes("const primaryAction = actions.find((action) => action.primary) ?? actions[0]")) {
  failures.push("WorldRunway should promote the explicit primary action, falling back to the first action");
}

if (!component.includes("const secondaryActions = actions.filter((action) => action !== primaryAction)")) {
  failures.push("WorldRunway should preserve non-primary actions as secondary exits");
}

if (!component.includes("world-runway__handoff") || !component.includes("world-runway__next-action")) {
  failures.push("WorldRunway should render a dedicated next-step handoff area");
}

if (!component.includes("建议先做")) {
  failures.push("WorldRunway next-step handoff should use clear Chinese product copy");
}

if (!component.includes("secondaryActions.map")) {
  failures.push("WorldRunway should keep rendering secondary actions after promoting the primary action");
}

const runwayRule = findRule(".world-runway");
if (!/grid-template-columns:\s*minmax\(240px,\s*0\.85fr\)\s+minmax\(320px,\s*1\.2fr\)\s+minmax\(240px,\s*0\.9fr\)/.test(runwayRule)) {
  failures.push("WorldRunway desktop layout should keep intro, steps and handoff in three balanced columns");
}

const handoffRule = findRule(".world-runway__handoff");
if (!/display:\s*grid/.test(handoffRule) || !/grid-template-rows:\s*auto\s+1fr/.test(handoffRule)) {
  failures.push("WorldRunway handoff should stack promoted next-step and secondary actions");
}

const handoffIndex = css.indexOf(".world-runway__handoff");
const nextActionRule = findRule(".world-runway__next-action", handoffIndex);
if (
  !/border-color:\s*rgba\(74,\s*124,\s*99,\s*0\.42\)/.test(nextActionRule) ||
  !/min-height:\s*96px/.test(nextActionRule)
) {
  failures.push("WorldRunway next-step card should be visually promoted without changing the product palette");
}

const mobileIndex = css.indexOf("@media (max-width: 680px)");
if (mobileIndex === -1) {
  failures.push("WorldRunway should keep a narrow mobile media query");
}

const mobileNextActionRule = findRule(".world-runway__next-action", mobileIndex);
if (!/min-height:\s*0/.test(mobileNextActionRule)) {
  failures.push("WorldRunway next-step card should not force tall mobile rows");
}

if (failures.length > 0) {
  console.error("WorldRunway UX check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("WorldRunway next-step handoff structure ok.");
