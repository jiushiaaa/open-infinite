import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/WorldlineDossierPage.tsx", "utf8");
const css = readFileSync("src/components/worldlineDossier.css", "utf8");

assert(
  page.includes("scrollToWorldlineItem"),
  "worldline dossier page should expose direct scroll actions",
);
assert(
  page.includes('className="worldline-mobile-guide"'),
  "worldline mobile guide should be present",
);
assert(
  page.indexOf('className="worldline-mobile-guide"') <
    page.indexOf('className="worldline-command"'),
  "worldline mobile guide should appear before the full workflow summary",
);
assert(
  page.indexOf('className="worldline-mobile-guide"') < page.indexOf("<WorldRunway"),
  "worldline mobile guide should appear before the explanatory runway",
);
for (const label of ["回放", "看代偿", "看任务", "长线卷"]) {
  assert(page.includes(label), `worldline mobile guide should include ${label}`);
}
for (const targetClass of [
  "worldline-actions-section",
  "worldline-consequence-section",
  "worldline-task-section",
]) {
  assert(page.includes(targetClass), `worldline dossier page should keep ${targetClass}`);
}
assert(
  css.includes(".worldline-mobile-guide") && css.includes("display: none"),
  "worldline mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.worldline-mobile-guide[\s\S]*display: grid/.test(css),
  "worldline mobile guide should be visible on mobile widths",
);

console.log("worldline dossier ux structure ok");
